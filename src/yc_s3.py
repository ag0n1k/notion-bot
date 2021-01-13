import boto3
from botocore import exceptions as bexc
import time
import json

TEMPLATES_SWITCH = {
    "link": "{user}_notion_link.json",
    "urls": "{user}_urls.json",
    "domains": "{user}_domains.json",
}

NOTION_LINK_TEMPLATE = "{user}_notion_link.json"
NOTION_URL_TEMPLATE = "{user}_urls.json"
NOTION_DOMAINS_TEMPLATE = "{user}_domains.json"


class NotionBotS3ClientError(Exception):
    pass


class NotionBotS3Client(object):
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
            key=TEMPLATES_SWITCH[value_type].format(user=user),
            body=json.dumps(
                dict(
                    user=user,
                    timestamp=int(time.time()),
                    value=value
                )
            )
        )

    def get(self, user, value_type):
        return self.get_string(key=TEMPLATES_SWITCH[value_type].format(user=user))

    def exists(self, user, value_type='link'):
        return self._object_exists(key=TEMPLATES_SWITCH[value_type].format(user=user))

    def put_string(self, key, body):
        return self.client.put_object(
            Bucket=self.bucket,
            StorageClass=self.storage_class,
            Key=key,
            Body=body
        )

    def get_string(self, key):
        obj = self._get_object(key)
        return json.loads(obj['Body'].read().decode('utf-8'))

    def _object_exists(self, key):
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
        except bexc.ClientError as e:
            if e.response['Error']['Code'] == "404":
                return False
            raise NotionBotS3ClientError
        return True

    def _get_object(self, key):
        return self.client.get_object(Bucket=self.bucket, Key=key)
