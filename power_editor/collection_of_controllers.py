from PyQt5.QtWidgets import QAction


class CheckedControllers:
    def __init__(self):
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

    def __init__(self, interface, scene, view):
        from zoom_controller import ZoomEnableDisable
        from text_in_image_controller import TextItem

        button_zoom: QAction = interface.findChild(QAction, 'Zoom_In_Out')
        button_text: QAction = interface.findChild(QAction, 'Add_Text')

        self.zoom_control = ZoomEnableDisable(view, button_zoom)
        self.text_item = TextItem(scene, button_text)

    def verify_only_one_active(self):
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
