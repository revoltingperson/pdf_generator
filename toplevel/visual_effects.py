import time
from pathlib import Path
from threading import Thread
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QWidget, QSlider

from power_editor.image_editor import ImageEditor


class BrightnessWidget(QWidget):
    def __init__(self, image_editor: ImageEditor):
        super().__init__()
        self.editor = image_editor
        path = Path.cwd().parent.joinpath('ui', 'brightness_filter.ui')
        uic.loadUi(path, self)
        self.brightness: QSlider = self.findChild(QSlider, 'brightness_slider')
        self.brightness.valueChanged.connect(lambda val: self.editor.last_bright_val(val))
        self.gamma = self.findChild(QSlider, 'gamma_slider')
        self.gamma.valueChanged.connect(lambda val: self.editor.set_last_gamma(val))
        self.blur = self.findChild(QSlider, 'blur')
        self.blur.valueChanged.connect(lambda val: self.editor.set_last_blur(val))

        self.brightness.valueChanged.connect(self.editor.set_all_filters)
        self.blur.valueChanged.connect(self.editor.set_all_filters)
        self.gamma.valueChanged.connect(self.editor.set_all_filters)
        self.brightness.sliderReleased.connect(self.editor.create_stamp_on_slider_release)
        self.gamma.sliderReleased.connect(self.editor.create_stamp_on_slider_release)
        self.blur.sliderReleased.connect(self.editor.create_stamp_on_slider_release)

        self.setWindowFlag(Qt.Window)

    def hello(self):
        print('hello')




