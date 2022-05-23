from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QAction, QGraphicsItem
from collection_of_controllers import CntrsHolder


class CheckedControllers:
    def __init__(self, interface):
        self.interface = interface
        self.last_active = False
        CntrsHolder.controllers.append(self)
        self.button = QAction

    def activate(self):
        self.last_active = True

    def disable(self):
        self.last_active = False
        self.button.setChecked(False)

