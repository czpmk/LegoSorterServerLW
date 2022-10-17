import os
import threading
import time
from typing import Callable

import numpy as np
import tensorflow as tf
import logging
from pathlib import Path

from lego_sorter_server.analysis.detection import DetectionUtils
from lego_sorter_server.analysis.detection.DetectionUtils import crop_with_margin

from lego_sorter_server.analysis.detection.detectors.LegoDetector import LegoDetector
from lego_sorter_server.common.DetectionResults import DetectionResultsList
from lego_sorter_server.common.ThreadSafeSingleton import ThreadSafeSingleton


class TFLegoDetector(LegoDetector, metaclass=ThreadSafeSingleton):

    def __init__(self, model_path=os.path.join("lego_sorter_server", "analysis", "detection", "models", "tf_model",
                                               "saved_model")):
        self.__initialized = False
        self.model_path = Path(model_path).absolute()

    @staticmethod
    def prepare_input_tensor(image):
        input_tensor = tf.convert_to_tensor(image)
        input_tensor = input_tensor[tf.newaxis, ...]
        return input_tensor

    def __initialize__(self):
        if self.__initialized:
            raise Exception("TFLegoDetector already initialized")

        if not self.model_path.exists():
            logging.error(f"[TFLegoDetector] No model found in {str(self.model_path)}")
            raise RuntimeError(f"[TFLegoDetector] No model found in {str(self.model_path)}")

        start_time = time.time()
        self.model = tf.saved_model.load(str(self.model_path))
        elapsed_time = time.time() - start_time

        logging.info("Loading model took {} seconds".format(elapsed_time))
        self.__initialized = True

    def detect_lego(self, image: np.array) -> DetectionResultsList:
        if not self.__initialized:
            logging.info("TFLegoDetector is not initialized, this process can take a few seconds for the first time.")
            self.__initialize__()

        input_tensor = self.prepare_input_tensor(image)
        detections = self.model(input_tensor)
        num_detections = int(detections.pop('num_detections'))
        detections = {key: value[0, :num_detections].numpy() for key, value in detections.items()}
        detections['num_detections'] = num_detections
        # detection_classes should be ints.
        detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

        detections_list = DetectionResultsList.from_dict(detections)

        return self.discard_results_under_threshold(detections_list)

    def detect_and_crop(self, image):
        width, height = image.size
        image_resized, scale = DetectionUtils.resize(image, 640)
        detections = self.detect_lego(np.array(image_resized))
        detected_counter = 0
        new_images = []

        transformation: Callable[[int], int] = lambda x: int(x * 640 * 1 / scale)

        for i in range(min(100, len(detections))):
            if detections[i].detection_score < 0.5:
                break  # IF SORTED

            detected_counter += 1
            db = detections[i].detection_box.copy()
            db.transform(transformation)

            # if bb is out of bounds
            if db.y_max >= height or db.x_max >= width:
                continue

            new_images += [crop_with_margin(image, db)]

        return new_images

    @staticmethod
    def discard_results_under_threshold(detections: DetectionResultsList, threshold=0.1) -> DetectionResultsList:
        limit = 1

        for idx in range(len(detections)):
            if detections[idx].detection_score < threshold:
                limit = idx
                break

        return detections[:limit]
