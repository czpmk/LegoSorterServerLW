import os
from enum import Enum


class Operation(Enum):
    SyncSorter = 0
    AsyncSorter = 1

    @classmethod
    def from_string(cls, operation_name: str):
        return {
            "SyncSorter": Operation.SyncSorter,
            "AsyncSorter": Operation.AsyncSorter
        }.get(operation_name)


class TesterConfig:
    def __init__(self, operation: Operation, time_run: int, delay: int, path_to_images: str):
        self.time_run: int = time_run
        ''' Tester time of run in seconds: int '''

        self.delay: float = float(delay) / 1000
        ''' Capture delay value in seconds: int. Expected delay argument in milliseconds. '''

        self.path_to_source_images: str = path_to_images
        self.conveyor_speed: int = 50
        self.operation: Operation = operation
