class CntrsHolder:
    controllers = []

    @staticmethod
    def verify_only_one_active():
        CntrsHolder.__disable_last_controller()
        CntrsHolder.__activate_new_controller()

    @staticmethod
    def __disable_last_controller():
        for controller in CntrsHolder.controllers:
            if controller.last_active:
                controller.disable()

    @staticmethod
    def __activate_new_controller():
        for controller in CntrsHolder.controllers:
            if controller.button.isChecked():
                controller.activate()

    @staticmethod
    def any_active() -> bool:
        for controller in CntrsHolder.controllers:
            if controller.button.isChecked():
                return True
        return False
