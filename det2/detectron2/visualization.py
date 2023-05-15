import cv2
import numpy as np
from PIL import Image, ImageDraw

class Visualize():

    def run_visual(self, img, objects_old, objects_new):
        img2 = img
        #self.old_visual(img, objects_old)
        self.new_visual(img2, objects_new)

    def new_visual(self, img, objects_new):
        """

        :param img:
        :param objects_new:
        :return:
        """
        for seg in objects_new:

            # print("objects_new", objects_new)
            #
            # x1 = seg['detection_polygon'][0]
            # y1 = seg['detection_polygon'][1]
            # x2 = seg['bounding_box'][2]
            # y2 = seg['bounding_box'][3]
            pts = np.array(seg['polygon'], np.int32)
            # if len(pts) >=2:
            #     print("Visualizing more.. ")
            #     for each in pts:
            #         #pts = np.array(([x1, y1], [x2, y2]), np.int32)
            #
            #         new_img = cv2.polylines(img, [each],
            #                           isClosed=True, color=(255, 0, 0), thickness = 5)
            #         supercat = seg['supercategory']
            #         subcat = seg['subcategory']
            #         confidence = str(seg['confidence'])
            #         name = supercat+"_"+confidence
            #         img = cv2.putText(new_img,name , (4500,4500),
            #                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 1)
            #         #cv2.imwrite("output6.jpg", new_img)
            #         pil_image = Image.fromarray(new_img)
            #     pil_image.show()

            new_img = cv2.polylines(img, [pts],
                                    isClosed=True, color=(255, 0, 0), thickness=5)
            supercat = seg['supercategory']
            subcat = seg['subcategory']
            confidence = str(seg['confidence'])
            name = supercat + "_" + confidence
            img = cv2.putText(new_img, name, (4500, 4500),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 1)
            cv2.imwrite("output6.jpg", new_img)
        #     pil_image = Image.fromarray(new_img)
        # pil_image.show()


    def visualization_all_masks(rgb_image, operations_elemnts2d):
        img_height, img_width = rgb_image.shape[0:2]
        acc_mask = np.zeros((img_height, img_width), dtype=np.uint8)
        i = 0
        for elem in operations_elemnts2d:
            if elem.supercategory == "countertop" or elem.supercategory == "island_countertop":
                continue
            if hasattr(elem, 'image_layout_polygon') and elem.image_layout_polygon is not None \
                    and len(elem.image_layout_polygon) > 0:
                image_layout_polygon = elem.image_layout_polygon
            elif hasattr(elem, 'bounding_box') and elem.bounding_box is not None:
                image_layout_polygon = elem.bounding_box
            elif hasattr(elem, 'perspective_bbox') and elem.perspective_bbox is not None:
                image_layout_polygon = elem.perspective_bbox
            else:
                continue

            image_layout_polygon_tuple = list2d_to_tuple_list(image_layout_polygon)
            curr_plane_mask = get_mask_from_polygon(image_layout_polygon_tuple, img_width, img_height)
            acc_mask[curr_plane_mask == 255] = 255 - (i * 5)
            acc_mask = draw_polylines(acc_mask, image_layout_polygon, constants.CV2_GREEN)
            i += 1
        pil_image = Image.fromarray(acc_mask)
        pil_image.show()

    def draw_polylines(rgb_image, polygon, color, thickness=3):
        pts = []
        for point in polygon:
            x = int(point[0])
            y = int(point[1])
            pts.append([x, y])
        # print("pts = ", pts)
        rgb_img = cv2.polylines(rgb_image, np.array([polygon], 'int32'), True, color, thickness=thickness)
        return rgb_img

    def get_mask_from_polygon(polygon, width, height):

        img = Image.new('L', (width, height), 0)
        ImageDraw.Draw(img).polygon(polygon, outline=255, fill=255)
        # img.show(title="mask2D")
        mask = np.array(img)
        return mask

    def list2d_to_tuple_list(list2d):
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

    # def old_visual(self, img, objects_old):
    #
    #     for seg in objects_old:
    #         x1 = seg['bounding_box'][0]
    #         y1 = seg['bounding_box'][1]
    #         x2 = seg['bounding_box'][2]
    #         y2 = seg['bounding_box'][3]
    #
    #         pts = np.array(seg['polygon'], np.int32)
    #         new_img = cv2.polylines(img, [pts],
    #                                 isClosed=True, color=(0, 255, 0), thickness=5)
    #         supercat = seg['supercategory']
    #         subcat = seg['subcategory']
    #         confidence = str(seg['confidence'])
    #         name = supercat + "_" + subcat + "_" + confidence
    #         img = cv2.putText(new_img,name , (x1, y1 - 5),
    #                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255) , 1)
    #         cv2.imwrite("left-wall-old.jpg", new_img)


