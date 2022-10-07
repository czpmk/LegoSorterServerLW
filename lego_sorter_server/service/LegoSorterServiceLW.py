import logging
import time

from lego_sorter_server.generated import LegoSorter_pb2_grpc, LegoSorterLW_pb2_grpc
from lego_sorter_server.generated.LegoSorter_pb2 import SorterConfiguration, ListOfBoundingBoxesWithIndexes, \
    BoundingBoxWithIndex
from lego_sorter_server.generated.Messages_pb2 import ImageRequest, BoundingBox, Empty
from lego_sorter_server.generated.LegoSorterLW_pb2 import PhotoRequest
from lego_sorter_server.service.ImageProtoUtils import ImageProtoUtils
from lego_sorter_server.service.BrickCategoryConfig import BrickCategoryConfig
from lego_sorter_server.sorter.SortingProcessor import SortingProcessor


class LegoSorterServiceLW(LegoSorterLW_pb2_grpc.LegoSorterLWServicer):

    def __init__(self):
        return


    def startMachine(self, request: Empty, context):
        self.sortingProcessor.start_machine()

        return Empty()

    def stopMachine(self, request: Empty, context):
        self.sortingProcessor.stop_machine()

        return Empty()


    def stopMachine(self, request: Empty, context):
        self.sortingProcessor.stop_machine()

        return Empty()


    def photoRequestStream(self, request: Empty, context):
        for i in range(1,100000):
            time.sleep(0.5)
            logging.info("Sending message")
            message = "Testowanie"
            pr = PhotoRequest()
            message_as_bytes = bytes(str.encode(str(message)))
            pr.test = message_as_bytes
            yield pr
