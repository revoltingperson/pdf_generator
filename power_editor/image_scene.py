import typing

import cv2

from text_in_image_controller import TextItem, ClickableText

from PyQt5.QtCore import Qt, QRectF, QByteArray, QBuffer, QIODevice
from PyQt5.QtGui import QPixmap, QPainter, QImage, QBrush, QColor, QPen, QKeyEvent
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsSceneMouseEvent, QGraphicsProxyWidget, \
    QGraphicsRectItem, QWidget, QGraphicsPixmapItem
from serializer.serializer import Serializable

debug = True


class MainCanvas(QGraphicsScene, Serializable):
    text_item: TextItem
    XY_ZERO = 0

    def __init__(self, graphics_view: QGraphicsView):
        super().__init__()

        self.view_widget = graphics_view
        self.image = None
        self.view_widget.setScene(self)
        self.view_widget.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.focusItemChanged.connect(lambda item: self.do_selection_on_focus(item))
        self.shift_pressed = False
        self.__set_placeholder_rectangle()

    def __set_placeholder_rectangle(self):
        width = 400
        height = 300
        rgb_white = 255
        pen = QPen(Qt.SolidLine)
        brush = QBrush(QColor(rgb_white, rgb_white, rgb_white, rgb_white))
        rect_item = QRectF(self.XY_ZERO, self.XY_ZERO, width, height)
        self.setSceneRect(self.XY_ZERO, self.XY_ZERO, width, height)
        self.addRect(rect_item, pen, brush)

    def save_image_from_canvas(self, where):
        image = QImage(int(self.width()), int(self.height()), QImage.Format_RGB32)
        painter = QPainter(image)
        self.render(painter)
        painter.end()
        image.save(where)

    def load_image(self, image, new_image: bool = True):
        self.image = image

        self.remove_pixmap_policy(new_image)
        frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width = frame.shape[0], frame.shape[1]

        q_image = QImage(frame, width, height, frame.strides[0], QImage.Format_RGB888)

        border = BeautifulBorder(width, height)
        self.addPixmap(QPixmap().fromImage(q_image))
        self.setSceneRect(self.XY_ZERO, self.XY_ZERO, width, height)
        self.addItem(border)

        # if debug:
        #     print(f'{self.sceneRect()}:SCENE SIZE \n{self.view_widget.geometry()}: VIEW SIZE')

    def remove_pixmap_policy(self, new_image):
        if self.find_pixmap():
            if new_image:
                self.clear()
            else:
                self.remove_old_instance()

    def remove_old_instance(self):
        for item in self.items():
            if isinstance(item, QGraphicsPixmapItem) or isinstance(item, BeautifulBorder):
                self.removeItem(item)

    def connect_text_items(self, text_obj):
        self.text_item = text_obj

    def mousePressEvent(self, event: "QGraphicsSceneMouseEvent") -> None:
        self.text_item.operate_text_editor(event)
        if debug:
            print(f'selected items: {self.selectedItems()}')
            print(f'all items: {self.items()}')
        super(MainCanvas, self).mousePressEvent(event)

    def do_selection_on_focus(self, item):
        if isinstance(item, QGraphicsProxyWidget):
            if not self.shift_pressed:
                [item.setSelected(False) for item in self.selectedItems()]
            item.parentItem().setSelected(True)

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Delete:
            [self.removeItem(item) for item in self.selectedItems()]
        if event.key() == Qt.Key_Shift:
            self.shift_pressed = True
        super(MainCanvas, self).keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Shift:
            self.shift_pressed = False

    def find_pixmap(self) -> QPixmap:
        for item in self.items():
            if isinstance(item, QGraphicsPixmapItem):
                return item.pixmap()

    def find_text_items_on_scene(self) -> list:
        items = []
        for item in self.items():
            print(item.__class__)
            if isinstance(item, ClickableText):
                items.append(item)
        return items

    def convert_to_bytes(self) -> QByteArray:
        pixmap = self.find_pixmap()
        bites = QByteArray()
        buff = QBuffer(bites)
        buff.open(QIODevice.WriteOnly)
        pixmap.save(buff, 'PNG')
        return bites

    def serialize(self):
        pixmap = self.convert_to_bytes()
        texts = self.find_text_items_on_scene()
        return {
            'pixmap': str(pixmap, 'ISO-8859-1'),
            'clickable_text': [item.serialize() for item in texts]
        }

    def deserialize(self, data):
        from_json = data['pixmap']
        bites = bytes(from_json, 'ISO-8859-1')
        ba = QByteArray.fromRawData(bites)
        pixmap = QPixmap()
        pixmap.loadFromData(ba, 'PNG')
        # self.map_pixmap(pixmap)
        for item in data['clickable_text']:
            self.text_item.load_from_json(item)



class BeautifulBorder(QGraphicsRectItem):
    def __init__(self, width, height):
        super().__init__()
        # +2 -1 added to make border appear outside of rendering area
        self.rect_item = QRectF(-1, -1, width + 2, height + 2)

    def paint(
            self,
            painter: QPainter,
            option: "QStyleOptionGraphicsItem",
            widget: typing.Optional[QWidget] = ...,
    ) -> None:
        pen = QPen(Qt.SolidLine)
        brush = QBrush(Qt.NoBrush)
        pen.setWidth(1)
        pen.setColor(Qt.white)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRect(self.rect_item)
