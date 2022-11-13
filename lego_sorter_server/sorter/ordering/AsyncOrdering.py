from collections import OrderedDict
from typing import List

from PIL.Image import Image

from lego_sorter_server.common.AnalysisResults import AnalysisResultsList
from lego_sorter_server.common.ClassificationResults import ClassificationResult
from lego_sorter_server.common.DetectionResults import DetectionResultsList


class AsyncOrdering:

    def __init__(self):
        self.current_state: OrderedDict[int, AnalysisResultsList] = OrderedDict()
        '''Bricks on the conveyor belt'''

        self.history: OrderedDict[int, AnalysisResultsList] = OrderedDict()
        '''Sorted bricks'''

        self.head_idx = -1
        '''Index of first brick on the tape'''

        self.image_idx = -1
        '''Index of the last picture'''

    def register_picture(self) -> int:
        self.image_idx += 1
        return self.image_idx

    def on_detection(self, image_id: int, detection_results_list: DetectionResultsList):
        pass

    def on_classification(self, brick_id: int, classification_result: ClassificationResult):
        pass

    def on_sort(self, brick_id: int):
        pass
