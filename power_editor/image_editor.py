from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTransform


class ImageEditor:
    def __init__(self, image):
        self.image = image
        self.edited = image
        self.height, self.width = self.image.shape[:2]

    def do_rotation(self, degree):
        pass
    def do_flip(self, x, y):
        pass
