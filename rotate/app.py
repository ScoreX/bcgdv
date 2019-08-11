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


class RotateHandler(tornado.web.RequestHandler):

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

    def post(self, degrees):
        """
        """

        try:
            # Check that it's a valid image
            bytes = BytesIO()
            bytes.write(self.request.body)
            image = Image.open(bytes)
        except OSError:
            self._set_error("Request body is not a valid image", status=400)
            return
        else:
            # Note that PIL rotates the images in a counter-clockwise direction
            rotated_image = image.rotate(int(degrees))

            # Save new rotated image so we can return it
            new_image = BytesIO()
            rotated_image.save(new_image, format=image.format)
            new_image.seek(0)
            self.write(new_image.read())

def make_app():

    return tornado.web.Application([
        (r"/api/image-service/rotate/(\d+)", RotateHandler),
    ])


if __name__ == "__main__":

    parse_command_line()

    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
