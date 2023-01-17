import logging
import os.path
import time
from datetime import datetime, timedelta
from typing import List

from PIL import Image

from lego_sorter_server.service.BrickCategoryConfig import BrickCategoryConfig
from lego_sorter_server.service.ImageProtoUtils import ImageProtoUtils
from lego_sorter_server.sorter.AsyncSortingProcessor import AsyncSortingProcessor
from lego_sorter_server.sorter.workers.WorkersContainer import WorkersContainer
from lego_sorter_server.tester.TesterConfig import TesterConfig


class AsyncSorterTester:
    def __init__(self, brick_category_config: BrickCategoryConfig, save_images_to_file: bool, reset_state_on_stop: bool,
                 skip_sorted_bricks_classification: bool, workers: WorkersContainer, tester_config: TesterConfig):
        self.sortingProcessor = AsyncSortingProcessor(brick_category_config, save_images_to_file, reset_state_on_stop,
                                                      skip_sorted_bricks_classification, workers)

        self.workers: WorkersContainer = workers
        self.tester_config: TesterConfig = tester_config
        self.source_images: List[Image] = []

        if not os.path.isdir(self.tester_config.path_to_source_images):
            logging.error('[AsyncSorterTester] Invalid path to source images dir: {0}'.format(
                self.tester_config.path_to_source_images))
            return
        self.read_images_from_directory()

    def run_test(self):
        if len(self.source_images) == 0:
            logging.error('[AsyncSorterTester] No images found in source image directory: {0}'.format(
                self.tester_config.path_to_source_images))
            return

        self.prepare_test()
        time.sleep(5)

        start_time = datetime.now()
        last_enqueue_time = start_time - timedelta(seconds=self.tester_config.delay)
        logging.info("[AsyncSorterTester] Start time: {}.".format(start_time))

        image_id = 0

        # Test run
        while (datetime.now() - start_time).total_seconds() < self.tester_config.time_run:
            # Delay
            while (datetime.now() - last_enqueue_time).total_seconds() < self.tester_config.delay:
                time.sleep(self.tester_config.delay / 100)

            logging.debug("[AsyncSorterTester] Sending image {0} to sorter.".format(image_id))
            self.process_image(self.source_images[image_id])
            last_enqueue_time = datetime.now()

            image_id += 0
            if image_id == len(self.source_images):
                image_id = 0

        logging.info("[AsyncSorterTester] Stopping sorter after {:.2f} seconds.".format(
            (datetime.now() - start_time).total_seconds()))

        self.end_test()

    def prepare_test(self):
        logging.info("[AsyncSorterTester] Setting conveyor speed: {0}.".format(self.tester_config.conveyor_speed))
        self.update_configuration(self.tester_config.conveyor_speed)

        logging.info("[AsyncSorterTester] Starting conveyor.")
        self.sortingProcessor.start_machine()

        logging.info("[AsyncSorterTester] Starting sorter.")
        self.sortingProcessor.start_sorting()

    def end_test(self):
        self.sortingProcessor.stop_sorting()
        self.sortingProcessor.stop_machine()
        logging.info("[AsyncSorterTester] Test finished.")
        self.workers.end_processes()

    def read_images_from_directory(self):
        image_file_names = [x for x in os.listdir(self.tester_config.path_to_source_images) if
                            os.path.isfile(os.path.join(self.tester_config.path_to_source_images, x))]
        for f_name in image_file_names:
            image = Image.open(os.path.join(self.tester_config.path_to_source_images, f_name))
            image = image.convert('RGB')
            self.source_images.append(image)

    def process_image(self, image: Image):
        image = ImageProtoUtils.prepare_image(image, 0)
        self.sortingProcessor.enqueue_image(image)

    def update_configuration(self, speed: int):
        logging.info("[AsyncSorterTester] Setting machine speed to: {0}.".format(speed))
        self.sortingProcessor.set_machine_speed(speed)
