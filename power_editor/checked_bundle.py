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





