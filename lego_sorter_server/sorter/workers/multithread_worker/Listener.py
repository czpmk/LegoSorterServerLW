from queue import Empty
from typing import Callable

from lego_sorter_server.sorter.workers.multithread_worker.ThreadWorker import ThreadWorker


class Listener(ThreadWorker):
    def __init__(self):
        super().__init__()

    def set_callback(self, callback: Callable):
        self.callback = callback

    def run(self):
        while self.running:
            try:
                queue_object = self.input_queue.get(timeout=0.5)
            except Empty:
                continue

            self.callback(*queue_object)
