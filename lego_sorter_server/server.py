import grpc

from concurrent import futures
from lego_sorter_server.generated import LegoSorter_pb2_grpc, LegoCapture_pb2_grpc, LegoAnalysis_pb2_grpc, \
    LegoSorterLW_pb2_grpc
from lego_sorter_server.service.LegoCaptureService import LegoCaptureService
from service.LegoAnalysisService import LegoAnalysisService
from service.LegoSorterService import LegoSorterService
from service.LegoSorterServiceLW import LegoSorterServiceLW

from lego_sorter_server.service.BrickCategoryConfig import BrickCategoryConfig


class Server:

    @staticmethod
    def run(sorterConfig: BrickCategoryConfig):
        options = [('grpc.max_receive_message_length', 100 * 1024 * 1024)]
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=16), options=options)
        LegoSorter_pb2_grpc.add_LegoSorterServicer_to_server(LegoSorterService(sorterConfig), server)
        LegoCapture_pb2_grpc.add_LegoCaptureServicer_to_server(LegoCaptureService(), server)
        LegoAnalysis_pb2_grpc.add_LegoAnalysisServicer_to_server(LegoAnalysisService(), server)
        LegoSorterLW_pb2_grpc.add_LegoSorterLWServicer_to_server(LegoSorterServiceLW(), server)
        server.add_insecure_port('[::]:50051')
        server.start()
        server.wait_for_termination()
