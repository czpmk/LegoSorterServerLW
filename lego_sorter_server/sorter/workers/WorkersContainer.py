from enum import Enum
from typing import Union, Optional

from lego_sorter_server.analysis.AnalysisService import AnalysisService
from lego_sorter_server.sorter.workers.multiprocess_worker.ClassificationProcessWorker import \
    ClassificationProcessWorker
from lego_sorter_server.sorter.workers.multiprocess_worker.DetectionProcessWorker import DetectionProcessWorker
from lego_sorter_server.sorter.workers.multithread_worker.ClassificationThreadWorker import ClassificationThreadWorker
from lego_sorter_server.sorter.workers.multithread_worker.DetectionThreadWorker import DetectionThreadWorker
from lego_sorter_server.sorter.workers.multithread_worker.SorterThreadWorker import SorterThreadWorker


class WorkerMode(Enum):
    Thread = 0
    Process = 1


class AnalysisServiceMode(Enum):
    SHARED = 0
    PER_WORKER = 1
    RUN_ON_PROCESS = 2


class WorkersContainer:
    def __init__(self):
        self.detection: Union[DetectionThreadWorker, DetectionProcessWorker, None] = None
        self.classification: Union[ClassificationThreadWorker, ClassificationProcessWorker, None] = None
        self.sorter: Union[SorterThreadWorker, None] = None

        self._analysis_service: Optional[AnalysisService] = None
        self._analysis_service_mode: AnalysisServiceMode = AnalysisServiceMode.SHARED

    def set_detection_worker(self, mode: WorkerMode):
        self.detection = {
            WorkerMode.Thread: DetectionThreadWorker(),
            WorkerMode.Process: DetectionProcessWorker()
        }.get(mode)

        self.detection.set_analysis_service(self._get_analysis_service(mode))

    def set_classification_worker(self, mode: WorkerMode):
        self.classification = {
            WorkerMode.Thread: ClassificationThreadWorker(),
            WorkerMode.Process: ClassificationProcessWorker()
        }.get(mode)

        self.classification.set_analysis_service(self._get_analysis_service(mode))

    def set_sorter_worker(self, mode: WorkerMode):
        self.sorter = {
            WorkerMode.Thread: SorterThreadWorker()
        }.get(mode)

    def set_analysis_service_work_mode(self, mode: AnalysisServiceMode):
        self._analysis_service_mode = mode
        if mode == AnalysisServiceMode.SHARED:
            self._analysis_service = AnalysisService()

    def _get_analysis_service(self, worker_mode: WorkerMode):
        if self._analysis_service_mode == AnalysisServiceMode.SHARED:
            return self._analysis_service

        elif self._analysis_service_mode == AnalysisServiceMode.PER_WORKER:
            return AnalysisService()

        else:
            if worker_mode == WorkerMode.Process:
                # has to be set on process method
                return None

            else:
                # provide as in PER_WORKER mode
                return AnalysisService()
