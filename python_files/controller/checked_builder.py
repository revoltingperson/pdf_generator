from PyQt5.QtWidgets import QAction

from collection_of_controllers import ControllerStateHolder


class CheckedControllers:
    def __init__(self):
        self.last_active = False
        self.button_active = False
        ControllerStateHolder.controllers.append(self)
        self.button = QAction

    def activate(self):
        self.last_active = True

    def disable(self):
        self.last_active = False
        self.button.setChecked(False)
