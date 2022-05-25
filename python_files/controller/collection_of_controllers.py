from PyQt5.QtWidgets import QAction


class CheckedControllers:
    def __init__(self, interface):
        self.interface = interface
        self.last_active = False
        ControllersHolder.controllers.append(self)
        self.button = QAction

    def activate(self):
        self.last_active = True

    def disable(self):
        self.last_active = False
        self.button.setChecked(False)


class ControllersHolder:
    controllers = []

    def __init__(self, interface):
        from zoom_controller import ZoomEnableDisable
        from text_in_image_controller import TextItem

        self.zoom_control = ZoomEnableDisable(interface)
        self.text_item = TextItem(interface)

    def verify_one_one_active(self):
        self.__disable_last_controller()
        self.__activate_new_controller()

    def __disable_last_controller(self):
        for controller in self.controllers:
            if controller.last_active:
                controller.disable()

    def __activate_new_controller(self):
        for controller in self.controllers:
            if controller.button.isChecked():
                controller.activate()
