import logging
from typing import Callable

from lego_sorter_server.sorter.workers.Worker import Worker
from lego_sorter_server.sorter.workers.multithread_worker.Listener import Listener


class ProcessWorker(Worker):
    def __init__(self):
        super().__init__()

        self._listener: Listener = Listener()
        self.output_queue = self._listener.input_queue

    def start(self):
        logging.info("[ProcessWorker] TODO: action on start")
        self._listener.start()

    def stop(self):
        logging.info("[ProcessWorker] TODO: action on stop")
        self._listener.stop()

    def reset(self):
        logging.info("[ProcessWorker] TODO: action on reset")
        self._listener.reset()

    def enqueue(self, *item):
        self.input_queue.put(item)

    def set_callback(self, callback: Callable):
        self._listener.set_callback(callback)

    @staticmethod
    def run(*args):
        pass

    # @staticmethod
    # def run(input_queue: Queue, output_queue: Queue, target_method: Callable):
    #     process_name = multiprocessing.current_process().name
    #
    #     while True:
    #         try:
    #             queue_object = input_queue.get(timeout=0.5)
    #
    #         except Empty:
    #             continue
    #
    #         except KeyboardInterrupt:
    #             logging.error('[{0}] KeyboardInterrupt. Exiting...'.format(process_name))
    #             break
    #
    #         except Exception as e:
    #             logging.error('[{0}] Exception while running process:\n'.format(process_name))
    #             logging.error('{0}'.format(e))
    #             logging.error('[{0}] Exiting...'.format(process_name))
    #             break
