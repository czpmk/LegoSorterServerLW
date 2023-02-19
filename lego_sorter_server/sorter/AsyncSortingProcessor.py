import logging
import os
from datetime import datetime
from typing import Optional

from PIL.Image import Image

from lego_sorter_server.analysis.AnalysisService import AnalysisService
from lego_sorter_server.service.BrickCategoryConfig import BrickCategoryConfig
from lego_sorter_server.sorter.LegoSorterController import LegoSorterController
from lego_sorter_server.sorter.ordering.AsyncOrdering import AsyncOrdering
from lego_sorter_server.sorter.workers.Worker import WorkerMode
from lego_sorter_server.sorter.workers.WorkersContainer import WorkersContainer


class AsyncSortingProcessor:
    def __init__(self, brick_category_config: BrickCategoryConfig, save_images_to_file: bool, reset_state_on_stop: bool,
                 workers: WorkersContainer):
        self._running = False
        self.reset_state_on_stop: bool = reset_state_on_stop

        self.workers: WorkersContainer = workers

        self.analysis_service: Optional[AnalysisService] = None
        self.sorter_controller: LegoSorterController = LegoSorterController(brick_category_config)

        self._set_analysis_service()
        self.workers.sorter.set_sorter_controller(self.sorter_controller)

        self.ordering: AsyncOrdering = AsyncOrdering(save_images_to_file, self.workers)

    def enqueue_image(self, image: Image):
        logging.debug('[AsyncSortingProcessor] New Image received from CameraController')
        image_idx: int = self.ordering.add_image(image)
        self.workers.detection.enqueue((image_idx, image))

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
        self.workers.start_all()

    def stop_sorting(self):
        logging.info('[AsyncSortingProcessor] Stopping Sorting processor...')
        if not self._running:
            logging.warning('[AsyncSortingProcessor] stop_sorting called yet the Sorter was not started')
            return

        self._running = False
        self.workers.stop_all()

        self.ordering.export_history_to_csv(
            os.path.join(os.getcwd(), 'AsyncExports',
                         'export_ASYNC_{0}.csv'.format(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))))

        if self.reset_state_on_stop:
            self.ordering.reset()

        logging.info('[AsyncSortingProcessor] Sorting processor STOP.')

    def set_machine_speed(self, speed: int):
        logging.debug('[AsyncSortingProcessor] Setting conveyor belt speed to: {0}'.format(speed))
        self.sorter_controller.set_machine_speed(speed)

    def _set_analysis_service(self):
        if self.workers.detection.mode == WorkerMode.Thread or self.workers.classification.mode == WorkerMode.Thread:
            self.analysis_service = AnalysisService()
        else:
            return

        if self.workers.detection.mode == WorkerMode.Thread:
            self.workers.detection.set_analysis_service(self.analysis_service)

        if self.workers.classification.mode == WorkerMode.Thread:
            self.workers.classification.set_analysis_service(self.analysis_service)
