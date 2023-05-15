import io
import numpy as np
import cv2
import json
import flask
import os
import boto3
from botocore.exceptions import ClientError
from detectron2.utils.logger import setup_logger
setup_logger()
from main_TEST import run
from main_TEST import setup


__author__ = "Heetika Gada"
__copyright__ = "Copyright 2022, Hosta a.i."
__credits__ = ["Heetika Gada"]
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = ["Heetika Gada"]
__email__ = ["hgada@hosta.ai"]
__status__ = "Test"  # Development / Test / Release.

ssm = boto3.client('ssm', region_name='us-east-2')
lambdaClient = boto3.client('lambda', region_name='us-east-2')

def get_config_parameter(name):
    try:
        p = ssm.get_parameter(Name=name)
    except (ssm.exceptions.ParameterNotFound, ssm.exceptions.ParameterVersionNotFound):
        raise RuntimeError('Invalid config parameter: {}'.format(name))
    return p['Parameter']['Value']

ENV = get_config_parameter('/hosta/env')
prefix = os.environ['MODEL_PATH']

model_name_bathroom = 'bathroom-v2.pth'
model_name_kitchen = 'kitchen-v2.pth'
model_name_bedroom = 'bedroom-v2.pth'
model_name_laundry = 'laundry-v2.pth'
model_name_living = 'living-v2.pth'
model_name_material = 'material-v2.pth'
model_name_reference = 'reference-v2.pth'
model_name_doortrim = 'doortrim-v2.pth'

model_path_bathroom = os.path.join(prefix, model_name_bathroom)
model_path_kitchen = os.path.join(prefix, model_name_kitchen)
model_path_bedroom = os.path.join(prefix, model_name_bedroom)
model_path_laundry = os.path.join(prefix, model_name_laundry)
model_path_living = os.path.join(prefix, model_name_living)
model_path_material = os.path.join(prefix, model_name_material)
model_path_reference = os.path.join(prefix, model_name_reference)
model_path_doortrim = os.path.join(prefix, model_name_doortrim)

MODEL_OUTPUT_BUCKET = "model-results-{}-hosta-ai".format(ENV)
IMAGE_BUCKET_NAME = 'input-images-{}-hosta-ai'.format(ENV)

def getRoom(s3Client, room):
    return {
        'images': [getImg(s3Client, imgName) for imgName in room['images']],
        'TaskToken': room['TaskToken']
    }

def getImg(s3Client, image_name):
    print("GETTING IMAGE: ", image_name)
    imgContent = io.BytesIO(s3Client.get_object(Bucket=IMAGE_BUCKET_NAME, Key=image_name)['Body'].read())
    img = cv2.imdecode(np.fromstring(imgContent.read(), np.uint8), cv2.IMREAD_COLOR)
    return (img, image_name)

def model_controller(cv_img, image_filename, flag, predictor):
    print("before run func")
    # path = "testing/bathroom-9:8:2022/bathroom_model_0244999_2022_Aug_09.pth"
    if flag == 'materials-structures':
        floor, ceiling, wall = run(predictor, cv_img, image_filename, flag)
        return floor, ceiling, wall
    else:

        objects = run(predictor, cv_img, image_filename, flag)
        return objects


def json_reference_format_create():
    data = {}
    data['reference_objects'] = []
    return data

def json_model2_format_create():
    data = {}
    data['objects'] = []
    return data

def json_model1_format_create():
    data = {}
    data['floor'] = []
    data['ceiling'] = []
    data['interior_wall'] = []
    return data

def main(s3Client, stepClient, room_list, flag, predictor):

    global model_prediction, objects, floor, ceiling, wall
    for roomListObj in room_list:

        room = getRoom(s3Client, roomListObj)

        for (image, imgname) in room['images']:

            if flag == 'materials-structures':
                floor, ceiling, wall = model_controller(image, imgname,flag, predictor)
            else:
                objects = model_controller(image, imgname, flag, predictor)

            if flag in ['bathroom-objects','kitchen-objects','bedroom-objects','dining-objects','sunroom-objects','living-objects',
                        'laundry-objects', 'other-objects', 'basement-objects']:
                model_prediction = json_model2_format_create()
                model_prediction['objects'] = objects
                write_model2(s3Client, imgname, model_prediction)
            elif flag in ['materials-structures']:
                model_prediction = json_model1_format_create()
                model_prediction['floor'] = floor
                model_prediction['ceiling'] = ceiling
                model_prediction['interior_wall'] = wall
                write_model1(s3Client, imgname, model_prediction)
            elif flag in ['reference-objects']:
                model_prediction = json_reference_format_create()
                model_prediction['reference_objects'] = objects
                write_model_reference(s3Client,imgname, model_prediction)
            elif flag in ['reference-doortrims-objects']:
                model_prediction = json_model2_format_create()
                model_prediction['objects'] = objects
                write_model_reference_doortrim(s3Client,imgname,model_prediction)

            # prediction = model_prediction
            print(model_prediction)
            print("JSON Created")
        
        # The room is complete, so send a success to the step function
        try:
            stepClient.send_task_success(
                taskToken=room['TaskToken'],
                output=json.dumps({})
            )

        except ClientError as e:
            print(e.response['Error']['Message'])
            continue
        except Exception as e:
            print(e)
            if (str(e) != "<class 'botocore.errorfactory.TaskTimedOut'>"):
                print("Stepfunction Timeout")
            else:
                lambdaClient.invoke(
                    FunctionName="errorHandler",
                    InvocationType='Event',
                    Payload=json.dumps({
                        'errorMsg': "Error in Reference Model predictor.",
                        'exception': str(e),
                        'info': roomListObj
                    })
                )
            continue


