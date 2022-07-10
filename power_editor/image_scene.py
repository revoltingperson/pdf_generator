
import random
import typing
import numpy as np
from power_editor.crop_control import *
from power_editor.excel_control import ExcelControl
from power_editor.image_editor import ImageEditor
from power_editor.picture_adding import PictureItem, ClickableImage
from power_editor.scene_history_stack import HistoryStack, HistoryStamp
from power_editor.resize_control import Resizer
from power_editor.rotation_control import Rotator
from toplevel.visual_effects import BrightnessWidget
from power_editor.zoom_control import ZoomEnableDisable
from power_editor.text_in_image_control import TextItem, ClickableText, CommunicateChange
from power_editor.checked_bundle import Collector

from PyQt5.QtCore import Qt, QRectF, QByteArray, QBuffer, QIODevice
from PyQt5.QtGui import QPixmap, QPainter, QImage, QBrush, QColor, QPen, QKeyEvent
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsSceneMouseEvent, QGraphicsProxyWidget, \
    QGraphicsRectItem, QWidget, QGraphicsPixmapItem
from serializer.serializer import Serializable


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
        self.shift_pressed = False
        self.black_back = QRectF()

        self.editor = ImageEditor(self)
        self.history = HistoryStack()
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
        self.black_back = rect_item
        self.setSceneRect(self.XY_ZERO, self.XY_ZERO, width, height)
        self.addRect(rect_item, pen, brush)

    def save_image_from_canvas(self, where):
        image = QImage(int(self.width()), int(self.height()), QImage.Format_RGB32)
        painter = QPainter(image)
        self.render(painter)
        painter.end()
        image.save(where)

    def load_new_image(self, image):
        self.editor.set_color_mask(image)
        self.editor.set_to_default()
        self.history.clear_history()
        self.convert_cv2_to_main_pixmap(image, save_size=True)
        self.map_pixmap_to_scene(new_image=True, pixmap=self.editor.base_pixmap)

    def convert_cv2_to_main_pixmap(self, image, save_size=False):
        import cv2 as cv2
        frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width = frame.shape[0], frame.shape[1]
        if save_size:
            self.editor.height, self.editor.width = height, width

        q_image = QImage(frame, width, height, frame.strides[0], QImage.Format_RGB888)
        pixmap = QPixmap().fromImage(q_image)
        self.editor.set_transform_pix(pixmap)

    def convert_qimage_clean(self, image):
        """ qimage does not destroy the alpha channel, that is why I am not
            using the convert_raw_to_pixmap func
        """
        q_image = QImage(image)
        pix = QPixmap().fromImage(q_image)
        return pix

    def map_pixmap_to_scene(self, new_image, pixmap=None, cropped=False):
        pixmap_to_show = pixmap
        if cropped and self.editor.base_pixmap.isNull():
            return

        self.remove_pixmap_policy(new_image)
        self.build_border(pixmap_to_show.height(), pixmap_to_show.width())
        self.addPixmap(pixmap_to_show)
        scene_rect = QRectF(self.XY_ZERO, self.XY_ZERO, pixmap_to_show.width(), pixmap_to_show.height())
        self.black_back = scene_rect
        self.setSceneRect(scene_rect)
        if self.editor.memory_mode:
            self.memorize_change_on_scene()
        self.editor.memory_mode = True

    def add_transformation_data(self, rules: dict):
        key, val = list(rules.items())[0]

        options = {'rotation': self.editor.write_value_to_angle,
                   'flip': self.editor.write_value_to_flip,
                   'resize': self.editor.write_value_to_resize,
                   }

        chosen = options.get(key)
        # noinspection PyArgumentList
        chosen(val)

    def send_transformation(self, rules):
        self.add_transformation_data(rules)
        self.transform_to_set_values()

    def transform_to_set_values(self):
        updated_pixmap = self.editor.restore_transformation()
        self.map_pixmap_to_scene(False, pixmap=updated_pixmap)

    def merge_pixmap_and_cv2(self, img):
        self.convert_cv2_to_main_pixmap(img)
        self.transform_to_set_values()

    def memorize_change_on_scene(self):
        items = self.prepare_items_for_history()
        editor = self.editor.__dict__.copy()

        editor['id'] = random.getrandbits(16)

        self.history.build_history_stamp(editor, items)

    def prepare_items_for_history(self):
        text_items = self.find_text_items_on_scene()
        excel = self.excel.find_excel()
        pictures = self.clickable_image.turn_items_to_pixmap()
        return {
            'clickable_text': [item.serialize() for item in text_items] if text_items else 'None',
            'excel': {'item': excel.serialize(), 'window': excel.excel_window.serialize()} if excel else 'None',
            'pictures': pictures
        }

    def drawBackground(self, painter, rect) -> None:
        painter.setBrush(Qt.black)
        painter.drawRect(self.black_back)

    def create_new_color_mask_after_loading(self):
        import cv2
        pixmap = self.return_scene_item_as_pixmap()
        byte = self.convert_to_bytes(pixmap)
        read_from_bytes = byte.data()
        img = np.frombuffer(read_from_bytes, dtype='uint8')
        frame = cv2.imdecode(img, cv2.IMREAD_COLOR)
        self.editor.set_color_mask(frame)

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

    def return_scene_item_as_pixmap(self) -> QPixmap:
        for item in self.items():
            if isinstance(item, QGraphicsPixmapItem):
                return item.pixmap()

    def mousePressEvent(self, event: "QGraphicsSceneMouseEvent") -> None:
        self.text_item.create_on_click(event)
        self.cropper.create_on_click(event)
        self.excel.create_on_click(event)

        super(MainCanvas, self).mousePressEvent(event)

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Delete:
            [self.removeItem(item) for item in self.selectedItems()]
        if event.key() == Qt.Key_Shift:
            self.shift_pressed = True
        super(MainCanvas, self).keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Shift:
            self.shift_pressed = False

    def do_selection_on_focus(self, item):
        if self.shift_pressed:
            if isinstance(item, (ClickableImage, ClickableText)):
                self.selectedItems().append(item)
                item.setSelected(True)
        if isinstance(item, QGraphicsProxyWidget):
            if not self.shift_pressed:
                [item.setSelected(False) for item in self.selectedItems()]
            item.parentItem().setSelected(True)

    def find_text_items_on_scene(self) -> list:
        items = []
        for item in self.items():
            if isinstance(item, ClickableText) and item.id in self.text_item.text_items_ids:
                items.append(item)
        return items

    def undo_redo_action(self, forward):
        self.history.restore_from_history(forward=forward)
        history_stamp: HistoryStamp = self.history.retrieve_stamp()
        if history_stamp:
            self.clear()
            self.editor.__dict__ = dict(history_stamp.editor)
            self.editor.memory_mode = False
            self.merge_pixmap_and_cv2(self.editor.color_mask)
            self.editor.set_all_filters()

    def convert_to_bytes(self, pixmap) -> QByteArray:
        if pixmap is not None:
            bites = QByteArray()
            buff = QBuffer(bites)
            buff.open(QIODevice.WriteOnly)
            pixmap.save(buff, 'PNG')

            return bites

    def convert_all_to_bytes(self, package) -> list:
        all_bites = []
        if package:
            for item in package:
                ready = self.convert_to_bytes(item.pix)
                all_bites.append(ready)
        return all_bites

    def load_from_bytes(self, from_json):
        bites = bytes(from_json, 'ISO-8859-1')
        ba = QByteArray.fromRawData(bites)
        pixmap = QPixmap()
        pixmap.loadFromData(ba, 'PNG')
        return pixmap

    def serialize(self):

        pixmap = self.return_scene_item_as_pixmap()
        byte_pixmap = self.convert_to_bytes(pixmap)
        pix_dict_val = str(byte_pixmap, 'ISO-8859-1')
        texts = self.find_text_items_on_scene()
        excel = self.excel.find_excel()
        pictures = self.clickable_image.find_clickable_images()
        byte_pictures = self.convert_all_to_bytes(pictures)

        return {
            'pixmap': pix_dict_val,
            'clickable_text': [item.serialize() for item in texts] if texts else 'None',
            'excel': {'item': excel.serialize(), 'window': excel.excel_window.serialize()} if excel else 'None',
            'pictures': [{'data': picture.serialize(), 'image': str(bites, 'ISO-8859-1')}
                         for picture, bites in zip(pictures, byte_pictures)] if pictures else 'None'
        }

    def deserialize(self, data, load_as_project_file=True):
        if load_as_project_file:
            self.history.clear_history()
            from_json = data['pixmap']
            pixmap = self.load_from_bytes(from_json)
            self.map_pixmap_to_scene(new_image=True, pixmap=pixmap)
            self.editor.set_transform_pix(pixmap)
            self.create_new_color_mask_after_loading()

        all_texts = data['clickable_text']
        if all_texts != 'None':
            for item in all_texts:
                self.text_item.call_json_loader(item)

        excel_json = data['excel']
        if excel_json != 'None':
            self.excel.call_json_loader(excel_json)

        if load_as_project_file:
            image_package = data['pictures']
            if image_package != 'None':
                for item in image_package:
                    pixmap_of_picture = self.load_from_bytes(item['image'])
                    self.clickable_image.call_json_loader(item['data'], pixmap_of_picture)


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
