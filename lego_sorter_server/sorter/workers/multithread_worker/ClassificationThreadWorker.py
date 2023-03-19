import logging
from queue import Empty
from tkinter import Image
from typing import Tuple, Callable, List

from lego_sorter_server.common.ClassificationResults import ClassificationResultsList, ClassificationResult
from lego_sorter_server.sorter.workers.multithread_worker.ThreadWorker import ThreadWorker


class ClassificationThreadWorker(ThreadWorker):
    def __init__(self):
        super().__init__()

    def enqueue(self, item: Tuple[int, int, Image]):
        super().enqueue(*item)

    def set_callback(self, callback: Callable[[List[Tuple[int, int, ClassificationResult]]], None]):
        self.callback = callback

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
