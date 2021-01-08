import boto3
from botocore import exceptions as bexc
import time
import json


def dict_to_binary(the_dict):
    return ' '.join(format(ord(letter), 'b') for letter in json.dumps(the_dict))


def generate_body(user, value):
    return json.dumps(
        dict(
            user=user,
            timestamp=int(time.time()),
            value=value
        )
    )


class YandexS3ClientError(Exception):
    pass


class YandexS3(object):
    def __init__(self,
                 bucket='notion-link-care',
                 service_name='s3',
                 endpoint_url='https://storage.yandexcloud.net',
                 storage_class='COLD'):
        self.service_name = service_name
        self.endpoint_url = endpoint_url
        self.bucket = bucket
        self.session = boto3.session.Session()
        self.storage_class = storage_class
        self.client = self.session.client(
            service_name=self.service_name,
            endpoint_url=self.endpoint_url
        )

    def put_string(self, key, body):
        return self.client.put_object(
            Bucket=self.bucket,
            StorageClass=self.storage_class,
            Key=key,
            Body=body
        )

    def object_exists(self, key):
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
        except bexc.ClientError as e:
            if e.response['Error']['Code'] == "404":
                return False
            raise YandexS3ClientError
        return True

    def get_object(self, key):
        return self.client.get_object(Bucket=self.bucket, Key=key)

    def get_string(self, key):
        obj = self.get_object(key)
        return json.loads(obj['Body'].read().decode('utf-8'))
