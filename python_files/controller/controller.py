from python_files.interface.interface import *
import os
from PyQt5.QtWidgets import QFileDialog, QWidget

from python_files.model.calculations import Model
from zoom_controller import ZoomInOut


class Controller:
    def __init__(self):
        self.model = Model()
        self.interface = Interface(self)

    def main(self):
        self.interface.main()

    def open_new_image(self):
        file_name, _ = QFileDialog.getOpenFileNames(self.interface, 'Open File', os.path.abspath(__name__),
                                                 "Image Files(*.png *.jpg *.bmp *.pdf *.raw)")
        """file_name gives back a list"""
        if file_name:
            self.interface.load_image_to_canvas(file_name[0])

    def activate_zoom_action(self):
        ZoomInOut(self.interface)


if __name__ == '__main__':
    app = Controller()
    app.main()
