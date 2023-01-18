import argparse
import os

from lego_sorter_server.server import Server
import logging
import sys
import threading
import multiprocessing as mp

from lego_sorter_server.service.BrickCategoryConfig import BrickCategoryConfig
from lego_sorter_server.sorter.workers.Worker import WorkerMode
from lego_sorter_server.sorter.workers.WorkersContainer import WorkersContainer
from lego_sorter_server.tester.SorterTester import SorterTester
from lego_sorter_server.tester.TesterConfig import TesterConfig, Operation


def exception_handler(exc_type=None, value=None, tb=None):
    logging.exception(f"Uncaught exception: {str(value)}")


def int_in_range_0_100(arg):
    try:
        int_val = int(arg)
        if int_val not in range(0, 100):
            raise argparse.ArgumentTypeError(
                "Invalid argument value. Must be in range 0 (inclusive) to 100 (exclusive).")
        else:
            return int_val

    except ValueError:
        raise argparse.ArgumentTypeError("Invalid argument type. Int required.")


if __name__ == '__main__':
    mp.set_start_method('spawn', force=True)

    parser = argparse.ArgumentParser()
    parser.add_argument("--brick_category_config", "-c", help='.json file with brick-category mapping specification',
                        type=str, required=False)
    parser.add_argument("--save_brick_images_to_file", "-f", action="store_true",
                        help="save cropped images (bricks only) to file")
    parser.add_argument("--reset_state_on_stop", "-r", action="store_true",
                        help="remove current state on each Stop Sorting call from app")
    parser.add_argument("--skipp_sorted_bricks_classification", "-s", action="store_true",
                        help="skip classification of brick images that have already passed the camera line "
                             "(and are assumed to be in process of sorting or already sorted). "
                             "(Asynchronous Sorter only!)")
    parser.add_argument("--queue_size_limit", '-l', type=int_in_range_0_100, required=False, default=0,
                        help="Limit the number of items in detection and classification queues "
                             "(Asynchronous Sorter only!). Discards all new items while max queue items are achieved. "
                             "Accepted range = [0, 100], where 0 means limit disabled. Default = 0 (disabled).")

    parser.add_argument("--detection_worker", type=str, required=False, default="Thread", choices=["Thread", "Process"],
                        help="Selected DETECTION worker mode (Asynchronous Sorter only!). Default = 'Thread'.")
    parser.add_argument("--classification_worker", type=str, required=False, default="Thread",
                        choices=["Thread", "Process"],
                        help="Selected CLASSIFICATION worker mode (Asynchronous Sorter only!). Default = 'Thread'.")

    parser.add_argument("--test_mode", action="store_true", help="set, in order to run sorter in test mode.")
    parser.add_argument("--test_operation", "-o", type=str, default="AsyncSorter",
                        choices=["AsyncSorter", "SyncSorter"], required=False,
                        help="select an operation to be tested. Default = 'AsyncSorter'")
    parser.add_argument("--test_time", "-t", type=int, default=60, required=False,
                        help="test time [seconds]. Discarded if 'test_mode' is not enabled. Default = 60s.")
    parser.add_argument("--capture_delay", "-d", type=int, default=500, required=False,
                        help="capture delay [milliseconds]. Discarded if 'test_mode' is not enabled. Default = 500ms.")

    args = parser.parse_args()
    logging.getLogger().setLevel(logging.INFO)
    sys.excepthook = exception_handler
    threading.excepthook = exception_handler

    # Spawning threads in __main__ for compatibility with Windows OS
    workers = WorkersContainer()
    workers.set_configuration(detection_mode=WorkerMode.from_string(args.detection_worker),
                              classification_mode=WorkerMode.from_string(args.classification_worker),
                              sorter_mode=WorkerMode.Thread,
                              max_queue_size=args.queue_size_limit)

    try:
        if args.test_mode:
            t_config = TesterConfig(Operation.from_string(args.test_operation), args.test_time, args.capture_delay,
                                    os.path.abspath('tester_images'))

            SorterTester.run(BrickCategoryConfig(args.brick_category_config), args.save_brick_images_to_file,
                             args.reset_state_on_stop, args.skipp_sorted_bricks_classification, workers, t_config)

        else:
            Server.run(BrickCategoryConfig(args.brick_category_config), args.save_brick_images_to_file,
                       args.reset_state_on_stop, args.skipp_sorted_bricks_classification, workers)

        del workers

    except Exception:
        exception_handler(*sys.exc_info())
        workers.end_processes()
        del workers
