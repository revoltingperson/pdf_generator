from PyQt5.QtCore import QPoint, QPointF, QRectF
from PyQt5.QtGui import QPainter, QPixmap

from checked_bundle import CheckedButtons
from text_in_image_control import ClickableText as Clickable


class PictureItem(CheckedButtons):
    def __init__(self, interface, scene):
        super().__init__()
        self.interface = interface
        self.scene = scene
        self.button = interface.impose_image

    def create_item(self):
        pix = self.interface.controller.help_open_file(clickable_p=True)
        if pix:
            item = ClickableImage(QPointF(0.0, 0.0), pixmap=pix)
            self.disable()
            self.scene.addItem(item)
            item.setSelected(True)

    def find_clickable_images(self):
        all_pics = []
        for item in self.scene.items():
            if item.__class__ == ClickableImage:
                all_pics.append(item)
        return all_pics

    def call_json_loader(self, data, picture):
        wid, height = data['width'], data['height']
        x, y = data['position'][0], data['position'][1]
        position = QPointF(x, y)
        item = ClickableImage(position, rect=QRectF(0, 0, wid, height), pixmap=picture)
        self.scene.addItem(item)


class ClickableImage(Clickable):
    width_inner = 150
    height_inner = 150

    def __init__(self, position, rect=QRectF(0, 0, width_inner, height_inner), pixmap=None):
        super().__init__(position, rect, extend_paint=True)
        self.pix: QPixmap = pixmap

    def extend_paint_action(self, painter: QPainter):
        new = self.pix.scaled(int(self.rect().width()), int(self.rect().height()))
        painter.drawPixmap(self.rect(), new, self.rect())

    def serialize(self):
        return {
            'id': self.id,
            'width': self.rect().width(),
            'height': self.rect().height(),
            'position': (self.pos().x(), self.pos().y())
                }

    def initialize_input(self):
        pass




