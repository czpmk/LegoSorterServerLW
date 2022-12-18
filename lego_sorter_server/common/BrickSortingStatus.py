from datetime import datetime
from typing import Optional

from lego_sorter_server.common.AnalysisResults import AnalysisResultsList


class BrickSortingStatus:
    def __init__(self, brick_id: int):
        self.brick_id = brick_id
        self.analysis_results_list: AnalysisResultsList = AnalysisResultsList()
        # no 'detected' field, results for brick are only stored once the brick has been detected
        self.classified = False
        self.final_classification_class = None
        '''Class selected out of multiple results in order to sort the brick'''
        self.sorted = False
        self.time_sorted: Optional[datetime] = None

    def to_dict(self, global_result_id: int = 0):
        results = {}
        for brick_result_id in range(len(self.analysis_results_list)):
            next_result = {
                'brick_id': self.brick_id,
                'result_id': brick_result_id,
                'detected': True,
                'classified': self.analysis_results_list[brick_result_id].classification_class is not None,
                'sorted': str(self.sorted),
                'final_classification_class': str(self.final_classification_class),
                'time_sorted': self.time_sorted.strftime('%H:%M:%S.%f') if self.time_sorted is not None else None,
            }
            next_result.update(self.analysis_results_list[brick_result_id].to_dict())

            results[global_result_id] = next_result
            global_result_id += 1

        return results
