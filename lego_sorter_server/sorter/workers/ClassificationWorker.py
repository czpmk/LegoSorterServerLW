import logging
from queue import Empty
from typing import Callable, Tuple, Optional

from PIL.Image import Image

from lego_sorter_server.analysis.AnalysisService import AnalysisService
from lego_sorter_server.common.ClassificationResults import ClassificationResult, ClassificationResultsList
from lego_sorter_server.sorter.workers.ClassificationProcessAttributes import ClassificationProcessAttributes
from lego_sorter_server.sorter.workers.Worker import Worker


class ClassificationWorker(Worker):
    def __init__(self, analysis_service: AnalysisService,
                 classification_process_attributes: ClassificationProcessAttributes):
        super().__init__()

        self.classification_process_attributes: ClassificationProcessAttributes = classification_process_attributes

        self.analysis_service: AnalysisService = analysis_service
        # self.set_target_method(self.__classify)
        self.set_target_method(self.listener_method)
        self._head_brick_idx = 0

    def enqueue(self, item: Tuple[int, int, Image]):
        # super(ClassificationWorker, self).enqueue(item)
        self.classification_process_attributes.input_queue.put(item)

    def set_head_brick_idx(self, new_idx: int):
        self._head_brick_idx = new_idx

    def set_callback(self, callback: Callable[[int, int, Optional[ClassificationResult]], None]):
        self._callback = callback

    def run(self):
        while self._running:
            try:
                queue_object = self.classification_process_attributes.output_queue.get(
                    timeout=3)
            except Empty:
                continue

            self._target_method(*queue_object)

    def listener_method(self, brick_id: int, detection_id: int, classification_result: Optional[ClassificationResult]):
        self._callback(brick_id, detection_id, classification_result)

    # TODO: remove or refactor -- not used
    def __classify(self, brick_id: int, detection_id: int, image: Image):
        # brick_id < head_idx ==> brick has already been sorted (passed the camera line)
        if brick_id < self._head_brick_idx:
            logging.info('[{0}] SKIPPING - BRICK ALREADY PASSED THE CAMERA LINE'.format(self._type(), brick_id))
            return

        classification_results_list: ClassificationResultsList = self.analysis_service.classify([image])

        if len(classification_results_list) == 0:
            logging.error('[{0}] Empty classification result received for brick {1} from '
                          'AnalysisService.classify().'.format(self._type(), brick_id,
                                                               len(classification_results_list)))
            self._callback(brick_id, detection_id, None)

        elif len(classification_results_list) != 1:
            logging.error('[{0}] Invalid number of classification results: {0}, 1 expected. '
                          'Discarding all but first result'.format(self._type(), len(classification_results_list)))
            self._callback(brick_id, detection_id, None)

        else:
            logging.debug('[{0}] Classification result: {1}, '
                          'score: {2}.'.format(self._type(),
                                               classification_results_list[0].classification_class,
                                               classification_results_list[0].classification_score))
            self._callback(brick_id, detection_id, classification_results_list[0])
