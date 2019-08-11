import uuid
import boto3
import logging
import tornado.ioloop
import tornado.web

from io import BytesIO
from tornado.options import parse_command_line
from PIL import Image


S3BUCKET = "dos-progimage"

logger = logging.getLogger('ProgImage')


class StorageApplication(tornado.web.Application):

    def __init__(self, *args, **kwargs):
        super(StorageApplication, self).__init__(*args, **kwargs)

        self.s3client = boto3.client('s3')


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


if __name__ == "__main__":

    parse_command_line()

    app = StorageApplication([
        (r"/api/image-service/store", StorageHandler),
    ])
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()