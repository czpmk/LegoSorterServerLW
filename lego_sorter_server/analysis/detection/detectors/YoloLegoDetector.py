import os
import threading
import time
import logging
import torch
import numpy
from pathlib import Path

from lego_sorter_server.analysis.detection.detectors.LegoDetector import LegoDetector
from lego_sorter_server.common.DetectionResults import DetectionResultsList, DetectionBox
from lego_sorter_server.common.ThreadSafeSingleton import ThreadSafeSingleton


class YoloLegoDetector(LegoDetector, metaclass=ThreadSafeSingleton):
    def __init__(self, model_path=os.path.join("lego_sorter_server", "analysis", "detection", "models", "yolo_model",
                                               "yolov5_medium_extended.pt")):
        self.__initialized = False
        self.model_path = Path(model_path).absolute()

    def __initialize__(self):
        if self.__initialized:
            raise Exception("YoloLegoDetector already initialized")

        if not self.model_path.exists():
            logging.error(f"[YoloLegoDetector] No model found in {str(self.model_path)}")
            raise RuntimeError(f"[YoloLegoDetector] No model found in {str(self.model_path)}")

        start_time = time.time()
        self.model = torch.hub.load('ultralytics/yolov5', 'custom', path=str(self.model_path))
        if torch.cuda.is_available():
            self.model.cuda()
        elapsed_time = time.time() - start_time

        logging.info("Loading model took {} seconds".format(elapsed_time))
        self.__initialized = True

    @staticmethod
    def xyxy2yxyx_scaled(xyxy):
        """
        returns (ymin, xmin, ymax, xmax)
        """
        return numpy.array([[coord[1], coord[0], coord[3], coord[2]] for coord in xyxy])

    @staticmethod
    def convert_results_to_common_format(results) -> DetectionResultsList:
        image_predictions = results.xyxyn[0].cpu().numpy()
        scores = image_predictions[:, 4]
        classes = image_predictions[:, 5].astype(numpy.int64) + 1
        boxes = YoloLegoDetector.xyxy2yxyx_scaled(image_predictions[:, :4])

        return DetectionResultsList.from_lists(
            detection_scores=scores,
            detection_classes=classes,
            detection_boxes=[DetectionBox.from_tuple(x) for x in boxes]
        )

    def detect_lego(self, image: numpy.ndarray) -> DetectionResultsList:
        if not self.__initialized:
            logging.info("YoloLegoDetector is not initialized, this process can take a few seconds for the first time.")
            self.__initialize__()

        logging.info("[YoloLegoDetector][detect_lego] Detecting bricks...")
        start_time = time.time()
        results = self.model([image], size=image.shape[0])
        elapsed_time = 1000 * (time.time() - start_time)
        logging.info("[YoloLegoDetector][detect_lego] Detecting bricks took {:.3f} milliseconds".format(elapsed_time))

        return self.convert_results_to_common_format(results)
