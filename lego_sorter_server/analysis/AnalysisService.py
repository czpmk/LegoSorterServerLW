import logging
from typing import Tuple, List, Callable

import numpy

from PIL.Image import Image

from lego_sorter_server.analysis.classification.LegoClassifierProvider import LegoClassifierProvider
from lego_sorter_server.analysis.classification.classifiers.TFLegoClassifier import TFLegoClassifier
from lego_sorter_server.analysis.detection import DetectionUtils
from lego_sorter_server.analysis.detection.detectors.LegoDetector import LegoDetector
from lego_sorter_server.analysis.detection.detectors.LegoDetectorProvider import LegoDetectorProvider
from lego_sorter_server.common.ClassificationResults import ClassificationResultsList
from lego_sorter_server.common.DetectionResults import DetectionResultsList


class AnalysisService:
    DEFAULT_IMAGE_DETECTION_SIZE = (640, 640)
    BORDER_MARGIN_RELATIVE = 0.001

    def __init__(self):
        self.detector: LegoDetector = LegoDetectorProvider.get_default_detector()
        self.classifier = LegoClassifierProvider.get_default_classifier()

    def detect(self, image: Image, resize: bool = True, threshold=0.5,
               discard_border_results: bool = True) -> DetectionResultsList:
        if image.size is not AnalysisService.DEFAULT_IMAGE_DETECTION_SIZE and resize is False:
            logging.warning(f"[AnalysisService] Requested detection on an image with a non-standard size {image.size} "
                            f"but 'resize' parameter is {resize}.")

        scale = 1
        original_size = image.size
        if image.size is not AnalysisService.DEFAULT_IMAGE_DETECTION_SIZE and resize is True:
            logging.info(f"[AnalysisService] Resizing an image from "
                         f"{image.size} to {AnalysisService.DEFAULT_IMAGE_DETECTION_SIZE}")
            image, scale = DetectionUtils.resize(image, AnalysisService.DEFAULT_IMAGE_DETECTION_SIZE[0])

        if discard_border_results:
            accepted_xy_range = [(original_size[0] * scale) / image.size[0], (original_size[1] * scale) / image.size[1]]
        else:
            accepted_xy_range = [1, 1]

        detection_results = self.detector.detect_lego(numpy.array(image))
        detection_results = self.filter_detection_results(detection_results, threshold, accepted_xy_range)

        return self.translate_bounding_boxes_to_original_size(detection_results,
                                                              scale,
                                                              original_size,
                                                              self.DEFAULT_IMAGE_DETECTION_SIZE[0])

    def classify(self, images: List[Image]) -> ClassificationResultsList:
        return self.classifier.predict(images)

    def detect_and_classify(self, image: Image, detection_threshold: float = 0.5, discard_border_results: bool = True) \
            -> Tuple[DetectionResultsList, ClassificationResultsList]:
        detection_results = self.detect(image, threshold=detection_threshold,
                                        discard_border_results=discard_border_results)

        cropped_images = []
        for result in detection_results:
            cropped_image = DetectionUtils.crop_with_margin_from_detection_box(image, result.detection_box)
            cropped_images.append(cropped_image)

        classification_results = self.classify(cropped_images)

        return detection_results, classification_results

    @staticmethod
    def translate_bounding_boxes_to_original_size(detection_results: DetectionResultsList,
                                                  scale: float,
                                                  target_image_size: Tuple[int, int],  # (width, height)
                                                  detection_image_size: int = 640) -> DetectionResultsList:
        width, height = target_image_size[0], target_image_size[1]
        transformation: Callable[[int], int] = lambda x: int(x * detection_image_size * 1 / scale)

        for i in range(len(detection_results)):
            detection_results[i].detection_box.transform(transformation)

            # if y_max >= target_image_size[1] or x_max >= target_image_size[0]:
            #     continue
            detection_results[i].detection_box.y_max = min(detection_results[i].detection_box.y_max, height)
            detection_results[i].detection_box.x_max = min(detection_results[i].detection_box.x_max, width)

        return detection_results

    def filter_detection_results(self, detection_results: DetectionResultsList, threshold: float,
                                 accepted_xy_range) -> DetectionResultsList:
        limit = len(detection_results)
        for idx in range(len(detection_results)):
            if detection_results[idx].detection_score < threshold:
                limit = idx
                break

        filtered_by_score: DetectionResultsList = detection_results[:limit]

        if accepted_xy_range == [1, 1]:
            return filtered_by_score
        else:
            # results = []
            filtered_by_box = DetectionResultsList()
            for res in filtered_by_score:
                if res.detection_box.y_min < self.BORDER_MARGIN_RELATIVE \
                        or res.detection_box.x_min < self.BORDER_MARGIN_RELATIVE \
                        or res.detection_box.y_max > accepted_xy_range[1] - self.BORDER_MARGIN_RELATIVE \
                        or res.detection_box.x_max > accepted_xy_range[0] - self.BORDER_MARGIN_RELATIVE:
                    continue
                filtered_by_box.append(res)

            return filtered_by_box
