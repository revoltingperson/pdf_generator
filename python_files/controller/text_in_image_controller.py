from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal, pyqtSlot, QRect
from PyQt5.QtGui import QPalette, QColor, QPixmap, QCursor, QPen
from PyQt5.QtWidgets import *
from checked_builder import CheckedControllers


class TextItem(CheckedControllers):
    def __init__(self, interface):
        super().__init__()
        from python_files.interface.interface import Interface

        self.interface: Interface = interface
        self.editor_active = False
        self.button: QAction = interface.findChild(QAction, 'Add_Text')

    def activate(self):
        self.editor_active = True
        self.last_active = True

    def disable(self):
        self.editor_active = False
        self.last_active = False
        self.button.setChecked(False)

    def operate_text_editor(self, event):
        position = event.scenePos()
        items = self.interface.scene.items(position)
        # print(f"{len(items)} items at click")
        # print(f"{len(self.interface.scene.items())} all items at scene")
        if self.editor_active:
            item = ClickableItem(position)
            self.interface.scene.addItem(item)


class ClickableItem(QGraphicsRectItem):
    width_inner = 80
    height_inner = 35

    def __init__(self, position, rect=QRectF(0, 0, width_inner, height_inner)):
        super().__init__(rect)
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
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

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
        print(parent)
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
            pen.setColor(QColor(237, 123, 24))
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
        self.text_edit = QTextEdit('Add text')
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











