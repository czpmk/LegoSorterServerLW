from lego_sorter_server.analysis.AnalysisService import AnalysisService
import logging
import time

from lego_sorter_server.common.DetectionResults import DetectionResultsList
from lego_sorter_server.generated import LegoAnalysis_pb2_grpc
from lego_sorter_server.generated.Messages_pb2 import ImageRequest, ListOfBoundingBoxes
from lego_sorter_server.service.ImageProtoUtils import ImageProtoUtils


class LegoAnalysisService(LegoAnalysis_pb2_grpc.LegoAnalysisServicer):
    def __init__(self):
        self.analysis_service = AnalysisService()

    def DetectBricks(self, request: ImageRequest, context) -> ListOfBoundingBoxes:
        logging.info("[LegoAnalysisService] Request received, processing...")
        start_time = time.time()

        detection_results: DetectionResultsList = self._detect_bricks(request)
        bbs_list: ListOfBoundingBoxes = ImageProtoUtils.prepare_bbs_response_from_detection_results(detection_results)

        elapsed_millis = int((time.time() - start_time) * 1000)
        logging.info(
            "[LegoAnalysisService] Detecting and preparing response took {:.3f} milliseconds.".format(elapsed_millis))

        return bbs_list

    def DetectAndClassifyBricks(self, request: ImageRequest, context) -> ListOfBoundingBoxes:
        logging.info("[LegoAnalysisService] Request received, processing...")
        start_time = time.time()

        image = ImageProtoUtils.prepare_image(request)
        detection_results, classification_results = self.analysis_service.detect_and_classify(image)
        bb_list: ListOfBoundingBoxes = ImageProtoUtils.prepare_response_from_analysis_results(detection_results,
                                                                                              classification_results)

        elapsed_millis = (time.time() - start_time) * 1000
        logging.info("[LegoAnalysisService] Detecting, classifying and preparing response took "
                     "{:.3f} milliseconds.".format(elapsed_millis))

        return bb_list

    def _detect_bricks(self, request: ImageRequest) -> DetectionResultsList:
        image = ImageProtoUtils.prepare_image(request)
        detection_results: DetectionResultsList = self.analysis_service.detect(image)

        return detection_results
