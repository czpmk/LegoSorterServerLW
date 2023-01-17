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

    def start(self):
        pass

    def stop(self):
        pass

    def reset(self):
        pass

    def clear_queue(self):
        pass

    def set_callback(self, callback: Callable):
        pass

    def enqueue(self, *item):
        pass
