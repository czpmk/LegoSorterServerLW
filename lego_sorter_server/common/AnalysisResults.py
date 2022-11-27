from typing import List, Dict, Any

from PIL.Image import Image

from lego_sorter_server.analysis.detection import DetectionUtils
from lego_sorter_server.common.ClassificationResults import ClassificationResult, ClassificationResultsList
from lego_sorter_server.common.DetectionResults import DetectionBox, DetectionResult, DetectionResultsList


class AnalysisResult:
    def __init__(self,
                 detection_box: DetectionBox = None,
                 detection_score: float = None,
                 detection_class: str = None,
                 classification_score: float = None,
                 classification_class: str = None,
                 image: Image = None):
        self.detection_box: DetectionBox = detection_box
        self.detection_score: float = detection_score
        self.detection_class: str = detection_class
        self.classification_score: float = classification_score
        self.classification_class: str = classification_class
        self.image: Image = image

    @classmethod
    def from_detection_result(cls, detection_result: DetectionResult, image: Image):
        return cls(
            detection_box=detection_result.detection_box,
            detection_class=detection_result.detection_class,
            detection_score=detection_result.detection_score,
            image=image
        )

    @classmethod
    def from_detection_and_classification_result(cls, classification_result: ClassificationResult,
                                                 detection_result: DetectionResult):
        return cls(
            detection_box=detection_result.detection_box,
            detection_class=detection_result.detection_class,
            detection_score=detection_result.detection_score,
            classification_score=classification_result.classification_score,
            classification_class=classification_result.classification_class
        )

    def merge_classification_result(self, classification_result: ClassificationResult):
        self.classification_score = classification_result.classification_score
        self.classification_class = classification_result.classification_class

    def to_dict(self) -> Dict[str, Any]:
        analysis_result = {
            'classification_class': self.classification_class,
            'classification_score': self.classification_score,
            'detection_class': self.detection_class,
            'detection_score': self.detection_score
        }
        analysis_result.update({'detection_box.{0}'.format(k): v for k, v in self.detection_box.to_dict().items()})
        return analysis_result


class AnalysisResultsList(List[AnalysisResult]):
    @classmethod
    def results_merged(cls, classification_results: ClassificationResultsList,
                       detection_results: DetectionResultsList):
        assert len(classification_results) \
               == len(detection_results)

        return cls(
            [
                AnalysisResult.from_detection_and_classification_result(
                    classification_result=classification_results[idx],
                    detection_result=detection_results[idx]
                ) for idx in range(len(classification_results))
            ]
        )

    @classmethod
    def from_detection_results_with_image(cls, detection_results_list: DetectionResultsList, image: Image):
        return cls(
            [
                AnalysisResult.from_detection_result(
                    detection_result,
                    DetectionUtils.crop_with_margin_from_detection_box(image,
                                                                       detection_result.detection_box)
                )
                for detection_result in detection_results_list
            ]
        )
