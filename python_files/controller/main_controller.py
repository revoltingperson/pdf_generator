import os
from PyQt5.QtGui import QPainter
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtWidgets import QFileDialog, QWidget, QMessageBox, QDialog
from pathlib import Path
from python_files.interface.pdf_dialog import PdfOpener
from python_files.model.calculations import Model
from collection_of_controllers import ControllerStateHolder


class Controller:
    def __init__(self):
        from python_files.interface.interface import Interface

        self.model = Model()
        self.interface = Interface(self)
        self.__build_action_objects()

    def main(self):
        self.interface.main()

    def __build_action_objects(self):
        from text_in_image_controller import TextItem
        from zoom_controller import ZoomEnableDisable

        self.zoom_control = ZoomEnableDisable(self.interface)
        self.interface.view_widget.connect_zoom_controller(self.zoom_control)

        self.text_to_image = TextItem(self.interface)
        self.interface.view_widget.connect_text_items(self.text_to_image)

    def tool_bar_actions(self):
        ControllerStateHolder.verify_only_one_active()

    def open_new_image(self):
        """file_name gives back a list"""
        if not self.interface.scene.image.isNull():
            box = QMessageBox.question(self.interface, 'Before continuing', 'Save before opening another image?',
                                       buttons=QMessageBox.StandardButtons(QMessageBox.Yes | QMessageBox.No))
            if box == QMessageBox.Yes:
                self.save_the_image()
            else:
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
            self.interface.scene.load_image_to_canvas(str_path)

    def save_the_image(self):
        dialog: QFileDialog = QFileDialog()
        image_file, _ = dialog.getSaveFileName(self.interface, 'Save Image', '',
                                               "Image Files(*.png *.jpg *.bmp *.raw *.jpeg)")
        allowed = ['.png', '.jpg', '.bmp', '.raw', '.jpeg']
        if image_file:
            # and not self.interface.scene.image.isNull()
            if all([not image_file.endswith(ending) for ending in allowed]):
                image_file = image_file + (allowed[0])
            self.interface.scene.save_image_from_canvas(image_file)
        else:
            QMessageBox.information(self.interface, 'Message', 'The image was not saved', QMessageBox.Ok)

    def open_pdf_file(self):
        self.__help_open_file(open_pdf=True)

    def print_file(self):
        printer = QPrinter()
        if QPrintDialog(printer).exec() == QDialog.Accepted:
            painter = QPainter(printer)
            painter.setRenderHints(QPainter.Antialiasing)
            self.interface.scene.render(painter)
            painter.end()





if __name__ == '__main__':
    app = Controller()
    app.main()
