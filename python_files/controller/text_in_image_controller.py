from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from checked_builder import CheckedControllers


class TextItem(CheckedControllers):
    def __init__(self, interface):
        super().__init__()
        from python_files.interface.interface import Interface

        self.interface: Interface = interface
        self.editor_active = False
        self.button: QAction = interface.findChild(QAction, 'Add_Text')
        # position = QtCore.QPointF(10.0, 20.0)
        # i = ClickableItem(position)
        # self.scene.addItem(i)

    def activate(self):
        self.editor_active = True
        self.last_active = True

    def disable(self):
        self.editor_active = False
        self.last_active = False
        self.button.setChecked(False)

    #
    def operate_text_editor(self, event):
        items = self.interface.scene.items(event.pos())
        if self.editor_active:
            position = event.pos()
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
        # self.input_field = InputFields()
        self.width = 80
        self.height = 35
        self.times = 0
        self.rect_alt = QtCore.QRectF(self.pos_x, self.pos_y, self.width+10, self.height+10)
        self.experimental()
        self.interaction_rules()

    def experimental(self):
        content = QGraphicsProxyWidget(self)
        self.title = QTextEdit()
        self.title.setGeometry(self.pos_x, self.pos_y, self.width, self.height)
        content.setWidget(self.title)

    def interaction_rules(self):
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setAcceptedMouseButtons(Qt.LeftButton)


    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(self.pos_x, self.pos_y, self.width, self.height).normalized()

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

    # def initialize_input(self):
    #     content = QGraphicsProxyWidget(self)
    #     self.input_field.setGeometry(self.pos_x, self.pos_y, self.width, self.height)
        # content.setWidget(self.input_field)


# class InputFields(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.text_edit = QTextEdit('Add text')
#         self.__initialize_ui()
#
#     def __initialize_ui(self):
#         self.layout = QVBoxLayout()
#         self.layout.setContentsMargins(0, 0, 0, 0)
#         self.layout.addWidget(self.text_edit)
#



