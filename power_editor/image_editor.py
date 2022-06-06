import cv2
import imutils as imutils
from PyQt5.QtGui import QTransform, QPixmap

# raw_image ->

class ImageEditor:
    last_rotation = 0
    last_custom_rot = 0
    last_brightness = 0
    flipped_x = 1
    flipped_y = 1
    last_size: tuple

    def __init__(self, scene):
        self.to_restore = None
        self.scene = scene
        self.edited = None
        self.pixmap = None
        self.restore = False
        self.base_pixmap = None

    def set_to_default(self):
        self.last_rotation = 0
        self.last_custom_rot = 0
        self.last_brightness = 0
        self.flipped_x = 1
        self.flipped_y = 1

    def set_pixmap(self, pix):
        self.pixmap = pix

    def do_rotation(self, degree):
        if not self.restore:
            add = self.last_rotation + degree
            self.last_rotation = add if degree % 90 == 0 else self.last_rotation

        rotated = self.pixmap.transformed(QTransform().rotate(degree))
        print(self.last_size)
        print(self.last_rotation)
        return rotated

    def do_custom_rotation(self, degree):
        if not self.restore:
            self.last_custom_rot = degree

        self.pixmap = self.base_pixmap
        print(self.pixmap.size())
        return self.do_rotation(degree)

    def do_flip(self, pack):
        x, y = pack
        if not self.restore:
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

        if not self.restore:
            self.last_size = size
            self.base_pixmap = scaled
        return scaled

    def refresh_data(self, pixmap):
        self.to_restore = [{'resize': self.last_size},
                           {'rotation': self.last_rotation + self.last_custom_rot},
                           {'flip': (self.flipped_x, self.flipped_y)}
                           ]
        self.restore = True

        for transformation in self.to_restore:
            self.scene.map_pixmap_to_scene(pixmap=pixmap, rules=transformation)
            pixmap = self.scene.return_scene_item_as_pixmap()

        self.restore = False

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
        print(self.to_restore)
        self.refresh_data(pixmap)

    def gamma_changed(self, value):
        value = value / 10
