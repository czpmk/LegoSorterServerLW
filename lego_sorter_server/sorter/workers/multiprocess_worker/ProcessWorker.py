import logging
from multiprocessing import Process
from queue import Empty
from typing import Callable, Optional

from lego_sorter_server.sorter.workers.Worker import Worker, WorkerMode
from lego_sorter_server.sorter.workers.multithread_worker.Listener import Listener


class ProcessWorker(Worker):
    def __init__(self):
        super().__init__()
        self.mode = WorkerMode.Process
        self._process: Optional[Process] = None

        self._listener: Listener = Listener()
        self.output_queue = self._listener.input_queue
        self.started = False
        ''' Cannot restart the process, only set "started" once '''

    def start(self):
        self._listener.start()
        if not self.started:
            self.start_process()
            self.started = True

    def stop(self):
        self._listener.stop()
        logging.info(
            '[{0}] Stopping process (Queue size: {1}, skipped items: {2})'.format(self._name, self.input_queue.qsize(),
                                                                                  self.skipped_items_count))

    def start_process(self):
        logging.info('[{0}] Starting Process.'.format(self._name))
        self._process.start()

    def end_process(self):
        logging.info('[{0}] Stopping Process.'.format(self._name))
        if self._process.is_alive():
            self._process.join(1)
        else:
            logging.exception('[{0}] Process exited before the join attempt.'.format(self._name))

        if self._process.is_alive():
            logging.exception('[{0}] Process did not end at join() call. Terminating.'.format(self._name))
            self._process.terminate()

    def _clear_queue(self):
        logging.info('[{0}] Clearing queue (Queue size: {1})'.format(self._name, self.input_queue.qsize()))
        try:
            while True:
                self.input_queue.get_nowait()
        except Empty:
            pass
        self._listener.clear_queue()

    def clear_state(self):
        self.clear_queue()
        self._listener.clear_state()

    def set_callback(self, callback: Callable):
        self._listener.set_callback(callback)

    @staticmethod
    def exception_handler(exc_type=None, value=None, tb=None):
        logging.exception("Uncaught exception: {0}".format(str(value)))

    @staticmethod
    def run(*args):
        pass
