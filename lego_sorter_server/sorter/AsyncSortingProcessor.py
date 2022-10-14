import logging
import time

from typing import List, Tuple, Dict
from PIL.Image import Image

from lego_sorter_server.service.BrickCategoryConfig import BrickCategoryConfig
from lego_sorter_server.sorter.LegoSorterController import LegoSorterController


class AsyncSortingProcessor:
    def __init__(self, brick_category_config: BrickCategoryConfig):
        self.sorter_controller: LegoSorterController = LegoSorterController(brick_category_config)

    def start_machine(self):
        self.sorter_controller.run_conveyor()

    def stop_machine(self):
        self.sorter_controller.stop_conveyor()

    def set_machine_speed(self, speed: int):
        self.sorter_controller.set_machine_speed(speed)
