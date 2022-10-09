import logging
from threading import Thread
from queue import Queue
import time

from PIL.Image import Image

from lego_sorter_server.analysis.AnalysisService import AnalysisService
from lego_sorter_server.analysis.classification.ClassificationResults import ClassificationResult, \
    ClassificationResultsList
from lego_sorter_server.analysis.detection import DetectionUtils
from lego_sorter_server.analysis.detection.DetectionResults import DetectionResultsList
from lego_sorter_server.service.BrickCategoryConfig import BrickCategoryConfig
from lego_sorter_server.sorter.LegoSorterController import LegoSorterController


class SortingAsyncProcessor:
    def __init__(self, brick_category_config: BrickCategoryConfig):
        # TODO: read and set addresses and ports of controllers from BrickCategoryConfig

        self.analysis_service: AnalysisService = AnalysisService()
        self.sorter_controller: LegoSorterController = LegoSorterController(brick_category_config)

        self.__detection_queue: Queue[Image] = Queue()
        self.__classification_queue: Queue[Image] = Queue()
        self.__sorting_queue: Queue[ClassificationResult] = Queue()
        # TODO: parametrize the queue max size to determine if the next brick can be extracted to the conveyor belt
        self.__sorting_buffer: Queue[bool] = Queue(maxsize=1)

        self.__detection_thread: Thread = Thread(target=self.__detect)
        self.__classification_thread: Thread = Thread(target=self.__classify)
        self.__sorter_thread: Thread = Thread(target=self.__sort)

        self.__running = False

    def run(self):
        self.__detection_thread.run()
        self.__classification_thread.run()
        self.__sorter_thread.run()

        # TODO -1: load the current state
        while True:
            if self.__running is False:
                logging.info('[SortingAsyncProcessor] Stop.')
                break

            # check if:
            #   detection_queue.empty() -> image is being processed
            #   sorting_buffer.full() -> no place to leave any potential recognized brick
            if not self.__detection_queue.empty() or self.__sorting_buffer.full():
                time.sleep(0.1)
                continue

            # TODO: request an image
            img: Image = Image()
            self.__detection_queue.put(img)

            # TODO 2: add rest of the logic
            # TODO 3: optional features, such as saving images to storage shall be operated via threads target methods

        self.__detection_thread.join(timeout=5)
        self.__classification_thread.join(timeout=5)
        self.__sorter_thread.join(timeout=20)

    def __detect(self):
        while True:
            if self.__running is False:
                logging.info('[SortingAsyncProcessor] Detection thread stopped. Detection queue size: {0}'.format(
                    self.__detection_queue.qsize()))
                break

            try:
                image: Image = self.__detection_queue.get(block=True, timeout=0.5)
                detection_results: DetectionResultsList = self.analysis_service.detect(image)

                if len(detection_results) == 0:
                    logging.info('[SortingAsyncProcessor] no brick detected')
                else:
                    logging.info('[SortingAsyncProcessor] Brick detected. Pushing to classification queue.')

                    cropped_image = DetectionUtils.crop_with_margin_from_bb(image, detection_box=detection_results[0])
                    self.__classification_queue.put(cropped_image)

            except TimeoutError:
                pass

    def __classify(self):
        while True:
            if self.__running is False:
                logging.info('[SortingAsyncProcessor] Classification thread stopped. '
                             'Classification queue size: {0}'.format(self.__classification_queue.qsize()))
                break

            try:
                cropped_image: Image = self.__classification_queue.get(block=True, timeout=0.5)
                classification_results: ClassificationResultsList = self.analysis_service.classify([cropped_image])

                if len(classification_results) == 0:
                    logging.info('[SortingAsyncProcessor] no brick classified')
                else:
                    result: ClassificationResult = classification_results[0]
                    logging.info('[SortingAsyncProcessor] Brick classified (class={0}, score={1}). '
                                 'Pushing to sorting queue'.format(
                        result.r_class,
                        result.r_score)
                    )

                    self.__sorting_queue.put(result)

            except TimeoutError:
                pass

    def __sort(self):
        while True:
            if self.__running is False:
                logging.info('[SortingAsyncProcessor] Sorting thread stopped. Sorting queue size: {0}'.format(
                    self.__sorting_queue.qsize()))
                break

            try:
                classification_result: ClassificationResult = self.__sorting_queue.get(block=True, timeout=0.5)
                self.sorter_controller.on_brick_recognized(classification_result)

                # TODO: wait until the brick is sorted
                logging.info('[SortingAsyncProcessor] Brick sorted (class={0}, score={1}). '
                             'Pushing to sorting queue'.format(
                    classification_result.r_class,
                    classification_result.r_score)
                )
                # Once sorted allow another brick to the conveyor belt
                self.__sorting_buffer.get()

            except TimeoutError:
                pass

    def start(self):
        if self.__running:
            logging.warning('[SortingAsyncProcessor] "start" called yet the sorting was already started')
        else:
            self.__running = True
            self.run()

    def stop(self):
        # TODO: clear the queues???
        if not self.__running:
            logging.warning('[SortingAsyncProcessor] "stop" called yet the sorting have not been started')
        else:
            self.__running = False
