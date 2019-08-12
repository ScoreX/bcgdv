import io
import requests

from urllib.parse import urljoin
from PIL import Image


# Keep a public session so we can reuse http connections, improving performance
_session = requests.Session()

DEFAULT_HOST = "http://localhost:8000"


def upload(image: Image, api_host: str=DEFAULT_HOST) -> str:
    return API(api_host).upload(image)


def download(identifier: str, format: str=None, api_host: str=DEFAULT_HOST) -> Image:
    return API(api_host).download(identifier, format=format)


def rotate(image: Image, degrees: int, api_host: str=DEFAULT_HOST) -> Image:
    return API(api_host).rotate(image, degrees)

def apply_filter(image: Image, filter:str, api_host: str=DEFAULT_HOST) -> Image:
    return API(api_host).apply_filter(image, filter)


class API(object):

    def __init__(self, host: str=DEFAULT_HOST):
        self.host = host

    def upload(self, image: Image) -> str:
        """ Upload an image to the ProgImage service and get back a unique identifier
        """
        url = "/api/image-service/image"


        bytes = io.BytesIO()
        image.save(bytes, format=image.format)
        bytes.seek(0)

        response = _session.put(urljoin(self.host, url), data=bytes.read())

        if response.status_code != 200:
            raise Exception(response.text)

        return response.text

    def download(self, identifier: str, format: str=None) -> Image:
        """ Download an image from the ProgImage service given it's unique identifier
        """
        url = "/api/image-service/image/%s" % identifier

        if format:
            url += "/%s" % format

        response = _session.get(urljoin(self.host, url))

        if response.status_code != 200:
            raise Exception(response.text)

        bytes = io.BytesIO(response.content)
        image = Image.open(bytes)

        return image

    def rotate(self, image: Image, degrees: int) -> Image:
        """ Rotate given image by specified number of degrees
        """

        url = "/api/image-service/transform/rotate/%s" % degrees

        bytes = io.BytesIO()
        image.save(bytes, format=image.format)
        bytes.seek(0)

        response = _session.post(urljoin(self.host, url), data=bytes.read())

        if response.status_code != 200:
            raise Exception(response.text)

        bytes = io.BytesIO(response.content)
        image = Image.open(bytes)

        return image

    def apply_filter(self, image: Image, filter:str) -> Image:
        """ Apply the specific image filter to the image
        """

        url = "/api/image-service/transform/filter/%s" % filter

        bytes = io.BytesIO()
        image.save(bytes, format=image.format)
        bytes.seek(0)

        response = _session.post(urljoin(self.host, url), data=bytes)

        if response.status_code != 200:
            raise Exception(response.text)

        bytes = io.BytesIO(response.content)
        image = Image.open(bytes)

        return image
