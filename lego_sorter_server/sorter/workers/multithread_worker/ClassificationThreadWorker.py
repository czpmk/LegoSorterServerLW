import logging
from tkinter import Image
from typing import Tuple, Callable, Optional

from lego_sorter_server.common.ClassificationResults import ClassificationResult, ClassificationResultsList
from lego_sorter_server.common.DetectionResults import DetectionResultsList
from lego_sorter_server.sorter.workers.DetectionWorker import DetectionWorker
from lego_sorter_server.sorter.workers.multithread_worker.ThreadWorker import ThreadWorker


class ClassificationThreadWorker(ThreadWorker):
    def __init__(self):
        super().__init__()
        self.target_method: Callable[[int, int, Image], None] = self.__classify
        self._head_brick_idx: int = 0

    def enqueue(self, item: Tuple[int, int, Image]):
        self.input_queue.put(item)

    def set_callback(self, callback: Callable[[int, int, ClassificationResultsList], None]):
        self.callback = callback

    def set_head_brick_idx(self, head_brick_idx: int):
        self._head_brick_idx = head_brick_idx

    def __classify(self, brick_id: int, detection_id: int, image: Image):
        # brick_id < head_idx ==> brick has already been sorted (passed the camera line)
        if brick_id < self._head_brick_idx:
            logging.info('[{0}] SKIPPING - BRICK ALREADY PASSED THE CAMERA LINE'.format(self._type(), brick_id))
            return

        classification_results_list: ClassificationResultsList = self.analysis_service.classify([image])

        logging.debug('[{0}] Classification result: {1}, '
                      'score: {2}.'.format(self._type(),
                                           classification_results_list[0].classification_class,
                                           classification_results_list[0].classification_score))
        self.callback(brick_id, detection_id, classification_results_list)
