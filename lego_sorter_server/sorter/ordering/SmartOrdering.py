from collections import OrderedDict
from typing import List

from lego_sorter_server.common.AnalysisResults import AnalysisResultsList


class SmartOrdering:

    def __init__(self):

        # current_state is always per 1 image. AnalysisResultsList per brick
        self.current_state: OrderedDict[int, AnalysisResultsList] = OrderedDict()

        # List of results of sorted bricks
        self.history: List[AnalysisResultsList] = []

