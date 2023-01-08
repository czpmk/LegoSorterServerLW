import logging
import os
import sys
from datetime import datetime

from PIL.Image import Image

from lego_sorter_server.analysis.AnalysisService import AnalysisService
from lego_sorter_server.service.BrickCategoryConfig import BrickCategoryConfig
from lego_sorter_server.sorter.LegoSorterController import LegoSorterController
from lego_sorter_server.sorter.ordering.AsyncOrdering import AsyncOrdering
from lego_sorter_server.sorter.workers.ClassificationWorker import ClassificationWorker
from lego_sorter_server.sorter.workers.DetectionWorker import DetectionWorker
from lego_sorter_server.sorter.workers.SortingWorker import SortingWorker


class AsyncSortingProcessor:
    def __init__(self, brick_category_config: BrickCategoryConfig, save_images_to_file: bool, reset_state_on_stop: bool,
                 skip_sorted_bricks_classification: bool):
        self._running: bool = False
        self.reset_state_on_stop: bool = reset_state_on_stop

        self.analysis_service: AnalysisService = AnalysisService()
        self.sorter_controller: LegoSorterController = LegoSorterController(brick_category_config)
        self.ordering: AsyncOrdering = AsyncOrdering(save_images_to_file, skip_sorted_bricks_classification)

        self.detection_worker: DetectionWorker = DetectionWorker(self.analysis_service)
        self.classification_worker: ClassificationWorker = ClassificationWorker(self.analysis_service)
        self.sorting_worker: SortingWorker = SortingWorker(self.sorter_controller)

        self.ordering.add_workers(self.detection_worker, self.classification_worker, self.sorting_worker)

    def enqueue_image(self, image: Image):
        logging.info('[AsyncSortingProcessor] New Image received from CameraController')
        image_idx: int = self.ordering.add_image(image)
        self.detection_worker.enqueue((image_idx, image))

    def start_machine(self):
        self.sorter_controller.run_conveyor()

    def stop_machine(self):
        self.sorter_controller.stop_conveyor()

    def start_sorting(self):
        if self._running:
            logging.warning('[AsyncSortingProcessor] start_sorting called yet the Sorter was already started')
            return

        logging.info('[AsyncSortingProcessor] Sorting processor START.')
        self._running = True
        self.detection_worker.start()
        self.classification_worker.start()
        self.sorting_worker.start()

    def stop_sorting(self):
        logging.info('[AsyncSortingProcessor] Stopping Sorting processor...')
        if not self._running:
            logging.warning('[AsyncSortingProcessor] stop_sorting called yet the Sorter was not started')
            return

        self._running = False
        self.detection_worker.stop()
        self.classification_worker.stop()
        self.sorting_worker.stop()

        self.ordering.export_history_to_csv(
            os.path.join(os.getcwd(), 'AsyncExports',
                         'export_ASYNC_{0}.csv'.format(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))))

        logging.info('[AsyncSortingProcessor] AsyncOrdering object size: {0} [MB]'.format(
            float(sys.getsizeof(self.ordering)) * 1000000))
        if self.reset_state_on_stop:
            self.ordering.reset()

        logging.info('[AsyncSortingProcessor] AsyncOrdering object size: {0} [MB]'.format(
            float(sys.getsizeof(self.ordering)) * 1000000))

        logging.info('[AsyncSortingProcessor] Sorting processor STOP.')

    def set_machine_speed(self, speed: int):
        logging.debug('[AsyncSortingProcessor] Setting conveyor belt speed to: {0}'.format(speed))
        self.sorter_controller.set_machine_speed(speed)
