from io import BytesIO
from typing import List, Tuple

from PIL import Image

from lego_sorter_server.analysis.detection import DetectionUtils
from lego_sorter_server.common.ClassificationResults import ClassificationResultsList
from lego_sorter_server.common.DetectionResults import DetectionBox, DetectionResultsList
from lego_sorter_server.generated.Messages_pb2 import ImageRequest, BoundingBox, ListOfBoundingBoxes


class ImageProtoUtils:
    DEFAULT_LABEL = "Lego"

    @staticmethod
    def prepare_image_from_request(request: ImageRequest) -> Image.Image:
        image = Image.open(BytesIO(request.image))
        image = image.convert('RGB')

        return ImageProtoUtils.prepare_image(image, request.rotation)

    @staticmethod
    def prepare_image(src_image: Image, rotation: int) -> Image.Image:
        image = src_image

        if rotation == 90:
            image = image.transpose(Image.ROTATE_270)
        elif rotation == 180:
            image = image.rotate(180)
        elif rotation == 270:
            image = image.transpose(Image.ROTATE_90)

        return image

    # TODO: Refactor or remove - never used
    @staticmethod
    def crop_bounding_boxes(image: Image.Image, bbs: List[BoundingBox]) -> List[Tuple[BoundingBox, Image.Image]]:
        bbs_with_blobs = []

        for bb in bbs:
            cropped_brick = DetectionUtils.crop_with_margin(image, DetectionBox.from_bounding_box(bb))
            bbs_with_blobs.append((bb, cropped_brick))

        return bbs_with_blobs

    @staticmethod
    def prepare_response_from_analysis_results(detection_results: DetectionResultsList,
                                               classification_results: ClassificationResultsList) -> ListOfBoundingBoxes:

        bounding_boxes = []
        for i in range(len(detection_results)):
            if detection_results[i].detection_score < 0.5:
                continue

            bb = detection_results[i].detection_box.to_bounding_box()
            bb.score = classification_results[i].classification_score
            bb.label = classification_results[i].classification_class
            bounding_boxes.append(bb)

        bb_list = ListOfBoundingBoxes()
        bb_list.packet.extend(bounding_boxes)

        return bb_list

    @staticmethod
    def prepare_bbs_response_from_detection_results(detection_results: DetectionResultsList) -> ListOfBoundingBoxes:
        bounding_boxes = []
        for i in range(len(detection_results)):
            if detection_results[i].detection_score < 0.5:
                continue

            bb = detection_results[i].detection_box.to_bounding_box()
            bb.score = detection_results[i].detection_score
            bb.label = ImageProtoUtils.DEFAULT_LABEL
            bounding_boxes.append(bb)

        bb_list = ListOfBoundingBoxes()
        bb_list.packet.extend(bounding_boxes)

        return bb_list
