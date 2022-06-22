
from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal, pyqtSlot, QObject
from PyQt5.QtGui import QColor, QPen, QTextCursor, QTextCharFormat
from PyQt5.QtWidgets import *
from power_editor.checked_bundle import CheckedButtons
from serializer.serializer import Serializable
from collections import namedtuple

debug = True


class CommunicateChange(QObject):
    position_new = pyqtSignal()


class TextItem(CheckedButtons):
    def __init__(self, interface, scene):
        super().__init__()
        self.scene = scene
        self.button = interface.add_text
        self.text_items_ids = []

    def create_on_click(self, event):
        position = event.scenePos()
        if self.button.isChecked():
            item = ClickableText(position)
            self.scene.addItem(item)
            self.text_items_ids.append(item.id)
            item.communicate.position_new.connect(self.scene.memorize_change_on_scene)
            item.setSelected(True)
            self.disable()
            self.scene.memorize_change_on_scene()

    def call_json_loader(self, data):
        item = self.load_from_json(ClickableText, data)
        item.communicate.position_new.connect(self.scene.memorize_change_on_scene)
        self.scene.addItem(item)


class ClickableText(QGraphicsRectItem, Serializable):
    width_inner = 80
    height_inner = 35
    my_selection_list = []

    def __init__(self, position, rect=QRectF(0, 0, width_inner, height_inner), extend_paint=False):
        super().__init__(rect)
        self.position_end = []
        self.position_start = []

        self.start_memorize = False
        self.communicate = CommunicateChange()

        self.id = id(self)

        self.optional_action: bool = extend_paint
        self._initialize_flags()
        self.setPos(position)
        self.setZValue(1)

        self.resizer = Resizer(parent=self)
        resizer_width = self.resizer.rect.width() / 2
        resizer_offset = QPointF(resizer_width, resizer_width)
        self.resizer.setPos(self.rect().bottomRight() - resizer_offset)
        self.resizer.resizeSignal[QPointF].connect(lambda change: self.resize(change))

        self.input_field = InputFields()
        self.content = QGraphicsProxyWidget(self)
        self.initialize_input()

    def _initialize_flags(self):
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

    def memorize_mode_on(self):
        if not self.start_memorize:
            self.start_memorize = True
            self.position_start.clear()
            for item in self.scene().items():
                if hasattr(item, 'id'):
                    Snapshot = namedtuple('Snapshot', 'id pos rect')
                    item_snap = Snapshot(item.id, item.scenePos(), item.rect())
                    self.my_selection_list.append(item_snap)

    def memorize_mode_off(self):
        if self.start_memorize:
            self.start_memorize = False
            self.position_end.clear()
            self.check_for_position_changes()
            self.my_selection_list.clear()

    def check_for_position_changes(self):
        for item in self.scene().items():
            if hasattr(item, 'id'):
                self.send_signal_if_something_changed(item)

    def send_signal_if_something_changed(self, item):
        changed_pos = ([item for saved in self.my_selection_list
                        if (item.id == saved.id and item.scenePos() != saved.pos)
                        or (item.id == saved.id and item.rect() != saved.rect)])
        no_duplicate_items = set([item.id for item in changed_pos])
        if no_duplicate_items:
            self.communicate_new_position()

    def communicate_new_position(self):
        self.communicate.position_new.emit()

    def mouseReleaseEvent(self, QGraphicsSceneMouseEvent):
        self.memorize_mode_off()
        super(ClickableText, self).mouseReleaseEvent(QGraphicsSceneMouseEvent)

    def paint(self, painter, option, widget=None):
        if self.input_field.text_edit.hasFocus():
            self.setSelected(True)
        if self.isSelected():
            # draw everything
            pen = QPen()
            pen.setColor(QColor('#ff5533'))
            self.resizer.show()
            painter.setPen(pen)
            painter.setBrush(Qt.transparent)
            painter.drawRect(self.rect())
            self.memorize_mode_on()

        elif self.resizer.isSelected():
            # important hack to keep circle visible
            pen = QPen()
            pen.setColor(Qt.black)
            painter.setPen(pen)
            painter.setBrush(Qt.transparent)
            painter.drawRect(self.rect())
            self.memorize_mode_on()
        else:
            self.resizer.hide()
        if self.optional_action:
            self.extend_paint_action(painter)

    @pyqtSlot()
    def resize(self, change):
        self.setRect(self.rect().adjusted(0, 0, change.x(), change.y()))
        self.prepareGeometryChange()
        self.update()
        rect: QRectF = self.rect()
        self.input_field.resize(int(rect.width()), int(rect.height()))

    def initialize_input(self):
        self.input_field.setMinimumSize(10, 10)
        self.input_field.setGeometry(0, 0,
                                     int(self.rect().width()), int(self.rect().height()))
        self.content.setWidget(self.input_field)


    def serialize(self):
        return {
            'id': self.id,
            'width': self.rect().width(),
            'height': self.rect().height(),
            'position': (self.pos().x(), self.pos().y()),
            'text': self.input_field.text_edit.toPlainText(),
            'color': self.input_field.text_edit.textColor().getRgb(),
            'font': self.input_field.text_edit.currentCharFormat().font().toString()
        }

    def extend_paint_action(self, painter):
        pass


