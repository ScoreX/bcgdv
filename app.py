import uuid
import boto3
import logging
import tornado.ioloop
import tornado.web

from io import BytesIO
from PIL import Image
from tornado.options import parse_command_line


S3BUCKET = "dos-progimage"

FORMATS = {
    'PNG': 'RGBA',
    'JPEG': 'RGB'
}

logger = logging.getLogger('ProgImage')


class StorageApplication(tornado.web.Application):

    def __init__(self, s3client, *args, **kwargs):
        super(StorageApplication, self).__init__(*args, **kwargs)

        self.s3client = s3client


class StorageHandler(tornado.web.RequestHandler):

    def _set_error(self, message, status=400):
        """
        Helper method to return a useful error message to the client rather than tornados default error html page

        :param message: Error message to show to the client
        :param status: HTTP Status code to use
        :return: None
        """
        self.write(message)
        self.set_status(status)
        self.finish()

    def get(self, identifier, format=None):
        """ Retrieve image using specified identifier and optionally convert it to a new format

            :param identifier: Unique id for the image
            :param format: Alternative format to return image in
        """

        format = format.upper() if format else None

        if format and format not in FORMATS.keys():
            self._set_error("Conversion to %s is not supported" % format, status=400)
            return

        try:
            response = self.application.s3client.get_object(
                Bucket=S3BUCKET,
                Key=identifier,
            )
        except self.application.s3client.exceptions.NoSuchKey:
            self._set_error("%s is not a valid identifier" % identifier)
            return

        image = response['Body'].read()

        if format:
            bytes = BytesIO()
            bytes.write(image)
            temp = Image.open(bytes)

            if temp.format == format:
                logger.warning("Image is already in specified format. No conversion required")
            else:
                new = BytesIO()
                temp = temp.convert(FORMATS[format])
                temp.save(new, format=format)
                new.seek(0)
                image = new.read()

        self.write(image)

    def post(self):
        """ Store image and return unique identifier
        """

        # Check that it's a valid image
        try:
            bytes = BytesIO()
            bytes.write(self.request.body)
            Image.open(bytes)
        except OSError:
            self._set_error("Request body is not a valid image", status=400)
            return

        # This will be used to uniquely identify the image
        # Note that original filename will not be preserved
        s3key = uuid.uuid4().hex

        self.application.s3client.put_object(
            Bucket=S3BUCKET,
            Key=s3key,
            Body=self.request.body
        )

        self.write(s3key)


def make_app(s3client):

    handlers = [
        (r"/api/image-service/store", StorageHandler),
        (r"/api/image-service/retrieve/([a-zA-Z0-9]+)(?:/([a-z]*))?", StorageHandler),
    ]

    return StorageApplication(
        s3client,
        handlers
    )


if __name__ == "__main__":

    parse_command_line()

    client = boto3.client('s3')

    app = make_app(client)
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()