import typing

from python_files.controller.main_controller import *
from PyQt5.QtCore import Qt, QRectF, QEvent
from PyQt5.QtGui import QPixmap, QPainter, QImage, QBrush, QColor, QPen, QMouseEvent, QKeyEvent

from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsSceneMouseEvent, QGraphicsProxyWidget, \
    QGraphicsRectItem

debug = True


class MainCanvas(QGraphicsScene):
    from python_files.controller.text_in_image_controller import TextItem
    text_item: TextItem
    XY_ZERO = 0

    def __init__(self, graphics_view: QGraphicsView):
        super().__init__()
        self.view_widget = graphics_view
        self.view_widget.setScene(self)
        self.image = QPixmap()
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
        # image = QImage(int(self.width()), int(self.height()), QImage.Format_Grayscale8)
        painter = QPainter(image)
        self.render(painter)
        painter.end()
        image.save(where)

    def load_image_to_canvas(self, image):
        pix_mapped = QPixmap(image)
        self.image = pix_mapped
        self.map_pixmap(pix_mapped)

    def map_pixmap(self, pix_mapped, new_image=True):
        if not self.image.isNull():
            if new_image:
                self.clear()
            else:
                self.remove_old_instance()

        width, height = pix_mapped.width(), pix_mapped.height()

        border = BeautifulBorder(width, height)
        self.addPixmap(pix_mapped)
        self.image = pix_mapped
        self.setSceneRect(self.XY_ZERO, self.XY_ZERO, width, height)
        self.addItem(border)

        if debug:
            print(f'{self.sceneRect()}:SCENE SIZE \n{self.view_widget.geometry()}: VIEW SIZE')

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
        if event.key() == Qt.Key_Delete: [self.removeItem(item) for item in self.selectedItems()]
        if event.key() == Qt.Key_Shift:
            self.shift_pressed = True
        super(MainCanvas, self).keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Shift:
            self.shift_pressed = False


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


