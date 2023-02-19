import logging
from enum import Enum
from multiprocessing import Queue
from typing import Callable, Optional


class WorkerMode(Enum):
    Thread = 0
    Process = 1

    @classmethod
    def from_string(cls, str_mode):
        return {
            "Thread": WorkerMode.Thread,
            "Process": WorkerMode.Process
        }.get(str_mode)


class Worker:
    def __init__(self):
        self.mode: Optional[WorkerMode] = None
        self.input_queue: Queue = Queue()
        self.callback: Optional[Callable] = None
        self.skipped_items_count = 0

        self._name: str = self._type()
        self._queue_size_limit = 0

    def start(self):
        pass

    def stop(self):
        pass

    def clear_state(self):
        pass

    def set_queue_size_limit(self, queue_size_limit: int):
        # Do not use Queue's 'maxsize' - compatibility issues with Ubuntu
        self._queue_size_limit = queue_size_limit

    def clear_queue(self):
        pass

    def set_callback(self, callback: Callable):
        pass

    def enqueue(self, *item):
        # Do not use Queue's 'maxsize' - compatibility issues on Ubuntu
        if self._queue_size_limit != 0 and self.input_queue.qsize() >= self._queue_size_limit:
            logging.debug('[{0}] Queue size reached the limit ({1}). '
                          'Discarding new item.'.format(self._name, self._queue_size_limit))
            self.skipped_items_count += 1

        else:
            self.input_queue.put(item)

    def _type(self) -> str:
        return self.__class__.__name__

    def __del__(self):
        logging.info('[{0}] Deleter called.'.format(self._name))
