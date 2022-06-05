import cv2
import imutils as imutils
from PyQt5.QtGui import QTransform, QPixmap


class ImageEditor:
    last_rotation = 0
    last_custom_rot = 0
    last_brightness = 0
    flipped_x = 1
    flipped_y = 1

    def __init__(self, scene):
        self.scene = scene
        self.edited = None
        self.pixmap = None
        self.base_pixmap = None

    def set_pixmap(self, pix):
        self.pixmap = pix

    def do_rotation(self, degree):
        add = self.last_rotation+degree
        self.last_rotation = add if degree % 90 == 0 else self.last_rotation
        print(self.last_rotation)

        rotated = self.pixmap.transformed(QTransform().rotate(degree))
        return rotated

    def do_custom_rotation(self, degree):
        self.last_custom_rot = degree
        self.pixmap = self.base_pixmap
        return self.do_rotation(degree)

    def do_flip(self, pack):
        x, y = pack
        self.flipped_x = self.check_flipped(x, self.flipped_x)
        self.flipped_y = self.check_flipped(y, self.flipped_y)

        flipped = self.pixmap.transformed(QTransform().scale(x, y))
        return flipped

    def check_flipped(self, axis, my_var):
        if axis < 0 and my_var < 0:
            return 1
        elif axis < 0:
            return axis
        else:
            return my_var

    def resize(self, size):
        w, h = size
        scaled = self.pixmap.scaled(w, h)
        return scaled

    def restore_transformation(self):
        to_restore = [{'rotation': self.last_rotation+self.last_custom_rot},
                      {'flip': (self.flipped_x, self.flipped_y)}]


    def changed_brightness(self, value):
        hsv = cv2.cvtColor(self.scene.color_image, cv2.COLOR_BGR2HSV)
        self.last_brightness = value
        h, s, v = cv2.split(hsv)
        lim = 255 - value
        v[v > lim] = 255
        v[v <= lim] += value
        final_hsv = cv2.merge((h, s, v))
        img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
        pixmap = self.scene.convert_raw_to_pixmap(img)
        self.scene.map_pixmap_to_scene(rules=None, pixmap=pixmap)

    def gamma_changed(self, value):
        value = value / 10
