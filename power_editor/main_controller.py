import json
import os

import numpy
from PyQt5.QtCore import QThread, pyqtSlot
from PyQt5.QtGui import QPainter
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QDialog, QVBoxLayout

import cv2 as cv
from image_scene import MainCanvas
from interface_setup.interface import Interface
from main_view import MainView
from toplevel.pdf_dialog import PdfOpener
from collection_of_controllers import Holder, Controllers
from image_editor import ImageEditor


class Controller:
    def __init__(self):

        self.interface = Interface(self)
        self.__set_working_background_to_work_with_graphics()
        self.__build_checked_button_actions()
        self.editor = ImageEditor(self.scene)

    def main(self):
        self.interface.main()

    def __build_checked_button_actions(self):
        self.holder = Holder(self)
        self.scene.connect_text_items(self.holder.text_item)
        self.view_widget.connect_zoom_controller(self.holder.zoom_control)

    def __set_working_background_to_work_with_graphics(self):
        layout = self.interface.findChild(QVBoxLayout, 'verticalLayout')
        self.view_widget = MainView(layout)
        self.scene = MainCanvas(self.view_widget)

    def tool_bar_checked_buttons(self):
        Controllers.verify_only_one_active()

    def prompt_box(self):
        box = QMessageBox.question(self.interface, 'Before continuing', 'Would you like to save the current image?',
                                   buttons=QMessageBox.StandardButtons(QMessageBox.Yes | QMessageBox.No))
        if box == QMessageBox.Yes:
            self.save_the_image()
        else:
            return False

    def open_new_image(self):
        """file_name gives back a list"""
        if self.scene.return_scene_item_as_pixmap():
            if not self.prompt_box():
                self.__help_open_file()
        else:
            self.__help_open_file()

    def __help_open_file(self, open_pdf=False):
        if open_pdf:
            format_to_use = '*.pdf'
        else:
            format_to_use = '*.png *.jpg *.bmp *.raw'

        file_name, _ = QFileDialog.getOpenFileNames(self.interface, 'Open File', os.path.abspath(__name__),
                                                    f"Image Files({format_to_use})")
        if file_name:
            str_path = file_name[0]
            dial = PdfOpener(str_path)
            if open_pdf:
                dial.build_dialog()
                dial.show()
                dial.exec()
            if dial.pdf_path is not None:
                str_path = dial.pdf_path
            image = cv.imread(str_path)
            self.scene.load_image(image)

    def save_the_image(self):
        dialog: QFileDialog = QFileDialog()
        image_file, _ = dialog.getSaveFileName(self.interface, 'Save Image', '',
                                               "Image Files(*.png *.jpg *.bmp *.raw *.jpeg)")
        allowed = ['.png', '.jpg', '.bmp', '.raw', '.jpeg']
        if image_file:
            if all([not image_file.endswith(ending) for ending in allowed]):
                image_file = image_file + (allowed[0])
            self.scene.save_image_from_canvas(image_file)
        else:
            QMessageBox.information(self.interface, 'Message', 'The image was not saved', QMessageBox.Ok)

    def open_pdf_file(self):
        self.__help_open_file(open_pdf=True)

    def print_file(self):
        printer = QPrinter()
        if QPrintDialog(printer).exec() == QDialog.Accepted:
            painter = QPainter(printer)
            painter.setRenderHints(QPainter.Antialiasing)
            self.scene.render(painter)
            painter.end()

    def save_project(self):
        dialog: QFileDialog = QFileDialog()
        project_file, _ = dialog.getSaveFileName(self.interface, 'Project file', '',
                                                 "File(*.json)")
        if self.scene.return_scene_item_as_pixmap():
            if not project_file.endswith('.json'):
                project_file += '.json'
            with open(project_file, 'w') as file:
                file.write(json.dumps(self.scene.serialize(), indent=4))
        else:
            QMessageBox.information(self.interface,
                                    'Empty canvas', 'No image found to save for the project', QMessageBox.Ok)

    def load_project(self):
        file_name, _ = QFileDialog.getOpenFileNames(self.interface, 'Open File', os.path.abspath(__name__),
                                                    "Saved Files(*.json)")
        if file_name:
            with open(file_name[0], 'r') as file:
                raw_data = json.loads(file.read())
                self.scene.deserialize(raw_data)

    def transform_image(self, command):
        if self.scene.return_scene_item_as_pixmap():
            self.editor.get_image()
            if command == 'rotate_right':
                self.editor.do_rotation(-90)
            if command == 'rotate_left':
                self.editor.do_rotation(90)
            if command == 'flip_horizontally':
                self.editor.do_flip(-1)
            if command == 'flip_vertically':
                self.editor.do_flip(1)
            if command == 'custom_rotation':
                self.editor.do_rotation(self.holder.get_spin_value())
            if command == 'resize':
                self.editor.resize(self.holder.get_resize_value())
            if command == 'brightness':
                self.editor.brightness_options(self.interface)


    def undo(self):
        pass


if __name__ == '__main__':
    app = Controller()
    app.main()
