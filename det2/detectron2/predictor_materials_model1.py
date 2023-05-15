import numpy as np
import json, cv2

class Model_Inference_Model1:

    def __init__(self, img, img_name):
        self.img = img
        self.img_name = img_name


    def grab_contours(self, counts):
        # if the length the contours tuple returned by cv2.findContours
        # is '2' then we are using either OpenCV v2.4, v4-beta, or
        # v4-official
        if len(counts) == 2:
            counts = counts[0]

        # if the length of the contours tuple is '3' then we are using
        # either OpenCV v3, v4-pre, or v4-alpha
        elif len(counts) == 3:
            counts = counts[1]

        # otherwise OpenCV has changed their cv2.findContours return
        # signature yet again and I have no idea WTH is going on
        else:
            raise Exception(("Contours tuple must have length 2 or 3, "
                             "otherwise OpenCV changed their cv2.findContours return "
                             "signature yet again. Refer to OpenCV's documentation "
                             "in that case"))

        # return the actual contours array
        return counts

    def refinement(self, polygon):
        cnts = cv2.findContours(polygon.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = self.grab_contours(cnts)
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
        # print("counts: ", cnts[0])

        if cnts:
            epsilon = 0.015 * cv2.arcLength(np.float32(cnts[0]), True)
            approx_poly = cv2.approxPolyDP(np.float32(cnts[0]), epsilon, True)

            points = approx_poly

            pts = points.reshape(len(approx_poly), 2).tolist()

            final_points = []
            for point in pts:
                point = [int(i) for i in point]
                final_points.append(point)

            return final_points


    def get_inference_model1(self, outputs, flag):

        if outputs != None:
            instances = outputs['instances']
            bboxes = instances.pred_boxes.tensor.detach().cpu().numpy()
            segmentation = np.float32(instances.pred_masks.detach().cpu().numpy() * 255)
            pred_ids = instances.pred_classes.detach().cpu().numpy()
            confidence = instances.scores.detach().cpu().numpy()
            print("pred_ids", pred_ids)
            # print("segmentation", segmentation)

            if flag == 'bathroom-objects':
                categories_names_path = "testing/category_names/bathroom_categories_v2.json"
            elif flag == 'bedroom-objects' or flag == 'dining-objects' or flag == 'sunroom-objects' or flag == 'other-objects' or flag == 'basement-objects':
                categories_names_path = "testing/category_names/bedroom_categories_v2.json"
            elif flag == 'living-objects':
                categories_names_path = 'testing/category_names/living-v2.json'
            elif flag == 'laundry-objects':
                categories_names_path ='testing/category_names/laundry_categories.json'
            elif flag == 'kitchen-objects':
                categories_names_path = "testing/category_names/kitchen_v2_categories.json"
            elif flag == 'reference-objects':
                categories_names_path = "testing/category_names/categories_names_reference.json"
            elif flag == 'materials-structures':
                categories_names_path ="testing/category_names/materials_categpries_v2.json"
            elif flag == 'reference-doortrim-objects':
                categories_names_path = "testing/category_names/reference_doortrim_categories.json"

            with open(categories_names_path, 'r') as cat_json:
                data = json.load(cat_json)
                print(data)

            objects = []
            floor = []
            ceiling = []
            wall = []

            print("Length of seg:", len(segmentation))

            data_dict = {}
            for i, each in enumerate(data['categories'][0]):
                data_dict[each['id']] = each['supercategory']

            print("data_dict", data_dict)

            for i, pred_id in enumerate(pred_ids):
                coords = np.column_stack(np.where(segmentation[i] > 0))
                if coords.shape[0] == 0 or coords.shape[1] == 0:
                    continue

                #print("data['categories'][0]",data['categories'][0])
                supercategory_name = data['categories'][0][pred_ids[i]]['supercategory']
                print("supercategory_name", supercategory_name)
                subcategory_name = data['categories'][0][pred_ids[i]]['name']
                #("subcategory_name", subcategory_name)

                if supercategory_name == "floor":
                    floor.append({
                        'supercategory': supercategory_name,
                        'subcategory': subcategory_name,
                        'detection_polygon': self.refinement(segmentation[i]),
                        'confidence': int(confidence[i] * 100)
                    })
                elif supercategory_name == "ceiling":
                    ceiling.append({
                        'supercategory': supercategory_name,
                        'subcategory': subcategory_name,
                        'detection_polygon': self.refinement(segmentation[i]),
                        'confidence': int(confidence[i] * 100)
                    })
                elif supercategory_name == "interior_wall":
                    wall.append({
                        'supercategory': supercategory_name,
                        'subcategory': subcategory_name,
                        'detection_polygon': self.refinement(segmentation[i]),
                        'confidence': int(confidence[i] * 100)
                    })

            return floor, ceiling, wall

