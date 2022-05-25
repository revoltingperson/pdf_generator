import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QTransform, QPixmap
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtWidgets import QFileDialog, QWidget, QMessageBox, QDialog, QGraphicsPixmapItem
from python_files.interface.pdf_dialog import PdfOpener
from python_files.model.image_editing import Model
from collection_of_controllers import ControllersHolder


class Controller:
    def __init__(self):
        from python_files.interface.interface import Interface

        self.model = Model()
        self.interface = Interface(self)
        self.__build_checked_button_actions()

    def main(self):
        self.interface.main()

    def __build_checked_button_actions(self):
        self.holder = ControllersHolder(self.interface)
        self.interface.scene.connect_text_items(self.holder.text_item)
        self.interface.view_widget.connect_zoom_controller(self.holder.zoom_control)

    def tool_bar_checked_buttons(self):
        self.holder.verify_one_one_active()

    def prompt_box(self):
        box = QMessageBox.question(self.interface, 'Before continuing', 'Would you like to save the current image?',
                                   buttons=QMessageBox.StandardButtons(QMessageBox.Yes | QMessageBox.No))
        if box == QMessageBox.Yes:
            self.save_the_image()
        else:
            return False

    def open_new_image(self):
        """file_name gives back a list"""
        if not self.interface.scene.image.isNull():
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
            self.interface.scene.load_image_to_canvas(str_path)

    def save_the_image(self):
        dialog: QFileDialog = QFileDialog()
        image_file, _ = dialog.getSaveFileName(self.interface, 'Save Image', '',
                                               "Image Files(*.png *.jpg *.bmp *.raw *.jpeg)")
        allowed = ['.png', '.jpg', '.bmp', '.raw', '.jpeg']
        if image_file:
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

    def check_if_pixmap_on_canvas(self) -> bool:
        for item in self.interface.scene.items():
            if isinstance(item, QGraphicsPixmapItem):
                return True
        return False

    def do_rotation(self, degree):
        if self.check_if_pixmap_on_canvas():
            rotated = self.interface.scene.image.transformed(QTransform().rotate(degree),
                                                             mode=Qt.SmoothTransformation)
            self.interface.scene.map_pixmap(rotated, new_image=False)

    def do_flip(self, x, y):
        if self.check_if_pixmap_on_canvas():
            flipped = self.interface.scene.image.transformed(QTransform().scale(x, y),
                                                             mode=Qt.SmoothTransformation)
            self.interface.scene.map_pixmap(flipped)

    def rotate_right(self):
        self.do_rotation(90)

    def rotate_left(self):
        self.do_rotation(-90)

    def flip_horizontally(self):
        self.do_flip(-1, 1)

    def flip_vertically(self):
        self.do_flip(1, -1)


if __name__ == '__main__':
    app = Controller()
    app.main()
