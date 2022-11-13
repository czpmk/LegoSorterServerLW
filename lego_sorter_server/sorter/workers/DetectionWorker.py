import logging
from queue import Queue
from typing import Callable, Tuple

from PIL.Image import Image

from lego_sorter_server.analysis.AnalysisService import AnalysisService
from lego_sorter_server.common.DetectionResults import DetectionResultsList
from lego_sorter_server.sorter.workers.Worker import Worker


class DetectionWorker(Worker):
    def __init__(self, analysis_service: AnalysisService, callback: Callable[[int, DetectionResultsList], None]):
        super().__init__()

        self.analysis_service: AnalysisService = analysis_service
        self.set_callback(callback)
        self.set_target_method(self.__detect)

    def enqueue(self, item: Tuple[int, Image]):
        super(DetectionWorker, self).enqueue(item)

    def __detect(self, image_id: int, image: Image):
        detection_results_list: DetectionResultsList = self.analysis_service.detect(image)

        logging.debug('[{0}] Bricks detected {1}.'.format(self._type(), len(detection_results_list)))
        self._callback(image_id, detection_results_list)

        # detection_results_list.sort(key=lambda x: x.detection_box.y_min, reverse=True)
        #
        # cropped_images_with_results: List[Tuple[Image, DetectionResult]] = [
        #     (DetectionUtils.crop_with_margin_from_detection_box(image, detection_result),
        #      detection_result)
        #     for detection_result in detection_results_list
        # ]
        #
        # self._callback(cropped_images_with_results)
