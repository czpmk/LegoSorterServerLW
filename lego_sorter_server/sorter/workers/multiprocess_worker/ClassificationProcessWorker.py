import logging
import multiprocessing
import sys
import multiprocessing as mp
import time
from multiprocessing import Queue
from queue import Empty
from typing import Tuple, List

from PIL.Image import Image

from lego_sorter_server.analysis.AnalysisService import AnalysisService
from lego_sorter_server.common.ClassificationResults import ClassificationResultsList
from lego_sorter_server.sorter.workers.multiprocess_worker.ProcessWorker import ProcessWorker

logging.basicConfig(level=logging.INFO)


class ClassificationProcessWorker(ProcessWorker):
    def __init__(self):
        super().__init__()
        self._process_name = 'ClassificationProcess'
        self._process = mp.Process(target=self.run,
                                   args=(
                                       self.input_queue,
                                       self.output_queue,
                                   ),
                                   name=self._process_name)

    def enqueue(self, item: Tuple[int, int, Image]):
        super().enqueue(*item)

    @staticmethod
    def run(input_queue: Queue, output_queue: Queue):
        process_name = multiprocessing.current_process().name
        analysis_service = AnalysisService()

        logging.info('[{0}] - READY'.format(process_name))
        while True:
            try:
                inputs: List[Tuple[int, int, Image]] = []
                while True:
                    try:
                        inputs.append(input_queue.get(timeout=0.01))
                    except Empty:
                        break

                if len(inputs) == 0:
                    logging.debug(
                        '[{0}] EMPTY INPUT.'.format(process_name))
                    time.sleep(0.5)
                    continue

                classification_results_list: ClassificationResultsList = analysis_service.classify(
                    [x[2] for x in inputs]
                )

                logging.debug(
                    '[{0}] Classification results received: {1}.'.format(process_name,
                                                                         len(classification_results_list)))

                assert len(inputs) == len(classification_results_list)

                # Format: Tuple[List[Tuple[brick_id, detection_id, image]]]
                # Keep Top level tuple for compatibility with unpacking method
                output_queue.put(
                    (
                        [(inputs[idx][0], inputs[idx][1], classification_results_list[idx]) for idx in
                         range(len(inputs))],
                    )
                )

            except KeyboardInterrupt:
                logging.error('[{0}] KeyboardInterrupt. Exiting...'.format(process_name))
                break

            except Exception:
                ClassificationProcessWorker.exception_handler(*sys.exc_info())
                break

        logging.info('[{0}] Process exited.'.format(process_name))
