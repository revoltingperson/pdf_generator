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

    def __init__(self, scene):
        self.height = None
        self.width = None
        self.scene = scene
        self.edited = None

    def get_image(self):
        self.height, self.width = self.scene.reserved_image.shape[:2]

    def do_rotation(self, degree):
        rot_point = (self.width // 2, self.height // 2)
        rot_matrix = cv2.getRotationMatrix2D(rot_point, degree + self.last_rotation, 1.0)
        self.last_rotation += degree

        dimensions = (self.width, self.height)
        rotated = cv2.warpAffine(self.scene.reserved_image, rot_matrix, dimensions)
        self.scene.load_image(rotated, new_image=False)

    def do_flip(self, x):
        # flip clean image and perform last rotation and display it
        only_last_rotation = 0
        flip = cv2.flip(self.scene.reserved_image, x)
        self.scene.reserved_image = flip
        self.do_rotation(only_last_rotation)

    def resize(self, size):
        wid, ht = size[0], size[1]
        resized = imutils.resize(self.scene.reserved_image, width=wid, height=ht)
        self.scene.load_image(resized, new_image=False)

    def brightness_options(self, parent):
        BrightnessWidget(parent, self)

    def changed_brightness(self, value):
        hsv = cv2.cvtColor(self.scene.reserved_image, cv2.COLOR_BGR2HSV)
        self.last_brightness = value
        h, s, v = cv2.split(hsv)
        print(value)
        lim = 255 - value
        v[v > lim] = 255
        v[v <= lim] += value
        final_hsv = cv2.merge((h, s, v))
        img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
        # self.scene.reserved_image = img

        self.scene.load_image(img, new_image=False)

    def gamma_changed(self, value):
        value = value / 10

