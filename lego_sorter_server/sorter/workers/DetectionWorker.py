import logging
from typing import Callable, Tuple

from PIL.Image import Image

from lego_sorter_server.analysis.AnalysisService import AnalysisService
from lego_sorter_server.common.DetectionResults import DetectionResultsList
from lego_sorter_server.sorter.workers.Worker import Worker

from multiprocessing import Queue
from queue import Empty


class DetectionWorker(Worker):
    def __init__(self, analysis_service: AnalysisService):
        super().__init__()

        self.analysis_service: AnalysisService = analysis_service
        self.set_target_method(self.__detect)

    def enqueue(self, item: Tuple[int, Image]):
        super(DetectionWorker, self).enqueue(item)

    def set_callback(self, callback: Callable[[int, DetectionResultsList], None]):
        self._callback = callback

    def __detect(self, queue_in: Queue, queue_out: Queue):  # image_idx: int, image: Image):
        while self._running:
            try:
                image_idx, image = queue_in.get()

                detection_results_list: DetectionResultsList = self.analysis_service.detect(image)

                logging.debug(
                    '[{0}] Bricks detected {1} at image {2}.'.format(self._type(), len(detection_results_list),
                                                                     image_idx))
                # self._callback(image_idx, detection_results_list)
                queue_out.put((image_idx, detection_results_list))
            except Empty:
                continue
