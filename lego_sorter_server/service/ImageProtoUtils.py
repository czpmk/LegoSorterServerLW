from io import BytesIO
from typing import List, Tuple

from PIL import Image

from lego_sorter_server.analysis.classification.ClassificationResults import ClassificationResults
from lego_sorter_server.analysis.detection import DetectionUtils
from lego_sorter_server.analysis.detection.DetectionResults import DetectionBox, DetectionResultsList
from lego_sorter_server.generated.Messages_pb2 import ImageRequest, BoundingBox, ListOfBoundingBoxes


class ImageProtoUtils:
    DEFAULT_LABEL = "Lego"

    @staticmethod
    def prepare_image(request: ImageRequest) -> Image.Image:
        image = Image.open(BytesIO(request.image))
        image = image.convert('RGB')

        if request.rotation == 90:
            image = image.transpose(Image.ROTATE_270)
        elif request.rotation == 180:
            image = image.rotate(180)
        elif request.rotation == 270:
            image = image.transpose(Image.ROTATE_90)

        return image

    @staticmethod
    def crop_bounding_boxes(image: Image.Image, bbs: List[BoundingBox]) -> List[Tuple[BoundingBox, Image.Image]]:
        bbs_with_blobs = [
            (bb, DetectionUtils.crop_with_margin(image, DetectionBox.from_bounding_box(bb))) for bb in bbs
        ]

        return bbs_with_blobs

    @staticmethod
    def prepare_response_from_analysis_results(detection_results: DetectionResultsList,
                                               classification_results: ClassificationResults) -> ListOfBoundingBoxes:
        bounding_boxes = []
        for idx in range(len(detection_results)):
            if detection_results[idx].d_score < 0.5:
                continue

            bb = detection_results[idx].to_bounding_box()
            bb.score = classification_results.classification_scores[idx]
            bb.label = classification_results.classification_classes[idx]

            bounding_boxes.append(bb)

        bb_list = ListOfBoundingBoxes()
        bb_list.packet.extend(bounding_boxes)

        return bb_list

    @staticmethod
    def prepare_bbs_response_from_detection_results(detection_results: DetectionResultsList) -> ListOfBoundingBoxes:
        bounding_boxes = []
        for idx in range(len(detection_results)):
            if detection_results[idx].detection_scores < 0.5:
                continue

            bb = detection_results[idx].to_bounding_box()
            bb.label = ImageProtoUtils.DEFAULT_LABEL

            bounding_boxes.append(bb)

        bb_list = ListOfBoundingBoxes()
        bb_list.packet.extend(bounding_boxes)

        return bb_list
