from detectron2.utils.visualizer import ColorMode
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
import cv2

def run_inference():
    cfg = get_cfg()
    # cfg.merge_from_file("reference_30000_config.yaml")
    cfg.MODEL.WEIGHTS = "output_v3/model_final.pth"
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.1  # set a custom testing threshold
    predictor = DefaultPredictor(cfg)
    imgs = ['./synthetic-images/pic_1.png']
    for im_path in imgs:
        im = cv2.imread(im_path)
        #print(im)

        output = predictor(im)
        v = Visualizer(im[:, :, ::-1], scale=0.5, instance_mode=ColorMode.IMAGE_BW)
        out = v.draw_instance_predictions(output['instances'].to('cpu'))
        print(output)
        print(out)
        cv2.imwrite('./synthetic-images/pic_1_out.png', out.get_image()[:, :, ::-1])

if __name__ == '__main__':
    run_inference()