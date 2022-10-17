import logging
import time

from lego_sorter_server.generated import LegoAsyncSorter_pb2_grpc
from lego_sorter_server.generated.Messages_pb2 import Empty, SorterConfigurationWithIP
from lego_sorter_server.service.BrickCategoryConfig import BrickCategoryConfig
from lego_sorter_server.sorter.AsyncSortingProcessor import AsyncSortingProcessor


class LegoAsyncSorterService(LegoAsyncSorter_pb2_grpc.LegoAsyncSorterServicer):
    PORT = 50052

    def __init__(self, brick_category_config: BrickCategoryConfig):
        self.sortingProcessor = AsyncSortingProcessor(brick_category_config)
        self.deviceIP: str = ""

    def startMachine(self, request: Empty, context):
        self.sortingProcessor.start_machine()

        return Empty()

    def stopMachine(self, request: Empty, context):
        self.sortingProcessor.stop_machine()

        return Empty()

    def getConfiguration(self, request, context) -> SorterConfigurationWithIP:
        return super().getConfiguration(request, context)

    def updateConfiguration(self, request: SorterConfigurationWithIP, context):
        self.sortingProcessor.set_machine_speed(request.speed)
        logging.info(f"[LegoSorterServiceLW] Setting new client IP: {request.deviceIP}.")
        self.deviceIP = request.deviceIP

        return Empty()
