from PyQt5.QtWidgets import QAction


class Collector:
    all_checked = []

    @staticmethod
    def verify_only_one_active():
        Collector.__disable_last_controller()
        Collector.__activate_new_controller()

    @staticmethod
    def __disable_last_controller():
        for controller in Collector.all_checked:
            if controller.last_active:
                controller.disable()

    @staticmethod
    def __activate_new_controller():
        for controller in Collector.all_checked:
            if controller.button.isChecked():
                controller.activate()


class CheckedButtons(Collector):
    def __init__(self):
        self.last_active = False
        self.all_checked.append(self)
        self.button = QAction

    def activate(self):
        self.last_active = True

    def disable(self):
        self.last_active = False
        self.button.setChecked(False)


class Holder:
    def __init__(self, controller):
        from zoom_control import ZoomEnableDisable
        from text_in_image_control import TextItem
        from rotation_control import Rotator
        from resize_control import Resizer
        from crop_control import Cropper
        from excel_control import ExcelController

        self.zoom_control = ZoomEnableDisable(controller)
        self.text_item = TextItem(controller)
        self.rotator = Rotator(controller)
        self.resizer = Resizer(controller)
        self.cropper = Cropper(controller)
        self.excel = ExcelController(controller)





