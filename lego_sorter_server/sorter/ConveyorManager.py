import logging
import math
import time

from collections import OrderedDict
from typing import List, Optional, Dict

from lego_sorter_server.common.AnalysisResults import AnalysisResult
from lego_sorter_server.service.BrickCategoryConfig import BrickCategoryConfig
from lego_sorter_server.sorter.LegoSorterController import LegoSorterController


class ConveyorManager:
    def __init__(self, brick_category_config: BrickCategoryConfig):
        self.CAMERA_POSITION_VERTICAL: float = 100.0
        """ Elevation of the camera over the conveyor belt """
        self.CAMERA_POSITION_HORIZONTAL: float = 20.0
        """ 
            Horizontal distance between the camera and the end of the conveyor belt. 
            Negative value if the camera is beyond the end of the belt. 
        """
        self.CAMERA_ANGLE: float = 0.35
        """
            Camera angle [radians]. 0 means it points vertically down.
        """
        self.SPEED: float = 50
        """
            Conveyor belt speed [-/sec]
        """

        self.sorter_controller: LegoSorterController = LegoSorterController(brick_category_config)

    def set_machine_speed(self, speed: float):
        self.SPEED = speed
        self.sorter_controller.set_machine_speed(speed)

    def place_in_a_bucket(self, brick: AnalysisResult):
        self.sorter_controller.on_brick_recognized(brick)

    def move_by(self, current_position: int, new_position: int):
        """
            Move conveyor belt so that the point at relative 'current_position' moves to relative 'new_position'
        """
        distance: float = self._get_real_distance(current_position, new_position)
        conveyor_run_time: float = abs(distance / self.SPEED)

        logging.info('[ConveyorManager] Moving conveyor by distance {:.2f}, (speed: {:.2f}, run time: {:.2f})'.format(
            distance, self.SPEED, conveyor_run_time
        ))
        self.sorter_controller.run_conveyor()
        time.sleep(conveyor_run_time)
        self.sorter_controller.stop_conveyor()

    def _get_real_distance(self, current_position: int, new_position: int) -> float:
        """
            Get distance by which the conveyor belt shall move in order to move the relative position of the point from
            'current_position' to 'new_position'
        """
        return self._get_real_position(new_position) - self._get_real_position(current_position)

    def _get_real_position(self, relative_position: int) -> float:
        """
            Get position of the point on conveyor belt given the 'relative_position' argument as position of the point
            on the picture.
        """
        y = self.CAMERA_POSITION_VERTICAL
        x = self.CAMERA_POSITION_HORIZONTAL
        alpha = self.CAMERA_ANGLE
        return x + y * (relative_position * math.cos(alpha) - x) / (y - relative_position * math.sin(alpha))
