from PyQt5.QtCore import QRectF, Qt, QPointF, pyqtSignal, pyqtSlot, QLine, QLineF, QObject, QRect
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtWidgets import QAction, QGraphicsRectItem, QGraphicsItem, QGraphicsObject, QPushButton, \
    QGraphicsProxyWidget, QWidget, QVBoxLayout, QGraphicsSceneMouseEvent

from checked_bundle import CheckedButtons
from text_in_image_control import Resizer as CropResizer


class CropperItem(QGraphicsRectItem):
    width_inner = 100
    height_inner = 100
    lines_number = 3

    def __init__(self, cropper, position, rect=QRectF(0, 0, width_inner, height_inner)):

        super().__init__(rect)
        self._initialize_flags()
        self.setPos(position)
        self.setZValue(1)
        self.cropper = cropper
        self.main_proxy = CropProxy(self)
        self.resizer = CropResizer(parent=self)
        self.main_proxy.crop_confirm.clicked.connect(self.initiate_crop)

        resizer_width = self.resizer.rect.width() / 2
        resizer_offset = QPointF(resizer_width, resizer_width)
        self.resizer.setPos(self.rect().bottomRight() - resizer_offset)
        self.resizer.resizeSignal[QPointF].connect(lambda change: self.resize(change))

    def _initialize_flags(self):
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

    def initiate_crop(self):
        self.cropper.crop_image_on_signal()

    def paint(self, painter, option, widget=None) -> None:
        if self.isSelected() or self.hasFocus():
            pen = QPen()
            pen.setWidth(1)
            pen.setColor(Qt.darkGray)
            painter.setBrush(Qt.NoBrush)
            painter.setPen(pen)
            vertical, horizontal = [], []
            for line in range(self.lines_number):
                factor = line / self.lines_number
                line = QLineF(self.rect().width() * factor,
                              self.rect().y(),
                              self.rect().width() * factor,
                              self.rect().height())
                vertical.append(QLineF(line))
            for line in range(self.lines_number):
                factor = line / self.lines_number
                line = QLineF(self.rect().x(),
                              self.rect().height() * factor,
                              self.rect().width(),
                              self.rect().height() * factor)
                horizontal.append(QLineF(line))
            painter.drawLines(*vertical)
            painter.drawLines(*horizontal)
            pen2 = QPen()
            pen2.setColor(Qt.black)
            painter.setPen(pen2)
            painter.drawRect(self.rect())

            self.main_proxy.draw_lines(horizontal, vertical, self.rect())
        elif self.resizer.isSelected():
            self.setFocus()

        else:
            self.cropper.remove_signal()

    @pyqtSlot()
    def resize(self, change):
        self.setRect(self.rect().adjusted(0, 0, change.x(), change.y()))
        self.prepareGeometryChange()
        self.update()


class Cropper(CheckedButtons):
    cropper_item: CropperItem

    def __init__(self, interface, scene):
        super().__init__()
        self.scene = scene
        self.button = interface.crop

    def create_on_click(self, event: QGraphicsSceneMouseEvent):
        position = event.scenePos()
        if self.button.isChecked():
            self.cropper_item = CropperItem(self, position)
            self.scene.addItem(self.cropper_item)
            self.cropper_item.setSelected(True)
            self.disable()

    def remove_signal(self):
        for item in self.scene.items():
            if item.__class__ in [CropResizer, CropperItem, CropProxy]:
                self.scene.removeItem(item)

    def crop_image_on_signal(self):
        item = self.scene.return_scene_item_as_pixmap()
        if item:
            area_to_crop = QRect(int(self.cropper_item.scenePos().x()),
                                 int(self.cropper_item.scenePos().y()),
                                 int(self.cropper_item.rect().width()),
                                 int(self.cropper_item.rect().height())
                                 )
            cropped_image_to_load = item.copy(area_to_crop)
            self.scene.map_pixmap_to_scene(pixmap=cropped_image_to_load, cropped=True)
            self.cropper_item.setSelected(False)


class CropProxy(QGraphicsProxyWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.proxy = QWidget()
        style = """
            background-color: transparent;
        """
        self.proxy.setStyleSheet(style)
        layout = QVBoxLayout()
        self.proxy.setLayout(layout)
        self.crop_confirm = QPushButton()

        layout.addWidget(self.crop_confirm)
        self.crop_confirm.setText('Crop')
        self.crop_confirm.setStyleSheet('background-color: #dff0fe')

        self.setWidget(self.proxy)

    def draw_lines(self, horizontal, vertical, rect):
        self.proxy.setGeometry(int(rect.width() // 2) - 20, int(rect.height() // 3), 20, 20)

        line, line1, line2 = vertical
        lineh, lineh1, lineh2 = horizontal
        """resizing of the button when borders change (a bit messy, but I don't feel like cleaning it up)"""
        if line2.x1() - line1.x1() <= 40:
            self.proxy.setGeometry(int(line1.x1()), int(rect.height() // 3), 20, 20)
            self.crop_confirm.setGeometry(0, 0, int(line2.x1() - line1.x1()), 20)
        if lineh2.y1() - lineh1.y1() <= 20:
            self.proxy.setGeometry(int(rect.width() // 2) - 20, int(rect.height() // 3), 20, 20)
            self.crop_confirm.setGeometry(0, 0, 40, int(lineh2.y1() - lineh1.y1()))
        if lineh2.y1() - lineh1.y1() <= 20 and line2.x1() - line1.x1() <= 40:
            self.proxy.setGeometry(int(line1.x1()), int(rect.height() // 3), 20, 20)
            self.crop_confirm.setGeometry(0, 0, int(line2.x1() - line1.x1()), int(lineh2.y1() - lineh1.y1()))
