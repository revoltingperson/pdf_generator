from icons import new
from python_files.controller.main_controller import *
from python_files.interface.image_scene import *
import sys
from pathlib import Path
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QGraphicsView, \
    QDesktopWidget, QFrame


class Interface(QMainWindow):
    view_widget: QGraphicsView

    def __init__(self, controller: Controller):
        self.app = QApplication(sys.argv)
        super().__init__()
        self.controller = controller
        path = Path.cwd().parent.parent.joinpath('ui', 'interfacev2.ui')
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
        zoom_button_in: QAction = self.findChild(QAction, 'Zoom_In')
        zoom_button_out: QAction = self.findChild(QAction, 'Zoom_Out')
        zoom_button_in.triggered.connect(self.controller.tool_bar_actions)
        zoom_button_out.triggered.connect(self.controller.tool_bar_actions)
        printer = self.findChild(QAction, 'Print')
        printer.triggered.connect(self.controller.print_file)
        add_text = self.findChild(QAction, 'Add_Text')
        add_text.triggered.connect(self.controller.tool_bar_actions)

    def __set_working_background_to_work_with_graphics(self):
        wid = self.findChild(QGraphicsView, 'backgroundView')
        scene = MainCanvas(wid)
        self.view_widget = wid
        self.scene = scene

    def __place_app_window_at_screencenter(self):
        desktop = QDesktopWidget().screenGeometry()
        screen_width = desktop.width()
        screen_height = desktop.height()
        self.move((screen_width - self.width()) // 2, (screen_height - self.height()) // 2)



