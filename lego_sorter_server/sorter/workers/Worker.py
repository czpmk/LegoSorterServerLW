from multiprocessing import Queue
from typing import Callable, Optional

from lego_sorter_server.analysis.AnalysisService import AnalysisService
from lego_sorter_server.sorter.LegoSorterController import LegoSorterController


class Worker:
    def __init__(self):
        self.input_queue: Queue = Queue()
        self.callback: Optional[Callable] = None
        self.analysis_service: Optional[AnalysisService] = None
        self.sorter_controller: Optional[LegoSorterController] = None
        self.running: bool = False

    def start(self):
        pass

    def stop(self):
        pass

    def reset(self):
        pass

    def set_callback(self, callback: Callable):
        pass

    def set_analysis_service(self, analysis_service: AnalysisService):
        self.analysis_service = analysis_service

    def set_sorter_controller(self, sorter_controller: LegoSorterController):
        self.sorter_controller = sorter_controller

    def enqueue(self, *item):
        pass

    # def __init__(self):
    #     self._thread: Thread = Thread()
    #     self._queue: Queue = Queue()
    #     self._target_method: Callable = lambda queue_object: None
    #     '''Override in init method.'''
    #     self._callback: Callable = lambda x: None
    #     '''Set with set_callback() method.'''
    #
    #     self._running: bool = False
    #
    # def start(self):
    #     if self._running is True:
    #         logging.exception('[{0}] Attempting to START the worker while it is running.'.format(self._type()))
    #         return
    #
    #     self._running = True
    #     self._thread: Thread = Thread(target=self.run)
    #     self._thread.start()
    #
    # def stop(self):
    #     if self._running is False:
    #         logging.exception('[{0}] Attempting to STOP the worker while it is not running.'.format(self._type()))
    #         return
    #
    #     self._running = False
    #     if self._thread.is_alive():
    #         self._thread.join(1)
    #     logging.info('[{0}] Stopping thread (Queue size: {1})'.format(self._type(), self._queue.qsize()))
    #
    # def clear_queue(self):
    #     logging.info('[{0}] Clearing queue (Queue size: {1})'.format(self._type(), self._queue.qsize()))
    #     with self._queue.mutex:
    #         self._queue.queue.clear()
    #
    # def reset(self):
    #     if self._running:
    #         self.stop()
    #
    #     self.clear_queue()
    #     self.start()
    #
    # def run(self):
    #     while self._running:
    #         try:
    #             queue_object = self._queue.get(timeout=0.5)
    #         except Empty:
    #             continue
    #
    #         self._target_method(*queue_object)
    #
    # def set_callback(self, callback: Callable):
    #     self._callback = callback
    #
    # def set_target_method(self, target_method: Callable):
    #     self._target_method = target_method
    #
    # def enqueue(self, item):
    #     self._queue.put(item)
    #
    # def _type(self) -> str:
    #     return self.__class__.__name__
