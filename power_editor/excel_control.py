from string import Template

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, QObject
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QAction
from checked_bundle import CheckedButtons
from text_in_image_control import ClickableText
from toplevel.excel_control_window import ExcelWindow


class ExcelItem(ClickableText):
    def __init__(self, position):
        super().__init__(position, extend_paint=True)
        self.input_field.text_edit.setText('Your Excel text will look like this')
        self.input_field.text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.input_field.text_edit.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.excel_window = ExcelWindow()
        self.excel_window.show()
        self.signal = self.Signaler()
        self.excel_window.window_signal[list].connect(lambda incoming: self.receive_excel_data(incoming))
        self.input_field.text_edit.double_click[bool].connect(lambda x: self.open_close_window(x))

    def extend_paint_action(self, painter):
        if not self.isSelected():
            self.excel_window.hide()

    def mouseDoubleClickEvent(self, event):
        self.excel_window.show()

    @pyqtSlot(bool)
    def open_close_window(self, check):
        if check:
            self.excel_window.show()

    @pyqtSlot(list)
    def receive_excel_data(self, incoming):
        self.setSelected(False)
        self.signal.pdf_complete[list].emit(incoming)

    class Signaler(QObject):
        pdf_complete = pyqtSignal(list)


class ExcelControl(CheckedButtons, QObject):
    excel_item: ExcelItem

    def __init__(self, interface, scene):
        super().__init__()
        self.controller = interface.controller
        self.scene = scene
        self.button = interface.excel_input
        self.format_saved = {}

    def create_on_click(self, event):
        position = event.scenePos()
        if self.button.isChecked():
            item = ExcelItem(position)
            self.excel_item = item
            self.excel_item.signal.pdf_complete[list].connect(lambda excel: self.send_to_scene(excel))
            self.disable()
            self.remove_old_instance()
            self.scene.addItem(item)
            item.setSelected(True)

    def capture_format(self):
        self.format_saved = self.excel_item.serialize()

    def remove_old_instance(self):
        for scene_item in self.scene.items():
            if scene_item.__class__ == ExcelItem:
                scene_item.excel_window.destroy()
                self.scene.removeItem(scene_item)

    @pyqtSlot(list)
    def send_to_scene(self, excel):
        self.capture_format()
        self.controller.print_file(excel, pdf_generator=True)

    def insert_with_right_format(self, line):
        font = self.format_saved['font']
        r, g, b, a = self.format_saved['color']

        split_font = font.split(',')
        family, size, weight, italics = split_font[0], split_font[1], split_font[4], split_font[5]

        self.excel_item.input_field.text_edit.setText(line)
        self.excel_item.input_field.text_edit.setFont(QFont(family, int(size), int(weight), int(italics)))
        set_c = Template("QTextEdit {color: rgb($r, $g, $b);}")
        formatted = set_c.safe_substitute(r=r, g=g, b=b)
        self.excel_item.input_field.text_edit.setStyleSheet(formatted)



