import logging
import multiprocessing
import sys
from multiprocessing import Queue
from queue import Empty
from typing import Optional, Tuple

from PIL.Image import Image

from lego_sorter_server.analysis.AnalysisService import AnalysisService
from lego_sorter_server.common.ClassificationResults import ClassificationResultsList
from lego_sorter_server.sorter.workers.multiprocess_worker.ProcessWorker import ProcessWorker

logging.basicConfig(level=logging.INFO)


class ClassificationProcessWorker(ProcessWorker):
    def __init__(self):
        super().__init__()

        self._head_brick_idx = 0

    def enqueue(self, item: Tuple[int, int, Image]):
        self.input_queue.put(item)

    def set_head_brick_idx(self, head_brick_idx: int):
        self._head_brick_idx = head_brick_idx

    def stop(self):
        logging.info('[{0}] Stopping. (Queue size: {1})'.format('ClassificationProcess', self.input_queue.qsize()))
        super().stop()

    @staticmethod
    def exception_handler(exc_type=None, value=None, tb=None):
        logging.exception(f"Uncaught exception: {str(value)}")

    @staticmethod
    def run(input_queue: Queue, output_queue: Queue, analysis_service: Optional[AnalysisService]):
        process_name = multiprocessing.current_process().name
        if analysis_service is None:
            analysis_service = AnalysisService()

        logging.info('[{0}] - READY'.format(process_name))
        while True:
            try:
                brick_id, detection_id, image = input_queue.get(timeout=0.5)
                logging.debug('[{0}] - queue object received'.format(process_name, brick_id, detection_id))

                # TODO: take head_brick_idx into account

                classification_results_list: ClassificationResultsList = analysis_service.classify([image])

                logging.debug(
                    '[{0}] {1} classification results received from '
                    'AnalysisService for brick {2}.'.format(process_name, len(classification_results_list), brick_id))
                output_queue.put((brick_id, detection_id, classification_results_list))

            except Empty:
                logging.debug('[{0}] - Empty'.format(process_name))
                continue

            except KeyboardInterrupt:
                logging.error('[{0}] KeyboardInterrupt. Exiting...'.format(process_name))
                break

            except Exception:
                ClassificationProcessWorker.exception_handler(*sys.exc_info())
                break

        logging.info('[{0}] Process exited.'.format(process_name))
