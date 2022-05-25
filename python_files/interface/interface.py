from PyQt5.QtGui import QCloseEvent

from icons import new
from python_files.controller.main_controller import *
from python_files.interface.image_scene import *
import sys
from pathlib import Path
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QGraphicsView, \
    QDesktopWidget, QFrame

from python_files.interface.main_view import MainView


class Interface(QMainWindow):
    def __init__(self, controller: Controller):
        self.app = QApplication(sys.argv)
        super().__init__()
        self.controller = controller
        path = Path.cwd().parent.parent.joinpath('ui', 'interface_v3.ui')
        uic.loadUi(path, self)
        self.__initialize_all_groups()

    def main(self):
        self.show()
        self.app.exec_()

    def __initialize_all_groups(self):
        self.__set_working_background_to_work_with_graphics()
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

    def __initialize_tool_bar(self):
        zoom_button_in: QAction = self.findChild(QAction, 'Zoom_In_Out')
        zoom_button_in.triggered.connect(self.controller.tool_bar_checked_buttons)
        printer = self.findChild(QAction, 'Print')
        printer.triggered.connect(self.controller.print_file)
        add_text = self.findChild(QAction, 'Add_Text')
        add_text.triggered.connect(self.controller.tool_bar_checked_buttons)
        rotate_right = self.findChild(QAction, 'Rotate_right')
        rotate_right.triggered.connect(self.controller.rotate_right)
        rotate_left = self.findChild(QAction, 'Rotate_left')
        rotate_left.triggered.connect(self.controller.rotate_left)
        flip_horizontally = self.findChild(QAction, 'Flip_horizontally')
        flip_horizontally.triggered.connect(self.controller.flip_horizontally)
        flip_vertically = self.findChild(QAction, 'Flip_vertically')
        flip_vertically.triggered.connect(self.controller.flip_vertically)

    def __set_working_background_to_work_with_graphics(self):

        self.view_widget = MainView(self)
        self.scene = MainCanvas(self.view_widget)

    def __place_app_window_at_screencenter(self):
        desktop = QDesktopWidget().screenGeometry()
        screen_width = desktop.width()
        screen_height = desktop.height()
        self.move((screen_width - self.width()) // 2, (screen_height - self.height()) // 2)

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.controller.prompt_box()


