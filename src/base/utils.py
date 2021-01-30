from urllib.parse import urlparse


def get_domain(link):
    parsed_uri = urlparse(link)
    return parsed_uri.netloc.replace('www.', '')


class MetaSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
