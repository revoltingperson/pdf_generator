import time
from pathlib import Path
from threading import Thread
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QWidget, QSlider


class BrightnessWidget(QWidget):
    __instance__ = None

    def __init__(self, parent, editor):
        if BrightnessWidget.__instance__ is None:
            BrightnessWidget.__instance__ = self
        else:
            return

        super().__init__(parent)
        path = Path.cwd().parent.joinpath('ui', 'brightness_filter.ui')
        uic.loadUi(path, self)
        self.editor = editor
        self.brightness: QSlider = self.findChild(QSlider, 'brightness_slider')
        self.brightness.setValue(self.editor.last_brightness)
        self.brightness.valueChanged.connect(lambda val: editor.changed_brightness(val, self.editor.input_image))

        self.gamma = self.findChild(QSlider, 'gamma_slider')
        self.gamma.valueChanged.connect(lambda val: editor.gamma_changed(val))
        self.setWindowFlag(Qt.Window)
        self.show()

    def closeEvent(self, event: QCloseEvent) -> None:
        BrightnessWidget.__instance__ = None



