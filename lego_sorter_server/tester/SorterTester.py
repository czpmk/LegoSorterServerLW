import logging
import os
import time
from abc import abstractmethod

from lego_sorter_server.service.BrickCategoryConfig import BrickCategoryConfig
from lego_sorter_server.sorter.workers.WorkersContainer import WorkersContainer
from lego_sorter_server.tester.AsyncSorterTester import AsyncSorterTester
from lego_sorter_server.tester.SyncSorterTester import SyncSorterTester
from lego_sorter_server.tester.TesterConfig import TesterConfig, Operation


class SorterTester:
    @staticmethod
    def run(brick_category_config: BrickCategoryConfig, save_images_to_file: bool, reset_state_on_stop: bool,
            skip_sorted_bricks_classification: bool, workers: WorkersContainer, tester_config: TesterConfig):
        tester = {
            Operation.AsyncSorter: AsyncSorterTester(brick_category_config, save_images_to_file, reset_state_on_stop,
                                                     skip_sorted_bricks_classification, workers, tester_config),
            Operation.SyncSorter: SyncSorterTester(brick_category_config, save_images_to_file,
                                                   reset_state_on_stop, tester_config)
        }.get(tester_config.operation)

        logging.info("[SorterTester] Waiting 10s for Analysis Service to initialize.")
        time.sleep(10)

        tester.run_test()
