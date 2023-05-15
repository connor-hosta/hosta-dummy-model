from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor

class set_config:

    def __init__(self, model_path, cfg, flag):
        # self.img = img
        self.model_path = model_path
        self.cfg = cfg
        self.flag = flag

    def inf(self):
        # img = self.img
        model_path = self.model_path
        cfg = self.cfg
        print("Loaded config.. ")
        cfg.MODEL.WEIGHTS = model_path
        print("Loaded weights.. ")
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.10  # set a custom testing threshold\
        #cfg.DATASETS.TEST = ('m1_structures',)
        predictor = DefaultPredictor(cfg)
        cfg.merge_from_file("./detectron2/configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")
        # cfg.DATASETS.TRAIN = ("m1_structures",)
        cfg.DATALOADER.NUM_WORKERS = 16
        #cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")
        cfg.SOLVER.IMS_PER_BATCH = 2
        cfg.SOLVER.BASE_LR = 0.0018
        # cfg.SOLVER.MAX_ITER = 15020
        cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 256
        if self.flag == 'bathroom-objects':
            cfg.MODEL.ROI_HEADS.NUM_CLASSES = 58
        elif self.flag == 'bedroom-objects' or self.flag =='dining-objects' or self.flag =='sunroom-objects' or self.flag == 'other-objects' or \
                self.flag == 'basement-objects':
            cfg.MODEL.ROI_HEADS.NUM_CLASSES = 46
        elif self.flag == 'living-objects':
            cfg.MODEL.ROI_HEADS.NUM_CLASSES = 37
        elif self.flag == 'laundry-objects':
            cfg.MODEL.ROI_HEADS.NUM_CLASSES = 35
        elif self.flag == 'kitchen-objects':
            cfg.MODEL.ROI_HEADS.NUM_CLASSES = 69
        elif self.flag == 'materials-structures':
            cfg.MODEL.ROI_HEADS.NUM_CLASSES = 17
        elif self.flag == 'reference-objects':
            cfg.MODEL.ROI_HEADS.NUM_CLASSES = 36
        elif self.flag == 'reference-doortrims-objects':
            cfg.MODEL.ROI_HEADS.NUM_CLASSES = 37
        else:
            cfg.MODEL.ROI_HEADS.NUM_CLASSES = 69

        # im = cv2.imread("image_samples/IMG_4487_ORIGINAL_HEETIKA.jpg")
        print("Starting prediction.. ")
        #outputs = predictor(img)
        # print("outputs", outputs)
        print("Prediction done. ")

        return predictor