from icons import new
from pathlib import Path
from python_files.controller.controller import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QResizeEvent, QIcon
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QGraphicsView, \
    QGraphicsScene, QSizePolicy, QDesktopWidget
from PyQt5 import uic


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
        path = Path.cwd().parent.parent.joinpath('ui', 'interface.ui')
        uic.loadUi(path, self)
        self.__initialize_all_groups()

    def main(self):
        self.show()
        self.app.exec_()

    def __initialize_all_groups(self):
        self.__initialize_menu_buttons()
        self.__set_working_background_to_work_with_graphics()
        self.__place_app_window_at_screencenter()
        self.__initialize_tool_bar()

    def __initialize_menu_buttons(self):
        image_open = self.findChild(QAction, 'actionOpen_Image')
        image_open.triggered.connect(self.controller.open_new_image)

    def __initialize_tool_bar(self):
        zoom_button: QAction = self.findChild(QAction, 'Zoom_In_Out')
        zoom_button.triggered.connect(self.controller.activate_zoom_action)

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
        self.scene.setSceneRect(self.XY_ZERO, self.XY_ZERO, image.width(), image.height())
        self.main_canvas.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.main_canvas.setMaximumSize(int(self.scene.width())+self.FRAME_CORRECTOR,
                                        int(self.scene.height())+self.FRAME_CORRECTOR)
        # print(f'graphicsScene {self.scene.width(), self.scene.height()}')
        # print(f'canvas {self.main_canvas.width(), self.main_canvas.height()}')
        self.__fix_scrollbar_appear_when_reduce_y_axis()

    def __fix_scrollbar_appear_when_reduce_y_axis(self):
        if self.main_canvas.width() > self.scene.width():
            self.main_canvas.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            # print("====from inside adder function====")
            # print(f'====scene {self.scene.sceneRect()}, GraphicsView {self.main_canvas.geometry()}====')
        else:
            self.main_canvas.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.__fix_scrollbar_appear_when_reduce_y_axis()
        QMainWindow.resizeEvent(self, event)

