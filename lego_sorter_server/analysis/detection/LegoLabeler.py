from typing import List

from lego_sorter_server.common.DetectionResults import DetectionBox


class LegoLabeler:

    def to_label_file(self, filename, path, image_width, image_height, detection_boxes: List[DetectionBox]):
        objects = ""
        for db in detection_boxes:
            objects += self.get_object(*db.to_tuple())

        return f"""<annotation>
                <folder>images</folder>
                <filename>{filename}</filename>
                <path>{path}</path>
                <source>
                        <database>LegoSorterPGR</database>
                </source>
                <size>
                        <width>{image_width}</width>
                        <height>{image_height}</height>
                        <depth>3</depth>
                </size>
                <segmented>0</segmented>
                {objects}
        </annotation>"""

    @staticmethod
    def get_object(y1, x1, y2, x2):
        return f"""<object>
                        <name>lego</name>
                        <pose>Unspecified</pose>
                        <truncated>0</truncated>
                        <difficult>0</difficult>
                        <bndbox>
                                <xmin>{int(x1)}</xmin>
                                <ymin>{int(y1)}</ymin>
                                <xmax>{int(x2)}</xmax>
                                <ymax>{int(y2)}</ymax>
                        </bndbox>
                </object>"""
