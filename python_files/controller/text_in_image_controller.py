from PyQt5.QtWidgets import QAction, QGraphicsItem, QGraphicsSceneMouseEvent
from PyQt5 import QtGui
from PyQt5 import QtCore
from python_files.interface.interface import Interface
from collection_of_controllers import ControllerStateHolder


class TextItem:
    def __init__(self, interface: Interface):
        super().__init__()
        self.last_active = False
        ControllerStateHolder.controllers.append(self)

        self.interface = interface
        self.scene = self.interface.scene
        self.editor_active = False
        self.button: QAction = self.interface.findChild(QAction, 'Add_Text')
        item = ClickableItem()
        self.scene.addItem(item)

    def activate(self):
        self.editor_active = True
        self.last_active = True

    def disable(self):
        self.editor_active = False
        self.last_active = False
        self.button.setChecked(False)

    #
    def operate_text_editor(self, event):
        items = self.scene.items(event.scenePos())
        if self.editor_active:
            position = event.scenePos()
            item = ClickableItem(position)
            self.scene.addItem(item)
        if items and isinstance(items[0], ClickableItem):
            QGraphicsItem.mousePressEvent(items[0], event)


class ClickableItem(QGraphicsItem):
    # def __init__(self, position):
    def __init__(self):
        super().__init__()
        # self.pos_x = int(position.x())
        # self.pos_y = int(position.y())
        self.pos_x = 20
        self.pos_y = 20
        self.width = 80
        self.height = 35
        self.interaction_rules()


    def interaction_rules(self):
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(self.pos_x, self.pos_y, self.width, self.height).normalized()

    def paint(self, painter: QtGui.QPainter, QStyleOptionGraphicsItem, widget=None) -> None:
        outline = QtGui.QPen(QtCore.Qt.DotLine)
        outline.setWidth(2)
        outline.setColor(QtCore.Qt.darkGray)
        painter.setPen(outline)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawRect(self.pos_x, self.pos_y, self.width, self.height)

    # def mousePressEvent(self, event: "QGraphicsSceneMouseEvent") -> None:
    #     print('h')


