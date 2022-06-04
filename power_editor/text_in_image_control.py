from string import Template

from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal, pyqtSlot, QSettings
from PyQt5.QtGui import QColor, QPen, QTextCursor, QTextCharFormat, QFont
from PyQt5.QtWidgets import *
from checked_bundle import CheckedButtons
from serializer.serializer import Serializable

debug = True


class TextItem(CheckedButtons):
    def __init__(self, controller):
        super().__init__()
        self.scene = controller.scene
        self.button = controller.interface.findChild(QAction, 'Add_Text')

    def operate_text_editor(self, event):
        position = event.scenePos()
        if self.button.isChecked():
            item = ClickableText(position)
            self.disable()
            self.scene.addItem(item)
            item.setSelected(True)

    def load_from_json(self, data):
        wid, height = data['width'], data['height']
        x, y = data['position'][0], data['position'][1]
        text = data['text']
        r, g, b, a = data['color']
        font = data['font']
        split_font = font.split(',')
        family, size, weight, italics = split_font[0], split_font[1], split_font[4], split_font[5]
        position = QPointF(x, y)
        item = ClickableText(position, rect=QRectF(0, 0, float(wid), float(height)))

        item.input_field.text_edit.setText(text)
        item.input_field.text_edit.setFont(QFont(family, int(size), int(weight), int(italics)))
        set_c = Template("QTextEdit {color: rgb($r, $g, $b);}")
        formatted = set_c.safe_substitute(r=r, g=g, b=b)
        item.input_field.text_edit.setStyleSheet(formatted)

        self.scene.addItem(item)


class ClickableText(QGraphicsRectItem, Serializable):
    width_inner = 80
    height_inner = 35

    def __init__(self, position, rect=QRectF(0, 0, width_inner, height_inner), add_event_handler=False):
        super().__init__(rect)

        self.optional_action: bool = add_event_handler
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

        elif self.resizer.isSelected():
            # important hack to keep circle visible
            pen = QPen()
            pen.setColor(Qt.black)
            painter.setPen(pen)
            painter.setBrush(Qt.transparent)
            painter.drawRect(self.rect())
        else:
            self.resizer.hide()
        if self.optional_action:
            self.extend_paint_action()

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
            'width': self.rect().width(),
            'height': self.rect().height(),
            'position': (self.pos().x(), self.pos().y()),
            'text': self.input_field.text_edit.toPlainText(),
            'color': self.input_field.text_edit.textColor().getRgb(),
            'font': self.input_field.text_edit.currentCharFormat().font().toString()
        }

    def extend_paint_action(self):
        pass


class Resizer(QGraphicsObject):
    resizeSignal = pyqtSignal(QPointF)

    def __init__(self, parent, rect=QRectF(0, 0, 10, 10)):
        super().__init__(parent)

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
        font, ok = QFontDialog.getFont(self.font(), self)
        cur: QTextCursor = self.textCursor()
        if ok:
            format_obj = QTextCharFormat()
            format_obj.setFont(font)
            cur.setCharFormat(format_obj)
            print(self.currentCharFormat().font().toString())

    def color_dialog(self):
        color = QColorDialog.getColor()
        self.setTextColor(color)

    def mouseDoubleClickEvent(self, QMouseEvent):
        self.double_click[bool].emit(True)
