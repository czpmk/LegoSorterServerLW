import logging
import time
from typing import Callable, Tuple

from PIL.Image import Image

from lego_sorter_server.analysis.AnalysisService import AnalysisService
from lego_sorter_server.analysis.detection import DetectionUtils
from lego_sorter_server.common.DetectionResults import DetectionResultsList
from lego_sorter_server.images.storage.LegoImageStorage import LegoImageStorage
from lego_sorter_server.sorter.workers.Worker import Worker


class DetectionWorker(Worker):
    def __init__(self, analysis_service: AnalysisService, save_image=True):
        super().__init__()

        self.analysis_service: AnalysisService = analysis_service
        self.save_image: bool = save_image
        self.storage: LegoImageStorage = LegoImageStorage()
        self.set_target_method(self.__detect)

    def enqueue(self, item: Tuple[int, Image]):
        super(DetectionWorker, self).enqueue(item)

    def set_callback(self, callback: Callable[[int, DetectionResultsList], None]):
        self._callback = callback

    def __detect(self, image_idx: int, image: Image):
        detection_results_list: DetectionResultsList = self.analysis_service.detect(image)

        logging.debug('[{0}] Bricks detected {1} at image {2}.'.format(self._type(), len(detection_results_list),
                                                                       image_idx))

        if self.save_image is True:
            start_time_saving = time.time()
            time_prefix = f"{int(start_time_saving * 10000) % 10000}"  # 10 seconds
            for idx in range(len(detection_results_list)):
                detection_box = detection_results_list[idx].detection_box
                cropped_image = DetectionUtils.crop_with_margin(image, detection_box)
                self.storage.save_image(cropped_image, str(idx), time_prefix)
            self.storage.save_image(image, "async_sorter", time_prefix)
            logging.info(
                f"[{self._type()}] Saving images took {1000 * (time.time() - start_time_saving)} ms.")

        self._callback(image_idx, detection_results_list)
