from string import Template

from PyQt5.QtCore import QPointF, QRectF
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QAction


class Collector:
    all_checked = []

    @staticmethod
    def verify_only_one_active():
        Collector.__disable_last_controller()
        Collector.__activate_new_controller()

    @staticmethod
    def __disable_last_controller():
        for controller in Collector.all_checked:
            if controller.last_active:
                controller.disable()

    @staticmethod
    def __activate_new_controller():
        for controller in Collector.all_checked:
            if controller.button.isChecked():
                controller.activate()


class CheckedButtons(Collector):
    def __init__(self):
        self.last_active = False
        self.all_checked.append(self)
        self.button = QAction

    def activate(self):
        self.last_active = True

    def disable(self):
        self.last_active = False
        self.button.setChecked(False)

    @staticmethod
    def load_from_json(cls_name, data):
        wid, height = data['width'], data['height']
        x, y = data['position'][0], data['position'][1]
        position = QPointF(x, y)
        item = cls_name(position, rect=QRectF(0, 0, wid, height))
        text = data['text']
        r, g, b, a = data['color']
        font = data['font']
        split_font = font.split(',')
        family, size, weight, italics = split_font[0], split_font[1], split_font[4], split_font[5]

        item.input_field.text_edit.setText(text)
        item.input_field.text_edit.setFont(QFont(family, int(size), int(weight), int(italics)))
        set_c = Template("QTextEdit {color: rgb($r, $g, $b);}")
        formatted = set_c.safe_substitute(r=r, g=g, b=b)
        item.input_field.text_edit.setStyleSheet(formatted)

        return item




