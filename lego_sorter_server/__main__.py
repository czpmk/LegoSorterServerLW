import argparse

from lego_sorter_server.server import Server
import logging
import sys
import threading
import multiprocessing as mp

from lego_sorter_server.service.BrickCategoryConfig import BrickCategoryConfig
from lego_sorter_server.sorter.workers.ClassificationProcessAttributes import ClassificationProcessAttributes


def exception_handler(exc_type, value, tb):
    logging.exception(f"Uncaught exception: {str(value)}")


if __name__ == '__main__':
    mp.set_start_method('spawn', force=True)

    process_attributes = ClassificationProcessAttributes()
    classification_process = mp.Process(target=ClassificationProcessAttributes.run,
                                        args=(process_attributes.input_queue,
                                              process_attributes.output_queue,
                                              ),
                                        name='ClassificationProcess')
    classification_process.start()

    parser = argparse.ArgumentParser()
    parser.add_argument("--brick_category_config", "-c", help='.json file with brick-category mapping specification',
                        type=str, required=False)
    args = parser.parse_args()
    logging.getLogger().setLevel(logging.INFO)
    sys.excepthook = exception_handler
    threading.excepthook = exception_handler
    Server.run(BrickCategoryConfig(args.brick_category_config), process_attributes)

    if classification_process.is_alive():
        classification_process.terminate()