class Resizer(QGraphicsObject):
    resizeSignal = pyqtSignal(QPointF)

    def __init__(self, parent, rect=QRectF(0, 0, 10, 10)):
        self.p = parent
        super().__init__(parent)
        self.setZValue(2)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        self.rect = rect

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget=None):
        if self.isSelected():
            pen = QPen()
            pen.setStyle(Qt.SolidLine)
            pen.setColor(QColor("#58a4ff"))
            painter.setPen(pen)
            painter.setBrush(Qt.Dense3Pattern)
        painter.setBrush(QColor(59, 47, 38))
        painter.drawEllipse(self.rect)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            if self.isSelected():
                self.resizeSignal[QPointF].emit(value - self.pos())

        return value

    def mouseReleaseEvent(self, event):
        self.p.memorize_mode_off()
        super(Resizer, self).mouseReleaseEvent(event)


class InputFields(QWidget):
    def __init__(self):
        super().__init__()
        self.text_edit = TextEdit()
        self.__initialize_ui()

    def __initialize_ui(self):
        self.painter = QStylePainter()
        self.layout = QVBoxLayout()
        style = """
            background-color: transparent;
        """
        self.setStyleSheet(style)
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 2, 0, 0)
        self.layout.addWidget(self.text_edit)


class TextEdit(QTextEdit):
    menu_style = """
        QMenu { background-color: #58a4ff;}
    """

    double_click = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.setText('Add text')
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet('QTextEdit {background: transparent}')

        self.font_selection = QAction('Font')
        self.font_selection.triggered.connect(self.font_dialog)
        self.color_selection = QAction('Text Color')
        self.color_selection.triggered.connect(self.color_dialog)

    def contextMenuEvent(self, event):
        menu: QMenu = self.createStandardContextMenu()
        menu.setStyleSheet(self.menu_style)
        menu.addSeparator()
        menu.addAction(self.font_selection)
        menu.addAction(self.color_selection)
        menu.exec(event.globalPos())
        menu.deleteLater()

    def font_dialog(self):
        # qfont takes passed string from widget as first argument
        font, ok = QFontDialog.getFont(self.font())
        cur: QTextCursor = self.textCursor()
        if ok:
            format_obj = QTextCharFormat()
            format_obj.setFont(font)
            cur.setCharFormat(format_obj)

    def color_dialog(self):
        color = QColorDialog.getColor()
        self.setTextColor(color)

    def mouseDoubleClickEvent(self, QMouseEvent):
        self.double_click[bool].emit(True)
