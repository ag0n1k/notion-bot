from notion.client import NotionClient
from base.utils import MetaSingleton
import boto3
from botocore import exceptions as bexc
import time
import json


class NBotClient(NotionClient, metaclass=MetaSingleton):
    def __init__(self, token):
        super().__init__(token_v2=token)

    def connect(self, link):
        return self.get_collection_view(link)


class NBotS3ClientError(Exception):
    pass


class NBotS3Client(metaclass=MetaSingleton):
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
        self.key_template = "nbot_{user}.json"

    def put(self, user, dict_value):
        return self.put_string(
            key=self.key_template.format(user=user),
            body=json.dumps(dict_value)
        )

    def get(self, user):
        return self.get_string(key=self.key_template.format(user=user))

    def exists(self, user):
        return self._object_exists(key=self.key_template.format(user=user))

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
            raise NBotS3ClientError
        return True

    def _get_object(self, key):
        if self._object_exists(key):
            return self.client.get_object(Bucket=self.bucket, Key=key)
        return None
