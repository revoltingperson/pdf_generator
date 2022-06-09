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
    grey = False

    def __init__(self, scene):
        self.scene = scene

        self.color_mask = None
        self.transformation_pixmap = QPixmap()

    # turn to property after finish
    def set_to_default(self):
        self.last_brightness = 0
        self.last_custom_rot = 0
        self.last_gamma = 10

    def set_transform_pix(self, pix):
        self.transformation_pixmap = pix

    def set_color_mask(self, image):
        self.color_mask = image

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
        if self.color_mask is None:
            return True
        return False

    def last_bright_val(self, value):
        self.last_brightness = value

    def set_last_gamma(self, value):
        self.last_gamma = value

    def set_last_blur(self, value):
        self.last_blur = value

    def change_brightness(self, in_img, value):
        if not self.is_mask_none():
            hsv = cv2.cvtColor(in_img, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsv)
            lim = 255 - value
            v[v > lim] = 255
            v[v <= lim] += value
            final_hsv = cv2.merge((h, s, v))
            img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
            return img

    def set_image_to_canvas(self, img):
        pixmap = self.scene.convert_raw_to_pixmap(img)
        self.scene.map_pixmap_to_scene(pixmap)

    def change_gamma(self, in_img, value):
        if not self.is_mask_none():
            gamma = 1/(value / 10)

            table = np.array([((i / 255.0) ** gamma) * 255
                              for i in np.arange(0, 256)]).astype("uint8")
            image = cv2.LUT(in_img, table)
            return image

    def turn_to_greyscale(self):
        if not self.is_mask_none():
            if not self.grey:
                self.grey = True
            else:
                self.grey = False
        self.set_all_filters()

    def apply_greyscale(self, img):
        if self.grey:
            grey = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            return grey
        return img

    def add_blur(self, in_img, val):
        if not self.is_mask_none():
            if val < 1:
                val = 1
            blur = cv2.blur(in_img, (val, val))
            return blur

    def set_all_filters(self):
        img = self.change_brightness(self.color_mask, self.last_brightness)
        gam_img = self.change_gamma(img, self.last_gamma)
        grey = self.apply_greyscale(gam_img)
        out = self.add_blur(grey, self.last_blur)
        self.set_image_to_canvas(out)