import sys
from icons import new
from pathlib import Path
from PyQt5 import uic
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QDesktopWidget


class Interface(QMainWindow):
    def __init__(self, controller):
        from power_editor.main_controller import Controller
        self.app = QApplication(sys.argv)
        super().__init__()
        self.controller: Controller = controller
        path = Path.cwd().parent.joinpath('ui', 'interface_v3.ui')
        uic.loadUi(path, self)
        self.__initialize_all_groups()

    def main(self):
        self.show()
        self.app.exec_()

    def __initialize_all_groups(self):
        self.__initialize_menu_buttons()
        self.__place_app_window_at_screencenter()
        self.__initialize_tool_bar()

    def __initialize_menu_buttons(self):
        image_open = self.findChild(QAction, 'Open_Image')
        image_open.triggered.connect(self.controller.open_new_image)
        image_save = self.findChild(QAction, 'Save_file')
        image_save.triggered.connect(self.controller.save_the_image)
        pdf_open = self.findChild(QAction, 'Open_PDF')
        pdf_open.triggered.connect(self.controller.open_pdf_file)
        save_project = self.findChild(QAction, 'Save_project')
        save_project.triggered.connect(self.controller.save_project)
        open_project = self.findChild(QAction, 'Load_project')
        open_project.triggered.connect(self.controller.load_project)
        brightness = self.findChild(QAction, 'Brightness_control')
        brightness.triggered.connect(self.controller.open_brightness_control)

        undo = self.findChild(QAction, 'Undo')
        undo.triggered.connect(self.controller.undo)

    def __initialize_tool_bar(self):
        self.zoom_button_in = self.findChild(QAction, 'Zoom_In_Out')
        self.zoom_button_in.triggered.connect(self.controller.tool_bar_checked_buttons)
        printer = self.findChild(QAction, 'Print')
        printer.triggered.connect(self.controller.print_file)
        self.add_text = self.findChild(QAction, 'Add_Text')
        self.add_text.triggered.connect(self.controller.tool_bar_checked_buttons)
        rotate_right = self.findChild(QAction, 'Rotate_right')
        rotate_right.triggered.connect(lambda command: self.controller.transform_image({'rotation': 90}))
        rotate_left = self.findChild(QAction, 'Rotate_left')
        rotate_left.triggered.connect(lambda command: self.controller.transform_image({'rotation': -90}))
        flip_horizontally = self.findChild(QAction, 'Flip_horizontally')
        flip_horizontally.triggered.connect(lambda command: self.controller.transform_image({'flip': (-1, 1)}))
        flip_vertically = self.findChild(QAction, 'Flip_vertically')
        flip_vertically.triggered.connect(lambda command: self.controller.transform_image({'flip': (1, -1)}))
        self.custom_rotation = self.findChild(QAction, 'Custom_rotation')
        self.custom_rotation.triggered.connect(self.controller.tool_bar_checked_buttons)
        self.resize = self.findChild(QAction, 'Resize_image')
        self.resize.triggered.connect(self.controller.tool_bar_checked_buttons)
        self.crop = self.findChild(QAction, 'Crop')
        self.crop.triggered.connect(self.controller.tool_bar_checked_buttons)
        self.excel_input = self.findChild(QAction, 'Excel_input')
        self.excel_input.triggered.connect(self.controller.tool_bar_checked_buttons)
        self.impose_image = self.findChild(QAction, 'Impose_image')
        self.impose_image.triggered.connect(self.controller.open_imposed_picture)

    def __place_app_window_at_screencenter(self):
        desktop = QDesktopWidget().screenGeometry()
        screen_width = desktop.width()
        screen_height = desktop.height()
        self.move((screen_width - self.width()) // 2, (screen_height - self.height()) // 2)

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.controller.prompt_box()
        self.app.closeAllWindows()


