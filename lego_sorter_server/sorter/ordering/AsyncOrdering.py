import logging
import os
from collections import OrderedDict
from typing import List, Tuple, Optional, Union
from datetime import datetime

import pandas as pd
from PIL.Image import Image

from lego_sorter_server.analysis.detection import DetectionUtils
from lego_sorter_server.common.AnalysisResults import AnalysisResultsList, AnalysisResult, ClassificationStrategy
from lego_sorter_server.common.BrickSortingStatus import BrickSortingStatus
from lego_sorter_server.common.ClassificationResults import ClassificationResultsList
from lego_sorter_server.common.DetectionResults import DetectionResultsList, DetectionResult, DetectionBox
from lego_sorter_server.sorter.workers.multiprocess_worker.ClassificationProcessWorker import \
    ClassificationProcessWorker
from lego_sorter_server.sorter.workers.multiprocess_worker.DetectionProcessWorker import DetectionProcessWorker
from lego_sorter_server.sorter.workers.multithread_worker.ClassificationThreadWorker import ClassificationThreadWorker
from lego_sorter_server.sorter.workers.multithread_worker.DetectionThreadWorker import DetectionThreadWorker
from lego_sorter_server.sorter.workers.multithread_worker.SorterThreadWorker import SorterThreadWorker


class AsyncOrdering:
    def __init__(self, save_images_to_file: bool, skip_sorted_bricks_classification: bool,
                 detection_worker: Union[DetectionThreadWorker, DetectionProcessWorker],
                 classification_worker: Union[ClassificationThreadWorker, ClassificationProcessWorker],
                 sorting_worker: Union[SorterThreadWorker]):
        # TODO: add image saving to file functionality and parametrize it with save_images_to_file arg
        self.save_images_to_file = save_images_to_file
        self.skip_sorted_bricks_classification = skip_sorted_bricks_classification

        self.classification_strategy = ClassificationStrategy.MEDIAN
        '''Determines the way of obtaining the single classification class based of multiple results'''

        self.conveyor_state: OrderedDict[int, DetectionBox] = OrderedDict()
        '''Bricks on the conveyor belt, format - key: brick_id: int, value = detection_box: DetectionBox'''

        self.head_brick_idx = 0
        '''Index of first brick on the tape'''
        self.bricks: OrderedDict[int, BrickSortingStatus] = OrderedDict()
        '''Ordered dict of all the bricks, sorted and in process'''

        self.head_image_idx = 0
        '''Index of the last image received'''
        self.images: OrderedDict[int, Image] = OrderedDict()
        '''OrderedDict of images, format - key = image_id: int, value = image: Image'''
        self.enqueue_times: OrderedDict[int, datetime] = OrderedDict()
        '''OrderedDict of timestamps, format - kye = image_id: int, value = timestamp: float'''
        self.detection_times: OrderedDict[int, datetime] = OrderedDict()
        '''OrderedDict of timestamps, format - kye = image_id: int, value = timestamp: float'''

        self.cropped_images: OrderedDict[int, List[Tuple[DetectionResult, Image]]] = OrderedDict()
        '''OrderedDict of DetectionResults and Images, format - key = image_id: int, 
        value = List[Tuple] (DetectionResult, Image)'''

        self.detection_worker: Union[DetectionThreadWorker, DetectionProcessWorker] = detection_worker
        self.classification_worker: Union[
            ClassificationThreadWorker, ClassificationProcessWorker] = classification_worker
        self.sorting_worker: Union[SorterThreadWorker] = sorting_worker

        self.set_callbacks()

    def set_callbacks(self):
        self.detection_worker.set_callback(self.on_detection)
        self.classification_worker.set_callback(self.on_classification)
        self.sorting_worker.set_callback(self.on_sort)

    def add_image(self, image: Image) -> int:
        self.head_image_idx += 1
        self.images[self.head_image_idx] = image
        self.enqueue_times[self.head_image_idx] = datetime.now()
        return self.head_image_idx

    def reset(self):
        logging.info('[AsyncOrdering] Resetting state.')
        self.conveyor_state.clear()

        self.head_brick_idx = 0
        self.bricks.clear()

        self.head_image_idx = 0
        self.images.clear()

        self.enqueue_times.clear()
        self.detection_times.clear()
        self.cropped_images.clear()

    def on_detection(self, image_idx: int, detection_results_list: DetectionResultsList):
        self.detection_times[image_idx] = datetime.now()
        detection_results_list.sort(key=lambda x: x.detection_box.y_min, reverse=True)

        # send sort order to sorter, remove bricks from self.conveyor_state etc.
        self._process_bricks_passed_the_camera_line(detection_results_list)

        self._prepare_for_classification(image_idx, detection_results_list)
        self.images.pop(image_idx)

    def on_classification(self, brick_id: int, detection_id: int,
                          classification_results_list: ClassificationResultsList):
        if len(classification_results_list) == 0:
            logging.error('[AsyncOrdering] Empty classification result received for brick {0} from '
                          'AnalysisService.classify().'.format(brick_id))
            return

        elif len(classification_results_list) != 1:
            logging.error('[AsyncOrdering] Invalid number of classification results: {0}, 1 expected. '
                          'Discarding all but first result'.format(len(classification_results_list)))

        classification_result = classification_results_list[0]
        logging.debug('[AsyncOrdering] Classification result: {0}, '
                      'score: {1}.'.format(classification_result.classification_class,
                                           classification_result.classification_score))

        self.bricks[brick_id].analysis_results_list[detection_id].time_classified = datetime.now()
        self.bricks[brick_id].analysis_results_list[detection_id].merge_classification_result(classification_result)

        # TODO: add image storing option
        self.bricks[brick_id].analysis_results_list[detection_id].image = None

        self.bricks[brick_id].classified = True

    def on_sort(self, brick_id):
        self.bricks[brick_id].time_sorted = datetime.now()
        self.bricks[brick_id].sorted = True

    def _process_bricks_passed_the_camera_line(self, current_detection_results: DetectionResultsList):
        current_first_detection = current_detection_results[0] if len(current_detection_results) > 0 else None

        if current_first_detection is None:
            bricks_passed_camera_line = list(self.conveyor_state.keys())

        else:
            bricks_passed_camera_line = list(filter(
                lambda x: not self._is_the_same_brick(self.conveyor_state[x],
                                                      current_first_detection.detection_box),
                self.conveyor_state.keys())
            )

        if len(bricks_passed_camera_line) > 0:
            self._set_new_head_brick_idx(bricks_passed_camera_line)
            self._send_to_sorter(bricks_passed_camera_line)

            for brick_id in bricks_passed_camera_line:
                self.conveyor_state.pop(brick_id)

    def _prepare_for_classification(self, image_idx: int, detection_results_list: DetectionResultsList):
        previous_first_brick_id, previous_first_detection_box = self._get_first_brick_from_conveyor_state()

        new_conveyor_state: OrderedDict[int, DetectionBox] = OrderedDict()

        if len(self.bricks.keys()) == 0:
            next_brick_id = self.head_brick_idx
        else:
            next_brick_id = next(reversed(self.bricks.keys())) + 1

        for detection_result in detection_results_list:
            # check if detected bricks are already on the conveyor belt
            if previous_first_detection_box is not None and \
                    self._is_the_same_brick(previous_first_detection_box, detection_result.detection_box):
                brick_id = previous_first_brick_id
                previous_first_brick_id, previous_first_detection_box = self._get_first_brick_from_conveyor_state()

            else:
                brick_id = next_brick_id
                next_brick_id += 1

            self._store_results_and_enqueue_for_classification(image_idx, brick_id, detection_result)
            new_conveyor_state[brick_id] = detection_result.detection_box

        self.conveyor_state = new_conveyor_state

    def _set_new_head_brick_idx(self, bricks_sent_to_sorter: List[int]):
        """
        bricks_sent_to_sorter: list of brick indexes, assumed to be a subset of conveyor_state
        """
        if len(bricks_sent_to_sorter) == 0:
            logging.error(
                '[AsyncOrdering] Invalid invocation of "set_new_head_brick_idx" method: empty list of bricks '
                'received (shall only be called when bricks pass the camera line)')
            return

        # All bricks passed the camera line
        if len(bricks_sent_to_sorter) == len(self.conveyor_state):
            self.head_brick_idx = max(bricks_sent_to_sorter) + 1

        # Only some of the last conveyor_state bricks passed the camera line
        elif len(bricks_sent_to_sorter) != len(self.conveyor_state):
            self.head_brick_idx = min([x for x in self.conveyor_state.keys() if x not in bricks_sent_to_sorter])

        if self.skip_sorted_bricks_classification:
            self.classification_worker.set_head_brick_idx(self.head_brick_idx)

    def _store_results_and_enqueue_for_classification(self, image_idx: int, brick_id: int,
                                                      detection_result: DetectionResult):
        cropped_image = DetectionUtils.crop_with_margin_from_detection_box(self.images[image_idx],
                                                                           detection_result.detection_box)
        analysis_result = AnalysisResult.from_detection_with_image(detection_result, cropped_image)
        analysis_result.time_enqueued = self.enqueue_times[image_idx]
        analysis_result.time_detected = self.detection_times[image_idx]
        analysis_result.image_id = image_idx

        if brick_id not in self.bricks.keys():
            self.bricks[brick_id] = BrickSortingStatus(brick_id)

        detection_id = len(self.bricks[brick_id].analysis_results_list)
        self.bricks[brick_id].analysis_results_list.append(analysis_result)

        self.classification_worker.enqueue((brick_id, detection_id, cropped_image))

    def _send_to_sorter(self, brick_id_list: List[int]):
        if len(brick_id_list) == 0:
            logging.error('[AsyncOrdering] Internal error - empty list of brick_id received')
            return

        if len(brick_id_list) > 1:
            logging.warning(
                '[AsyncOrdering] Multiple bricks passed the camera line: {0}. '
                'Attempting sort just the first brick'.format(len(brick_id_list)))

        brick_id = brick_id_list[0]
        analysis_result = self._get_analysis_result(brick_id)
        if analysis_result is None:
            return

        self.bricks[brick_id].final_classification_class = analysis_result.classification_class
        self.sorting_worker.enqueue((brick_id, analysis_result))

    def _get_analysis_result(self, brick_id) -> Optional[AnalysisResult]:
        analysis_results_list = self.bricks[brick_id].analysis_results_list
        analysis_results_list_classified: AnalysisResultsList = AnalysisResultsList(
            [result for result in analysis_results_list if
             result.classification_score is not None])

        if len(analysis_results_list_classified) == 0:
            logging.warning('[AsyncOrdering] Attempting to sort a brick which lacks classification results')
            return None

        return analysis_results_list_classified.get_result(self.classification_strategy)

    def _get_first_brick_from_conveyor_state(self) -> Tuple[Optional[int], Optional[DetectionBox]]:
        if len(self.conveyor_state) == 0:
            return None, None
        else:
            first_brick_id = list(self.conveyor_state.keys())[0]
            return first_brick_id, self.conveyor_state.pop(first_brick_id)

    @staticmethod
    def _is_the_same_brick(previous_detection: DetectionBox, current_detection: DetectionBox) -> bool:
        return previous_detection.y_min <= current_detection.y_min or \
            previous_detection.y_max <= current_detection.y_max

    def export_history_to_csv(self, file_path: str):
        results_list = {}
        global_brick_result_idx = 0
        for brick_id in self.bricks.keys():
            results_list.update(self.bricks[brick_id].to_dict(global_brick_result_idx))
            global_brick_result_idx = len(results_list)

        for image_id in self.images.keys():
            results_list.update({
                global_brick_result_idx: {
                    'brick_id': -1,
                    'result_id': -1,
                    'detected': False,
                    'classified': False,
                    'sorted': False,
                    'image_id': image_id,
                    'time_enqueued': self.enqueue_times[image_id]
                }
            })
            global_brick_result_idx += 1
        results_list = {r['image_id']: r for r in results_list.values()}

        df = pd.DataFrame.from_dict(results_list).transpose()

        if not os.path.isdir(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))

        logging.info('[AsyncOrdering] Saving Ordering history to file: {0}'.format(file_path))
        df.to_csv(file_path)
