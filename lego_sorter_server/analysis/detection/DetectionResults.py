import copy
from typing import List, Tuple
from lego_sorter_server.generated.Messages_pb2 import BoundingBox

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

    @classmethod
    def from_bounding_box(cls, bounding_box: BoundingBox):
        return cls(
            bounding_box.ymin,
            bounding_box.xmin,
            bounding_box.ymax,
            bounding_box.xmax
        )

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

    def to_bounding_box(self) -> BoundingBox:
        bb = BoundingBox()
        bb.ymin, bb.xmin, bb.ymax, bb.xmax = self.y_min, self.x_min, self.y_max, self.x_max
        return bb


class DetectionResult:
    def __init__(self, detection_score: float, detection_class: str, detection_box: DetectionBox):
        self.d_score: float = detection_score
        self.d_class: str = detection_class
        self.d_box: DetectionBox = detection_box

    @classmethod
    def from_bounding_box(cls, bounding_box: BoundingBox):
        return cls(
            bounding_box.score,
            bounding_box.label,
            DetectionBox.from_bounding_box(bounding_box)
        )

    def to_bounding_box(self) -> BoundingBox:
        bb = self.d_box.to_bounding_box()
        bb.score = self.d_score
        bb.label = self.d_class
        return bb


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

    def scores_to_list(self):
        return [r.d_score for r in self]

    def classes_to_list(self):
        return [r.d_class for r in self]

    def boxes_to_list(self):
        return [r.d_box for r in self]
