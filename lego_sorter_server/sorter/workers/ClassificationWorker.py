import logging
from typing import Callable, Tuple

from PIL.Image import Image

from lego_sorter_server.analysis.AnalysisService import AnalysisService
from lego_sorter_server.common.ClassificationResults import ClassificationResult, ClassificationResultsList
from lego_sorter_server.sorter.workers.Worker import Worker


class ClassificationWorker(Worker):
    def __init__(self, analysis_service: AnalysisService, callback: Callable[[int, int, ClassificationResult], None]):
        super().__init__()

        self.analysis_service: AnalysisService = analysis_service
        self.set_callback(callback)
        self.set_target_method(self.__classify)

    def enqueue(self, item: Tuple[int, int, Image]):
        super(ClassificationWorker, self).enqueue(item)

    def __classify(self, brick_id: int, detection_id: int, image: Image):
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
