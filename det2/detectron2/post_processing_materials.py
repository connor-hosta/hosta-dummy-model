# import itertools
import yaml
from shapely.geometry import Polygon
from shapely.geometry import Point
import math
import numpy as np
import cv2

__author__ = "Heetika Gada"
__copyright__ = "Copyright 2022, Hosta a.i."
__credits__ = ["Heetika Gada"]
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = ["Heetika Gada"]
__email__ = ["hgada@hosta.ai"]
__status__ = "Test"  # Development / Test / Release.

from typing import List, Any


class PostprocessingMat():

    def valid_polygons(self, objects):
        delete_list = []
        refined_list = []
        for i, seg in enumerate(objects):

            polygons = seg['detection_polygon']
            if len(polygons) <= 3:
                delete_list.append(i)
            else:
                continue

        for i, seg in enumerate(objects):
            if i not in delete_list:
                refined_list.append(seg)

        return refined_list

    def confidence_floor(self, objects):

        confidence_list_floor = []
        delete_list = []
        refined_list = []

        for i, seg in enumerate(objects):

            subcategory = seg['subcategory']
            supercategory = seg['supercategory']
            confidence = seg['confidence']
            print(supercategory, subcategory, confidence)
            confidence_list_floor.append(confidence)

        mat_picked = sorted(confidence_list_floor, reverse=True)
        for i, seg in enumerate(objects):

            confidence = seg['confidence']

            if confidence != mat_picked[0]:
                delete_list.append(i)
            else:
                pass

        for i, seg in enumerate(objects):
            if i not in delete_list:
                refined_list.append(seg)

        return refined_list

    def confidence_walls(self, objects):

        delete_list = []
        refined_list = []

        for i, seg in enumerate(objects):

            confidence = seg['confidence']
            if confidence <=30:
                delete_list.append(i)

        for i, seg in enumerate(objects):
            if i not in delete_list:
                refined_list.append(seg)

        return refined_list


    def post_process_materials(self, floor, wall, ceiling, img, flag):
        """
        :param objects: Original list of objects
        :param img:
        :return: Refined list of objects
        """

        valid_polygon_floor = self.valid_polygons(floor)
        confidence_floor = self.confidence_floor(valid_polygon_floor)
        valid_polygon_ceiling = self.valid_polygons(ceiling)
        confidence_ceilings = self.confidence_floor(valid_polygon_ceiling)
        valid_polygon_wall = self.valid_polygons(wall)
        confidence_walls = self.confidence_walls(valid_polygon_wall)

        refined_list_floor = confidence_floor
        refined_list_ceiling = confidence_ceilings
        refined_list_wall = confidence_walls

        return refined_list_floor, refined_list_ceiling, refined_list_wall




