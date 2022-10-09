from lego_sorter_server.generated import LegoSorterAsync_pb2_grpc
from lego_sorter_server.generated.Messages_pb2 import ImageRequest, BoundingBox, Empty
from lego_sorter_server.service.BrickCategoryConfig import BrickCategoryConfig
from lego_sorter_server.sorter.SortingAsyncProcessor import SortingAsyncProcessor


class LegoSorterAsyncService(LegoSorterAsync_pb2_grpc.LegoSorterAsyncServicer):

    def __init__(self, brick_category_config: BrickCategoryConfig):
        self.sortingProcessor = SortingAsyncProcessor(brick_category_config)

    def start(self, request: Empty, context):
        self.sortingProcessor.start()

    def stop(self, request: Empty, context):
        self.sortingProcessor.stop()

    def photoRequestStream(self, request, context):
        pass
