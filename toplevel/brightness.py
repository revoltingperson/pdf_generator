import time
from pathlib import Path
from threading import Thread
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QWidget, QSlider


class BrightnessWidget(QWidget):
    def __init__(self, image_editor):
        super().__init__()
        self.editor = image_editor
        path = Path.cwd().parent.joinpath('ui', 'brightness_filter.ui')
        uic.loadUi(path, self)
        self.brightness: QSlider = self.findChild(QSlider, 'brightness_slider')
        self.brightness.valueChanged.connect(lambda val: self.editor.changed_brightness(val))

        self.gamma = self.findChild(QSlider, 'gamma_slider')
        # self.gamma.valueChanged.connect(lambda val: editor.gamma_changed(val))
        self.setWindowFlag(Qt.Window)





