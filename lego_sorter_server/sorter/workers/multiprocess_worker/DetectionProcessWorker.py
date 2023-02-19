import logging
import multiprocessing
import sys
import multiprocessing as mp
from multiprocessing import Queue
from queue import Empty
from typing import Tuple

from PIL.Image import Image

from lego_sorter_server.analysis.AnalysisService import AnalysisService
from lego_sorter_server.common.DetectionResults import DetectionResultsList
from lego_sorter_server.sorter.workers.multiprocess_worker.ProcessWorker import ProcessWorker

logging.basicConfig(level=logging.INFO)


class DetectionProcessWorker(ProcessWorker):
    def __init__(self):
        super().__init__()
        self._process_name = 'DetectionProcess'
        self._process = mp.Process(target=self.run,
                                   args=(
                                       self.input_queue,
                                       self.output_queue,
                                   ),
                                   name=self._process_name)

    def enqueue(self, item: Tuple[int, Image]):
        super().enqueue(*item)

    @staticmethod
    def run(input_queue: Queue, output_queue: Queue):
        process_name = multiprocessing.current_process().name
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
