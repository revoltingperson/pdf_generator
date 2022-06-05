import typing
import cv2
from checked_bundle import Collector, CheckedButtons
from crop_control import *
from excel_control import ExcelControl
from image_editor import ImageEditor
from picture_adding import PictureItem
from resize_control import Resizer
from rotation_control import Rotator
from toplevel.brightness import BrightnessWidget
from zoom_control import ZoomEnableDisable
from text_in_image_control import TextItem, ClickableText
import numpy as np
from PyQt5.QtCore import Qt, QRectF, QByteArray, QBuffer, QIODevice, QRect
from PyQt5.QtGui import QPixmap, QPainter, QImage, QBrush, QColor, QPen, QKeyEvent, QTransform
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsSceneMouseEvent, QGraphicsProxyWidget, \
    QGraphicsRectItem, QWidget, QGraphicsPixmapItem
from serializer.serializer import Serializable

debug = True


class MainCanvas(QGraphicsScene, Serializable):
    text_item: TextItem
    cropper: Cropper
    excel: ExcelControl
    resizer: Resizer
    rotator: Rotator
    zoom_control: ZoomEnableDisable
    XY_ZERO = 0

    def __init__(self, interface, graphics_view: QGraphicsView):
        super().__init__()
        self.interface = interface
        self.view_widget = graphics_view
        self.color_image = None
        self.shift_pressed = False

        self.editor = ImageEditor(self)
        self.brightness = BrightnessWidget(self.editor)
        self.view_widget.setScene(self)
        self.view_widget.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.focusItemChanged.connect(lambda item: self.do_selection_on_focus(item))
        self.__set_placeholder_rectangle()
        self.__build_scene_control_objects()

    def __build_scene_control_objects(self):
        self.zoom_control = ZoomEnableDisable(self.interface, self.view_widget)
        self.text_item = TextItem(self.interface, self)
        self.rotator = Rotator(self.interface, self)
        self.resizer = Resizer(self.interface, self)
        self.cropper = Cropper(self.interface, self)
        self.clickable_image = PictureItem(self.interface, self)
        self.excel = ExcelControl(self.interface, self)

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

    def convert_raw_to_pixmap(self, image, new_image: bool = False, byte_mode=False):
        if new_image:
            self.color_image = image
        self.remove_pixmap_policy(new_image)

        if byte_mode:
            read_from_bytes = image.data()
            img = np.frombuffer(read_from_bytes, dtype='uint8')
            frame = cv2.imdecode(img, cv2.IMREAD_COLOR)
            self.color_image = frame
            image = frame

        frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width = frame.shape[0], frame.shape[1]
        print(frame.strides)
        q_image = QImage(frame, width, height, frame.strides[0], QImage.Format_RGB888)
        pixmap = QPixmap().fromImage(q_image)
        if new_image:
            self.editor.base_pixmap = pixmap
        return pixmap

    def convert_qimage_clean(self, image):
        """ qimage does not destroy the alpha channel, that is why I am not
            using the convert_raw_to_pixmap func
        """
        q_image = QImage(image)
        pix = QPixmap().fromImage(q_image)
        return pix

    def transform_to_rules(self, pixmap: QPixmap, rules: dict):
        key, val = list(rules.items())[0]
        self.editor.set_pixmap(pixmap)
        options = {'rotation': self.editor.do_rotation,
                   'custom_rotation': self.editor.do_custom_rotation,
                   'flip': self.editor.do_flip,
                   'resize': self.editor.resize
                   }
        chosen = options.get(key)
        return chosen(val)

    def return_scene_item_as_pixmap(self) -> QPixmap:
        for item in self.items():
            if isinstance(item, QGraphicsPixmapItem):
                return item.pixmap()

    def map_pixmap_to_scene(self, rules, pixmap=None):
        if pixmap is None:
            item = self.return_scene_item_as_pixmap()
            if item:
                pixmap = item

        if rules is not None:
            pixmap = self.transform_to_rules(pixmap, rules)

        self.remove_pixmap_policy(new_image=False)
        self.build_border(pixmap.height(), pixmap.width())
        self.addPixmap(pixmap)
        self.setSceneRect(self.XY_ZERO, self.XY_ZERO, pixmap.width(), pixmap.height())
        if debug: print(f"pixmap: {pixmap.size()}")
        if debug: print(f'scene rect: {self.sceneRect()}')

    def build_border(self, height, width):
        border = BeautifulBorder(width, height)
        self.addItem(border)

    def remove_pixmap_policy(self, new_image):
        if new_image:
            self.clear()
        else:
            self.remove_old_pixmap_instance()

    def remove_old_pixmap_instance(self):
        for item in self.items():
            if isinstance(item, QGraphicsPixmapItem) or isinstance(item, BeautifulBorder):
                self.removeItem(item)

    def mousePressEvent(self, event: "QGraphicsSceneMouseEvent") -> None:
        self.text_item.create_on_click(event)
        self.cropper.create_on_click(event)
        self.excel.create_on_click(event)

        if debug:
            print(f'selected items: {self.selectedItems()}')
            print(f'all items: {self.items()}')

        super(MainCanvas, self).mousePressEvent(event)

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Delete:
            [self.removeItem(item) for item in self.selectedItems()]
        if event.key() == Qt.Key_Shift:
            self.shift_pressed = True
        super(MainCanvas, self).keyPressEvent(event)

    def do_selection_on_focus(self, item):
        if debug: print(f'selection changed to {item}')
        if isinstance(item, QGraphicsProxyWidget):
            if not self.shift_pressed:
                [item.setSelected(False) for item in self.selectedItems()]
            item.parentItem().setSelected(True)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Shift:
            self.shift_pressed = False

    def find_text_items_on_scene(self) -> list:
        items = []
        for item in self.items():
            if isinstance(item, ClickableText):
                items.append(item)
        return items

    def convert_to_bytes(self, pixmap) -> QByteArray:
        bites = QByteArray()
        buff = QBuffer(bites)
        buff.open(QIODevice.WriteOnly)
        pixmap.save(buff, 'PNG')
        return bites

    def serialize(self):
        pixmap = self.return_scene_item_as_pixmap()
        byte_pixmap = self.convert_to_bytes(pixmap)
        texts = self.find_text_items_on_scene()
        return {
            'pixmap': str(byte_pixmap, 'ISO-8859-1'),
            'clickable_text': [item.serialize() for item in texts]
        }

    def deserialize(self, data):
        from_json = data['pixmap']
        bites = bytes(from_json, 'ISO-8859-1')
        ba = QByteArray.fromRawData(bites)
        pixmap = QPixmap()
        pixmap.loadFromData(ba, 'PNG')
        self.map_pixmap_to_scene(rules=None, pixmap=pixmap)
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
