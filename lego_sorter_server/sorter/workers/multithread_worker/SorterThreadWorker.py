import logging
from queue import Empty
from typing import Tuple, Callable

from lego_sorter_server.common.AnalysisResults import AnalysisResult
from lego_sorter_server.sorter.workers.multithread_worker.ThreadWorker import ThreadWorker


class SorterThreadWorker(ThreadWorker):
    def __init__(self):
        super().__init__()

    def start(self):
        self.sorter_controller.run_conveyor()
        super().start()

    def stop(self):
        super().stop()
        self.sorter_controller.stop_conveyor()

    def enqueue(self, item: Tuple[int, AnalysisResult]):
        super().enqueue(*item)

    def set_callback(self, callback: Callable[[int], None]):
        self.callback = callback

    def run(self):
        while self.running:
            try:
                brick_id, analysis_result = self.input_queue.get(timeout=0.5)
            except Empty:
                continue

            self.sorter_controller.on_brick_recognized(analysis_result)
            logging.debug('[{0}] Bricks {1} sorted.'.format(self._name, brick_id))

            self.callback(brick_id)
