import logging
import multiprocessing
from multiprocessing import Queue
from queue import Empty

from lego_sorter_server.analysis.AnalysisService import AnalysisService
from lego_sorter_server.common.ClassificationResults import ClassificationResultsList


class ClassificationProcessAttributes:
    def __init__(self):
        self.input_queue: Queue = Queue()
        self.output_queue: Queue = Queue()
        self.head_brick_idx = 0

    @staticmethod
    def run(input_queue: Queue,
            output_queue: Queue):
        process_name = multiprocessing.current_process().name
        analysis_service: AnalysisService = AnalysisService()

        while True:
            try:
                brick_id, detection_id, image = input_queue.get(timeout=0.5)

                # TODO: take head_brick_idx into account

                classification_results_list: ClassificationResultsList = analysis_service.classify([image])

                if len(classification_results_list) == 0:
                    logging.error('[{0}] Empty classification result received for brick {1} from '
                                  'AnalysisService.classify().'.format(process_name, brick_id,
                                                                       len(classification_results_list)))
                    output_queue.put((brick_id, detection_id, None))

                elif len(classification_results_list) != 1:
                    logging.error('[{0}] Invalid number of classification results: {0}, 1 expected. '
                                  'Discarding all but first result'.format(process_name,
                                                                           len(classification_results_list)))
                    output_queue.put((brick_id, detection_id, None))

                else:
                    logging.debug('[{0}] Classification result: {1}, '
                                  'score: {2}.'.format(process_name,
                                                       classification_results_list[0].classification_class,
                                                       classification_results_list[0].classification_score))
                    output_queue.put((brick_id, detection_id, classification_results_list[0]))

            except Empty:
                continue

            except KeyboardInterrupt:
                logging.error('[{0}] KeyboardInterrupt. Exiting...'.format(process_name))
                break

            except Exception as e:
                logging.error('[{0}] Exception while running process:\n'.format(process_name))
                logging.error('{0}'.format(e))
                logging.error('[{0}] Exiting...'.format(process_name))
                break
