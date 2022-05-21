from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPalette
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

    #
    def operate_text_editor(self, event):
        position = event.scenePos()
        items = self.interface.scene.items(position)
        if self.editor_active:
            item = ClickableItem(position)
            # inputs = InputFields()
            # inputs.setGeometry(int(event.scenePos().x()), int(event.scenePos().y()), 80, 35)
            # proxy = self.interface.scene.addWidget(inputs)
            # proxy.setFlag(QGraphicsItem.ItemIsSelectable)
            # proxy.setFlag(QGraphicsItem.ItemIsMovable)
            self.interface.scene.addItem(item)


class ClickableItem(QGraphicsItem):
    def __init__(self, position):
        super().__init__()
        self.pos_x = int(position.x())
        self.pos_y = int(position.y())
        self.input_field = InputFields()
        self.width = 90
        self.height = 35
        self.times = 0
        # self.rect_alt = QtCore.QRectF(self.pos_x, self.pos_y, self.width+10, self.height+10)
        self.experimental()
        self.initialize_input()
        self.interaction_rules()

    def experimental(self):
        pass

    def interaction_rules(self):
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setAcceptedMouseButtons(Qt.LeftButton)


    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(self.pos_x-5, self.pos_y-5, self.width+5, self.height+5).normalized()

    def paint(self, painter: QtGui.QPainter, QStyleOptionGraphicsItem, widget=None) -> None:
        outline = QtGui.QPen(QtCore.Qt.DotLine)
        outline.setWidth(2)
        outline.setColor(QtCore.Qt.darkGray)
        painter.setPen(outline)
        painter.setBrush(QtCore.Qt.NoBrush)
        rect_def = QtCore.QRectF(self.pos_x, self.pos_y, self.width, self.height)
        painter.drawRect(rect_def)

        # if self.times == 0:
        #     painter.drawRect(rect_def)
        #     self.times += 1


    def mousePressEvent(self, event: "QGraphicsSceneMouseEvent") -> None:
        item = self.boundingRect()
        print(f'bound rect {item}')
        print(self.isSelected())
        self.setCursor(Qt.ClosedHandCursor)


    def mouseReleaseEvent(self, event: "QGraphicsSceneMouseEvent") -> None:
        self.setCursor(Qt.ArrowCursor)
        super(ClickableItem, self).mouseReleaseEvent(event)

    def initialize_input(self):
        content = QGraphicsProxyWidget(self)
        self.input_field.setMinimumSize(self.width//2, self.height)
        self.input_field.setGeometry(self.pos_x, self.pos_y, self.width - 20, self.height)
        content.setWidget(self.input_field)


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




