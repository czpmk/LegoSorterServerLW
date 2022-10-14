import logging
import time
from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread

from lego_sorter_server.generated import LegoSorterLW_pb2_grpc
from lego_sorter_server.generated.LegoSorterLW_pb2 import SorterConfiguration, ListOfBoundingBoxesWithIndexes, \
    BoundingBoxWithIndex
from lego_sorter_server.generated.Messages_pb2 import ImageRequest, BoundingBox, Empty
from lego_sorter_server.service.ImageProtoUtils import ImageProtoUtils
from lego_sorter_server.service.BrickCategoryConfig import BrickCategoryConfig
from lego_sorter_server.sorter.SortingProcessor import SortingProcessor


class LegoSorterServiceLW(LegoSorterLW_pb2_grpc.LegoSorterLWServicer):

    PORT = 50052

    def __init__(self, brickCategoryConfig: BrickCategoryConfig):
        self.sortingProcessor = SortingProcessor(brickCategoryConfig)
        self.deviceIP = None

    def processNextImage(self, request: ImageRequest, context) -> ListOfBoundingBoxesWithIndexes:
        start_time = time.time()
        logging.info("[LegoSorterServiceLW] Got an image request. Processing...")
        image = ImageProtoUtils.prepare_image(request)
        current_state = self.sortingProcessor.process_next_image(image)

        response = self._prepare_response_from_sorter_state(current_state=current_state)
        elapsed_milliseconds = int(1000 * (time.time() - start_time))
        logging.info(f"[LegoSorterServiceLW] Processing the request took {elapsed_milliseconds} milliseconds.")

        return response

    def startMachine(self, request: Empty, context):
        self.sortingProcessor.start_machine()

        return Empty()

    def stopMachine(self, request: Empty, context):
        self.sortingProcessor.stop_machine()

        return Empty()

    def getConfiguration(self, request, context) -> SorterConfiguration:
        return super().getConfiguration(request, context)

    def updateConfiguration(self, request: SorterConfiguration, context):
        self.sortingProcessor.set_machine_speed(request.speed)
        logging.info(f"[LegoSorterServiceLW] Setting new client IP: {request.deviceIP}.")
        self.deviceIP = request.deviceIP
        return Empty()

    @staticmethod
    def _prepare_response_from_sorter_state(current_state: dict) -> ListOfBoundingBoxesWithIndexes:
        bbs_with_indexes = []
        for key, value in current_state.items():
            bb = BoundingBox()
            bb.ymin, bb.xmin, bb.ymax, bb.xmax = value[0]
            bb.label = value[1]
            bb.score = value[2]

            bb_index = BoundingBoxWithIndex()
            bb_index.bb.CopyFrom(bb)
            bb_index.index = key

            bbs_with_indexes.append(bb_index)

        response = ListOfBoundingBoxesWithIndexes()
        response.packet.extend(bbs_with_indexes)

        return response


    def send_image_order(self):
        if self.deviceIP is not None and self.deviceIP != "":
            sock = socket(AF_INET, SOCK_DGRAM)  # UDP Socket
            logging.info(f"[LegoSorterServiceLW] Sending image order to client {self.deviceIP}.")
            sock.sendto(bytes("IMAGE_ORDER", 'utf-8'), (self.deviceIP, self.PORT))

