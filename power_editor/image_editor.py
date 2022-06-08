import cv2
import imutils as imutils
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTransform, QPixmap


# custom rotation -> use pixitem from scene -> save rotation -> apply when pix_mask moves around

# raw -> transformation pixmap saved

# transform command> transformation pixmap changed as needed -> clone it[pix_to_show]
# -> display_pixmap[pix_to_show] -> convert it to bytes -> save as color_mask
# COLORS
# color_mask-> apply filter -> save filter numbers ->
# -> raw (flag as not new)-> only pix_to_show created -> display

class ImageEditor:
    last_custom_rot = 0
    last_brightness = 0
    last_gamma = 10
    last_blur = 1

    def __init__(self, scene):
        self.scene = scene

        self.color_mask_clean = None
        self.color_mask_active = None
        self.transformation_pixmap = QPixmap()

    # turn to property after finish
    def set_to_default(self):
        self.last_brightness = 0
        self.last_custom_rot = 0
        self.last_gamma = 10

    def set_transform_pix(self, pix):
        self.transformation_pixmap = pix

    def set_color_mask(self, image):
        self.color_mask_clean = image

    def do_rotation(self, degree=0, post_trans_pix=None):
        if post_trans_pix:
            rotated = post_trans_pix.transformed(QTransform().rotate(degree+self.last_custom_rot), mode=Qt.SmoothTransformation)
        else:
            rotated = self.transformation_pixmap.transformed(QTransform().rotate(degree))
        return rotated

    def do_custom_rotation(self, degree):
        self.last_custom_rot = degree
        return self.do_rotation(degree)

    def do_flip(self, pack):
        x, y = pack
        flipped = self.transformation_pixmap.transformed(QTransform().scale(x, y))
        return flipped

    def resize(self, size):
        w, h = size
        scaled = self.transformation_pixmap.scaled(w, h)
        return scaled

    def is_mask_none(self):
        if self.color_mask_clean is None:
            return True
        return False

    def change_brightness(self, value):
        if not self.is_mask_none():
            hsv = cv2.cvtColor(self.color_mask_clean, cv2.COLOR_BGR2HSV)
            self.last_brightness = value
            h, s, v = cv2.split(hsv)
            lim = 255 - value
            v[v > lim] = 255
            v[v <= lim] += value
            final_hsv = cv2.merge((h, s, v))
            img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
            self.set_image_to_canvas(img)

    def set_image_to_canvas(self, img):
        pixmap = self.scene.convert_raw_to_pixmap(img)
        self.scene.map_pixmap_to_scene(pixmap=pixmap)

    def change_gamma(self, value):
        if not self.is_mask_none():
            self.last_gamma = value
            gamma = 1/(value / 10)

            table = np.array([((i / 255.0) ** gamma) * 255
                              for i in np.arange(0, 256)]).astype("uint8")
            image = cv2.LUT(self.color_mask_clean, table)
            self.set_image_to_canvas(image)

    def turn_to_greyscale(self):
        if not self.is_mask_none():
            gray = cv2.cvtColor(self.color_mask_clean, cv2.COLOR_BGR2GRAY)
            self.set_image_to_canvas(gray)

    def add_blur(self, val):
        if not self.is_mask_none():
            if val < 1:
                val = 1
            self.last_blur = val
            blur = cv2.blur(self.color_mask_clean, (val, val))
            self.set_image_to_canvas(blur)

    def restore_values(self):
        self.change_brightness(self.last_brightness)
        self.change_gamma(self.last_gamma)
        self.add_blur(self.last_blur)