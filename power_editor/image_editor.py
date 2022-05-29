from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTransform


class ImageEditor:
    def __init__(self, image):
        self.image = image
        self.edited = image

    def do_rotation(self, degree):
        rotated = self.image.transformed(QTransform().rotate(degree),
                                         mode=Qt.SmoothTransformation)
        self.edited = rotated

    def do_flip(self, x, y):
        flipped = self.image.transformed(QTransform().scale(x, y),
                                         mode=Qt.SmoothTransformation)
        self.edited = flipped
