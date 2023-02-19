import logging
import os
import subprocess
import base64
from PIL import Image
from io import BytesIO
from AppTier.Utils import AWSUtils, AppTierProperties


log = logging.getLogger(__name__)

class ImageClassifier:
    def __init__(self, request_queue_name=None, response_queue_name=None, request_bucket_name=None, response_bucket_name=None):
        self.aws_utils = AWSUtils(request_queue_name, response_queue_name, request_bucket_name, response_bucket_name)

    def start_classifier(self):
        loop = True
        while loop:
            try:
                message = self.aws_utils.receive_message_from_request_queue()
                image_data = base64.b64decode(message['Body'])
                img = Image.open(BytesIO(image_data))

                local_image_path = os.path.join(os.getcwd(), img)
                image_content = self.aws_utils.download_from_request_s3(img)
                with open(local_image_path, "wb") as f:
                    f.write(image_content)

                recognition_result = self.get_result(local_image_path)

                self.aws_utils.upload_to_response_s3(img, recognition_result)

                self.aws_utils.send_message_to_request_queue(recognition_result)

                self.aws_utils.delete_message_from_request_queue(message)
                
            except Exception as e:
                log.exception(f"An error occurred while processing the message: {e}")
                loop = False

    def get_result(self, image_path):
        try:
            command = f"python image_classification.py {image_path}"
            log.info(f"Command being executed on AppTier: {command}")

            with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, timeout=100) as process:
                stdout, stderr = process.communicate()

            if process.returncode == 0:
                return stdout.decode().strip()
            else:
                return f"Timeout for image recognition passed no result. Error: {stderr.decode().strip()}"
        except subprocess.TimeoutExpired:
            return "Timeout for image recognition passed no result"
