import logging
import multiprocessing
import sys
from multiprocessing import Queue
from queue import Empty
from typing import Callable, Optional

from lego_sorter_server.analysis.AnalysisService import AnalysisService
from lego_sorter_server.common.ClassificationResults import ClassificationResultsList
from lego_sorter_server.sorter.workers.multiprocess_worker.ProcessWorker import ProcessWorker


class ClassificationProcessWorker(ProcessWorker):
    def __init__(self):
        super().__init__()

    @staticmethod
    def run(input_queue: Queue, output_queue: Queue, target_method: Callable, excepthook: Callable,
            analysis_service: Optional[AnalysisService]):
        process_name = multiprocessing.current_process().name
        if analysis_service is None:
            analysis_service = AnalysisService()

        while True:
            logging.info('[{0}] - PING'.format(process_name))
            try:
                brick_id, detection_id, image = input_queue.get(timeout=0.5)

                # TODO: take head_brick_idx into account

                classification_results_list: ClassificationResultsList = analysis_service.classify([image])

                logging.debug(
                    '[{0}] {1} classification results received from '
                    'AnalysisService for brick {2}.'.format(process_name, len(classification_results_list), brick_id))
                output_queue.put((brick_id, detection_id, classification_results_list))

            except Empty:
                continue

            except KeyboardInterrupt:
                logging.error('[{0}] KeyboardInterrupt. Exiting...'.format(process_name))
                break

            except Exception:
                excepthook(*sys.exc_info())
                break

        logging.info('[{0}] Process exited.'.format(process_name))
