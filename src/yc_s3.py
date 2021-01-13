import boto3
from botocore import exceptions as bexc
import time
import json

NOTION_LINK_TEMPLATE = "{user}_notion_link.json"
NOTION_URL_TEMPLATE = "{user}_url_{ts}.json"
NOTION_DOMAINS_TEMPLATE = "{user}_domains.json"


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


class NotionBotS3ClientError(Exception):
    pass


class NotionBotS3Client(object):
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

    def put_link(self, user, link):
        return self.put_string(
            key=NOTION_LINK_TEMPLATE.format(user=user),
            body=json.dumps(
                dict(
                    user=user,
                    timestamp=int(time.time()),
                    value=link
                )
            )
        )

    def put_url(self, user, links):
        return self.put_string(
            key=NOTION_URL_TEMPLATE.format(user=user, ts=int(time.time())),
            body=json.dumps(
                dict(
                    user=user,
                    timestamp=int(time.time()),
                    value=links
                )
            )
        )

    def put_domains(self, user, domains):
        return self.put_string(
            key=NOTION_DOMAINS_TEMPLATE.format(user=user),
            body=json.dumps(
                dict(
                    user=user,
                    timestamp=int(time.time()),
                    value=domains
                )
            )
        )

    def get_string(self, key):
        obj = self._get_object(key)
        return json.loads(obj['Body'].read().decode('utf-8'))

    def get_link(self, user):
        return self.get_string(key=NOTION_LINK_TEMPLATE.format(user=user))

    def get_domains(self, user):
        return self.get_string(key=NOTION_DOMAINS_TEMPLATE.format(user=user))

    def link_exists(self, user):
        return self._object_exists(key=NOTION_LINK_TEMPLATE.format(user=user))

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
