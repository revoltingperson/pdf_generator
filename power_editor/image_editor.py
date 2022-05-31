import cv2
import imutils as imutils
from toplevel.brightness import BrightnessWidget

"""We operate with two images simultaneously: one for displaying, and one for storing the original size and rotation 
(done to preserve quality). if displayed image changes we store those changes in values and apply them to the 
original image when transformation is needed. """

class ImageEditor:
    last_rotation = 0
    last_flip = 0
    last_brightness = 0

    def __init__(self):
        self.height = None
        self.width = None
        self.parsed_image = None
        self.edited = None

    def parse_image(self, image):
        self.parsed_image = image
        self.height, self.width = self.parsed_image.shape[:2]

    def do_rotation(self, degree=0):
        # if value is zero we perform the rotation based on the old value
        rot_point = (self.width // 2, self.height // 2)
        rot_matrix = cv2.getRotationMatrix2D(rot_point, degree + self.last_rotation, 1.0)
        self.last_rotation += degree

        dimensions = (self.width, self.height)
        rotated = cv2.warpAffine(self.parsed_image, rot_matrix, dimensions)
        return rotated

    def do_flip(self, x):
        # flip clean image and perform last rotation and display it
        flip = cv2.flip(self.parsed_image, x)
        self.last_flip = x
        return flip

    def resize(self, size):
        wid, ht = size[0], size[1]
        resized = cv2.resize(self.parsed_image, size)
        return resized

    def brightness_options(self, parent):
        BrightnessWidget(parent, self)

    def changed_brightness(self, value):
        hsv = cv2.cvtColor(self.parsed_image, cv2.COLOR_BGR2HSV)
        self.last_brightness = value
        h, s, v = cv2.split(hsv)
        lim = 255 - value
        v[v > lim] = 255
        v[v <= lim] += value
        final_hsv = cv2.merge((h, s, v))
        img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)

        return img

    def gamma_changed(self, value):
        value = value / 10

