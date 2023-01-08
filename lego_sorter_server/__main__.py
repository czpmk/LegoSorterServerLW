import argparse

from lego_sorter_server.server import Server
import logging
import sys
import threading

from lego_sorter_server.service.BrickCategoryConfig import BrickCategoryConfig


def exception_handler(exc_type, value, tb):
    logging.exception(f"Uncaught exception: {str(value)}")


if __name__ == '__main__':
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
    Server.run(BrickCategoryConfig(args.brick_category_config), args.save_brick_images_to_file,
               args.reset_state_on_stop, args.skipp_sorted_bricks_classification)
