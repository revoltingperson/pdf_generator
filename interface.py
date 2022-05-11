from controller import *
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QColor, QBrush, QResizeEvent
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QMenu, QAction, QFileDialog, QLabel, QGraphicsView, \
    QGraphicsScene, QSizePolicy, QDesktopWidget
from PyQt5 import uic
from typing import Type
import os


class Interface(QMainWindow):
    scene: QGraphicsScene
    main_canvas: QGraphicsView
    XY_ZERO = 0
    #fixes appearance of scrollbars for smaller images
    FRAME_CORRECTOR = 2

    def __init__(self, controller: Controller):
        self.app = QApplication(sys.argv)
        super().__init__()
        self.controller = controller
        uic.loadUi('ui/interface.ui', self)
        self.__initialize_all_groups()

    def main(self):
        self.show()
        self.app.exec_()

    def __initialize_all_groups(self):
        self.__initialize_menu_buttons()
        self.__set_working_background_to_work_with_graphics()
        self.__place_app_window_at_screencenter()

    def __initialize_menu_buttons(self):
        image_open = self.findChild(QAction, 'actionOpen_Image')
        image_open.triggered.connect(self.controller.open_new_image)

    def __set_working_background_to_work_with_graphics(self):
        scene = QGraphicsScene(self)
        wid = self.findChild(QGraphicsView, 'test')
        wid.setScene(scene)
        self.main_canvas = wid
        self.scene = scene

    def __place_app_window_at_screencenter(self):
        desktop = QDesktopWidget().screenGeometry()
        screen_width = desktop.width()
        screen_height = desktop.height()
        self.move((screen_width - self.width()) // 2, (screen_height - self.height()) // 2)

    def load_image_to_canvas(self, image):
        image = QPixmap(image)
        self.scene.clear()
        self.scene.addPixmap(image)
        self.main_canvas.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.main_canvas.setMaximumSize(image.width()+self.FRAME_CORRECTOR,
                                        image.height()+self.FRAME_CORRECTOR)
        print(self.scene.width(), self.scene.height())
        self.scene.setSceneRect(self.XY_ZERO, self.XY_ZERO, image.width(), image.height())
        print(f'canvas {self.main_canvas.width(), self.main_canvas.height()}')
        # self.__add_pixels_to_x_axis_to_remove_scroll_bars()
        # print(self.scene.width(), self.scene.height())
        # print(self.scene.sceneRect())

    def __add_pixels_to_x_axis_to_remove_scroll_bars(self):
        # it is a hackish way to remove needless scrollbars when loading an image to canvas
        # and its width is small enough to fit without any scrollbars
        central_widget: QWidget = self.findChild(QWidget, 'centralwidget')
        cen_height = central_widget.height()
        if cen_height < self.scene.height():
            self.main_canvas.setMaximumSize(self.main_canvas.width() + 10 ,self.main_canvas.height())
            print("from inside adder function")
            print(self.scene.width(), self.scene.height())
            print(f'canvas {self.main_canvas.width(), self.main_canvas.height()}')

            self.scene.setSceneRect(self.XY_ZERO, self.XY_ZERO,
                                    self.scene.width() + 10, self.scene.height())


