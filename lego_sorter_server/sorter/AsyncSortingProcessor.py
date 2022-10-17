import logging
from queue import Queue
from threading import Thread
from typing import Tuple

from PIL.Image import Image

from lego_sorter_server.analysis.AnalysisService import AnalysisService
from lego_sorter_server.analysis.detection import DetectionUtils
from lego_sorter_server.common.AnalysisResults import AnalysisResult
from lego_sorter_server.common.ClassificationResults import ClassificationResult, ClassificationResultsList
from lego_sorter_server.common.DetectionResults import DetectionResultsList, DetectionResult
from lego_sorter_server.common.Singleton import Singleton
from lego_sorter_server.service.BrickCategoryConfig import BrickCategoryConfig
from lego_sorter_server.sorter.LegoSorterController import LegoSorterController


class AsyncSortingProcessor(metaclass=Singleton):
    def __init__(self, brick_category_config: BrickCategoryConfig):
        self.sorter_controller: LegoSorterController = LegoSorterController(brick_category_config)
        self.analysis_service: AnalysisService = AnalysisService()

        self.__detection_queue: Queue[Image] = Queue()
        self.__classification_queue: Queue[Tuple[Image, DetectionResult]] = Queue()
        self.__sorting_queue: Queue[Tuple[Image, AnalysisResult]] = Queue()

        self.__detection_thread: Thread = Thread(target=self.__detect)
        self.__classification_thread: Thread = Thread(target=self.__classify)
        self.__sorter_thread: Thread = Thread(target=self.__sort)

        self.__sorting_processor_thread: Thread = Thread(target=self.__run())

        self.__running = False

    def start_sorting(self):
        logging.info('[AsyncSortingProcessor] Sorting processor START.')
        self.__running = True
        self.__sorting_processor_thread.run()

    def stop_sorting(self):
        logging.info('[AsyncSortingProcessor] Stopping Sorting processor...')
        self.__running = False
        self.__sorting_processor_thread.join(timeout=20)
        logging.info('[AsyncSortingProcessor] Sorting processor STOP.')

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

    def set_machine_speed(self, speed: int):
        self.sorter_controller.set_machine_speed(speed)

    def set_camera_ip(self, ip: str):
        # TODO: set ip when camera controller is implemented
        pass

    def __run(self):
        pass
        self.__detection_thread.run()
        self.__classification_thread.run()
        self.__sorter_thread.run()

        # TODO -1: load the current state
        while True:
            if self.__running is False:
                logging.info('[SortingAsyncProcessor] Sorting Processor thread stopped.')
                break

            # check if:
            #   detection_queue.empty() -> image is being processed
            #   sorting_buffer.full() -> no place to leave any potential recognized brick
            # if not self.__detection_queue.empty() or self.__sorting_buffer.full():
            #     continue

            # TODO: request an image
            img: Image = Image()
            self.__detection_queue.put(img)

            # TODO 2: add rest of the logic
            # TODO 3: optional features, such as saving images to storage shall be operated via threads target methods

        self.__detection_thread.join(timeout=5)
        self.__classification_thread.join(timeout=5)
        self.__sorter_thread.join(timeout=10)

    def __detect(self):
        while True:
            if self.__running is False:
                logging.info('[AsyncSortingProcessor] Detection thread stopped. Detection queue size: {0}'.format(
                    self.__detection_queue.qsize()))
                break

            try:
                image: Image = self.__detection_queue.get(block=True, timeout=0.5)
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

                    logging.info('[AsyncSortingProcessor] Bricks detected {0}. Pushing {1} to classification queue.')

                    for detection_result in selected_detection_results:
                        cropped_image = \
                            DetectionUtils.crop_with_margin_from_detection_box(image, detection_result.detection_box)
                        self.__classification_queue.put((cropped_image, detection_result))

            except TimeoutError:
                pass

    def __classify(self):
        while True:
            if self.__running is False:
                logging.info('[AsyncSortingProcessor] Classification thread stopped. '
                             'Classification queue size: {0}'.format(self.__classification_queue.qsize()))
                break

            try:
                cropped_image, detection_result = self.__classification_queue.get(block=True, timeout=0.5)
                classification_results_list: ClassificationResultsList = self.analysis_service.classify([cropped_image])

                # TODO: determine an action in case of lack of classification,
                #  otherwise it is going to loop the sorting processor if there is no classification result
                #  (take another picture?, retry X times)
                if len(classification_results_list) != 1:
                    logging.error(
                        '[AsyncSortingProcessor] Invalid number of classification results: {0}, 1 expected'.format(
                            len(classification_results_list)))
                else:
                    classification_result: ClassificationResult = classification_results_list[0]
                    logging.info('[AsyncSortingProcessor] Brick classified (class={0}, score={1}). '
                                 'Pushing to sorting queue'.format(
                        classification_result.classification_class,
                        classification_result.classification_score)
                    )
                    analysis_result = AnalysisResult.results_merged(classification_result=classification_result,
                                                                    detection_result=detection_result)
                    self.__sorting_queue.put((cropped_image, analysis_result))

            except TimeoutError:
                pass

    def __sort(self):
        while True:
            if self.__running is False:
                logging.info('[AsyncSortingProcessor] Sorting thread stopped. Sorting queue size: {0}'.format(
                    self.__sorting_queue.qsize()))
                break

            try:
                image, analysis_result = self.__sorting_queue.get(block=True, timeout=0.5)
                self.sorter_controller.on_brick_recognized(analysis_result)

                # TODO: wait until the brick is sorted
                logging.info('[AsyncSortingProcessor] Brick sorted (class={0}, score={1}). '
                             'Pushing to sorting queue'.format(
                    analysis_result.classification_class,
                    analysis_result.classification_score)
                )

            except TimeoutError:
                pass
