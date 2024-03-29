import logging
from abc import abstractmethod
from queue import Empty
from threading import Thread
from typing import Optional

from lego_sorter_server.analysis.AnalysisService import AnalysisService
from lego_sorter_server.sorter.LegoSorterController import LegoSorterController
from lego_sorter_server.sorter.workers.Worker import Worker, WorkerMode


class ThreadWorker(Worker):
    def __init__(self):
        super().__init__()
        self.mode = WorkerMode.Thread
        self.thread: Thread = Thread()
        self.running: bool = False

        self.analysis_service: Optional[AnalysisService] = None
        self.sorter_controller: Optional[LegoSorterController] = None

    def start(self):
        if self.running is True:
            logging.exception('[{0}] Attempting to START the worker while it is running.'.format(self._name))
            return

        self.running = True
        self.thread: Thread = Thread(target=self.run)
        self.thread.start()

    def stop(self):
        if self.running is False:
            logging.exception('[{0}] Attempting to STOP the worker while it is not running.'.format(self._name))
            return

        self.running = False
        if self.thread.is_alive():
            self.thread.join(1)

        logging.info(
            '[{0}] Stopping thread (Queue size: {1}, skipped items: {2})'.format(self._name, self.input_queue.qsize(),
                                                                                 self.skipped_items_count))

    def clear_queue(self):
        logging.info('[{0}] Clearing queue (Queue size: {1})'.format(self._name, self.input_queue.qsize()))
        try:
            while True:
                self.input_queue.get_nowait()
        except Empty:
            pass
        except BrokenPipeError:
            logging.debug('[{0}] Attempting worker\'s queue clear while the Pipe has already been closed.')
            pass

    def clear_state(self):
        self.clear_queue()

    def set_analysis_service(self, analysis_service: AnalysisService):
        self.analysis_service = analysis_service

    def set_sorter_controller(self, sorter_controller: LegoSorterController):
        self.sorter_controller = sorter_controller

    @abstractmethod
    def run(self, *args):
        pass

    def __del__(self):
        self.clear_state()
        if self.thread.is_alive():
            self.thread.join(1)
        logging.info('[{0}] Thread closed.'.format(self._name))
        super().__del__()
