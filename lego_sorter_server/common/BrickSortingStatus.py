from lego_sorter_server.common.AnalysisResults import AnalysisResultsList


class BrickSortingStatus:
    def __init__(self, brick_id: int):
        self.brick_id = brick_id
        self.analysis_results_list: AnalysisResultsList = AnalysisResultsList()
        self.detected = False
        self.classified = False
        self.final_classification_class = None
        self.sorted = False

    def to_dict(self, global_result_id: int = 0):
        results = {}
        for brick_result_id in range(len(self.analysis_results_list)):
            next_result = {
                'brick_id': self.brick_id,
                'result_id': brick_result_id,
                'detected': str(self.detected),
                'classified': str(self.classified),
                'sorted': str(self.sorted),
                'final_classification_class': str(self.final_classification_class),
            }
            next_result.update(self.analysis_results_list[brick_result_id].to_dict())

            results[global_result_id] = next_result
            global_result_id += 1

        return results
