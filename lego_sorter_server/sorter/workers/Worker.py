from enum import Enum
from multiprocessing import Queue
from queue import Full
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

    def start(self):
        pass

    def stop(self):
        pass

    def clear_state(self):
        pass

    def set_queue_size_limit(self, queue_size_limit: int):
        if queue_size_limit != 0:
            self.input_queue: Queue = Queue(maxsize=queue_size_limit)

    def clear_queue(self):
        pass

    def set_callback(self, callback: Callable):
        pass

    def enqueue(self, *item):
        try:
            self.input_queue.put(item)
        except Full:
            self.skipped_items_count += 1
