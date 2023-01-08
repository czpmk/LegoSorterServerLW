import argparse
from multiprocessing import Process
from typing import Optional

from lego_sorter_server.server import Server
import logging
import sys
import threading
import multiprocessing as mp

from lego_sorter_server.service.BrickCategoryConfig import BrickCategoryConfig
from lego_sorter_server.sorter.workers.WorkersContainer import AnalysisServiceMode, WorkerMode, WorkersContainer


def exception_handler(exc_type=None, value=None, tb=None):
    logging.exception(f"Uncaught exception: {str(value)}")


if __name__ == '__main__':
    mp.set_start_method('spawn', force=True)

    parser = argparse.ArgumentParser()
    parser.add_argument("--brick_category_config", "-c", help='.json file with brick-category mapping specification',
                        type=str, required=False)
    parser.add_argument("--save_brick_images_to_file", "-s", action="store_true",
                        help="save cropped images (bricks only) to file")
    parser.add_argument("--reset_state_on_stop", "-r", action="store_true",
                        help="remove current state on each Stop Sorting call from app")
    parser.add_argument("--skipp_sorted_bricks_classification", "-b", action="store_true",
                        help="skip classification of brick images that have already passed the camera line "
                             "(and are assumed to be in process of sorting or already sorted)")
    args = parser.parse_args()
    logging.getLogger().setLevel(logging.INFO)
    sys.excepthook = exception_handler
    threading.excepthook = exception_handler

    # ------------------ TOGGLES - for Async sorter only ------------------
    ANALYSIS_SERVICE_MODE = AnalysisServiceMode.RUN_ON_PROCESS

    DETECTION_WORKER_MODE = WorkerMode.Process
    CLASSIFICATION_WORKER_MODE = WorkerMode.Process
    # ---------------------------------------------------------------------

    # Workers initialization
    workers = WorkersContainer()
    workers.set_analysis_service_work_mode(ANALYSIS_SERVICE_MODE)
    # Set desired Thread/Process worker configuration (only Thread worker allowed for sorter_worker)
    workers.set_detection_worker(DETECTION_WORKER_MODE)
    workers.set_classification_worker(CLASSIFICATION_WORKER_MODE)
    workers.set_sorter_worker(WorkerMode.Thread)

    # LAUNCH PROCESSES
    detection_process: Optional[Process] = None
    classification_process: Optional[Process] = None

    if DETECTION_WORKER_MODE == WorkerMode.Process:
        detection_process = mp.Process(target=workers.detection.run,
                                       args=(
                                           workers.detection.input_queue,
                                           workers.detection.output_queue,
                                           workers.detection.analysis_service,
                                       ),
                                       name="DetectionProcess")
        detection_process.start()

    if CLASSIFICATION_WORKER_MODE == WorkerMode.Process:
        classification_process = mp.Process(target=workers.classification.run,
                                            args=(
                                                workers.classification.input_queue,
                                                workers.classification.output_queue,
                                                workers.classification.analysis_service,
                                            ),
                                            name="ClassificationProcess")
        classification_process.start()

    Server.run(BrickCategoryConfig(args.brick_category_config), args.save_brick_images_to_file,
               args.reset_state_on_stop, args.skipp_sorted_bricks_classification, workers)

    if CLASSIFICATION_WORKER_MODE == WorkerMode.Process and classification_process.is_alive():
        classification_process.terminate()

    if DETECTION_WORKER_MODE == WorkerMode.Process and detection_process.is_alive():
        detection_process.terminate()
