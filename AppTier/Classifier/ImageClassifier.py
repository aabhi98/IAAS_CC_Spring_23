import logging
import os
import subprocess
import base64
from PIL import Image
from io import BytesIO
import sys
import signal

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from Utils.AWSUtils import AWSUtils
from Properties.AppTierProperties import AppTierProperties

log = logging.getLogger(__name__)

class ImageClassifier:
    def __init__(self, request_queue_name=None, response_queue_name=None, request_bucket_name=None, response_bucket_name=None):
        self.aws_utils = AWSUtils(request_queue_name, response_queue_name, request_bucket_name, response_bucket_name)

    def start_classifier(self):
        loop = True
        while loop:
            try:
                print("ImageClassifier: entered")
                message = self.aws_utils.receive_message_from_request_queue()
                # print("***8message***",message)
                # print("####################################")
                image_data = base64.b64decode(message['Body'])
                # decoded_data = image_data

                local_image_path = os.path.join(os.getcwd(), 'image.jpg')
                with open(local_image_path, "wb") as f:
                    f.write(image_data)

                recognition_result = self.get_result(local_image_path)

                response_image_data = open(local_image_path, 'rb').read()
                response_image_data_base64 = base64.b64encode(response_image_data).decode('utf-8')
                response_body = {
                    'image_data': response_image_data_base64,
                    'recognition_result': recognition_result
                }
                # print("***********response_image_data:**********",response_image_data)
                # print("*********response_image_data_base64********",response_image_data_base64)
                self.aws_utils.upload_to_response_s3(response_body["recognition_result"], response_image_data)
                self.aws_utils.send_message_to_response_queue(response_body["recognition_result"])
                self.aws_utils.delete_message_from_sqs(message)
            except Exception as e:
                log.exception("Error in ImageClassifier: {}".format(str(e)))
                loop = False

    def get_result(self, image_path):
        try:
            print("get result entered")
            print(image_path)
            command = f"python3 image_classification.py {image_path}"
            result = subprocess.check_output(command, shell=True)
            return result.decode("utf-8")
        except subprocess.CalledProcessError as e:
            log.error(f"Error running TensorFlow Image Classification: {e}")
            return "Error"
