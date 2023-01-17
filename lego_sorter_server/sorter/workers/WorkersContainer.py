from typing import Union

from lego_sorter_server.sorter.workers.Worker import WorkerMode
from lego_sorter_server.sorter.workers.multiprocess_worker.ClassificationProcessWorker import \
    ClassificationProcessWorker
from lego_sorter_server.sorter.workers.multiprocess_worker.DetectionProcessWorker import DetectionProcessWorker
from lego_sorter_server.sorter.workers.multithread_worker.ClassificationThreadWorker import ClassificationThreadWorker
from lego_sorter_server.sorter.workers.multithread_worker.DetectionThreadWorker import DetectionThreadWorker
from lego_sorter_server.sorter.workers.multithread_worker.SorterThreadWorker import SorterThreadWorker


class WorkersContainer:
    def __init__(self):
        self.detection: Union[DetectionThreadWorker, DetectionProcessWorker, None] = None
        self.classification: Union[ClassificationThreadWorker, ClassificationProcessWorker, None] = None
        self.sorter: Union[SorterThreadWorker, None] = None

    def _set_detection_worker(self, mode: WorkerMode):
        if mode == WorkerMode.Thread:
            self.detection = DetectionThreadWorker()

        elif mode == WorkerMode.Process:
            self.detection = DetectionProcessWorker()

        else:
            raise Exception('Invalid WorkerMode: {0}'.format(mode))

    def _set_classification_worker(self, mode: WorkerMode):
        if mode == WorkerMode.Thread:
            self.classification = ClassificationThreadWorker()

        elif mode == WorkerMode.Process:
            self.classification = ClassificationProcessWorker()

        else:
            raise Exception('Invalid WorkerMode: {0}'.format(mode))

    def _set_sorter_worker(self, mode: WorkerMode):
        if mode == WorkerMode.Thread:
            self.sorter = SorterThreadWorker()

        elif mode == WorkerMode.Process:
            raise Exception('WorkerMode "{0}" not allowed for Sorter Worker.'.format(mode))

        else:
            raise Exception('Invalid WorkerMode: {0}'.format(mode))

    def set_configuration(self, detection_mode: WorkerMode, classification_mode: WorkerMode,
                          sorter_mode: WorkerMode):
        self._set_detection_worker(detection_mode)
        self._set_classification_worker(classification_mode)
        self._set_sorter_worker(sorter_mode)

    def end_processes(self):
        if self.classification.mode == WorkerMode.Process:
            self.classification.end_process()

        if self.detection.mode == WorkerMode.Process:
            self.detection.end_process()

    def start_all(self):
        self.detection.start()
        self.classification.start()
        self.sorter.start()

    def stop_all(self):
        self.detection.stop()
        self.classification.stop()
        self.sorter.stop()
