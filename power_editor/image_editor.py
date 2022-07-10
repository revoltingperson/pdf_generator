import numpy as np
from PyQt5.QtGui import QTransform, QPixmap
import cv2


# separate color mask from pixmapy


class ImageEditor:
    last_brightness = 0
    last_gamma = 10
    last_blur = 1
    last_resize = None
    mask_resized = None
    last_custom_rotation = 0
    last_angle = 0
    last_flip = None
    grey = False

    def __init__(self, scene):
        self.id = 0
        self.scene = scene

        self.color_mask = None
        self.base_pixmap = QPixmap()
        self.worker_pixmap = QPixmap()
        self.height = 0
        self.width = 0
        self.memory_mode: bool = True

    # turn to property after finish
    def set_to_default(self):
        self.last_brightness = 0
        self.last_gamma = 10
        self.last_blur = 1
        self.last_resize = None
        self.last_custom_rotation = 0
        self.last_angle = 0
        self.last_flip = None
        self.grey = False

    def set_transform_pix(self, pix):
        self.base_pixmap = pix

    def set_color_mask(self, image):
        self.color_mask = image

    def write_value_to_angle(self, value):
        if value % 90 == 0:
            self.last_angle += value
        else:
            self.last_custom_rotation = value

    def write_value_to_flip(self, value):
        if self.last_flip is None:
            self.last_flip = value
        else:
            self.last_flip = None

    def write_value_to_resize(self, value):
        self.last_resize = value

    def last_bright_val(self, value):
        self.last_brightness = value
        self.set_all_filters()

    def set_last_gamma(self, value):
        self.last_gamma = value
        self.set_all_filters()

    def set_last_blur(self, value):
        self.last_blur = value
        self.set_all_filters()

    def restore_transformation(self):
        self.worker_pixmap = self.base_pixmap.copy()
        self.resize(self.last_resize)
        self.do_rotation(self.last_angle)
        self.do_flip(self.last_flip)
        return self.worker_pixmap

    def do_rotation(self, degree):
        rotated = self.worker_pixmap.transformed(QTransform().rotate(degree + self.last_custom_rotation))
        self.worker_pixmap = rotated

    def do_flip(self, pack):
        if pack is not None:
            x, y = pack
            flipped = self.worker_pixmap.transformed(QTransform().scale(x, y))
            self.worker_pixmap = flipped

    def resize(self, size):
        if size is not None:
            w, h = size
            scaled = self.worker_pixmap.scaled(w, h)
            self.worker_pixmap = scaled
            self.mask_resized = size

    def is_mask_none(self):
        if self.color_mask is None:
            return True
        return False

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

    def output_image_as_pixmap(self, img):
        if not self.is_mask_none():
            self.scene.merge_pixmap_and_cv2(img)

    def change_gamma(self, in_img, value):
        if not self.is_mask_none():
            gamma = 1 / (value / 10)

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
        self.set_all_filters(force_memory_mode=True)

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

    def set_all_filters(self, force_memory_mode=False):
        self.memory_mode = force_memory_mode
        img = self.change_brightness(self.color_mask, self.last_brightness)
        gam_img = self.change_gamma(img, self.last_gamma)
        grey = self.apply_greyscale(gam_img)
        out = self.add_blur(grey, self.last_blur)
        self.output_image_as_pixmap(out)

    def crop_color_mask_as_pixmap(self, area):
        cropped_color_mask = self.color_mask[area.y():area.y()+area.height(),
                                             area.x():area.x()+area.width()
                                             ]
        self.color_mask = cropped_color_mask
        return cropped_color_mask

    def create_stamp_on_slider_release(self):
        self.scene.memorize_change_on_scene()
