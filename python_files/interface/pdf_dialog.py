from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QPushButton, QSpinBox
from pathlib import Path
from pdf2image import convert_from_path
import os

class PdfOpener(QDialog):
    def __init__(self, pdf_path):
        super().__init__()
        self.page_num = 0
        self.temp = pdf_path
        self.pdf_path = None

    def build_dialog(self):
        self.pdf_path = self.temp
        path = Path.cwd().parent.parent.joinpath('ui', 'pdf_dialog.ui')
        uic.loadUi(path, self)
        self.__connect_buttons()

    def __connect_buttons(self):
        buttons: QDialogButtonBox = self.findChild(QDialogButtonBox, 'buttonBox')
        ok, cancel = buttons.buttons()
        ok.clicked.connect(self.__accept)
        cancel.clicked.connect(self.__reject)

    def __accept(self):
        spinbox: QSpinBox = self.findChild(QSpinBox, 'spinBox')
        self.page_num = spinbox.value()
        self.__convert_pdf_to_image()
        self.close()

    def __reject(self):
        self.close()

    def __convert_pdf_to_image(self):
        with Path.cwd().parent.parent.joinpath('temp') as path:
            self.__navigate_through_directories(path)
            image_from_pdf = convert_from_path(self.pdf_path,
                                               fmt='jpg',
                                               first_page=self.page_num,
                                               last_page=self.page_num,
                                               output_file='from_pdf',
                                               output_folder=path)
            self.__navigate_through_directories(path, removal_mode=False)

    def __navigate_through_directories(self, directory_to_img_file: Path, removal_mode=True):
        for entry in directory_to_img_file.iterdir():
            if 'from_pdf' in entry.name:
                if removal_mode:
                    os.remove(os.path.join(directory_to_img_file, entry))
                else:
                    complete = os.path.join(directory_to_img_file, entry)
                    self.pdf_path = complete
