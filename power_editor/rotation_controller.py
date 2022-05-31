
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSpinBox, QPushButton, QAction
from collection_of_controllers import CheckedControllers


class Rotator(CheckedControllers):
    def __init__(self, controller):
        super().__init__()
        self.button = controller.interface.findChild(QAction, 'Custom_rotation')

        self.frame = QWidget(controller.view_widget)
        self.new_layout = QHBoxLayout()
        self.frame.setLayout(self.new_layout)

        self.spin_box = QSpinBox()
        self.push = QPushButton()
        self.push.setText('Ok')
        self.push.clicked.connect(lambda command: controller.transform_image('custom_rotation'))
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



