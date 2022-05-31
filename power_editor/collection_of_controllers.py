from PyQt5.QtWidgets import QAction


class Controllers:
    controllers = []

    @staticmethod
    def verify_only_one_active():
        Controllers.__disable_last_controller()
        Controllers.__activate_new_controller()

    @staticmethod
    def __disable_last_controller():
        for controller in Controllers.controllers:
            if controller.last_active:
                controller.disable()

    @staticmethod
    def __activate_new_controller():
        for controller in Controllers.controllers:
            if controller.button.isChecked():
                controller.activate()


class CheckedControllers(Controllers):
    def __init__(self):
        self.last_active = False
        self.controllers.append(self)
        self.button = QAction

    def activate(self):
        self.last_active = True

    def disable(self):
        self.last_active = False
        self.button.setChecked(False)


class Holder:
    def __init__(self, controller):
        from zoom_controller import ZoomEnableDisable
        from text_in_image_controller import TextItem
        from rotation_controller import Rotator
        from resize_controller import Resizer

        self.zoom_control = ZoomEnableDisable(controller)
        self.text_item = TextItem(controller)
        self.rotator = Rotator(controller)
        self.resizer = Resizer(controller)

    def get_spin_value(self):
        return self.rotator.spin_box.value()

    def get_resize_value(self):
        return self.resizer.width_box.value(), self.resizer.height_box.value()



