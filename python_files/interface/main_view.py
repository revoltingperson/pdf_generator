from PyQt5.QtGui import QPainter, QMouseEvent, QWheelEvent
from PyQt5.QtWidgets import QGraphicsView, QWidget, QVBoxLayout
from python_files.controller.zoom_controller import ZoomEnableDisable


class MainView(QGraphicsView):
    zoom_control: ZoomEnableDisable

    def __init__(self, interface):

        # wid = interface.findChild(QWidget, 'CentralWidget')
        super().__init__()
        layout: QVBoxLayout = interface.findChild(QVBoxLayout, 'verticalLayout')
        layout.addWidget(self)
        self.interface = interface
        self.__create_settings()


    def __create_settings(self):
        self.setMouseTracking(True)
        self.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing
                            | QPainter.SmoothPixmapTransform | QPainter.TextAntialiasing)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)


    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.zoom_control.operate_zoom(event)
        self.text_item.operate_text_editor(event)
        print(f'{event.button()}, {event.x(), event.y()}')
        super(MainView, self).mousePressEvent(event)


    def connect_zoom_controller(self, zoom_obj):
        self.zoom_control: ZoomEnableDisable = zoom_obj

    def connect_text_items(self, text_obj):
        self.text_item = text_obj

    def wheelEvent(self, event: QWheelEvent) -> None:
        self.zoom_control.operate_zoom(event)




