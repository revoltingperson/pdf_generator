import cv2
import imutils as imutils
from PyQt5.QtGui import QTransform, QPixmap

from toplevel.brightness import BrightnessWidget


class ImageEditor:
    last_rotation = 0
    last_brightness = 0

    def __init__(self, scene):
        self.scene = scene
        self.edited = None
        self.pixmap = None
        self.base_pixmap = None

    def set_pixmap(self, pix):
        self.pixmap = pix

    def do_rotation(self, degree):
        rotated = self.pixmap.transformed(QTransform().rotate(degree))
        return rotated

    def do_custom_rotation(self, degree):
        self.pixmap = self.base_pixmap
        return self.do_rotation(degree)

    def do_flip(self, pack):
        x, y = pack
        flipped = self.pixmap.transformed(QTransform().scale(x, y))
        return flipped

    def resize(self, size):
        w, h = size
        scaled = self.pixmap.scaled(w, h)
        return scaled

    def changed_brightness(self, value):
        hsv = cv2.cvtColor(self.input_image, cv2.COLOR_BGR2HSV)
        self.last_brightness = value
        h, s, v = cv2.split(hsv)
        lim = 255 - value
        v[v > lim] = 255
        v[v <= lim] += value
        final_hsv = cv2.merge((h, s, v))
        img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)

    def gamma_changed(self, value):
        value = value / 10
