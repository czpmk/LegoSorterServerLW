import logging

from PIL.Image import Image

from lego_sorter_server.analysis.AnalysisService import AnalysisService
from lego_sorter_server.service.BrickCategoryConfig import BrickCategoryConfig
from lego_sorter_server.sorter.LegoSorterController import LegoSorterController
from lego_sorter_server.sorter.ordering.AsyncOrdering import AsyncOrdering
from lego_sorter_server.sorter.workers.ClassificationWorker import ClassificationWorker
from lego_sorter_server.sorter.workers.DetectionWorker import DetectionWorker
from lego_sorter_server.sorter.workers.SortingWorker import SortingWorker


class AsyncSortingProcessor:
    def __init__(self, brick_category_config: BrickCategoryConfig):
        self._running = False

        self.analysis_service: AnalysisService = AnalysisService()
        self.sorter_controller: LegoSorterController = LegoSorterController(brick_category_config)
        self.ordering: AsyncOrdering = AsyncOrdering()

        self.detection_worker: DetectionWorker = DetectionWorker(self.analysis_service, self.ordering.on_detection)
        self.classification_worker: ClassificationWorker = ClassificationWorker(self.analysis_service,
                                                                                self.ordering.on_classification)
        self.sorting_worker: SortingWorker = SortingWorker(self.sorter_controller, self.ordering.on_sort)

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
        logging.info('[AsyncSortingProcessor] Sorting processor STOP.')

    def set_machine_speed(self, speed: int):
        logging.debug('[AsyncSortingProcessor] Setting conveyor belt speed to: {0}'.format(speed))
        self.sorter_controller.set_machine_speed(speed)

    def enqueue_image(self, image: Image):
        logging.debug('[AsyncSortingProcessor] New Image received from CameraController')
        image_idx = self.ordering.register_picture()
        self.detection_worker.enqueue((image_idx, image))

    # def __sort(self):
    #     while True:
    #         if self.__is_active is False:
    #             logging.info(
    #                 '[AsyncSortingProcessor] Sorting thread stopped. Sorting queue size: {0}'.format(
    #                     self.__sorting_queue.qsize()))
    #             return
    #
    #         try:
    #             image, analysis_result = self.__sorting_queue.get(timeout=0.5)
    #             # TODO: save the original image height
    #             original_image_height = 640
    #
    #             # move the conveyor belt to push the brick out of it
    #             self.conveyor_manager.move_by(analysis_result.detection_box.y_max, original_image_height)
    #             # sort the brick
    #             self.conveyor_manager.place_in_a_bucket(analysis_result)
    #
    #             # TODO: wait until the brick is sorted
    #             logging.info('[AsyncSortingProcessor] Brick sorted (class={:}, score={:.2f}). '.format(
    #                 analysis_result.classification_class,
    #                 analysis_result.classification_score)
    #             )
    #
    #         except Empty:
    #             pass
