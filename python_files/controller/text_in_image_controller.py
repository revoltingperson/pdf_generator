from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal, pyqtSlot, QRect
from PyQt5.QtGui import QPalette, QColor, QPixmap, QCursor, QPen, QTextCursor, QTextCharFormat
from PyQt5.QtWidgets import *
from checked_builder import CheckedControllers


class TextItem(CheckedControllers):
    def __init__(self, interface):
        super().__init__()
        """TODO:
        connect signal on click with slots
        """
        from python_files.interface.interface import Interface

        self.interface: Interface = interface
        self.button: QAction = interface.findChild(QAction, 'Add_Text')


    def operate_text_editor(self, event):
        position = event.scenePos()
        items = self.interface.scene.items(position)
        print(f"{len(items)} items at click")
        if items:
            print(items[0].flags())
        # print(f"{len(self.interface.scene.items())} all items at scene")
        if self.button.isChecked():
            item = ClickableItem(position)
            self.interface.scene.addItem(item)
            item.input_field.text_edit.font()


class ClickableItem(QGraphicsRectItem):
    width_inner = 80
    height_inner = 35

    def __init__(self, position, rect=QRectF(0, 0, width_inner, height_inner)):
        super().__init__(rect)
        self.flag_list = [(QGraphicsItem.ItemIsSelectable, True),
                          (QGraphicsItem.ItemIsMovable, True),
                          (QGraphicsItem.ItemIsFocusable, True),
                          (QGraphicsItem.ItemSendsGeometryChanges, True)
                          ]
        self._initialize_flags()

        self.setPos(position)
        self.position = position

        self.resizer = Resizer(parent=self)
        resizer_width = self.resizer.rect.width() / 2
        resizer_offset = QPointF(resizer_width, resizer_width)
        self.resizer.setPos(self.rect().bottomRight() - resizer_offset)
        self.resizer.resizeSignal[QPointF].connect(lambda change: self.resize(change))

        self.input_field = InputFields()
        self.content = QGraphicsProxyWidget(self)
        self.initialize_input()

    def _initialize_flags(self):
        for flag in self.flag_list:
            self.setFlag(*flag)

    def paint(self, painter, option, widget=None):
        # print(f'{self.isUnderMouse()} mouse hover')
        # print(f'{self.isSelected()} rect item selected')
        # print(f'{self.input_field.text_edit.hasFocus()} textedit')
        if self.isSelected() or self.input_field.text_edit.hasFocus():
            # draw everything
            pen = QPen()
            pen.setColor(Qt.black)
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
                                     self.width_inner, self.height_inner)
        self.content.setWidget(self.input_field)


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
            # pen.setColor(QColor(237, 123, 24))
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

    def color_dialog(self):
        color = QColorDialog.getColor()
        self.setTextColor(color)
