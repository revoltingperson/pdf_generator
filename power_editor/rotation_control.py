
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSpinBox, QPushButton, QAction
from checked_bundle import CheckedButtons


class Rotator(CheckedButtons):
    def __init__(self, interface, scene):
        super().__init__()
        self.scene = scene
        self.button = interface.custom_rotation

        self.frame = QWidget(scene.view_widget)
        self.new_layout = QHBoxLayout()
        self.frame.setLayout(self.new_layout)

        self.spin_box = QSpinBox()
        self.push = QPushButton()
        self.push.setText('Ok')
        self.push.clicked.connect(lambda rules: self.scene.map_pixmap_to_scene({'custom_rotation': self.spin_box.value()}))
        self.spin_box.setMaximum(360)
        self.spin_box.setMinimum(-360)
        self.new_layout.addWidget(self.spin_box)
        self.new_layout.addWidget(self.push)
        self.build_rotator()

    def activate(self):
        self.last_active = True
        self.frame.show()

    def disable(self):
        self.last_active = False
        self.button.setChecked(False)
        self.frame.hide()

    def build_rotator(self):
        self.frame.setGeometry(100, 0, 100, 50)
        self.frame.setStyleSheet('background-color: #dff0fe')
        self.frame.hide()



