import logging
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

    def __detect(self, image_idx: int, image: Image):
        detection_results_list: DetectionResultsList = self.analysis_service.detect(image)

        logging.debug('[{0}] Bricks detected {1} at image {2}.'.format(self._type(), len(detection_results_list),
                                                                       image_idx))
        self._callback(image_idx, detection_results_list)
