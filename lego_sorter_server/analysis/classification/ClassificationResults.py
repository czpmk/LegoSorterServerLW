from typing import List

CLASSIFICATION_SCORES_NAME = 'classification_scores'
CLASSIFICATION_CLASSES_NAME = 'classification_classes'


class ClassificationResult:
    def __init__(self, r_class: str, r_score: float):
        self.r_class: str = r_class
        self.r_score: float = r_score


class ClassificationResultsList(List):
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


class ClassificationResults:
    def __init__(self, classification_classes: List[str], classification_scores: List[float]):
        self.classification_classes = classification_classes
        self.classification_scores = classification_scores

    @staticmethod
    def from_dict(classification_results_dict):
        return ClassificationResults(classification_results_dict['classification_classes'],
                                     classification_results_dict['classification_scores'])

    @staticmethod
    def empty():
        return ClassificationResults([], [])

    def get_as_dict(self):
        return {'classification_classes', self.classification_classes,
                'classification_scores', self.classification_scores}
