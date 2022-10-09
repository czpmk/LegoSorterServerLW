from typing import List, Tuple

CLASSIFICATION_SCORES_NAME = 'classification_scores'
CLASSIFICATION_CLASSES_NAME = 'classification_classes'


class ClassificationResult:
    def __init__(self, r_class: str, r_score: float):
        self.r_class: str = r_class
        self.r_score: float = r_score

    def to_tuple(self) -> Tuple[float, str]:
        return self.r_score, self.r_class


class ClassificationResultsList(List[ClassificationResult]):
    @classmethod
    def from_lists(cls, classes: List[str], scores: List[float]):
        assert len(classes) == len(scores)

        return cls(
            [ClassificationResult(classes[idx], scores[idx]) for idx in range(len(classes))]
        )

    @classmethod
    def from_dict(cls, results_dict: dict):
        assert len(results_dict[CLASSIFICATION_SCORES_NAME]) == len(results_dict[CLASSIFICATION_CLASSES_NAME])

        return cls(
            [
                ClassificationResult(results_dict[CLASSIFICATION_CLASSES_NAME][idx],
                                     results_dict[CLASSIFICATION_SCORES_NAME][idx])
                for idx in range(len(results_dict[CLASSIFICATION_CLASSES_NAME]))
            ]
        )

    def to_dict(self):
        return {
            CLASSIFICATION_CLASSES_NAME: [x.r_class for x in self],
            CLASSIFICATION_SCORES_NAME: [x.r_score for x in self]
        }

    def scores_to_list(self):
        return [r.r_score for r in self]

    def class_to_list(self):
        return [r.r_class for r in self]
