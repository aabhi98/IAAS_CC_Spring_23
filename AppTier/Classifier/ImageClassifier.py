import logging
import os
import subprocess
import base64
from PIL import Image
from io import BytesIO
import sys

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
                message = self.aws_utils.receive_message_from_request_queue()
                print(message['Body'])
                image_data = base64.b64decode(message['Body'])
                img = Image.open(BytesIO(image_data))
                img.show()

                local_image_path = os.path.join(os.getcwd(), 'image.jpg')
                with open(local_image_path, "wb") as f:
                    f.write(image_data)

                recognition_result = self.get_result(local_image_path)

                response_image_data = open(local_image_path, 'rb').read()
                response_image_data_base64 = response_image_data.decode('utf-8')
                response_body = {
                    'result': recognition_result,
                    'image': response_image_data_base64
                }

                self.aws_utils.upload_to_response_s3(message['MessageId'], response_image_data)
                self.aws_utils.send_message_to_response_queue(response_body)
                self.aws_utils.delete_message_from_sqs(self.aws_utils.sqs, message['ReceiptHandle'])

            except Exception as e:
                log.exception(f"An error occurred while processing the message: {e}")
                loop = False

    def get_result(self, image_path):
        try:
            command = f"python image_classification.py {image_path}"
            result = subprocess.check_output(command, shell=True)
            return result.decode("utf-8")
        except subprocess.CalledProcessError as e:
            raise ValueError(f"An error occurred while executing the command {command}: {e}")
