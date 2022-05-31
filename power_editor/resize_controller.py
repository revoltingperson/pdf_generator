from PyQt5.QtWidgets import QAction, QWidget, QSpinBox, QPushButton, QHBoxLayout, QLabel

from collection_of_controllers import CheckedControllers


class Resizer(CheckedControllers):
    def __init__(self, controller):
        super().__init__()
        self.button = controller.interface.findChild(QAction, 'Resize_image')
        self.controller = controller
        self.frame = QWidget(controller.view_widget)
        self.new_layout = QHBoxLayout()
        self.frame.setLayout(self.new_layout)

        self.width_box = QSpinBox()
        self.height_box = QSpinBox()
        self.push = QPushButton()
        label_x, label_y = QLabel(), QLabel()
        label_x.setText('W:')
        label_y.setText('H:')
        self.push.setText('Ok')
        self.push.clicked.connect(controller.resize)
        self.width_box.setMaximum(9999)
        self.height_box.setMaximum(9999)
        self.width_box.setMinimum(1)
        self.height_box.setMinimum(1)

        self.new_layout.addWidget(label_x)
        self.new_layout.addWidget(self.width_box)
        self.new_layout.addWidget(label_y)
        self.new_layout.addWidget(self.height_box)
        self.new_layout.addWidget(self.push)
        self.build_resizer()

    def activate(self):
        self.last_active = True
        width, height = self.controller.scene.return_size_of_image()
        self.width_box.setValue(width)
        self.height_box.setValue(height)
        self.frame.show()

    def disable(self):
        self.last_active = False
        self.button.setChecked(False)
        self.frame.hide()

    def build_resizer(self):
        self.frame.setGeometry(200, 0, 250, 50)
        self.frame.setStyleSheet('background-color: #dff0fe')
        self.frame.hide()




