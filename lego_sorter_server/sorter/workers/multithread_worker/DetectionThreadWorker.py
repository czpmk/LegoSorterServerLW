import logging
from queue import Empty
from tkinter import Image
from typing import Tuple, Callable

from lego_sorter_server.common.DetectionResults import DetectionResultsList
from lego_sorter_server.sorter.workers.multithread_worker.ThreadWorker import ThreadWorker


class DetectionThreadWorker(ThreadWorker):
    def __init__(self):
        super().__init__()

    def enqueue(self, item: Tuple[int, Image]):
        super().enqueue(*item)

    def set_callback(self, callback: Callable[[int, DetectionResultsList], None]):
        self.callback = callback

    def run(self):
        while self.running:
            try:
                image_idx, image = self.input_queue.get(timeout=0.5)
            except Empty:
                continue

            detection_results_list: DetectionResultsList = self.analysis_service.detect(image)

            logging.debug('[{0}] Bricks detected {1} at image {2}.'.format(self._name, len(detection_results_list),
                                                                           image_idx))
            self.callback(image_idx, detection_results_list)
