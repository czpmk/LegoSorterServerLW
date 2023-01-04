import logging
import multiprocessing
import sys
from multiprocessing import Queue
from queue import Empty
from typing import Optional, Tuple

from PIL.Image import Image

from lego_sorter_server.analysis.AnalysisService import AnalysisService
from lego_sorter_server.common.DetectionResults import DetectionResultsList
from lego_sorter_server.sorter.workers.multiprocess_worker.ProcessWorker import ProcessWorker

logging.basicConfig(level=logging.INFO)


class DetectionProcessWorker(ProcessWorker):
    def __init__(self):
        super().__init__()

    def enqueue(self, item: Tuple[int, Image]):
        self.input_queue.put(item)

    def stop(self):
        logging.info('[{0}] Stopping. (Queue size: {1})'.format('DetectionProcess', self.input_queue.qsize()))
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
                image_idx, image = input_queue.get(timeout=0.5)

                detection_results_list: DetectionResultsList = analysis_service.detect(image)
                logging.debug(
                    '[{0}] Bricks detected {1} at image {2}.'.format(process_name, len(detection_results_list),
                                                                     image_idx))
                output_queue.put((image_idx, detection_results_list))

            except Empty:
                logging.debug('[{0}] - Empty'.format(process_name))
                continue

            except KeyboardInterrupt:
                logging.error('[{0}] KeyboardInterrupt. Exiting...'.format(process_name))
                break

            except Exception:
                DetectionProcessWorker.exception_handler(*sys.exc_info())
                break

        logging.info('[{0}] Process exited.'.format(process_name))
