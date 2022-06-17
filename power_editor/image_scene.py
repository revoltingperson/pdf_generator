import typing
import cv2
import numpy as np

from checked_bundle import Collector, CheckedButtons
from crop_control import *
from excel_control import ExcelControl
from image_editor import ImageEditor
from picture_adding import PictureItem, ClickableImage
from power_editor.scene_history_stack import HistoryStack
from resize_control import Resizer
from rotation_control import Rotator
from toplevel.visual_effects import BrightnessWidget
from zoom_control import ZoomEnableDisable
from text_in_image_control import TextItem, ClickableText, CommunicateChange

from PyQt5.QtCore import Qt, QRectF, QByteArray, QBuffer, QIODevice, QRect
from PyQt5.QtGui import QPixmap, QPainter, QImage, QBrush, QColor, QPen, QKeyEvent, QTransform, QPaintDevice
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsSceneMouseEvent, QGraphicsProxyWidget, \
    QGraphicsRectItem, QWidget, QGraphicsPixmapItem
from serializer.serializer import Serializable

debug = False


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
        pixmap = self.convert_raw_to_pixmap(image, new_image=True)
        self.remove_pixmap_policy(new_image=True)
        self.map_pixmap_to_scene(pixmap=pixmap)
        self.editor.set_transform_pix(pixmap)

    def convert_raw_to_pixmap(self, image, new_image: bool = False):
        frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width = frame.shape[0], frame.shape[1]

        if new_image:
            self.editor.set_color_mask(image)
            self.editor.set_to_default()

        q_image = QImage(frame, width, height, frame.strides[0], QImage.Format_RGB888)
        pixmap = QPixmap().fromImage(q_image)

        if new_image:
            self.history.clear_history()
            self.history.add_pix_to_memory(pixmap, self.editor, self.serialize(exclude_pixmap=True))

        return pixmap

    def convert_qimage_clean(self, image):
        """ qimage does not destroy the alpha channel, that is why I am not
            using the convert_raw_to_pixmap func
        """
        q_image = QImage(image)
        pix = QPixmap().fromImage(q_image)
        return pix

    def return_scene_item_as_pixmap(self) -> QPixmap:
        for item in self.items():
            if isinstance(item, QGraphicsPixmapItem):
                return item.pixmap()

    def map_pixmap_to_scene(self, pixmap=None, cropped=False):
        pixmap_to_show = pixmap
        if cropped and self.editor.transformation_pixmap.isNull():
            return
        elif cropped:
            self.editor.set_transform_pix(pixmap)
            self.history.add_pix_to_memory(pixmap, self.editor, self.serialize(exclude_pixmap=True))

        self.remove_pixmap_policy(new_image=False)
        self.build_border(pixmap_to_show.height(), pixmap_to_show.width())
        self.addPixmap(pixmap_to_show)
        scene_rect = QRectF(self.XY_ZERO, self.XY_ZERO, pixmap_to_show.width(), pixmap_to_show.height())
        self.black_back = scene_rect
        self.setSceneRect(scene_rect)
        self.post_transform(cropped)

        if debug:
            print(f"pixmap in map_pixmap: {pixmap_to_show.size()}")
        if debug:
            print(f'scene rect in map_pixmap: {self.sceneRect()}')

    def transform_to_rules(self, rules: dict):
        key, val = list(rules.items())[0]

        options = {'rotation': self.editor.do_rotation,
                   'flip': self.editor.do_flip,
                   'resize': self.editor.resize,
                   'custom_rotation': self.editor.do_custom_rotation
                   }

        chosen = options.get(key)
        self.editor.set_color_mask(None)
        # noinspection PyArgumentList
        return chosen(val)

    def send_transformation(self, rules, from_history=False):
        key, val = list(rules.items())[0]
        if key == 'custom_rotation':
            pixmap_to_show = self.transform_to_rules(rules)
            self.memorize_image_change()
        else:
            pixmap_to_show = self.transform_to_rules(rules)
            self.editor.set_transform_pix(pixmap_to_show)
            pixmap_to_show = self.editor.do_rotation(post_trans_pix=pixmap_to_show)
            if not from_history:
                self.memorize_image_change()

        self.map_pixmap_to_scene(pixmap_to_show)

    def memorize_image_change(self):
        self.history.add_pix_to_memory(self.editor.transformation_pixmap, self.editor, self.serialize(exclude_pixmap=True))

    def post_transform(self, cropped):
        if self.editor.color_mask is None \
                and not self.editor.transformation_pixmap.isNull():
            self.create_new_color_mask_after_transform()
            self.editor.set_all_filters()

        elif cropped:
            self.create_new_color_mask_after_transform()
            self.editor.set_to_default()

    def drawBackground(self, painter, rect) -> None:
        painter.setBrush(Qt.black)
        painter.drawRect(self.black_back)

    def create_new_color_mask_after_transform(self):
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

    def coordinate_selected_items(self):
        pass

    def mousePressEvent(self, event: "QGraphicsSceneMouseEvent") -> None:
        self.text_item.create_on_click(event)
        self.cropper.create_on_click(event)
        self.excel.create_on_click(event)

        if debug:
            print(f'selected items: {self.selectedItems()}')
            # print(f'items at {event.scenePos()} {self.itemAt(event.scenePos(), QTransform())}')

        super(MainCanvas, self).mousePressEvent(event)

    def keyPressEvent(self, event) -> None:
        if debug:
            print(f'selected items: {self.selectedItems()}')
            print(f'all items: {self.items()}')
        if event.key() == Qt.Key_Delete:
            [self.removeItem(item) for item in self.selectedItems()]
        if event.key() == Qt.Key_Shift:
            self.shift_pressed = True
        super(MainCanvas, self).keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Shift:
            self.shift_pressed = False

    def do_selection_on_focus(self, item):
        if debug: print(f'selection changed to {item}')

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
            if isinstance(item, ClickableText):
                items.append(item)
        return items

    def undo_redo_action(self, forward):
        self.history.restore_from_history(forward=forward)
        history_stamp = self.history.retrieve_stamp()
        if history_stamp:
            self.clear()
            self.editor.set_transform_pix(history_stamp.pixmap)
            self.editor.last_custom_rot = history_stamp.rotation
            self.editor.last_brightness = history_stamp.brightness
            self.editor.last_gamma = history_stamp.gamma
            self.editor.last_blur = history_stamp.blur
            self.editor.grey = history_stamp.grey
            self.deserialize(history_stamp.serialized, load_as_project_file=False)
            self.send_transformation({'rotation': history_stamp.rotation}, from_history=True)

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

    def serialize(self, exclude_pixmap=False):
        if exclude_pixmap:
            pix_dict_val = 'None'
        else:
            pixmap = self.return_scene_item_as_pixmap()
            byte_pixmap = self.convert_to_bytes(pixmap)
            pix_dict_val = str(byte_pixmap, 'ISO-8859-1')
        texts = self.find_text_items_on_scene()
        excel = self.excel.find_excel()
        pictures = self.clickable_image.find_clickable_images()
        byte_pictures = self.convert_all_to_bytes(pictures)

        if excel is not None:
            texts = list([item for item in texts if item.id != excel.id])
        if pictures:
            for picture in pictures:
                for text in texts:
                    if picture.id == text.id:
                        texts.remove(text)
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
            self.remove_pixmap_policy(new_image=True)
            from_json = data['pixmap']
            pixmap = self.load_from_bytes(from_json)
            self.map_pixmap_to_scene(pixmap=pixmap)
            self.editor.set_transform_pix(pixmap)
            self.create_new_color_mask_after_transform()

        all_texts = data['clickable_text']
        if all_texts != 'None':
            for item in all_texts:
                self.text_item.call_json_loader(item)

        excel_json = data['excel']
        if excel_json != 'None':
            self.excel.call_json_loader(excel_json)

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
