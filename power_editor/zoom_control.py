from PyQt5.QtCore import QRect
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QAction, QSlider
from checked_bundle import CheckedButtons


class ZoomEnableDisable(CheckedButtons):
    def __init__(self, controller):

        super().__init__()
        self.frame = QWidget(controller.view_widget)
        self.view_widget = controller.view_widget
        self.horizontal_slider = QSlider(self.frame)
        self.horizontal_slider.valueChanged.connect(lambda change: self.slider_slot(change))

        self.button = controller.interface.findChild(QAction, 'Zoom_In_Out')

        self.__zoom_in_factor = 1.3
        self.__zoom = 6
        self.__zoom_step = 1
        self.__lower_limit, self.__upper_limit = 0, 12
        self.__zoom_out_factor = 1 / self.__zoom_in_factor
        self.build_slider()

    def activate(self):
        self.last_active = True
        self.frame.show()

    def disable(self):
        self.last_active = False
        self.button.setChecked(False)
        self.frame.hide()

    def operate_zoom(self, event):
        if hasattr(event, 'angleDelta'):
            self.__wheel_zoom(event)
        elif self.button.isChecked() and event.key() == Qt.Key_Escape:
            self.disable()

    def __zoom_in(self):
        if self.__zoom < self.__upper_limit:
            zoom_fact = self.__zoom_in_factor
            self.__zoom += self.__zoom_step
            self.view_widget.scale(zoom_fact, zoom_fact)
            self.horizontal_slider.setSliderPosition(self.__zoom)

    def __zoom_out(self):
        if self.__zoom > self.__lower_limit:
            zoom_fact = self.__zoom_out_factor
            self.__zoom -= self.__zoom_step
            self.view_widget.scale(zoom_fact, zoom_fact)
            self.horizontal_slider.setSliderPosition(self.__zoom)

    def __wheel_zoom(self, event):
        if event.angleDelta().y() > 0:
            self.__zoom_in()
        else:
            self.__zoom_out()

    def build_slider(self):
        self.horizontal_slider.setGeometry(QRect(5, 10, 120, 20))
        self.horizontal_slider.setMaximum(12)
        self.horizontal_slider.setSliderPosition(self.__zoom)
        self.horizontal_slider.setOrientation(Qt.Horizontal)
        self.horizontal_slider.setTickPosition(QSlider.TicksAbove)
        self.frame.setStyleSheet("""
          border-radius: 15px;
          padding: 0px;
          background-color: #dff0fe
        """
                                 )
        self.frame.setGeometry(0, 0, 130, 40)
        self.frame.hide()

    def slider_slot(self, change):
        if change < self.__zoom:
            self.__zoom_out()
        if change > self.__zoom:
            self.__zoom_in()
