from PyQt5.QtCore import Qt, QRect
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.QtWidgets import QWidget, QAction, QSlider, QFrame, QToolBar
from checked_builder import CheckedControllers


class ZoomEnableDisable(CheckedControllers):
    def __init__(self, interface):
        from python_files.interface.interface import Interface
        super().__init__(interface)
        self.__zoom_in_factor = 1.3
        self.__zoom = 6
        self.__zoom_step = 1
        self.__lower_limit, self.__upper_limit = 0, 12
        self.__zoom_out_factor = 1 / self.__zoom_in_factor

        self.interface: Interface = interface
        self.central_widget: QWidget = self.interface.findChild(QWidget, 'CentralWidget')
        self.button: QAction = self.interface.findChild(QAction, 'Zoom_In_Out')
        # self.build_slider()


    def operate_zoom(self, event):
        if self.button.isChecked() and hasattr(event, 'button'):
            if event.button() == Qt.LeftButton:
                self.__zoom_in()
            elif event.button() == Qt.RightButton:
                self.__zoom_out()
        elif hasattr(event, 'angleDelta'):
            self.__wheel_zoom(event)
        elif self.button.isChecked() and event.key() == Qt.Key_Escape:
            self.disable()

    def __zoom_in(self):
        if self.__zoom < self.__upper_limit:
            zoom_fact = self.__zoom_in_factor
            self.__zoom += self.__zoom_step
            self.interface.view_widget.scale(zoom_fact, zoom_fact)

    def __zoom_out(self):
        if self.__zoom > self.__lower_limit:
            zoom_fact = self.__zoom_out_factor
            self.__zoom -= self.__zoom_step
            self.interface.view_widget.scale(zoom_fact, zoom_fact)

    def __wheel_zoom(self, event):
        if event.angleDelta().y() > 0:
            self.__zoom_in()
        else:
            self.__zoom_out()


    def build_slider(self):
        # <widget class="QToolBar" name="toolBar">
        tool = self.interface.findChild(QToolBar, 'toolBar')
        print(tool.pos())
        self.frame = QFrame(self.interface.view_widget)
        self.frame.setStyleSheet('background-color: rgb(255,255,255);')
        self.horizontalSlider = QSlider(self.frame)
        self.horizontalSlider.setObjectName(u"horizontalSlider")
        self.horizontalSlider.setGeometry(QRect(0, 10, 160, 16))
        self.horizontalSlider.setMaximum(12)
        self.horizontalSlider.setSliderPosition(6)
        self.horizontalSlider.setOrientation(Qt.Horizontal)

