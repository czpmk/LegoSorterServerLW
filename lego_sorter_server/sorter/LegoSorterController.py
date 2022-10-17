import logging

import requests

from lego_sorter_server.common.AnalysisResults import AnalysisResult
from lego_sorter_server.service.BrickCategoryConfig import BrickCategoryConfig


class LegoSorterController:
    # TODO: PARAMETERIZE WITH CONFIG!
    # CONVEYOR_LOCAL_ADDRESS = "http://192.168.83.45:8000"
    # SORTER_LOCAL_ADDRESS = "http://192.168.83.45:8001"

    CONVEYOR_LOCAL_ADDRESS = "http://127.0.0.1:8000"
    SORTER_LOCAL_ADDRESS = "http://127.0.0.1:8001"

    def __init__(self, brick_category_config: BrickCategoryConfig):
        self.speed = 50
        self.brickCategoryConfig = brick_category_config

    def run_conveyor(self):
        requests.get(f"{self.CONVEYOR_LOCAL_ADDRESS}/start?duty_cycle={self.speed}")

    def stop_conveyor(self):
        requests.get(f"{self.CONVEYOR_LOCAL_ADDRESS}/stop")

    def on_brick_recognized(self, brick: AnalysisResult):
        brick_coords, brick_cls, brick_prob = brick.detection_box, brick.classification_class, brick.classification_score
        cat_name, pos = self.brickCategoryConfig[brick_cls]
        logging.info(f"Moving brick with class: {brick_cls} to stack: {cat_name} (pos: {pos})")
        requests.get(f"{self.SORTER_LOCAL_ADDRESS}/sort?action={pos}")

    def set_machine_speed(self, speed):
        self.speed = speed
