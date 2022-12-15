from datetime import datetime
from enum import Enum
from math import floor
from typing import List, Dict, Any, Optional

from PIL.Image import Image

from lego_sorter_server.analysis.detection import DetectionUtils
from lego_sorter_server.common.ClassificationResults import ClassificationResult, ClassificationResultsList
from lego_sorter_server.common.DetectionResults import DetectionBox, DetectionResult, DetectionResultsList


class ClassificationStrategy(Enum):
    MEDIAN = 1
    BEST = 2
    WORST = 3


class AnalysisResult:
    def __init__(self,
                 detection_box: DetectionBox = None,
                 detection_score: float = None,
                 detection_class: str = None,
                 classification_score: float = None,
                 classification_class: str = None,
                 image_id: int = None,
                 image: Image = None,
                 time_enqueued: datetime = None,
                 time_detected: datetime = None,
                 time_classified: datetime = None,
                 time_sorted: datetime = None):
        self.detection_box: DetectionBox = detection_box
        self.detection_score: float = detection_score
        self.detection_class: str = detection_class
        self.classification_score: float = classification_score
        self.classification_class: str = classification_class
        self.image_id: int = image_id
        self.image: Image = image
        self.time_enqueued: datetime = time_enqueued
        self.time_detected: datetime = time_detected
        self.time_classified: datetime = time_classified
        self.time_sorted: datetime = time_sorted

    @classmethod
    def from_results(cls, classification_result: ClassificationResult,
                     detection_result: DetectionResult):
        return cls(
            detection_box=detection_result.detection_box,
            detection_class=detection_result.detection_class,
            detection_score=detection_result.detection_score,
            classification_score=classification_result.classification_score,
            classification_class=classification_result.classification_class
        )

    @classmethod
    def from_detection_with_image(cls, detection_result: DetectionResult, image: Image):
        return cls(
            detection_box=detection_result.detection_box,
            detection_class=detection_result.detection_class,
            detection_score=detection_result.detection_score,
            image=image
        )

    def set_classification_score(self, classification_score: float):
        self.classification_score = classification_score

    def set_classification_class(self, classification_class: str):
        self.classification_class = classification_class

    def merge_classification_result(self, classification_result: ClassificationResult):
        self.classification_score = classification_result.classification_score
        self.classification_class = classification_result.classification_class

    def to_dict(self) -> Dict[str, Any]:
        analysis_result = {
            'time_enqueued': self.time_enqueued.strftime('%H:%M:%S.%f') if self.time_enqueued is not None else None,
            'time_detected': self.time_detected.strftime('%H:%M:%S.%f') if self.time_detected is not None else None,
            'time_classified': self.time_classified.strftime(
                '%H:%M:%S.%f') if self.time_classified is not None else None,
            'image_id': self.image_id,
            'classification_class': self.classification_class,
            'classification_score': self.classification_score,
            'detection_class': self.detection_class,
            'detection_score': self.detection_score,
        }
        analysis_result.update({'detection_box.{0}'.format(k): v for k, v in self.detection_box.to_dict().items()})
        return analysis_result


class AnalysisResultsList(List[AnalysisResult]):
    @classmethod
    def from_results_lists(cls, classification_results: ClassificationResultsList,
                           detection_results: DetectionResultsList):
        assert len(classification_results) \
               == len(detection_results)

        return cls(
            [
                AnalysisResult.from_results(
                    classification_result=classification_results[idx],
                    detection_result=detection_results[idx]
                ) for idx in range(len(classification_results))
            ]
        )

    @classmethod
    def from_detections_with_image(cls, detection_results_list: DetectionResultsList, image: Image):
        return cls(
            [
                AnalysisResult.from_detection_with_image(
                    detection_result=detection_result,
                    image=DetectionUtils.crop_with_margin_from_detection_box(image, detection_result.detection_box)
                )
                for detection_result in detection_results_list
            ]
        )

    def get_classified(self):
        return AnalysisResultsList([x for x in self if x.classification_class is not None])

    def get_result(self, strategy: ClassificationStrategy) -> Optional[AnalysisResult]:
        subset: AnalysisResultsList = self.get_classified()
        if len(subset) == 0:
            return None

        subset.sort(key=lambda x: x.classification_class, reverse=True)

        return {
            ClassificationStrategy.MEDIAN: subset[floor(len(subset) / 2)],
            ClassificationStrategy.BEST: subset[0],
            ClassificationStrategy.WORST: subset[-1]
        }.get(strategy, None)
