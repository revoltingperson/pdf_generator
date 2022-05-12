from python_files.interface.interface import *
from icons import new
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QCursor
from PyQt5.QtWidgets import QWidget, QAction


class ZoomInOut:
    def __init__(self, interface):
        self.ui = interface
        self.central_widget: QWidget = self.ui.findChild(QWidget, 'centralwidget')
        self.zoom_button: QAction = self.ui.findChild(QAction, 'Zoom_In_Out')
        self.zoom_active = False
        if self.zoom_button.isChecked():
            self.__activate_zoom()
        else:
            self.__disable_zoom()

    def __zoom_in(self):
        pass

    def __activate_zoom(self):
        zoom_cursor = QPixmap(":/icons/active-zoom.png")
        cursor = QCursor(zoom_cursor)
        self.central_widget.setCursor(cursor)
        self.zoom_active = True

    def __disable_zoom(self):
        cursor = QCursor()
        cursor.setShape(Qt.ArrowCursor)
        self.central_widget.setCursor(cursor)
        self.zoom_active = False


