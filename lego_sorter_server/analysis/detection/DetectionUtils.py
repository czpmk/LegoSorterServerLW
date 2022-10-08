from PIL import Image

from lego_sorter_server.analysis.detection.DetectionResults import DetectionBox


def resize(img: Image, target: int) -> (Image, float):
    width, height = img.size
    scaling_factor = target / max(width, height)
    im_resized = img.resize((int(width * scaling_factor), int(height * scaling_factor)), Image.BICUBIC)
    new_im = Image.new('RGB', (target, target), color=(0, 0, 0))
    new_im.paste(im_resized, (0, 0))
    return new_im, scaling_factor


def crop_with_margin_from_bb(image: Image, detection_box: DetectionBox, abs_margin: float = 0,
                             rel_margin: float = 0.10) -> Image:
    return crop_with_margin(image, detection_box, abs_margin, rel_margin)


def crop_with_margin(image: Image, detection_box: DetectionBox, abs_margin: float = 0,
                     rel_margin: float = 0.10) -> Image:
    return image.crop(detection_box.resize(abs_margin, rel_margin).to_tuple())
