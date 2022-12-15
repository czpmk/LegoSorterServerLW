import logging
import os
import time

import tensorflow as tf
import numpy as np

from typing import List

from tensorflow import keras
from PIL.Image import Image

from lego_sorter_server.analysis.classification.classifiers.LegoClassifier import LegoClassifier
from lego_sorter_server.analysis.classification.toolkit.transformations.simple import Simple
from lego_sorter_server.common.ClassificationResults import ClassificationResultsList

gpus = tf.config.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)


class KerasClassifier(LegoClassifier):
    def __init__(self, model_path=os.path.join("lego_sorter_server", "analysis", "classification", "models",
                                               "keras_model", "447_classes.h5")):
        super().__init__()
        tf.get_logger().setLevel('DEBUG')
        tf.debugging.disable_traceback_filtering()
        self.model_path = model_path
        self.model = None
        self.initialized = False
        self.size = (224, 224)

    def load_model(self):
        self.model = keras.models.load_model(self.model_path)
        self.initialized = True

    def predict(self, images: List[Image]) -> ClassificationResultsList:
        if not self.initialized:
            self.load_model()

        if len(images) == 0:
            return ClassificationResultsList()

        images_array = []
        start_time = time.time()
        for img in images:
            transformed = Simple.transform(img, self.size[0])
            img_array = np.array(transformed)
            img_array = np.expand_dims(img_array, axis=0)
            images_array.append(img_array)
        processing_elapsed_time_ms = 1000 * (time.time() - start_time)

        vstack = np.vstack(images_array)

        predictions = self.model(vstack)

        predicting_elapsed_time_ms = 1000 * (time.time() - start_time) - processing_elapsed_time_ms

        logging.info("[KerasClassifier] Preparing images took {:.3f} ms, "
                     "when predicting took {:.3f} ms.".format(processing_elapsed_time_ms,
                                                              predicting_elapsed_time_ms))

        indices = [int(np.argmax(values)) for values in predictions]
        classes = [self.class_names[index] for index in indices]
        scores = [float(prediction[index]) for index, prediction in zip(indices, predictions)]

        return ClassificationResultsList.from_lists(classification_classes=classes, classification_scores=scores)
