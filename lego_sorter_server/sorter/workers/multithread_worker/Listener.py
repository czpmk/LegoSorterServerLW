from queue import Empty

from lego_sorter_server.sorter.workers.multithread_worker.ThreadWorker import ThreadWorker


class Listener(ThreadWorker):
    def __init__(self):
        super().__init__()

    def run(self):
        """ Unlike other ThreadWorkers - does not process the input in any way, just passes it to callback method. """
        while self.running:
            try:
                queue_object = self.input_queue.get(timeout=0.5)
            except Empty:
                continue

            self.callback(*queue_object)
