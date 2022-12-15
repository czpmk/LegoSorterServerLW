import logging
from queue import Empty
from typing import Callable, Tuple

from torch.multiprocessing import Queue

from lego_sorter_server.common.AnalysisResults import AnalysisResult
from lego_sorter_server.sorter.LegoSorterController import LegoSorterController
from lego_sorter_server.sorter.workers.Worker import Worker


class SortingWorker(Worker):
    def __init__(self, sorter_controller: LegoSorterController, multiprocessing: bool):
        super().__init__()
        self._multiprocessing = multiprocessing
        self.sorter_controller: LegoSorterController = sorter_controller
        self.set_target_method(self.__sort)

        self._target_method = self.__sort

    def enqueue(self, item: Tuple[int, AnalysisResult]):
        super(SortingWorker, self).enqueue(item)

    def start(self):
        self.sorter_controller.run_conveyor()
        super(SortingWorker, self).start()

    def stop(self):
        self.sorter_controller.stop_conveyor()
        super(SortingWorker, self).stop()

    def set_callback(self, callback: Callable[[int], None]):
        self._callback = callback

    def __sort(self, queue_in: Queue, queue_out: Queue):  # brick_id: int, analysis_result: AnalysisResult):
        while self._running:
            try:
                brick_id, analysis_result = queue_in.get()
                self.sorter_controller.on_brick_recognized(analysis_result)
                logging.debug('[{0}] Bricks {1} sorted.'.format(self._type(), brick_id))
                queue_out.put((brick_id,))
                # self._callback(brick_id)
            except Empty:
                continue
