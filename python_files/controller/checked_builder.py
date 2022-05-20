from PyQt5.QtWidgets import QAction

from collection_of_controllers import ControllerStateHolder


class CheckedControllers:
    def __init__(self):
        self.last_active = False
        ControllerStateHolder.controllers.append(self)
        self.button = QAction

    def activate(self):
        raise NotImplementedError

    def disable(self):
        raise NotImplementedError
