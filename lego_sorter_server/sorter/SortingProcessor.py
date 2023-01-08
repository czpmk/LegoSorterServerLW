import logging
import time
import os
from datetime import datetime

from typing import List, Tuple, Dict, Union, Any, Optional
from PIL.Image import Image

from lego_sorter_server.analysis.AnalysisService import AnalysisService
from lego_sorter_server.analysis.detection import DetectionUtils
from lego_sorter_server.common.AnalysisResults import AnalysisResultsList, AnalysisResult
from lego_sorter_server.images.storage.LegoImageStorage import LegoImageStorage
from lego_sorter_server.service.BrickCategoryConfig import BrickCategoryConfig
from lego_sorter_server.sorter.LegoSorterController import LegoSorterController
from lego_sorter_server.sorter.ordering.SimpleOrdering import SimpleOrdering


class SortingProcessor:
    def __init__(self, brick_category_config: BrickCategoryConfig):
        self.analysis_service: AnalysisService = AnalysisService()
        self.sorter_controller: LegoSorterController = LegoSorterController(brick_category_config)
        self.ordering: SimpleOrdering = SimpleOrdering()
        self.storage: LegoImageStorage = LegoImageStorage()
        self.ids: List[int] = []

    def process_next_image(self, image: Image, save_image: bool = True) -> Dict[int, AnalysisResult]:

        time_enqueued = datetime.now()
        start_time = time.time()
        current_results, time_detected, time_classified = self._process(image)
        elapsed_ms = 1000 * (time.time() - start_time)

        logging.info(f"[SortingProcessor] Processing an image took {elapsed_ms} ms.")

        brick_id = self.ordering.process_current_results(current_results, image_height=image.height,
                                                         time_enqueued=time_enqueued, time_detected=time_detected,
                                                       time_classified=time_classified)
        if brick_id is not None and brick_id not in self.ids:
            self.ids.append(brick_id)

        if save_image is True and len(current_results) > 0:
            start_time_saving = time.time()
            time_prefix = f"{int(start_time_saving * 10000) % 10000}"  # 10 seconds
            for key, value in self.ordering.get_current_state().items():
                detection_box = value.detection_box
                cropped_image = DetectionUtils.crop_with_margin(image, detection_box)
                self.storage.save_image(cropped_image, str(key), time_prefix)
            self.storage.save_image(image, "original_sorter", time_prefix)
            logging.info(f"[SortingProcessor] Saving images took {1000 * (time.time() - start_time_saving)} ms.")

        while self.ordering.get_count_of_results_to_send() > 0:
            # Clear out the queue of processed bricks
            self._send_results_to_controller()

        return self.ordering.get_current_state()

    def _send_results_to_controller(self):
        processed_brick = self.ordering.pop_first_processed_brick()

        if processed_brick is None:
            return False

        best_result = self.get_best_result(processed_brick)
        time_sorted = datetime.now()
        id = self.ids.pop(0)
        self.ordering.set_time_sorted(time_sorted, id)
        logging.info(f"[SortingProcessor] Got the best result {best_result}. Returning the results...")
        self.sorter_controller.on_brick_recognized(best_result)

    def _process(self, image: Image) -> Tuple[Optional[AnalysisResultsList], Optional[datetime], Optional[datetime]]:
        """
        Returns a list of recognized bricks ordered by the position on the belt - ymin desc
        """
        detection_results, classification_results = self.analysis_service.detect_and_classify(image,
                                                                                              detection_threshold=0.8)
        time_detected = datetime.now()
        time_classified = datetime.now()
        detected_count = len(detection_results)
        if detected_count == 0:
            return AnalysisResultsList(), None, None

        logging.info(f"[SortingProcessor] Detected a lego brick, processing...")

        if detected_count > 1:
            logging.warning(f"[SortingProcessor] More than one brick detected '(detected_count = {detected_count}), "
                            f"there should be only one brick on the tape at the same time.")

        analysis_results = AnalysisResultsList.from_results_lists(
            classification_results=classification_results,
            detection_results=detection_results
        )
        analysis_results.sort(key=lambda x: x.detection_box.y_min, reverse=True)

        return analysis_results, time_detected, time_classified

    def start_machine(self):
        self.sorter_controller.run_conveyor()

    def stop_machine(self):
        self.sorter_controller.stop_conveyor()
        self.ordering.export_history_to_csv(os.path.join(os.getcwd(), 'SyncExports', 'export_SYNC_{0}.csv'.format(
            datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))))

    def set_machine_speed(self, speed: int):
        self.sorter_controller.set_machine_speed(speed)

    def reset(self):
        logging.info(f"[SortingProcessor] Resetting ids list.")
        self.ids: List[int] = []
        self.ordering.reset()

    @staticmethod
    def get_best_result(results) -> AnalysisResult:
        # TODO - max score, average score, max count?
        return results[0]
