import logging
import time

from lego_sorter_server.generated.Messages_pb2 import ImageRequest
from lego_sorter_server.generated import LegoAsyncSorter_pb2_grpc
from lego_sorter_server.generated.Messages_pb2 import Empty, SorterConfiguration
from lego_sorter_server.service.BrickCategoryConfig import BrickCategoryConfig
from lego_sorter_server.service.ImageProtoUtils import ImageProtoUtils
from lego_sorter_server.sorter.AsyncSortingProcessor import AsyncSortingProcessor


class LegoAsyncSorterService(LegoAsyncSorter_pb2_grpc.LegoAsyncSorterServicer):

    def __init__(self, brick_category_config: BrickCategoryConfig):
        self.sortingProcessor = AsyncSortingProcessor(brick_category_config)

    def processImage(self, request: ImageRequest, context):
        image = ImageProtoUtils.prepare_image(request)
        self.sortingProcessor.enqueue_image(image)
        return Empty()

    def start(self, request: Empty, context):
        self.sortingProcessor.start_sorting()

        return Empty()

    def stop(self, request: Empty, context):
        self.sortingProcessor.stop_sorting()

        return Empty()

    def getConfiguration(self, request, context) -> SorterConfiguration:
        return super().getConfiguration(request, context)

    def updateConfiguration(self, request: SorterConfiguration, context):
        logging.info("[LegoAsyncSorterService] Setting machine speed to: {0}.".format(request.speed))
        self.sortingProcessor.set_machine_speed(request.speed)

        return Empty()
