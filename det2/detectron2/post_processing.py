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


class Postprocessing():

    def area_img(self, img):
        h, w, c = img.shape
        area_img = h * w
        return area_img

    def area_obj(self, objects, area_img):
        """
        :param objects:
        :param area_img:
        :return:
        """

        refined_list = []  # type: List[Any]
        delete_list = []

        for i,seg in enumerate(objects):
            box = seg['bounding_box']

            supercategory = seg['supercategory']
            polygon = seg['polygon']
            polygon = Polygon(polygon)
            polygon_area = polygon.area
            # area_obj = (box[2] - box[0]) * (box[3] - box[1])
            area_percent_obj = (polygon_area / area_img) * 100

            if area_percent_obj<0.03:
                print("Removing", supercategory, "in small obj removal with area % =",area_percent_obj )
                delete_list.append(i)
            elif supercategory == 'shower' and area_percent_obj<10:
                delete_list.append(i)
            else:
                pass


        delete_list = list(set(delete_list))
        print("delete_list in small obj removal", delete_list)


        for i, seg in enumerate(objects):
            if i not in delete_list:
                refined_list.append(seg)

        return refined_list



    def list2d_to_tuple_list(self, list2d):
        """
        converts 2D list to list of tuples
        input:
            list2d -- 2D list of points
        output:
            list of tuples
        """
        if list2d is None:
            return
        tuple_list = []

        for p in list2d:
            if p is None:
                return
            x = p[0]
            y = p[1]
            xy = (x, y)
            tuple_list.append(xy)
        return tuple_list

    def area_img(self, img):
        h, w, c = img.shape
        area_img = h * w
        return area_img

    def overlap_poly(self, poly, poly2):
        print(poly, "+", poly2)
        poly_2d_dps = Polygon(self.list2d_to_tuple_list(poly)).buffer(0)
        poly_2d_dps2 = Polygon(self.list2d_to_tuple_list(poly2)).buffer(0)
        poly_area = Polygon(self.list2d_to_tuple_list(poly)).area
        poly_area2 = Polygon(self.list2d_to_tuple_list(poly2)).area
        print("poly_area", poly_area)
        print("poly_area2", poly_area2)

        if poly_area > poly_area2:

            if poly_2d_dps.is_valid:
                poly_area_intersection = poly_2d_dps.intersection(
                    poly_2d_dps2).area
                print("poly_area_intersection", poly_area_intersection)
                poly_area_union = poly_2d_dps.union(poly_2d_dps2).area
                percent_area = (poly_area_intersection / poly_area_union) * 100
                print("poly_area", percent_area)
            else:
                pass

        else:

            if poly_2d_dps.is_valid:
                poly_area_intersection = poly_2d_dps2.intersection(
                    poly_2d_dps).area
                print("poly_area_intersection", poly_area_intersection)
                poly_area_union = poly_2d_dps.union(poly_2d_dps2).area
                percent_area = (poly_area_intersection / poly_area_union) * 100
                print("poly_area", percent_area)

            else:
                pass

        return percent_area

    def valid_polygons(self, objects):
        delete_list = []
        refined_list = []
        for i, seg in enumerate(objects):

            polygons = seg['polygon']
            if len(polygons) <= 3:
                delete_list.append(i)
            else:
                continue

        for i, seg in enumerate(objects):
            if i not in delete_list:
                refined_list.append(seg)

        return refined_list

    def dedup(self, objects):
        """
        :param objects:
        :return:
        """

        delete_list = []
        checked_items = []

        for i, seg in enumerate(objects):
            box = seg['bounding_box']
            poly1 = seg['polygon']
            supercat1 = seg['supercategory']
            confidence1 = seg['confidence']
            for j, seg2 in enumerate(objects):
                box2 = seg2['bounding_box']
                poly2 = seg2['polygon']
                supercat2 = seg2['supercategory']
                confidence2 = seg['confidence']

                if i != j and sorted([i, j]) not in checked_items:
                    overlap_poly = self.overlap_poly(poly1, poly2)
                    print("Overlap is:", overlap_poly, "between", supercat1,
                          supercat2)
                    if overlap_poly >= 1:  # shapely bigger.smaller is always 0, thus this is 1
                        if supercat1 == supercat2:
                            print("Supercategory is same in dedup func .. ")
                            if confidence1 >= confidence2:
                                delete_list.append(j)
                                checked = [i, j]
                                checked_items.append(sorted(checked))
                            else:
                                delete_list.append(i)
                                checked = [i, j]
                                checked_items.append(sorted(checked))
                        elif supercat1 not in ['faucet', 'vanity_cabinet', 'sink'] and supercat2 not in ['faucet','vanity_cabinet','sink']:
                            if confidence1 >= confidence2:
                                delete_list.append(j)
                                checked = [i, j]
                                checked_items.append(sorted(checked))
                            else:
                                delete_list.append(i)
                                checked = [i, j]
                                checked_items.append(sorted(checked))

                            # print("Supercategory is not the same .. ")
                            # area1 = (box[2] - box[0]) * (box[3] - box[1])
                            # area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
                            #
                            # if area1 < area2:
                            #     print("Deleted i..", supercat1)
                            #     delete_list.append(i)
                            #     checked = [i, j]
                            #     checked_items.append(sorted(checked))
                            # else:
                            #     print("Deleted j..", supercat2)
                            #     delete_list.append(j)
                            #     checked = [i, j]
                            #     checked_items.append(sorted(checked))
                    else:
                        pass
                else:
                    pass

        delete_list = list(set(delete_list))
        print("delete_list in dedup", delete_list)
        refined_list = []

        for i, seg in enumerate(objects):
            if i not in delete_list:
                refined_list.append(seg)

        return refined_list

    def check_shower_confidence(self, objects):


        delete_list = []
        for i,seg in enumerate(objects):
            supercategory = seg['supercategory']
            confidence = seg['confidence']
            if supercategory == 'shower':
                if confidence <= 70:
                    delete_list.append(i)
                else:
                    pass

        delete_list = list(set(delete_list))
        print("delete_list in shower confidence removal", delete_list)
        refined_list = []

        for i, seg in enumerate(objects):
            if i not in delete_list:
                refined_list.append(seg)

        return refined_list

    def remove_objects(self, objects):
        """
        Removes doors/faceplates from doortrims model
        """
        delete_list = []
        for i,seg in enumerate(objects):
            supercategory = seg['supercategory']
            if supercategory == 'door' or supercategory == 'faceplate':
                delete_list.append(i)
            else:
                pass

        refined_list = []

        for i, seg in enumerate(objects):
            if i not in delete_list:
                refined_list.append(seg)

        return refined_list

    def reference_confidence(self, objects):
        """
        Removes reference objects with low confidence
        """

        delete_list = []
        for i,seg in enumerate(objects):
            supercategory = seg['supercategory']
            subcategory = seg['subcategory']
            confidence = seg['confidence']
            print(subcategory, confidence)
            if supercategory == 'door':
                if subcategory == 'single_flush-glass' or subcategory == 'double_flush-glass':
                    if confidence<=20:#40
                        delete_list.append(i)
                    else:
                        pass
                elif subcategory == 'double_flush-wood':
                    if confidence<=28: #40
                        delete_list.append(i)
                    else:
                        pass
                elif subcategory == 'double_sliding-wood':
                    if confidence<=50:
                        delete_list.append(i)
                    else:
                        pass
                elif subcategory == 'folding-wood':
                    if confidence<=16: #25
                        delete_list.append(i)
                elif subcategory == 'single_sliding-wood':
                    if confidence<=25: #25
                        delete_list.append(i)

                else:
                    if confidence<=80:
                        delete_list.append(i)

            elif supercategory == 'faceplate':
                if confidence<=50: #was 58
                    delete_list.append(i)
                if subcategory == 'outlet-one_gang':
                    if confidence<=82:
                        delete_list.append(i)
                else:
                    pass
            else:
                pass

        refined_list = []

        for i, seg in enumerate(objects):
            if i not in delete_list:
                refined_list.append(seg)

        return refined_list

    def confidence_laundry(self, objects):
        """
        Removes laundry objects with low confidence.
        """
        delete_list = []
        for i, seg in enumerate(objects):
            supercategory = seg['supercategory']
            confidence = seg['confidence']
            subcategory = seg['subcategory']
            if supercategory == 'base_cabinet':
                if confidence <= 20:
                    delete_list.append(i)
            elif supercategory == 'air_terminal':
                if confidence <= 44:
                    delete_list.append(i)
            elif supercategory == 'interior_window' and subcategory == 'blind':
                if confidence <= 28:
                    delete_list.append(i)
            elif supercategory == 'interior_window' and subcategory == 'fixed':
                if confidence <= 44:
                    delete_list.append(i)
            elif supercategory == 'baseboard':
                if confidence <= 20:
                    delete_list.append(i)
            elif supercategory == 'sink' and subcategory == 'built_in':
                if confidence <= 20:
                    delete_list.append(i)
            elif supercategory == 'faucet':
                if confidence <= 13:
                    delete_list.append(i)
            elif supercategory == 'molding':
                if confidence <= 39:
                    delete_list.append(i)
            elif supercategory == 'shelf' and subcategory == 'single':
                if confidence <= 20:
                    delete_list.append(i)
            elif supercategory == 'fireplace':
                if confidence <= 20:
                    delete_list.append(i)
            elif supercategory == 'shelf' and subcategory == 'assembly':
                if confidence <= 20:
                    delete_list.append(i)
            else:
                pass

        refined_list = []

        for i, seg in enumerate(objects):
            if i not in delete_list:
                refined_list.append(seg)

        return refined_list

    def confidence_living(self, objects):
        """
        Removes living room objects with low confidence
        """
        delete_list = []
        for i, seg in enumerate(objects):
            supercategory = seg['supercategory']
            confidence = seg['confidence']
            subcategory = seg['subcategory']
            if supercategory == 'air_terminal':
                if confidence <= 18:
                    delete_list.append(i)
            elif supercategory == 'interior_window' and subcategory == 'blind':
                if confidence <= 15:
                    delete_list.append(i)
            elif supercategory == 'interior_window' and subcategory == 'fixed':
                if confidence <= 20:
                    delete_list.append(i)
            elif supercategory == 'molding':
                if confidence <= 27:
                    delete_list.append(i)
            elif supercategory == 'baseboard':
                if confidence <= 41:
                    delete_list.append(i)
            elif supercategory == 'rug':
                if confidence <= 37:
                    delete_list.append(i)
            elif supercategory == 'base_cabinet':
                if confidence <=10:
                    delete_list.append(i)
            elif supercategory == 'shelf' and subcategory == 'assembly':
                if confidence <= 13:
                    delete_list.append(i)
            elif supercategory == 'ceiling_light' and subcategory == 'recessed':
                if confidence <= 20:
                    delete_list.append(i)
            else:
                pass

        refined_list = []

        for i, seg in enumerate(objects):
            if i not in delete_list:
                refined_list.append(seg)

        return refined_list

    def confidence_kitchen(self, objects):
        """
        Removes Kitchen room objects with low confidence.
        """
        delete_list = []
        for i, seg in enumerate(objects):
            supercategory = seg['supercategory']
            confidence = seg['confidence']
            subcategory = seg['subcategory']
            if supercategory == 'interior_window' and subcategory == 'curtain':
                if confidence <= 26:
                    delete_list.append(i)
                else:
                    pass
            elif supercategory == 'ceiling_light':
                if confidence <= 20:
                    delete_list.append(i)
                else:
                    pass
            elif supercategory == 'baseboard':
                if confidence <= 27:
                    delete_list.append(i)
                else:
                    pass
            elif supercategory == 'refrigerator':
                if confidence <= 18:
                    delete_list.append(i)
                else:
                    pass
            elif supercategory == 'shelf' and subcategory == 'assembly':
                if confidence <= 30:
                    delete_list.append(i)
                else:
                    pass
            elif supercategory == 'exhaust_hood':
                if confidence <= 12:
                    delete_list.append(i)
                else:
                    pass
            elif supercategory == 'molding':
                if confidence <= 34:
                    delete_list.append(i)
                else:
                    pass
            elif supercategory == 'interior_window' and subcategory == 'fixed':
                if confidence <= 18:
                    delete_list.append(i)
                else:
                    pass
            else:
                pass

        refined_list = []

        for i, seg in enumerate(objects):
            if i not in delete_list:
                refined_list.append(seg)

        return refined_list

    def confidence_bathroom(self, objects):
        """
        Removes bathroom objects with low accuracy.
        """
        delete_list = []
        for i, seg in enumerate(objects):
            supercategory = seg['supercategory']
            confidence = seg['confidence']
            subcategory = seg['subcategory']
            if supercategory == 'fan':
                if confidence <= 23:
                    delete_list.append(i)
            elif supercategory == 'molding':
                if confidence <= 33:
                    delete_list.append(i)
            elif supercategory == 'door' and subcategory == 'shower':
                if confidence <= 12:
                    delete_list.append(i)
            elif supercategory == 'tub' and subcategory == 'surround':
                if confidence <= 12:
                    delete_list.append(i)
            elif supercategory == 'baseboard':
                if confidence <= 38:
                    delete_list.append(i)
            elif supercategory == 'door':
                if confidence <= 30:
                    delete_list.append(i)
            elif supercategory == 'shelf' and subcategory == 'single':
                if confidence <= 21:
                    delete_list.append(i)
            else:
                pass

        refined_list = []

        for i, seg in enumerate(objects):
            if i not in delete_list:
                refined_list.append(seg)

        return refined_list

    def get_4pt_bbox(self, bbox):
        return [[bbox[0],bbox[1]],[bbox[2],bbox[1]],[bbox[2],bbox[3]],[bbox[0],bbox[3]]]

    def change_bbox(self, objects):
        """
        Code to convert BBOx to 8 pts to support grid measurement.
        """
        refined_list = []
        for i, seg in enumerate(objects):
            bbox = seg['bounding_box']
            new_bbox = self.get_4pt_bbox(bbox)
            seg.update({'bounding_box': new_bbox})
            refined_list.append(seg)
        return refined_list

    def reduce_poly_to_4pts(self, polygon):
        """
        Reduces object polygon points to 4 points.
        Credits: Kavita Anant
        """
        polygon = np.float32(list(polygon))
        alpha = 0.01
        ct = 0
        poly_appr = []
        prev_lengths = []
        while len(polygon) > 4:
            print("Entered while loop", len(polygon))
            epsilon = alpha * cv2.arcLength(np.float32(polygon), True)
            approx = cv2.approxPolyDP(np.float32(polygon), epsilon, True)
            poly_prev = poly_appr
            poly_appr = []
            for p in approx:
                poly_appr.append([p[0][0], p[0][1]])
            if len(poly_appr) < 4:
                poly_appr = poly_prev
                polygon = np.float32(poly_appr)
                break
            polygon = np.float32(poly_appr)
            alpha += 0.001
            ct += 1
            prev_lengths.append(len(polygon))
            if len(prev_lengths) > 20 and len(list(set(prev_lengths[-20:]))):
                print('Seems to be running into an infinite loop', len(prev_lengths))
                break

        return polygon.tolist()

    def confidence_bedroom(self, objects):
        """
        Removes objects in bedroom with no confidence.
        """
        delete_list = []
        for i, seg in enumerate(objects):
            supercategory = seg['supercategory']
            confidence = seg['confidence']
            subcategory = seg['subcategory']
            if supercategory == 'base_cabinet':
                if confidence <= 39:
                    delete_list.append(i)
            elif supercategory == 'wall_mounted_light':
                if confidence <= 22:
                    delete_list.append(i)
            elif supercategory == 'air_terminal' and subcategory == 'regular':
                if confidence <= 37: #78
                    delete_list.append(i)
            elif supercategory == 'wall_mounted_light':
                if confidence <= 20:
                    delete_list.append(i)
            elif supercategory == 'ceiling_light' and subcategory == 'pendant':
                if confidence <= 27:
                    delete_list.append(i)
            elif supercategory == 'countertop':
                if confidence <= 15:
                    delete_list.append(i)
            elif supercategory == 'faceplate' and subcategory == 'custom':
                if confidence <= 90:
                    delete_list.append(i)
            elif supercategory == 'interior_window' and subcategory == 'curtain':
                if confidence <= 35: #35
                    delete_list.append(i)
            elif supercategory == 'interior_window' and subcategory == 'hung':
                if confidence <= 10:
                    delete_list.append(i)
            elif supercategory == 'interior_window' and subcategory == 'fixed':
                if confidence <= 20: #47, 44
                    delete_list.append(i)
            elif supercategory == 'interior_window' and subcategory == 'blind':
                if confidence <= 10:
                    delete_list.append(i)
            elif supercategory == 'interior_window' and subcategory == 'casement':
                if confidence <= 20: #20
                    delete_list.append(i)
            elif supercategory == 'mirror':
                if confidence <= 60:
                    delete_list.append(i)
            elif supercategory == 'shelf' and subcategory == 'assembly':
                if confidence <= 14:
                    delete_list.append(i)
            elif supercategory == 'shelf' and subcategory == 'single':
                if confidence <= 44: #18
                    delete_list.append(i)
            elif supercategory == 'ceiling_light' and subcategory == 'track_light':
                if confidence <= 12:
                    delete_list.append(i)
            elif supercategory == 'ceiling_light' and subcategory == 'chandelier':
                if confidence <= 40:
                    delete_list.append(i)
            elif supercategory == 'ceiling_light' and subcategory == 'recessed':
                if confidence <= 30:
                    delete_list.append(i)
            elif supercategory == 'bathroom_vanity_light':
                if confidence <= 80:
                    delete_list.append(i)
            elif supercategory == 'motion_sensor':
                if confidence <= 12:
                    delete_list.append(i)
            elif supercategory == 'fireplace':
                if confidence <= 40:
                    delete_list.append(i)
            elif supercategory == 'air_conditioner':
                if confidence <= 15:
                    delete_list.append(i)
            elif supercategory == 'upper_cabinet' and subcategory == 'single-wood':
                if confidence <= 45:
                    delete_list.append(i)
            elif supercategory == 'vanity_cabinet':
                if confidence <= 80:
                    delete_list.append(i)
            elif supercategory == 'rug':
                if confidence <= 68:
                    delete_list.append(i)
            elif supercategory == 'speaker':
                if confidence <= 81:
                    delete_list.append(i)
            elif supercategory == 'molding':
                if confidence <= 80:
                    delete_list.append(i)
            elif supercategory == 'baseboard':
                if confidence <= 84:
                    delete_list.append(i)
            elif supercategory == 'staircase':
                if confidence <= 44:
                    delete_list.append(i)
            else:
                pass

        refined_list = []
        for i, seg in enumerate(objects):
            if i not in delete_list:
                refined_list.append(seg)

        return refined_list


    def reduce_faceplate_pts(self, objects):
        """
        Reduces faceplate polygon points to 4.
        """

        refined_list = []
        for i, seg in enumerate(objects):
            polygon = seg['polygon']
            supercategory = seg['supercategory']
            if supercategory == 'faceplate':
                new_polygon = self.reduce_poly_to_4pts(polygon)
                seg.update({'polygon': new_polygon})
                print("Reducing faceplate points .. ")
                refined_list.append(seg)
            else:
                refined_list.append(seg)

        return refined_list

    def smoothening_polygons(self, objects):
        """
        Smoothening polygons to make it into a 4pt polygon for better visualization and computation.
        """
        refined_list = []
        for i, seg in enumerate(objects):
            polygon = seg['polygon']
            supercategory = seg['supercategory']

            if supercategory == 'base_cabinet' or supercategory == 'upper_cabinet':
                new_polygon = self.reduce_poly_to_4pts(polygon)
                seg.update({'polygon': new_polygon})
                refined_list.append(seg)
            else:
                refined_list.append(seg)

        return refined_list

    def low_confident_objects(self, objects):
        """
        Removes low confident objects before Deduping
        """

        delete_list = []
        for i,seg in enumerate(objects):
            supercategory = seg['supercategory']
            confidence = seg['confidence']
            subcategory = seg['subcategory']
            if supercategory == 'mirror':
                if confidence <= 60:
                    delete_list.append(i)
            elif supercategory == 'interior_window' and subcategory == 'hung':
                if confidence <= 20: #20
                    delete_list.append(i)
            elif supercategory == 'base_cabinet':
                if confidence <=40:
                    delete_list.append(i)
            elif supercategory == 'staircase':
                if confidence <=30:
                    delete_list.append(i)
            elif supercategory == 'door' and subcategory == 'single_flush-wood':
                if confidence <=80:
                    delete_list.append(i)
            elif supercategory == 'door' and subcategory == 'double_flush-wood':
                if confidence <=54:
                    delete_list.append(i)
            elif supercategory == 'door' and subcategory == 'single_flush-glass':
                if confidence <=22:
                    delete_list.append(i)
            elif supercategory == 'ceiling_light' and subcategory == 'flush':
                if confidence <=40:
                    delete_list.append(i)
            else:
                pass

        refined_list = []

        for i, seg in enumerate(objects):
            if i not in delete_list:
                refined_list.append(seg)

        return refined_list



    def post_process(self, objects, img, flag):
        """
        :param objects: Original list of objects
        :param img:
        :return: Refined list of objects
        """
        # flag = 'reference-objects'

        valid_polygons = self.valid_polygons(objects)
        low_confident_objects = self.low_confident_objects(valid_polygons)
        deduped_objects = self.dedup(low_confident_objects)
        smoothened_polygons = self.smoothening_polygons(deduped_objects)
        area_img = self.area_img(img)
        small_obj_removed = self.area_obj(deduped_objects, area_img)

        if flag == 'bathroom-objects':
            shower_confidence_checked = self.check_shower_confidence(small_obj_removed)
            confidence_bathroom = self.confidence_bathroom(shower_confidence_checked)
            refined_list = confidence_bathroom

        elif flag == 'reference-doortrims-objects':
            remove_additional_obj = self.remove_objects(smoothened_polygons)
            refined_list = remove_additional_obj

        elif flag == 'reference-objects':
            confidence_check = self.reference_confidence(smoothened_polygons)
            reduced_points_faceplate = self.reduce_faceplate_pts(confidence_check)
            refined_list = reduced_points_faceplate

        elif flag == 'laundry-objects':
            confidence_laundry = self.confidence_laundry(smoothened_polygons)
            refined_list = confidence_laundry

        elif flag == 'living-objects':
            confidence_living = self.confidence_living(smoothened_polygons)
            refined_list = confidence_living

        elif flag == 'kitchen-objects':
            confidence_kitchen = self.confidence_kitchen(smoothened_polygons)
            refined_list = confidence_kitchen

        elif flag == 'bedroom-objects' or flag == 'other-objects' or flag == 'dining-objects' or flag == 'sunroom-objects':
            confidence_bedroom = self.confidence_bedroom(deduped_objects)
            refined_list = confidence_bedroom

        else:
            refined_list = small_obj_removed

        refined_list = self.change_bbox(refined_list)

        return refined_list




