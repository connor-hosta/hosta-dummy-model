import cv2
from config_TEST import *
from inference_TEST import *
from predictor_materials import *
from predictor_materials_model1 import *
# from threshold_check import *
from post_processing import Postprocessing
from visualization import Visualize
from post_processing_materials import PostprocessingMat

#
# img_name = "testing/images/downloadImages (2)/ab3d4c9e-7d59-4f9b-b88b-c2cd5c8583b7_2.jpg" #uncomment for testing locally
# img = cv2.imread(img_name) #uncomment for testing locally
# model_path = "testing/bathroom-9:8:2022/bathroom_model_v2.pth" #uncomment for testing locally
# flag = 'bathroom-objects'

def setup(model_path, flag):
    ###################### Sets new config ##################
    con = config(flag)
    setconfig = set_config(model_path, con, flag)
    predictor = setconfig.inf()
    predictor = setconfig.inf()
    return predictor
    ###################### PREDICTION ##################


def run(predictor, img, img_name, flag):

    if flag != 'materials-structures':
        outputs = predictor(img)
        model_out = Model_Inference(img, img_name)
        objects = model_out.get_inference(outputs, flag)
        processed_objects = Postprocessing()
        new_list = processed_objects.post_process(objects, img, flag)
        return new_list
    else:
        outputs = predictor(img)
        model_out = Model_Inference_Model1(img, img_name)
        floor, ceiling, wall = model_out.get_inference_model1(outputs, flag)
        processed_objects = PostprocessingMat()
        new_floor, new_ceiling, new_wall = processed_objects.post_process_materials(floor, wall, ceiling, img, flag)

        return new_floor, new_ceiling, new_wall

# img_name = "testing/images/0003fad1-0e07-4298-8194-ba1289964736.rgb_0000.png" #uncomment for testing locally
# img = cv2.imread(img_name) #uncomment for testing locally
# model_path = "testing/bathroom-9:8:2022/bathroom_model_0244999_2022_Aug_09.pth" #uncomment for testing locally
# roomtype = 'Bathroom'

# predictor = setup(model_path, roomtype)
# run(predictor, img, img_name, roomtype)
