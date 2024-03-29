import logging
import time
from typing import Dict

from lego_sorter_server.common.AnalysisResults import AnalysisResult
from lego_sorter_server.generated import LegoSorter_pb2_grpc
from lego_sorter_server.generated.Messages_pb2 import ImageRequest, BoundingBox, Empty, SorterConfiguration, \
    ListOfBoundingBoxesWithIndexes, BoundingBoxWithIndex
from lego_sorter_server.service.ImageProtoUtils import ImageProtoUtils
from lego_sorter_server.service.BrickCategoryConfig import BrickCategoryConfig
from lego_sorter_server.sorter.SortingProcessor import SortingProcessor


class LegoSorterService(LegoSorter_pb2_grpc.LegoSorterServicer):

    def __init__(self, brick_category_config: BrickCategoryConfig, save_images_to_file: bool,
                 reset_state_on_stop: bool):
        self.sortingProcessor = SortingProcessor(brick_category_config)
        self.save_images_to_file = save_images_to_file
        self.reset_state_on_stop = reset_state_on_stop

    def processNextImage(self, request: ImageRequest, context) -> ListOfBoundingBoxesWithIndexes:
        start_time = time.time()
        logging.info("[LegoSorterService] Got an image request. Processing...")
        image = ImageProtoUtils.prepare_image_from_request(request)
        current_state = self.sortingProcessor.process_next_image(image, self.save_images_to_file)

        response = self._prepare_response_from_sorter_state(current_state=current_state)
        elapsed_milliseconds = int(1000 * (time.time() - start_time))
        logging.info(f"[LegoSorterService] Processing the request took {elapsed_milliseconds} milliseconds.")

        return response

    def startMachine(self, request: Empty, context):
        self.sortingProcessor.start_machine()

        return Empty()

    def stopMachine(self, request: Empty, context):
        self.sortingProcessor.stop_machine()

        if self.reset_state_on_stop:
            self.sortingProcessor.reset()

        return Empty()

    def getConfiguration(self, request, context) -> SorterConfiguration:
        return super().getConfiguration(request, context)

    def updateConfiguration(self, request: SorterConfiguration, context):
        self.sortingProcessor.set_machine_speed(request.speed)

        return Empty()

    @staticmethod
    def _prepare_response_from_sorter_state(current_state: Dict[int, AnalysisResult]) -> ListOfBoundingBoxesWithIndexes:
        bbs_with_indexes = []
        for key, value in current_state.items():
            bb = BoundingBox()
            bb.ymin, bb.xmin, bb.ymax, bb.xmax = value.detection_box.to_tuple()
            bb.label = value.classification_class
            bb.score = value.classification_score

            bb_index = BoundingBoxWithIndex()
            bb_index.bb.CopyFrom(bb)
            bb_index.index = key

            bbs_with_indexes.append(bb_index)

        response = ListOfBoundingBoxesWithIndexes()
        response.packet.extend(bbs_with_indexes)

        return response
