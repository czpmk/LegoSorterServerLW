import logging
import time
from queue import Queue, Empty
from threading import Thread
from typing import Tuple

from PIL.Image import Image

from lego_sorter_server.analysis.AnalysisService import AnalysisService
from lego_sorter_server.analysis.detection import DetectionUtils
from lego_sorter_server.common.AnalysisResults import AnalysisResult
from lego_sorter_server.common.ClassificationResults import ClassificationResult, ClassificationResultsList
from lego_sorter_server.common.DetectionResults import DetectionResultsList, DetectionResult
from lego_sorter_server.service.BrickCategoryConfig import BrickCategoryConfig
from lego_sorter_server.sorter.CameraController import CameraController
from lego_sorter_server.sorter.ConveyorManager import ConveyorManager


class AsyncSortingProcessor:
    def __init__(self, brick_category_config: BrickCategoryConfig):
        self.__is_active = False

        self.conveyor_manager: ConveyorManager = ConveyorManager(brick_category_config)
        self.analysis_service: AnalysisService = AnalysisService()
        self.camera_controller: CameraController = CameraController()

        self.__detection_queue: Queue[Image] = Queue()
        self.__classification_queue: Queue[Tuple[Image, DetectionResult]] = Queue()
        self.__sorting_queue: Queue[Tuple[Image, AnalysisResult]] = Queue()

        self.__detection_thread: Thread = Thread(target=self.__detect)
        self.__classification_thread: Thread = Thread(target=self.__classify)
        self.__sorter_thread: Thread = Thread(target=self.__sort)
        self.__sorting_processor_thread: Thread = Thread(target=self.__run)

    def start_sorting(self):
        logging.info('[AsyncSortingProcessor] Sorting processor START.')
        if self.__is_active:
            logging.warning('[AsyncSortingProcessor] start_sorting called yet the Sorter was already started')
            return

        self.__is_active = True
        self._start_threads()

    def stop_sorting(self):
        logging.info('[AsyncSortingProcessor] Stopping Sorting processor...')
        if not self.__is_active:
            logging.warning('[AsyncSortingProcessor] stop_sorting called yet the Sorter was not started')
            return

        self.__is_active = False
        self._stop_threads()
        logging.info('[AsyncSortingProcessor] Sorting processor STOP.')

    def set_machine_speed(self, speed: int):
        logging.debug('[AsyncSortingProcessor] Setting conveyor belt speed to: {0}'.format(speed))
        self.conveyor_manager.set_machine_speed(speed)

    def set_camera_ip(self, ip: str):
        logging.debug('[AsyncSortingProcessor] Setting camera IP to: {0}'.format(ip))
        self.camera_controller.setIP(ip)

    def enqueue_image(self, image: Image):
        logging.debug('[AsyncSortingProcessor] New Image received from CameraController')
        self.__detection_queue.put(image)

    def __run(self):
        logging.info('[AsyncSortingProcessor] Sorting Processor thread started.')

        # TODO -1: load the current state
        while True:
            time.sleep(1)
            if self.__is_active is False:
                logging.info('[AsyncSortingProcessor] Sorting Processor thread stopped.')
                return

            self.camera_controller.send_image_order()

    def __detect(self):
        while True:
            if self.__is_active is False:
                logging.info('[AsyncSortingProcessor] Detection thread stopped. Detection queue size: {0}'.format(
                    self.__detection_queue.qsize()))
                return

            try:
                image: Image = self.__detection_queue.get(timeout=0.5)
                detection_results_list: DetectionResultsList = self.analysis_service.detect(image)

                if len(detection_results_list) == 0:
                    logging.info('[AsyncSortingProcessor] no brick detected')
                else:
                    detection_results_list.sort(key=lambda x: x.detection_box.y_min, reverse=True)

                    # TODO: Determine how many bricks to classify on each state.
                    #  Currently only the first brick is going to be classified
                    classification_limit_per_image = 1
                    if len(detection_results_list) > classification_limit_per_image:
                        selected_detection_results = detection_results_list[:classification_limit_per_image]
                    else:
                        selected_detection_results = detection_results_list

                    logging.info(
                        '[AsyncSortingProcessor] Bricks detected {0}. Pushing {1} to classification queue.'.format(
                            len(detection_results_list), len(selected_detection_results)
                        ))

                    for detection_result in selected_detection_results:
                        cropped_image = \
                            DetectionUtils.crop_with_margin_from_detection_box(image, detection_result.detection_box)
                        self.__classification_queue.put((cropped_image, detection_result))

            except Empty:
                pass

    def __classify(self):
        while True:
            if self.__is_active is False:
                logging.info(
                    '[AsyncSortingProcessor] Classification thread stopped. Classification queue size: {0}'.format(
                        self.__classification_queue.qsize()))
                return

            try:
                cropped_image, detection_result = self.__classification_queue.get(timeout=0.5)
                classification_results_list: ClassificationResultsList = self.analysis_service.classify([cropped_image])

                # TODO: establish an action in case of lack of classification,
                #  otherwise it is going to loop the sorting processor if there is no classification result
                #  (take another picture?, retry X times)
                if len(classification_results_list) != 1:
                    logging.error(
                        '[AsyncSortingProcessor] Invalid number of classification results: {0}, 1 expected'.format(
                            len(classification_results_list)))
                else:
                    classification_result: ClassificationResult = classification_results_list[0]
                    logging.info('[AsyncSortingProcessor] Brick classified (class={:}, score={:.2f}). '
                                 'Pushing to sorting queue'.format(
                        classification_result.classification_class,
                        classification_result.classification_score)
                    )
                    analysis_result = AnalysisResult.results_merged(classification_result=classification_result,
                                                                    detection_result=detection_result)
                    self.__sorting_queue.put((cropped_image, analysis_result))

            except Empty:
                pass

    def __sort(self):
        while True:
            if self.__is_active is False:
                logging.info(
                    '[AsyncSortingProcessor] Sorting thread stopped. Sorting queue size: {0}'.format(
                        self.__sorting_queue.qsize()))
                return

            try:
                image, analysis_result = self.__sorting_queue.get(timeout=0.5)
                # TODO: save the original image height
                original_image_height = 640

                # move the conveyor belt to push the brick out of it
                self.conveyor_manager.move_by(analysis_result.detection_box.y_max, original_image_height)
                # sort the brick
                self.conveyor_manager.place_in_a_bucket(analysis_result)

                # TODO: wait until the brick is sorted
                logging.info('[AsyncSortingProcessor] Brick sorted (class={:}, score={:.2f}). '.format(
                    analysis_result.classification_class,
                    analysis_result.classification_score)
                )

            except Empty:
                pass

    def _stop_threads(self):
        if self.__detection_thread.is_alive():
            self.__detection_thread.join(timeout=1)
        if self.__classification_thread.is_alive():
            self.__classification_thread.join(timeout=1)
        if self.__sorter_thread.is_alive():
            self.__sorter_thread.join(timeout=1)
        if self.__sorting_processor_thread.is_alive():
            self.__sorting_processor_thread.join(timeout=1)

    def _start_threads(self):
        self.__detection_thread: Thread = Thread(target=self.__detect)
        self.__classification_thread: Thread = Thread(target=self.__classify)
        self.__sorter_thread: Thread = Thread(target=self.__sort)
        self.__sorting_processor_thread: Thread = Thread(target=self.__run)

        self.__detection_thread.start()
        self.__classification_thread.start()
        self.__sorter_thread.start()
        self.__sorting_processor_thread.start()

    def reset(self):
        self.stop_sorting()
        logging.info('[AsyncSortingProcessor] Clearing detection, classification and sorting queues...')
        with self.__detection_queue.mutex:
            self.__detection_queue.queue.clear()

        with self.__classification_queue.mutex:
            self.__classification_queue.queue.clear()

        with self.__sorting_queue.mutex:
            self.__sorting_queue.queue.clear()

        self.start_sorting()
