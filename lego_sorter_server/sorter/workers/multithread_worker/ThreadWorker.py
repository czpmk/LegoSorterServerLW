import logging
from multiprocessing import Queue
from queue import Empty
from threading import Thread
from typing import Callable, Optional

from lego_sorter_server.analysis.AnalysisService import AnalysisService
from lego_sorter_server.sorter.LegoSorterController import LegoSorterController
from lego_sorter_server.sorter.workers.Worker import Worker, WorkerMode


class ThreadWorker(Worker):
    def __init__(self):
        super().__init__()
        self.mode = WorkerMode.Thread
        self.thread: Thread = Thread()
        self.target_method: Optional[Callable] = None
        self.running: bool = False

        self.analysis_service: Optional[AnalysisService] = None
        self.sorter_controller: Optional[LegoSorterController] = None

    def start(self):
        if self.running is True:
            logging.exception('[{0}] Attempting to START the worker while it is running.'.format(self._type()))
            return

        self.running = True
        self.thread: Thread = Thread(target=self.run)
        self.thread.start()

    def stop(self):
        if self.running is False:
            logging.exception('[{0}] Attempting to STOP the worker while it is not running.'.format(self._type()))
            return

        self.running = False
        if self.thread.is_alive():
            self.thread.join(1)

        logging.info('[{0}] Stopping thread (Queue size: {1})'.format(self._type(), self.input_queue.qsize()))

    def clear_queue(self):
        logging.info('[{0}] Clearing queue (Queue size: {1})'.format(self._type(), self.input_queue.qsize()))
        with self.input_queue.mutex:
            self.input_queue.queue.clear()

    def reset(self):
        if self.running:
            self.stop()

        self.clear_queue()
        self.start()

    def set_analysis_service(self, analysis_service: AnalysisService):
        self.analysis_service = analysis_service

    def set_sorter_controller(self, sorter_controller: LegoSorterController):
        self.sorter_controller = sorter_controller

    def run(self):
        while self.running:
            try:
                queue_object = self.input_queue.get(timeout=0.5)
            except Empty:
                continue

            self.target_method(*queue_object)

    def _type(self) -> str:
        return self.__class__.__name__
