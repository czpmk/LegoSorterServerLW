from lego_sorter_server.common.AnalysisResults import AnalysisResultsList


class BrickSortingStatus:
    def __init__(self, brick_id: int):
        self.brick_id = brick_id
        self.analysis_results_list: AnalysisResultsList = AnalysisResultsList()
        self.detected = False
        self.classified = False
        self.final_classification_class = None
        self.sorted = False

    def to_list_of_dicts(self):
        results = []
        for result_id in range(len(self.analysis_results_list)):
            results.append(
                {
                    'brick_id': self.brick_id,
                    'result_id': result_id,
                    'detected': str(self.detected),
                    'classified': str(self.classified),
                    'sorted': str(self.sorted),
                    'final_classification_class': str(self.final_classification_class),
                }
            )
            results[-1].update(self.analysis_results_list[result_id].to_dict())

        return results
