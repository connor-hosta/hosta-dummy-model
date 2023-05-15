
import detectron2
import numpy as np
import os, json, cv2, random
import matplotlib.pyplot as plt
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog
from detectron2.engine import DefaultTrainer
from detectron2.utils.visualizer import ColorMode
from detectron2.evaluation import COCOEvaluator, inference_on_dataset
from detectron2.data import build_detection_test_loader

def config(flag):

    cfg = get_cfg()
    print("Flag detected in config", flag)

    if flag == 'bathroom-objects':
        config_path = "testing/configs/bathroom-v2.yaml"
    if flag == 'kitchen-objects':
        config_path = "testing/configs/kitchen-v2.yaml"
    if flag == 'bedroom-objects' or flag =='dining-objects' or flag =='sunroom-objects' or flag == 'other-objects' or flag == 'basement-objects':
        config_path = "testing/configs/bedroom-v2.yaml"
    if flag == 'living-objects': #Need to change this
        config_path = 'testing/configs/living-v2.yaml'
    if flag == 'laundry-objects':
        config_path = 'testing/configs/laundry-v2.yaml'
    if flag == 'materials-structures':
        config_path = 'testing/configs/material-v2.yaml'
    if flag == 'reference-objects':
        config_path = 'testing/configs/reference-v2.yaml'
    if flag == 'reference-doortrims-objects':
        config_path = 'testing/configs/doortrim-v2.yaml'

    print("Config path decided:", config_path)
    cfg.merge_from_file(config_path)
    # cfg = cfg.merge_from_file(
    #     "/home/ubuntu/platform-cv-reference/det2/detectron2/testing/bathroom-9:8:2022/bathroom_50000_config.yaml")
    return cfg