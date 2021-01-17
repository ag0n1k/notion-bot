import boto3
from botocore import exceptions as bexc
import time
import json
from utils import MetaSingleton

S3_TEMPLATE = "{user}_notion_bot_{value}.json"


class NotionBotS3ClientError(Exception):
    pass


class NotionBotS3Client(metaclass=MetaSingleton):
    def __init__(self,
                 bucket='notion-link-care',
                 service_name='s3',
                 endpoint_url='https://storage.yandexcloud.net',
                 storage_class='STANDARD'):
        self.service_name = service_name
        self.endpoint_url = endpoint_url
        self.bucket = bucket
        self.session = boto3.session.Session()
        self.storage_class = storage_class
        self.client = self.session.client(
            service_name=self.service_name,
            endpoint_url=self.endpoint_url
        )

    def put(self, user, value, value_type):
        return self.put_string(
            key=S3_TEMPLATE.format(user=user, value=value_type),
            body=json.dumps(
                dict(
                    user=user,
                    timestamp=int(time.time()),
                    value=value
                )
            )
        )

    def get(self, user, value_type):
        return self.get_string(key=S3_TEMPLATE.format(user=user, value=value_type))

    def exists(self, user, value_type='link'):
        return self._object_exists(key=S3_TEMPLATE.format(user=user, value=value_type))

    def put_string(self, key, body):
        return self.client.put_object(
            Bucket=self.bucket,
            StorageClass=self.storage_class,
            Key=key,
            Body=body
        )

    def get_string(self, key):
        obj = self._get_object(key)
        if obj:
            return json.loads(obj['Body'].read().decode('utf-8'))
        return None

    def _object_exists(self, key):
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
        except bexc.ClientError as e:
            if e.response['Error']['Code'] == "404":
                return False
            raise NotionBotS3ClientError
        return True

    def _get_object(self, key):
        if self._object_exists(key):
            return self.client.get_object(Bucket=self.bucket, Key=key)
        return None
