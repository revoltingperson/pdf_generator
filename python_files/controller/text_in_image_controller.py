from PyQt5.QtWidgets import QAction, QGraphicsItem
from PyQt5 import QtGui
from PyQt5 import QtCore
from python_files.interface.interface import Interface
from collection_of_controllers import ControllerStateHolder


class TextItem(QGraphicsItem):
    def __init__(self, interface: Interface):
        super().__init__()
        self.last_active = False
        ControllerStateHolder.controllers.append(self)

        self.interface = interface
        self.scene = self.interface.scene
        self.editor_active = False
        self.width = 80
        self.height = 35
        self.button: QAction = self.interface.findChild(QAction, 'Add_Text')
        self.__position = None

    def activate(self):
        self.editor_active = True
        self.last_active = True

    def disable(self):
        self.editor_active = False
        self.last_active = False
        self.button.setChecked(False)

    def operate_text_editor(self, event):
        if self.editor_active:
            self.__position = int(event.scenePos())
            self.scene.addItem(self)

    # def build_text_edit_container(self, pos):
    #     outline = QtGui.QPen(QtCore.Qt.DotLine)
    #     outline.setWidth(2)
    #     outline.setColor(QtCore.Qt.darkGray)
    #     interior = QtGui.QBrush(QtCore.Qt.NoBrush)
    #     rect_item = QtCore.QRectF(pos.x(), pos.y(), self.width, self.height)
    #
    #     self.scene.addRect(rect_item, outline, interior)

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(self.__position.x(), self.__position.y(), self.width, self.height).normalized()


    def paint(self, painter: QtGui.QPainter, QStyleOptionGraphicsItem, widget=None) -> None:
        outline = QtGui.QPen(QtCore.Qt.DotLine)
        outline.setWidth(2)
        outline.setColor(QtCore.Qt.darkGray)
        painter.setPen(outline)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawRect(self.__position.x(), self.__position.y(), self.width, self.height)
