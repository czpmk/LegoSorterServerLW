import logging
from multiprocessing import Process, Queue
from typing import Callable


class Worker:
    def __init__(self):
        self._process: Process = Process()
        self._queue: Queue = Queue()
        self._target_method: Callable = lambda queue_object: None
        '''Override in init method.'''
        self._callback: Callable = lambda x: None
        '''Set with set_callback() method.'''

        self._running: bool = False

    def start(self):
        if self._running is True:
            logging.exception('[{0}] Attempting to START the worker while it is running.'.format(self._type()))
            return

        self._running = True
        self._process: Process = Process(target=self.run)
        self._process.start()

    def stop(self):
        if self._running is False:
            logging.exception('[{0}] Attempting to STOP the worker while it is not running.'.format(self._type()))
            return

        self._running = False
        if self._process.is_alive():
            self._process.join(1)
        logging.info('[{0}] Stopping process (Queue size: {1})'.format(self._type(), self._queue.qsize()))

    def clear_queue(self):
        logging.info('[{0}] Clearing queue (Queue size: {1})'.format(self._type(), self._queue.qsize()))
        with self._queue.mutex:
            self._queue.queue.clear()

    def reset(self):
        if self._running:
            self.stop()

        self.clear_queue()
        self.start()

    def run(self):
        while self._running:
            if self._queue.empty():
                continue

            queue_object = self._queue.get(timeout=0.5)

            self._target_method(*queue_object)

    def set_callback(self, callback: Callable):
        self._callback = callback

    def set_target_method(self, target_method: Callable):
        self._target_method = target_method

    def enqueue(self, item):
        self._queue.put(item)

    def _type(self) -> str:
        return self.__class__.__name__
