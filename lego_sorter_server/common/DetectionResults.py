import copy
from typing import Tuple, Callable, List

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
            bounding_box.xmax,
        )

    def to_bounding_box(self) -> BoundingBox:
        bb = BoundingBox()
        bb.ymin = self.y_min
        bb.xmin = self.x_min
        bb.ymax = self.y_max
        bb.xmax = self.x_max

        return bb

    def transform(self, func: Callable[[int], int]):
        self.y_min: int = func(self.y_min)
        self.x_min: int = func(self.x_min)
        self.y_max: int = func(self.y_max)
        self.x_max: int = func(self.x_max)

    def copy(self):
        return DetectionBox(
            copy.deepcopy(self.y_min),
            copy.deepcopy(self.x_min),
            copy.deepcopy(self.y_max),
            copy.deepcopy(self.x_max)
        )

    def to_tuple(self):
        """
        Returns Tuple[   y_min,  x_min,  y_max,  x_max   ]
        """
        return [self.y_min, self.x_min, self.y_max, self.x_max]


class DetectionResult:
    def __init__(self, detection_box: DetectionBox, detection_score: float, detection_class: str):
        self.detection_box: DetectionBox = detection_box
        self.detection_class: str = detection_class
        self.detection_score: float = detection_score

    def to_bounding_box(self) -> BoundingBox:
        bb = BoundingBox()
        bb.ymin = self.detection_box.y_min
        bb.xmin = self.detection_box.x_min
        bb.ymax = self.detection_box.y_max
        bb.xmax = self.detection_box.x_max

        bb.label = self.detection_class
        bb.score = self.detection_score
        return bb


class DetectionResultsList(List[DetectionResult]):
    @classmethod
    def from_dict(cls, results: dict):
        assert len(results[DETECTION_BOXES_NAME]) \
               == len(results[DETECTION_CLASSES_NAME]) \
               == len(results[DETECTION_SCORES_NAME])

        return cls(
            [
                DetectionResult(
                    detection_box=DetectionBox.from_tuple(results[DETECTION_BOXES_NAME][idx]),
                    detection_class=results[DETECTION_CLASSES_NAME][idx],
                    detection_score=results[DETECTION_SCORES_NAME][idx]
                ) for idx in range(len(results[DETECTION_BOXES_NAME]))
            ]
        )

    @classmethod
    def from_lists(cls,
                   detection_boxes: List[DetectionBox] = None,
                   detection_classes: List[str] = None,
                   detection_scores: List[float] = None):
        assert len(detection_boxes) == \
               len(detection_classes) == \
               len(detection_scores)

        return cls(
            [
                DetectionResult(
                    detection_box=detection_boxes[idx],
                    detection_class=detection_classes[idx],
                    detection_score=detection_scores[idx]
                ) for idx in range(len(detection_boxes))
            ]
        )

    def to_list_of_boxes(self) -> List[DetectionBox]:
        return [x.detection_box for x in self]

    def to_list_of_boxes_as_tuples(self) -> List[List[int]]:
        return [x.detection_box.to_tuple() for x in self]

    def to_list_of_scores(self) -> List[float]:
        return [x.detection_score for x in self]

    def to_list_of_classes(self) -> List[str]:
        return [x.detection_class for x in self]
