from PyQt5.QtCore import QPoint, QPointF
from PyQt5.QtGui import QPainter, QPixmap

from checked_bundle import CheckedButtons
from text_in_image_control import ClickableText


class PictureItem(CheckedButtons):
    def __init__(self, interface, scene):
        super().__init__()
        self.interface = interface
        self.scene = scene
        self.button = interface.impose_image

    def create_item(self):
        pix = self.interface.controller.help_open_file(clickable_p=True)
        if pix:
            item = ClickableImage(QPointF(0.0, 0.0), pix)
            self.disable()
            self.scene.addItem(item)
            item.setSelected(True)


class ClickableImage(ClickableText):
    def __init__(self, position, pixmap):
        super().__init__(position, extend_paint=True)
        self.pix: QPixmap = pixmap

    def extend_paint_action(self, painter: QPainter):
        new = self.pix.scaled(int(self.rect().width()), int(self.rect().height()))
        painter.drawPixmap(self.rect(), new, self.rect())

    def initialize_input(self):
        pass




