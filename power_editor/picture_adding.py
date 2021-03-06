from PyQt5.QtCore import QPointF, QRectF
from PyQt5.QtGui import QPainter, QPixmap

from power_editor.checked_bundle import CheckedButtons
from power_editor.text_in_image_control import ClickableText as Clickable, CommunicateChange


class PictureItem(CheckedButtons):
    def __init__(self, interface, scene):
        super().__init__()
        self.interface = interface
        self.scene = scene
        self.button = interface.impose_image

    def create_on_click(self):
        pix = self.interface.controller.help_open_file(clickable_p=True)
        if pix:
            item = ClickableImage(QPointF(0.0, 0.0), pixmap=pix)
            item.communicate.position_new.connect(self.scene.memorize_change_on_scene)
            self.disable()
            self.scene.addItem(item)
            item.setSelected(True)
            self.scene.memorize_change_on_scene()

    def find_clickable_images(self):
        all_pics = []
        for item in self.scene.items():
            if item.__class__ == ClickableImage:
                all_pics.append(item)
        return all_pics

    def turn_items_to_pixmap(self):
        images = self.find_clickable_images()
        pixes = []
        for picture in images:
            picture_to_save = picture.pix.copy()
            pixes.append({'data': picture.serialize(), 'pixmap': picture_to_save})
        print([item for item in pixes])
        return pixes

    def call_json_loader(self, data, picture):
        wid, height = data['width'], data['height']
        x, y = data['position'][0], data['position'][1]
        position = QPointF(x, y)
        item = ClickableImage(position, rect=QRectF(0, 0, wid, height), pixmap=picture)
        item.communicate.position_new.connect(self.scene.memorize_change_on_scene)
        self.scene.addItem(item)


class ClickableImage(Clickable):
    width_inner = 150
    height_inner = 150

    def __init__(self, position, rect=QRectF(0, 0, width_inner, height_inner), pixmap=None):
        super().__init__(position, rect, extend_paint=True)
        self.pix: QPixmap = pixmap
        self.communicate = CommunicateChange()

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

    def communicate_new_position(self):
        self.communicate.position_new.emit()




