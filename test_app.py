import app
import io

from unittest.mock import patch, MagicMock
from PIL import Image
from tornado.testing import AsyncHTTPTestCase


class TestStore(AsyncHTTPTestCase):

    def setUp(self):
        self.s3client = MagicMock()

        super(TestStore, self).setUp()

    def get_app(self):
        return app.make_app(self.s3client)

    @patch('app.uuid')
    def test(self, uuid):

        uid = 'ef85db5f47f146dc8d1822fe85f10aad'
        uuid.uuid4.return_value = MagicMock(hex=uid)

        bytes = io.BytesIO()
        image = Image.open('doom.jpg')
        image.save(bytes, format=image.format)
        bytes.seek(0)
        bytes = bytes.read()

        response = self.fetch('/api/image-service/store', method="POST", body=bytes)

        self.assertTrue(type(response.body), 'byte')
        self.assertTrue(response.body == uid.encode())
        self.s3client.put_object.assert_called_once_with(Bucket=app.S3BUCKET, Key=uid, Body=bytes)

    def test_invalid_image(self):

        response = self.fetch('/api/image-service/store', method="POST", body=b'')

        self.assertEqual(response.code, 400)
        self.assertEqual(response.body, b"Request body is not a valid image")


class TestRetrieve(AsyncHTTPTestCase):

    def setUp(self):
        self.s3client = MagicMock()

        super(TestRetrieve, self).setUp()

    def get_app(self):
        return app.make_app(self.s3client)

    def test(self):
        uid = 'ef85db5f47f146dc8d1822fe85f10aad'

        bytes = io.BytesIO()
        image = Image.open('doom.jpg')
        image.save(bytes, format=image.format)
        bytes.seek(0)
        bytes = bytes.read()

        body = MagicMock()
        body.read.return_value = bytes
        obj = MagicMock()
        obj.__getitem__.return_value = body
        self.s3client.get_object.return_value = obj

        response = self.fetch('/api/image-service/retrieve/%s' % uid, method="GET")

        self.assertEqual(response.body, bytes)

    def test_conversion_jpeg_png(self):
        uid = 'ef85db5f47f146dc8d1822fe85f10aad'

        bytes = io.BytesIO()
        image = Image.open('doom.jpg')
        image.save(bytes, format=image.format)
        bytes.seek(0)
        bytes = bytes.read()

        body = MagicMock()
        body.read.return_value = bytes
        obj = MagicMock()
        obj.__getitem__.return_value = body
        self.s3client.get_object.return_value = obj

        response = self.fetch('/api/image-service/retrieve/%s/png' % uid, method="GET")

        bytes = io.BytesIO()
        bytes.write(response.body)
        image = Image.open(bytes)

        self.assertEqual(image.format, "PNG")


    # ** Works when tested manually but can't quite work out how to get around the magic exceptions in boto **
    #
    # def test_invalid_identifier(self):
    #
    #     import boto3
    #     client = boto3.client("s3")
    #
    #     self.s3client.get_object.side_effect = client.exceptions.NoSuchKey({}, "get_object")
    #
    #     response = self.fetch('/api/image-service/retrieve/123', method="GET")
    #
    #     self.assertEqual(response.code, 400)
    #     self.assertEqual(response.body, "123 is not a valid identifier")

