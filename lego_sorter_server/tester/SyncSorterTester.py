import logging
import os.path
import time
from datetime import datetime, timedelta
from typing import List, Dict

from PIL import Image

from lego_sorter_server.common.AnalysisResults import AnalysisResult
from lego_sorter_server.service.BrickCategoryConfig import BrickCategoryConfig
from lego_sorter_server.generated.Messages_pb2 import ImageRequest, BoundingBox, Empty, SorterConfiguration, \
    ListOfBoundingBoxesWithIndexes, BoundingBoxWithIndex
from lego_sorter_server.service.ImageProtoUtils import ImageProtoUtils
from lego_sorter_server.sorter.SortingProcessor import SortingProcessor
from lego_sorter_server.tester.TesterConfig import TesterConfig


class SyncSorterTester:
    def __init__(self, brick_category_config: BrickCategoryConfig, save_images_to_file: bool,
                 reset_state_on_stop: bool, tester_config: TesterConfig):
        self.sortingProcessor = SortingProcessor(brick_category_config)
        self.save_images_to_file = save_images_to_file
        self.reset_state_on_stop = reset_state_on_stop

        self.tester_config: TesterConfig = tester_config
        self.source_images: List[Image] = []

        if not os.path.isdir(self.tester_config.path_to_source_images):
            logging.error('[SyncSorterTester] Invalid path to source images dir: {0}'.format(
                self.tester_config.path_to_source_images))
            return
        self.read_images_from_directory()

    def run_test(self):
        if len(self.source_images) == 0:
            logging.error('[SyncSorterTester] No images found in source image directory: {0}'.format(
                self.tester_config.path_to_source_images))
            return

        self.prepare_test()
        self.initialize_sorter(30)

        start_time = datetime.now()
        last_enqueue_time = start_time - timedelta(seconds=self.tester_config.delay)
        logging.info("[SyncSorterTester] Start time: {}.".format(start_time))

        image_id = 0
        # main loop - lasts for time provided as time_run
        while (datetime.now() - start_time).total_seconds() < self.tester_config.time_run:
            # inner loop - waits for delay
            while (datetime.now() - last_enqueue_time).total_seconds() < self.tester_config.delay:
                time.sleep(self.tester_config.delay / 100)

            logging.debug("[SyncSorterTester] Sending image {0} to sorter.".format(image_id))
            self.process_image(self.source_images[image_id])
            last_enqueue_time = datetime.now()

            image_id += 0
            if image_id == len(self.source_images):
                image_id = 0

        logging.info("[SyncSorterTester] Stopping sorter after {:.2f} seconds.".format(
            (datetime.now() - start_time).total_seconds()))

        self.end_test()

    def initialize_sorter(self, timeout: int):
        """ Send initial request item to sorter and wait until classified. timeout: int [s] """
        start_time = datetime.now()
        self.process_image(self.source_images[0])

        while True:
            time.sleep(0.5)

            # check if brick has been classified
            brick_id: int = next(iter(self.sortingProcessor.ordering.bricks.keys()), None)
            if brick_id is not None:
                brick = self.sortingProcessor.ordering.bricks[brick_id]
                if len(brick.analysis_results_list) > 0 and \
                        brick.analysis_results_list[0].classification_class is not None:
                    break

            if (datetime.now() - start_time).total_seconds() > timeout:
                logging.exception(
                    "[SyncSorterTester] Initialization Timeout {0}. Proceeding with the test.".format(timeout))
                break

            logging.info("[SyncSorterTester] Waiting for classification...")

        logging.info("[SyncSorterTester] Initialization took {:.2f} seconds.".format(
            (datetime.now() - start_time).total_seconds()))


    def prepare_test(self):
        logging.info("[SyncSorterTester] Setting conveyor speed: {0}.".format(self.tester_config.conveyor_speed))
        self.update_configuration(self.tester_config.conveyor_speed)

        logging.info("[SyncSorterTester] Starting sorter.")
        self.sortingProcessor.start_machine()

    def end_test(self):
        self.sortingProcessor.stop_machine()

        if self.reset_state_on_stop:
            self.sortingProcessor.reset()
        logging.info("[SyncSorterTester] Test finished.")

    def process_image(self, image: Image) -> ListOfBoundingBoxesWithIndexes:
        start_time = time.time()
        logging.info("[SyncSorterTester] Got an image request. Processing...")
        image = ImageProtoUtils.prepare_image(image, 0)
        current_state = self.sortingProcessor.process_next_image(image, self.save_images_to_file)

        response = self._prepare_response_from_sorter_state(current_state=current_state)
        elapsed_milliseconds = int(1000 * (time.time() - start_time))
        logging.info(f"[SyncSorterTester] Processing the request took {elapsed_milliseconds} milliseconds.")

        return response

    def update_configuration(self, speed: int):
        logging.info("[SyncSorterTester] Setting machine speed to: {0}.".format(speed))
        self.sortingProcessor.set_machine_speed(speed)

    def read_images_from_directory(self):
        image_file_names = [x for x in os.listdir(self.tester_config.path_to_source_images) if
                            os.path.isfile(os.path.join(self.tester_config.path_to_source_images, x))]
        for f_name in image_file_names:
            image = Image.open(os.path.join(self.tester_config.path_to_source_images, f_name))
            image = image.convert('RGB')
            self.source_images.append(image)

    @staticmethod
    def _prepare_response_from_sorter_state(current_state: Dict[int, AnalysisResult]) -> ListOfBoundingBoxesWithIndexes:
        bbs_with_indexes = []
        for key, value in current_state.items():
            bb = BoundingBox()
            bb.ymin, bb.xmin, bb.ymax, bb.xmax = value.detection_box.to_tuple()
            bb.label = value.classification_class
            bb.score = value.classification_score

            bb_index = BoundingBoxWithIndex()
            bb_index.bb.CopyFrom(bb)
            bb_index.index = key

            bbs_with_indexes.append(bb_index)

        response = ListOfBoundingBoxesWithIndexes()
        response.packet.extend(bbs_with_indexes)

        return response
