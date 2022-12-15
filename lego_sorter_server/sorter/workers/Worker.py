import logging
from torch.multiprocessing import Process, Queue, set_start_method
from queue import Empty
from threading import Thread
from typing import Callable


class Worker:
    def __init__(self):
        self._thread: Thread = Thread()
        self._queue: Queue = Queue()

        self._multiprocessing: bool = False

        self._listener: Thread = Thread()
        self._process: Process = Process()
        self._queue_in: Queue = Queue()
        self._queue_out: Queue = Queue()
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
        if self._multiprocessing:
            self._process: Process = Process(target=self._target_method, args=(self._queue_in, self._queue_out))
            self._process.start()
            self._listener: Thread = Thread(target=self._listen)
            self._listener.start()
        else:
            self._thread: Thread = Thread(target=self.run)
            self._thread.start()

    def run(self):
        while self._running:
            try:
                queue_object = self._queue.get(timeout=0.5)
            except Empty:
                continue

            self._target_method(*queue_object)

    def stop(self):
        if self._running is False:
            logging.exception('[{0}] Attempting to STOP the worker while it is not running.'.format(self._type()))
            return

        self._running = False

        if self._multiprocessing:
            if self._process.is_alive():
                self._process.join(1)
            if self._listener.is_alive():
                self._listener.join(1)
            logging.info('[{0}] Stopping process (queue_in size: {1}, queue_out size: {2})'.format(self._type(),
                                                                                                   self._queue_in.qsize(),
                                                                                                   self._queue_out.qsize()))
        else:
            if self._thread.is_alive():
                self._thread.join(1)
            logging.info('[{0}] Stopping thread (Queue size: {1})'.format(self._type(), self._queue.qsize()))

    def clear_queue(self):
        if self._multiprocessing:
            logging.info('[{0}] Clearing queue (queue_in size: {1}, queue_out size: {2})'.format(self._type(),
                                                                                                 self._queue_in.qsize(),
                                                                                                 self._queue_out.qsize()))
            with self._queue_out.mutex:
                self._queue_out.queue.clear()
            with self._queue_in.mutex:
                self._queue_in.queue.clear()
        else:
            logging.info('[{0}] Clearing queue (Queue size: {1})'.format(self._type(), self._queue.qsize()))
            with self._queue.mutex:
                self._queue.queue.clear()

    def reset(self):
        if self._running:
            self.stop()

        self.clear_queue()
        self.start()

    def set_callback(self, callback: Callable):
        self._callback = callback

    def set_target_method(self, target_method: Callable):
        self._target_method = target_method

    def enqueue(self, item):
        if self._multiprocessing:
            self._queue_in.put(item)
        else:
            self._queue.put(item)

    def _listen(self):
        while True:
            try:
                value = self._queue_out.get()
                self._callback(*value)
            except Empty:
                continue

    def _type(self) -> str:
        return self.__class__.__name__


if __name__ == '__main__':
    # set the start method
    set_start_method('spawn')
