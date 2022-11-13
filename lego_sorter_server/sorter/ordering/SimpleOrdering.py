import logging

from collections import OrderedDict
from typing import List, Optional, Dict

from lego_sorter_server.common.AnalysisResults import AnalysisResultsList, AnalysisResult


class SimpleOrdering:
    BORDER_MARGIN = 5

    def __init__(self):
        self.memorized_state: OrderedDict[int, AnalysisResultsList] = OrderedDict()
        '''
        memorized state: for each index in OrderDict there is AnalysisResultsList OF THE SAME BRICK.
        e.g. given there are 6 nearly identical photos of the same layout of 3 bricks, memorized state shall contain
        3 lists (1 per brick), each of them containing 6 AnalysisResults (1 per photo)
        '''
        self.processed_bricks: List[AnalysisResultsList] = []
        '''processed_bricks: AnalysisResultsList per each processed brick'''
        self.head_index = -1
        '''this indicates the index of the first brick on the tape'''

    def process_current_results(self, results: AnalysisResultsList, image_height: int):
        if len(results) == 0:
            logging.info("[SimpleOrdering] No bricks detected. It means that all bricks have surpassed the camera line")
            self._extract_processed_bricks(len(self.memorized_state))
            return

        results = self.discard_border_results(results, image_height)

        if len(results) == 0:
            logging.info("[SimpleOrdering] There is no bricks to process after skipping border results.")
            self._extract_processed_bricks(len(self.memorized_state))
            return

        first_brick_from_history = self._get_first_brick()

        if first_brick_from_history is None:
            logging.info(f"[SimpleOrdering] Nothing in history, adding all results and moving the head index by 1")

            self.head_index = self.head_index + 1
            self._add_results_to_current_state(results, start_from=self.head_index)
            return

        first_brick_from_results: AnalysisResult = results[0]

        if self._is_the_same_brick(first_brick_from_history, first_brick_from_results):
            logging.info(f"[SimpleOrdering] No brick has surpassed the camera line."
                         f"\n\t\t\t First brick from the history:"
                         f"\n\t\t\t {first_brick_from_history}"
                         f"\n\t\t\t Is the same brick as the current first brick:"
                         f"\n\t\t\t {first_brick_from_results}")
            self._add_results_to_current_state(results, start_from=self.head_index)
            return
        else:
            logging.info(f"[SimpleOrdering] Another brick detected at the head position. "
                         f"It means that the previous first brick has surpassed the camera line.")
            passed_bricks_count = self._get_count_of_passed_bricks(current_state=results)
            if passed_bricks_count >= 2:
                logging.error(
                    f"[SimpleOrdering] {passed_bricks_count} bricks have overpassed the camera line!"
                    f"Such a state shouldn't happen. Sorting results can be incorrect.")

            self._extract_processed_bricks(count=passed_bricks_count)
            self._add_results_to_current_state(results, start_from=self.head_index)

    def _add_results_to_current_state(self, results: AnalysisResultsList, start_from: int):
        for idx in range(len(results)):
            history_of_brick: AnalysisResultsList = self.memorized_state.get(start_from + idx, AnalysisResultsList())
            history_of_brick.append(results[idx])
            self.memorized_state[start_from + idx] = history_of_brick

        logging.info(f"[SimpleOrdering] Added results, the current state is:"
                     f"\n {list(self.memorized_state.items())}")

    def get_current_state(self) -> Dict[int, AnalysisResult]:
        """
        Returns the memorized state of the belt in the following form:
            { index_of_the_brick: AnalysisResultsList, ... }
        """
        current_state = dict()
        for key, value in self.memorized_state.items():
            current_state[key] = value[-1]  # assign the most recent value

        return current_state

    def _get_first_brick(self) -> Optional[AnalysisResult]:
        res_list: AnalysisResultsList = self.memorized_state.get(self.head_index, AnalysisResultsList())
        if len(res_list) == 0:
            return None
        else:
            return res_list[-1]

    def reset(self):
        self.memorized_state.clear()
        self.head_index = -1
        self.processed_bricks: List[AnalysisResultsList] = []

    @staticmethod
    def _is_the_same_brick(older_view: AnalysisResult, current_view: AnalysisResult) -> bool:
        # Check if the position of the bounding box moved along the tape direction
        # Compare both y_min and y_max
        return older_view.detection_box.y_min <= current_view.detection_box.y_min or \
               older_view.detection_box.y_max <= current_view.detection_box.y_max

    def _extract_processed_bricks(self, count):
        for i in range(count):
            current_first: AnalysisResultsList = self.memorized_state.pop(self.head_index + i)
            self.processed_bricks.append(current_first)
            logging.info(f"[SimpleOrdering] A brick with id {self.head_index + i} was moved to the processed queue:"
                         f"\n {current_first}")

        self.head_index = self.head_index + count

    def get_count_of_results_to_send(self) -> int:
        return len(self.processed_bricks)

    def pop_first_processed_brick(self) -> Optional[AnalysisResultsList]:
        if len(self.processed_bricks) == 0:
            return None

        return self.processed_bricks.pop(0)

    def _get_count_of_passed_bricks(self, current_state: AnalysisResultsList) -> int:
        first_brick_on_the_tape_current = current_state[0]

        passed_count = 0
        for brick_snapshots in self.memorized_state.values():
            last_snapshot: AnalysisResult = brick_snapshots[-1]

            if first_brick_on_the_tape_current.detection_box.y_min <= last_snapshot.detection_box.y_min:
                passed_count = passed_count + 1
            else:
                break

        return passed_count

    def discard_border_results(self, results: AnalysisResultsList, image_height) -> AnalysisResultsList:
        first_brick = results[0]
        last_brick = results[-1]

        if first_brick.detection_box.y_max + self.BORDER_MARGIN >= image_height:
            logging.info(f"[SimpleOrdering] One result has been discarded as it exceeds the bottom camera line:"
                         f"\n{first_brick}")
            results = results[1:]

        if last_brick.detection_box.y_min - self.BORDER_MARGIN <= 0:
            logging.info(f"[SimpleOrdering] One result has been discarded as it exceeds the top camera line:"
                         f"\n{last_brick}")
            results = results[:-1]

        return results
