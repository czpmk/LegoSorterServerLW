import logging
from typing import Callable, Tuple

from lego_sorter_server.common.AnalysisResults import AnalysisResult
from lego_sorter_server.sorter.LegoSorterController import LegoSorterController
from lego_sorter_server.sorter.workers.Worker import Worker


class SortingWorker(Worker):
    def __init__(self, sorter_controller: LegoSorterController, callback: Callable[[int], None]):
        super().__init__()

        self.sorter_controller: LegoSorterController = sorter_controller
        self.set_callback(callback)
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

    def __sort(self, brick_id: int, analysis_result: AnalysisResult):
        self.sorter_controller.on_brick_recognized(analysis_result)
        logging.debug('[{0}] Bricks {1} sorted.'.format(self._type(), brick_id))

        self._callback(brick_id)