def write_model2(s3Client, image_name, inference_output):
    print("Writing Detection Output: ", image_name)
    outputJsonName = "{}_objects.json".format(image_name.split(".")[0])
    response = s3Client.put_object(Body=bytes(json.dumps(inference_output).encode('UTF-8')), Bucket=MODEL_OUTPUT_BUCKET,
                                   Key=outputJsonName)
    return image_name

def write_model1(s3Client, image_name, inference_output):
    print("Writing Detection Output: ", image_name)
    outputJsonName = "{}_surfaces.json".format(image_name.split(".")[0])
    response = s3Client.put_object(Body=bytes(json.dumps(inference_output).encode('UTF-8')), Bucket=MODEL_OUTPUT_BUCKET,
                                   Key=outputJsonName)
    return image_name

def write_model_reference(s3Client, image_name, inference_output):
    print("Writing Detection Output: ", image_name)
    outputJsonName = "{}_reference.json".format(image_name.split(".")[0])
    response = s3Client.put_object(Body=bytes(json.dumps(inference_output).encode('UTF-8')), Bucket=MODEL_OUTPUT_BUCKET,
                                   Key=outputJsonName)
    return image_name

def write_model_reference_doortrim(s3Client, image_name, inference_output):
    print("Writing Detection Output: ", image_name)
    outputJsonName = "{}_reference_doortrim.json".format(image_name.split(".")[0])
    response = s3Client.put_object(Body=bytes(json.dumps(inference_output).encode('UTF-8')), Bucket=MODEL_OUTPUT_BUCKET,
                                   Key=outputJsonName)
    return image_name


# The flask app for serving predictions
app = flask.Flask(__name__)


@app.route('/ping', methods=['GET'])
def ping():
    """Determine if the container is working and healthy. In this sample container, we declare
    it healthy if we can load the model successfully."""
    print('ping')
    # health = ScoringService.get_model() is not None  # You can insert a health check here

    # status = 200 if health else 404
    status = 200
    return flask.Response(response='\n', status=status, mimetype='text/plain')


@app.route('/invocations', methods=['POST'])
def transformation():
    """Do an inference on a single batch of data. In this sample server, we take data as CSV, convert
    it to a pandas data frame for internal use and then convert the predictions back to CSV (which really
    just means one prediction per line, since there's a single column.
    # """
    req = flask.request.get_json()

    s3Client = None
    stepClient = None
    try:
        s3Client = boto3.client('s3')
        stepClient = boto3.client("stepfunctions", region_name='us-east-2')
    except ClientError as e:
        print(e.response['Error']['Message'])
        raise Exception("Client init error")

    print("req = ", req)

    inferenceType = req["inferenceType"].lower()
    roomList = req["rooms"]

    print("roomList = ", roomList)

    if inferenceType == 'bathroom-objects':
        print("Bathroom detected!")
        model_path = model_path_bathroom
    elif inferenceType == 'kitchen-objects':
        print("Kitchen detected!")
        model_path = model_path_kitchen
    elif inferenceType == 'bedroom-objects' or inferenceType == 'dining-objects' or inferenceType == 'sunroom-objects' or inferenceType == \
            'other-objects' or inferenceType == 'basement-objects':
        print("Bedroom/Dining/Sunroom detected!")
        model_path = model_path_bedroom
    elif inferenceType == 'living-objects':
        print("Living Room detected!")
        model_path = model_path_living
    elif inferenceType == 'laundry-objects':
        print("Laundry detected!")
        model_path = model_path_laundry
    elif inferenceType == 'materials-structures':
        print("Structure model detected!")
        model_path = model_path_material
    elif inferenceType == 'reference-objects':
        print("Reference model detected!")
        model_path = model_path_reference
    elif inferenceType == 'reference-doortrims-objects':
        print("Reference doortrims model detected!")
        model_path = model_path_doortrim
    else:
        print("Unsupported inference type")
        for room in roomList:
            # The room is complete, so send a success to the step function
            try:
                stepClient.send_task_success(
                    taskToken=room['TaskToken'],
                    output=json.dumps({})
                )
            except ClientError as e:
                print(e.response['Error']['Message'])
                continue
            except Exception as e:
                print(e)
                if (str(e) != "<class 'botocore.errorfactory.TaskTimedOut'>"):
                    print("Stepfunction Timeout")
                continue
        return flask.Response(response=json.dumps(roomList), status=200, mimetype='application/json')

    predictor = setup(model_path, inferenceType)
    predictions = main(s3Client, stepClient, roomList, inferenceType, predictor)


    if flask.request.content_type != 'application/json':
        return flask.Response(response='This predictor only supports JSON data', status=415, mimetype='text/plain')

    return flask.Response(response=json.dumps(roomList), status=200, mimetype='application/json')