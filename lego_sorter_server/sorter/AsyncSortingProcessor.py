import logging
import os
import sys
from datetime import datetime
from typing import Union

from PIL.Image import Image

from lego_sorter_server.service.BrickCategoryConfig import BrickCategoryConfig
from lego_sorter_server.sorter.LegoSorterController import LegoSorterController
from lego_sorter_server.sorter.ordering.AsyncOrdering import AsyncOrdering
from lego_sorter_server.sorter.workers.WorkersContainer import WorkersContainer
from lego_sorter_server.sorter.workers.multiprocess_worker.ClassificationProcessWorker import \
    ClassificationProcessWorker
from lego_sorter_server.sorter.workers.multiprocess_worker.DetectionProcessWorker import DetectionProcessWorker
from lego_sorter_server.sorter.workers.multithread_worker.ClassificationThreadWorker import ClassificationThreadWorker
from lego_sorter_server.sorter.workers.multithread_worker.DetectionThreadWorker import DetectionThreadWorker
from lego_sorter_server.sorter.workers.multithread_worker.SorterThreadWorker import SorterThreadWorker


class AsyncSortingProcessor:
    def __init__(self, brick_category_config: BrickCategoryConfig, save_images_to_file: bool, reset_state_on_stop: bool,
                 skip_sorted_bricks_classification: bool, workers: WorkersContainer):
        self._running = False
        self.reset_state_on_stop: bool = reset_state_on_stop

        self.detection_worker: Union[DetectionThreadWorker, DetectionProcessWorker] = workers.detection
        self.classification_worker: Union[
            ClassificationThreadWorker, ClassificationProcessWorker] = workers.classification

        self.sorting_worker: SorterThreadWorker = workers.sorter

        self.sorter_controller: LegoSorterController = LegoSorterController(brick_category_config)
        self.sorting_worker.set_sorter_controller(self.sorter_controller)

        self.ordering: AsyncOrdering = AsyncOrdering(save_images_to_file, skip_sorted_bricks_classification,
                                                     self.detection_worker, self.classification_worker,
                                                     self.sorting_worker)

    def enqueue_image(self, image: Image):
        logging.debug('[AsyncSortingProcessor] New Image received from CameraController')
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
