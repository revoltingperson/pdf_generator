from python_files.controller.main_controller import *
from PIL import Image
from PyQt5.QtCore import Qt, QEvent, QSize, QRectF, QMarginsF, QMargins, QObject
from PyQt5.QtGui import QPixmap, QMouseEvent, QTransform, QPainter, QImage, QBrush, QColor, QPen, QPagedPaintDevice, \
    QKeyEvent
from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog, QPrintDialog

from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QSizePolicy, QGraphicsSceneMouseEvent, QGraphicsRectItem, \
    QPushButton, QGraphicsItem

from python_files.controller.text_in_image_controller import ClickableItem


class MainCanvas(QGraphicsScene):
    XY_ZERO = 0

    def __init__(self, graphics_view: QGraphicsView):
        super().__init__()
        self.text_label = None
        self.zoom_control = None
        self.view_widget = graphics_view
        self.view_widget.setScene(self)
        self.image = QPixmap()
        self.view_widget.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
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

    def load_image_to_canvas(self, image):
        pix_mapped = QPixmap(image)
        self.image = pix_mapped
        if not self.image.isNull():
            self.clear()

        width, height = pix_mapped.width(), pix_mapped.height()
        # add border to working area
        pen = QPen(Qt.SolidLine)
        pen.setWidth(1)
        pen.setColor(Qt.white)
        brush = QBrush(Qt.NoBrush)
        rect_item = QRectF(self.XY_ZERO-1, self.XY_ZERO-1, width+2, height+2)

        self.addRect(rect_item, pen, brush)
        self.addPixmap(pix_mapped)
        self.setSceneRect(self.XY_ZERO, self.XY_ZERO, width, height)
        print(f'{self.sceneRect()}:SCENE SIZE \n{self.view_widget.geometry()}: VIEW SIZE')



