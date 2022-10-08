import copy
from enum import Enum
from typing import List, Tuple

DETECTION_SCORES_NAME = 'detection_scores'
DETECTION_CLASSES_NAME = 'detection_classes'
DETECTION_BOXES_NAME = 'detection_boxes'


class DetectionBox:
    def __init__(self, y_min: int, x_min: int, y_max: int, x_max: int):
        self.y_min: int = y_min
        self.x_min: int = x_min
        self.y_max: int = y_max
        self.x_max: int = x_max

    @classmethod
    def from_tuple(cls, coords: Tuple[int, int, int, int]):
        return cls(coords[0], coords[1], coords[2], coords[3])

    def transform(self, func):
        self.y_min = func(self.y_min)
        self.x_min = func(self.x_min)
        self.y_max = func(self.y_max)
        self.x_max = func(self.x_max)

    def resize(self, abs_margin: float, rel_margin: float):
        avg_length = ((self.x_max - self.x_min) + (self.y_max - self.y_min)) / 2
        self.y_min = max(self.y_min - abs_margin - (rel_margin * avg_length), 0)
        self.x_min = max(self.x_min - abs_margin - (rel_margin * avg_length), 0)
        self.y_max = max(self.y_max + abs_margin + (rel_margin * avg_length), 0)
        self.x_max = max(self.x_max + abs_margin + (rel_margin * avg_length), 0)

    def copy(self):
        return DetectionBox(
            copy.deepcopy(self.y_min),
            copy.deepcopy(self.x_min),
            copy.deepcopy(self.y_max),
            copy.deepcopy(self.x_max)
        )

    def to_tuple(self) -> Tuple[int, int, int, int]:
        return self.x_min, self.y_min, self.x_max, self.y_max


class DetectionResult:
    def __init__(self, detection_score: float, detection_class: str, detection_box: DetectionBox):
        self.detection_score: float = detection_score
        self.detection_class: str = detection_class
        self.detection_box: DetectionBox = detection_box


class DetectionResultsList(List[DetectionResult]):
    @classmethod
    def from_lists(cls, scores: List[float], classes: List[str], boxes: List[Tuple[int, int, int, int]]):
        assert len(scores) == len(classes) == len(boxes)

        return cls(
            [
                DetectionResult(scores[idx], classes[idx], DetectionBox.from_tuple(boxes[idx]))
                for idx in range(len(scores))
            ]
        )

    @classmethod
    def from_dict(cls, results_dict: dict):
        assert len(results_dict[DETECTION_SCORES_NAME]) \
               == len(results_dict[DETECTION_CLASSES_NAME]) \
               == len(results_dict[DETECTION_BOXES_NAME])

        return cls(
            [
                DetectionResult(results_dict[DETECTION_SCORES_NAME][idx],
                                results_dict[DETECTION_CLASSES_NAME][idx],
                                DetectionBox.from_tuple(results_dict[DETECTION_BOXES_NAME][idx]))
                for idx in range(len(results_dict[DETECTION_SCORES_NAME]))
            ]
        )
