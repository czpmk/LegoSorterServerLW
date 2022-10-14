from typing import List

CLASSIFICATION_SCORES_NAME = 'classification_scores'
CLASSIFICATION_CLASSES_NAME = 'classification_classes'


class ClassificationResult:
    def __init__(self, classification_score: float, classification_label: str):
        self.classification_label: str = classification_label
        self.classification_score: float = classification_score


class ClassificationResultsList(List[ClassificationResult]):
    @classmethod
    def from_dict(cls, results: dict):
        assert len(results[CLASSIFICATION_SCORES_NAME]) \
               == len(results[CLASSIFICATION_CLASSES_NAME])

        return cls(
            [
                ClassificationResult(
                    classification_score=results[CLASSIFICATION_SCORES_NAME][idx],
                    classification_label=results[CLASSIFICATION_CLASSES_NAME][idx]
                ) for idx in range(len(results[CLASSIFICATION_SCORES_NAME]))
            ]
        )

    @classmethod
    def from_lists(cls,
                   classification_classes: List[str] = None,
                   classification_scores: List[float] = None):
        assert len(classification_scores) \
               == len(classification_classes)

        return cls(
            [
                ClassificationResult(
                    classification_score=classification_scores[idx],
                    classification_label=classification_classes[idx]
                ) for idx in range(len(classification_classes))
            ]
        )
