import logging
import tornado.ioloop
import tornado.web

from io import BytesIO
from PIL import Image, ImageFilter
from tornado.options import parse_command_line


logger = logging.getLogger('ProgImage')

FILTERS = {
    'BLUR': ImageFilter.BLUR,
    'CONTOUR': ImageFilter.CONTOUR,
    'DETAIL': ImageFilter.DETAIL,
    'EDGE_ENHANCE': ImageFilter.EDGE_ENHANCE,
    'EDGE_ENHANCE_MORE': ImageFilter.EDGE_ENHANCE_MORE,
    'EMBOSS': ImageFilter.EMBOSS,
    'FIND_EDGES': ImageFilter.FIND_EDGES,
    'SHARPEN': ImageFilter.SHARPEN,
    'SMOOTH': ImageFilter.SMOOTH,
    'SMOOTH_MORE': ImageFilter.SMOOTH_MORE,
}


class FilterHandler(tornado.web.RequestHandler):

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

    def post(self, _filter):
        """ Rotate the provided image by specified degrees
        """

        if _filter.upper() not in FILTERS.keys():
            self._set_error(
                "%s is not a valid filter. Valid filters: %s" % (_filter, ", ".join(FILTERS.keys())),
                status=400
            )
            return

        try:
            # Check that it's a valid image
            bytes = BytesIO()
            bytes.write(self.request.body)
            image = Image.open(bytes)
        except OSError:
            self._set_error("Request body is not a valid image", status=400)
            return
        else:
            original_format = image.format
            image = image.filter(FILTERS[_filter.upper()])

            # Save new filtered image so we can return it
            new_image = BytesIO()
            image.save(new_image, format=original_format)
            new_image.seek(0)
            self.write(new_image.read())

def make_app():

    return tornado.web.Application([
        (r"/api/image-service/transform/filter/([a-zA-Z]+)", FilterHandler),
    ])


if __name__ == "__main__":

    parse_command_line()

    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
