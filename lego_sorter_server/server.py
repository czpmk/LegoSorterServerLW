import threading

import grpc

from concurrent import futures
from lego_sorter_server.generated import LegoSorter_pb2_grpc, LegoAsyncSorter_pb2_grpc, LegoCapture_pb2_grpc, \
    LegoAnalysis_pb2_grpc
from lego_sorter_server.service.LegoCaptureService import LegoCaptureService
from lego_sorter_server.service.LegoAnalysisService import LegoAnalysisService
from lego_sorter_server.service.LegoSorterService import LegoSorterService
from lego_sorter_server.service.LegoAsyncSorterService import LegoAsyncSorterService

from lego_sorter_server.service.BrickCategoryConfig import BrickCategoryConfig


class Server:

    @staticmethod
    def run(sorter_config: BrickCategoryConfig, save_images_to_file: bool):
        options = [('grpc.max_receive_message_length', 100 * 1024 * 1024)]
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=16), options=options)
        LegoAsyncSorter_pb2_grpc.add_LegoAsyncSorterServicer_to_server(
            LegoAsyncSorterService(sorter_config, save_images_to_file),
            server)
        LegoSorter_pb2_grpc.add_LegoSorterServicer_to_server(LegoSorterService(sorter_config, save_images_to_file),
                                                             server)

        LegoCapture_pb2_grpc.add_LegoCaptureServicer_to_server(LegoCaptureService(), server)
        LegoAnalysis_pb2_grpc.add_LegoAnalysisServicer_to_server(LegoAnalysisService(), server)
        server.add_insecure_port('[::]:50051')
        server.start()
        server.wait_for_termination()
