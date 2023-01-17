import logging
from tkinter import Image
from typing import Tuple, Callable

from lego_sorter_server.common.DetectionResults import DetectionResultsList
from lego_sorter_server.sorter.workers.multithread_worker.ThreadWorker import ThreadWorker


class DetectionThreadWorker(ThreadWorker):
    def __init__(self):
        super().__init__()
        self.target_method: Callable[[int, Image], None] = self.__detect

    def enqueue(self, item: Tuple[int, Image]):
        self.input_queue.put(item)

    def set_callback(self, callback: Callable[[int, DetectionResultsList], None]):
        self.callback = callback

    def __detect(self, image_idx: int, image: Image):
        detection_results_list: DetectionResultsList = self.analysis_service.detect(image)

        logging.debug('[{0}] Bricks detected {1} at image {2}.'.format(self._type(), len(detection_results_list),
                                                                       image_idx))
        self.callback(image_idx, detection_results_list)
