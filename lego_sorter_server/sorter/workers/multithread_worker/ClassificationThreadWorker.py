import logging
from queue import Empty
from tkinter import Image
from typing import Tuple, Callable, List

from lego_sorter_server.common.ClassificationResults import ClassificationResultsList, ClassificationResult
from lego_sorter_server.sorter.workers.multithread_worker.ThreadWorker import ThreadWorker


class ClassificationThreadWorker(ThreadWorker):
    def __init__(self):
        super().__init__()
        # self.target_method: Callable[[int, int, Image], None] = self.__classify
        # self._head_brick_idx: int = 0

    def enqueue(self, item: Tuple[int, int, Image]):
        super().enqueue(*item)

    def set_callback(self, callback: Callable[[List[Tuple[int, int, ClassificationResult]]], None]):
        self.callback = callback

    # def __classify(self, brick_id: int, detection_id: int, image: Image):
    #     # brick_id < head_idx ==> brick has already been sorted (passed the camera line)
    #     if brick_id < self._head_brick_idx:
    #         logging.info('[{0}] SKIPPING - BRICK {1} ALREADY PASSED THE CAMERA LINE'.format(self._name, brick_id))
    #         return
    #
    #     classification_results_list: ClassificationResultsList = self.analysis_service.classify([image])
    #
    #     logging.debug('[{0}] Classification result: {1}, '
    #                   'score: {2}.'.format(self._name,
    #                                        classification_results_list[0].classification_class,
    #                                        classification_results_list[0].classification_score))
    #     self.callback(brick_id, detection_id, classification_results_list)

    def run(self):
        while self.running:
            inputs: List[Tuple[int, int, Image]] = []
            try:
                inputs.append(self.input_queue.get(timeout=0.01))
            except Empty:
                continue

            classification_results_list: ClassificationResultsList = self.analysis_service.classify(
                [x[2] for x in inputs]
            )

            logging.debug(
                '[{0}] Classification results received: {1}.'.format(self._name, len(classification_results_list)))

            assert len(inputs) == len(classification_results_list)

            # Format: List[Tuple[brick_id, detection_id, image]]
            self.callback(
                [(inputs[idx][0], inputs[idx][1], classification_results_list[idx]) for idx in range(len(inputs))]
            )
