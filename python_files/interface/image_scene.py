from PIL import Image
from PyQt5.QtCore import Qt, QEvent, QSize, QRectF, QMarginsF, QMargins, QObject
from PyQt5.QtGui import QPixmap, QMouseEvent, QTransform, QPainter, QImage, QBrush, QColor, QPen, QPagedPaintDevice, \
    QKeyEvent
from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog, QPrintDialog
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QSizePolicy, QGraphicsSceneMouseEvent, QGraphicsRectItem

class MainCanvas(QGraphicsScene):
    XY_ZERO = 0

    def __init__(self, graphics_view: QGraphicsView):
        super().__init__()
        self.text_label = None
        self.zoom_control = None
        self.view_widget = graphics_view
        self.view_widget.setScene(self)
        self.image = QPixmap()
        self.installEventFilter(self)
        self.__set_placeholder_rectangle()

    def __set_placeholder_rectangle(self):
        width = 400
        height = 300
        rgb_white = 255
        pen = QPen(Qt.SolidLine)
        brush = QBrush(QColor(rgb_white, rgb_white, rgb_white, rgb_white))
        rect_item = QRectF(self.XY_ZERO, self.XY_ZERO, width, height)
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

        self.addPixmap(pix_mapped)
        self.setSceneRect(self.XY_ZERO, self.XY_ZERO, pix_mapped.width(), pix_mapped.height())
        print(f'{self.sceneRect()}:SCENE SIZE \n{self.view_widget.geometry()}: VIEW SIZE')

    def connect_zoom_control(self, zoom_obj):
        self.zoom_control = zoom_obj

    def connect_text_labeler(self, text_label_obj):
        self.text_label = text_label_obj

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.zoom_control.operate_zoom(event)
        self.text_label.operate_text_editor(event)

        print(self.sceneRect())
        print(event.scenePos().x(), event.scenePos().y())


    def keyPressEvent(self, event: QKeyEvent) -> None:
        self.zoom_control.operate_zoom(event)

