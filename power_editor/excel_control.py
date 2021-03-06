from string import Template

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, QObject, QRectF
from PyQt5.QtGui import QFont
from power_editor.checked_bundle import CheckedButtons
from power_editor.text_in_image_control import ClickableText, CommunicateChange
from toplevel.excel_control_window import ExcelWindow


class ExcelItem(ClickableText):
    width_inner = 150
    height_inner = 50

    def __init__(self, position, rect=QRectF(0, 0, width_inner, height_inner)):
        super().__init__(position, rect, extend_paint=True)
        self.input_field.text_edit.setText('Your Excel text goes here')
        self.input_field.text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.input_field.text_edit.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.excel_window = ExcelWindow()
        self.communicate = CommunicateChange()
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

    def communicate_new_position(self):
        self.communicate.position_new.emit()

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
            item.communicate.position_new.connect(self.scene.memorize_change_on_scene)

            self.excel_item = item
            self.excel_item.signal.pdf_complete[list].connect(lambda excel: self.send_to_scene(excel))
            self.disable()
            self.remove_old_instance()
            self.scene.addItem(item)
            item.setSelected(True)
            self.scene.memorize_change_on_scene()

    def capture_format(self):
        self.format_saved = self.excel_item.serialize()

    def remove_old_instance(self):
        excel = self.find_excel()
        if excel:
            excel.excel_window.destroy()
            self.scene.removeItem(excel)

    def find_excel(self):
        for scene_item in self.scene.items():
            if scene_item.__class__ == ExcelItem:
                return scene_item

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

    def call_json_loader(self, data):
        item_ready = self.load_from_json(ExcelItem, data['item'])
        item_ready.excel_window.deserialize(data['window'])
        item_ready.communicate.position_new.connect(self.scene.memorize_change_on_scene)
        self.scene.addItem(item_ready)


