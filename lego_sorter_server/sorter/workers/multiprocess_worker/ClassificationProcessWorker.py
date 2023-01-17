import logging
import multiprocessing
import sys
import multiprocessing as mp
from multiprocessing import Queue
from queue import Empty
from typing import Tuple

from PIL.Image import Image

from lego_sorter_server.analysis.AnalysisService import AnalysisService
from lego_sorter_server.common.ClassificationResults import ClassificationResultsList
from lego_sorter_server.sorter.workers.multiprocess_worker.ProcessWorker import ProcessWorker

logging.basicConfig(level=logging.INFO)


class ClassificationProcessWorker(ProcessWorker):
    def __init__(self):
        super().__init__()
        self._process_name = 'ClassificationProcess'
        self._head_brick_idx_queue: Queue[int] = Queue()
        self._process = mp.Process(target=self.run,
                                   args=(
                                       self.input_queue,
                                       self.output_queue,
                                       self._head_brick_idx_queue,
                                   ),
                                   name=self._process_name)

    def enqueue(self, item: Tuple[int, int, Image]):
        self.input_queue.put(item)

    def set_head_brick_idx(self, head_brick_idx: int):
        self._head_brick_idx_queue.put(head_brick_idx)

    @staticmethod
    def run(input_queue: Queue, output_queue: Queue, head_brick_idx_queue: Queue):
        process_name = multiprocessing.current_process().name
        analysis_service = AnalysisService()

        head_brick_idx = -1

        logging.info('[{0}] - READY'.format(process_name))
        while True:
            try:
                brick_id, detection_id, image = input_queue.get(timeout=0.5)

                # brick_id < head_idx ==> brick has already been sorted (passed the camera line)
                while True:
                    try:
                        head_brick_idx = head_brick_idx_queue.get_nowait()
                    except Empty:
                        break

                if brick_id < head_brick_idx:
                    logging.info(
                        '[{0}] SKIPPING - BRICK {1} ALREADY PASSED THE CAMERA LINE'.format(process_name, brick_id))
                    continue

                logging.debug('[{0}] - queue object received'.format(process_name, brick_id, detection_id))

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
