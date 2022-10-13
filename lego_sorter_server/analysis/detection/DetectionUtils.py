from PIL import Image

from lego_sorter_server.common.DetectionResults import DetectionBox


def resize(img, target):
    width, height = img.size
    scaling_factor = target / max(width, height)
    im_resized = img.resize((int(width * scaling_factor), int(height * scaling_factor)), Image.BICUBIC)
    new_im = Image.new('RGB', (target, target), color=(0, 0, 0))
    new_im.paste(im_resized, (0, 0))
    return new_im, scaling_factor


def crop_with_margin_from_detection_box(image, detection_box: DetectionBox, abs_margin=0, rel_margin=0.10):
    return crop_with_margin(image, detection_box, abs_margin, rel_margin)


def crop_with_margin(image, detection_box: DetectionBox, abs_margin=0, rel_margin=0.10):
    width, height = image.size

    # Apply margins
    avg_length = ((detection_box.x_max - detection_box.x_min) + (detection_box.y_max - detection_box.y_min)) / 2
    y_min = max(detection_box.y_min - abs_margin - rel_margin * avg_length, 0)
    x_min = max(detection_box.x_min - abs_margin - rel_margin * avg_length, 0)
    y_max = min(detection_box.y_max + abs_margin + rel_margin * avg_length, height)
    x_max = min(detection_box.x_max + abs_margin + rel_margin * avg_length, width)

    return image.crop([x_min, y_min, x_max, y_max])
