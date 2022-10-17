from typing import List

from lego_sorter_server.common.ClassificationResults import ClassificationResult, ClassificationResultsList
from lego_sorter_server.common.DetectionResults import DetectionBox, DetectionResult, DetectionResultsList


class AnalysisResult:
    def __init__(self,
                 detection_box: DetectionBox = None,
                 detection_score: float = None,
                 detection_class: str = None,
                 classification_score: float = None,
                 classification_class: str = None):
        self.detection_box: DetectionBox = detection_box
        self.detection_score: float = detection_score
        self.detection_class: str = detection_class
        self.classification_score: float = classification_score
        self.classification_class: str = classification_class

    @classmethod
    def results_merged(cls, classification_result: ClassificationResult,
                       detection_result: DetectionResult):
        return cls(
            detection_box=detection_result.detection_box,
            detection_class=detection_result.detection_class,
            detection_score=detection_result.detection_score,
            classification_score=classification_result.classification_score,
            classification_class=classification_result.classification_class
        )


class AnalysisResultsList(List[AnalysisResult]):
    @classmethod
    def results_merged(cls, classification_results: ClassificationResultsList,
                       detection_results: DetectionResultsList):
        assert len(classification_results) \
               == len(detection_results)

        return cls(
            [
                AnalysisResult.results_merged(
                    classification_result=classification_results[idx],
                    detection_result=detection_results[idx]
                ) for idx in range(len(classification_results))
            ]
        )
