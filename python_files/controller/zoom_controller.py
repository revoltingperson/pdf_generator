from PyQt5.QtCore import Qt
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.QtWidgets import QWidget, QAction

from checked_builder import CheckedControllers


class ZoomEnableDisable(CheckedControllers):
    def __init__(self, interface):
        from python_files.interface.interface import Interface
        super().__init__()
        self.zoom_active = False

        self.__zoom_in_factor = 1.3
        self.__zoom = 6
        self.__zoom_step = 1
        self.__lower_limit, self.__upper_limit = 0, 12
        self.__zoom_out_factor = 1 / self.__zoom_in_factor

        self.ui: Interface = interface
        self.central_widget: QWidget = self.ui.findChild(QWidget, 'CentralWidget')
        self.button: QAction = self.ui.findChild(QAction, 'Zoom_In_Out')


    def activate(self):
        zoom_cursor = QPixmap(":/icons/active-zoom.png")
        cursor = QCursor(zoom_cursor)
        self.central_widget.setCursor(cursor)
        self.zoom_active = True
        self.last_active = True

    def disable(self):
        cursor = QCursor()
        cursor.setShape(Qt.ArrowCursor)
        self.central_widget.setCursor(cursor)
        self.zoom_active = False
        self.last_active = False
        self.button.setChecked(False)

    def operate_zoom(self, event):
        if self.zoom_active and hasattr(event, 'button'):
            if event.button() == Qt.LeftButton:
                self.__zoom_in()
            elif event.button() == Qt.RightButton:
                self.__zoom_out()
        elif hasattr(event, 'angleDelta'):
            self.__wheel_zoom(event)
        elif self.zoom_active and event.key() == Qt.Key_Escape:
            self.disable()

    def __zoom_in(self):
        if self.__zoom < self.__upper_limit:
            zoom_fact = self.__zoom_in_factor
            self.__zoom += self.__zoom_step
            self.ui.view_widget.scale(zoom_fact, zoom_fact)

    def __zoom_out(self):
        if self.__zoom > self.__lower_limit:
            zoom_fact = self.__zoom_out_factor
            self.__zoom -= self.__zoom_step
            self.ui.view_widget.scale(zoom_fact, zoom_fact)

    def __wheel_zoom(self, event):
        if event.angleDelta().y() > 0:
            self.__zoom_in()
        else:
            self.__zoom_out()

