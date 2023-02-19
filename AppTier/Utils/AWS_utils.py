import boto3
from botocore.exceptions import ClientError
from AppTierProperties import AppTierProperties

class AWSUtils:
    def __init__(self, request_queue_name=None, response_queue_name=None, request_bucket_name=None, response_bucket_name=None):
        self.request_queue_name = request_queue_name or AppTierProperties.REQUEST_SQS
        self.response_queue_name = response_queue_name or AppTierProperties.RESPONSE_SQS
        self.request_bucket_name = request_bucket_name or AppTierProperties.REQUEST_S3
        self.response_bucket_name = response_bucket_name or AppTierProperties.RESPONSE_S3

        self.sqs = boto3.client('sqs', **AppTierProperties.aws_credentials)
        self.s3 = boto3.client('s3', **AppTierProperties.aws_credentials)

    def send_message_to_request_queue(self, message):
        try:
            queue_url = self.sqs.get_queue_url(QueueName=self.request_queue_name)['QueueUrl']
            self.sqs.send_message(QueueUrl=queue_url, MessageBody=message)
            print(f"Message Sent to Request Queue: {message}")
        except ClientError as e:
            print(f"Error sending message to Request Queue: {e}")
            raise

    def receive_message_from_request_queue(self):
        try:
            queue_url = self.sqs.get_queue_url(QueueName=self.request_queue_name)['QueueUrl']
            response = self.sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1, WaitTimeSeconds=20)
            messages = response.get("Messages", [])
            if not messages:
                print("No messages present in the Request Queue")
                return None
            message = messages[0]
            print(f"Received Message from Request Queue: {message['Body']}")
            return message
        except ClientError as e:
            print(f"Error receiving message from Request Queue: {e}")
            raise

    def download_from_request_s3(self, object_key):
        try:
            response = self.s3.get_object(Bucket=self.request_bucket_name, Key=object_key)
            content = response['Body'].read()
            print(f"Downloaded object from Request S3: {object_key}")
            return content
        except ClientError as e:
            print(f"Error downloading object from Request S3: {e}")
            raise

    def upload_to_response_s3(self, object_key, content):
        try:
            self.s3.put_object(Bucket=self.response_bucket_name, Key=object_key, Body=content)
            print(f"Uploaded object to Response S3: {object_key}")
        except ClientError as e:
            print(f"Error uploading object to Response S3: {e}")
            raise
