from PyQt5.QtGui import QPainter, QWheelEvent
from PyQt5.QtWidgets import QGraphicsView
from power_editor.zoom_control import ZoomEnableDisable


class MainView(QGraphicsView):
    zoom_control: ZoomEnableDisable

    def __init__(self, layout):
        super().__init__()
        layout.addWidget(self)
        self.__create_settings()

    def __create_settings(self):
        self.setMouseTracking(True)
        self.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing
                            | QPainter.SmoothPixmapTransform | QPainter.TextAntialiasing)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def connect_zoom_controller(self, zoom_obj):
        self.zoom_control: ZoomEnableDisable = zoom_obj

    def wheelEvent(self, event: QWheelEvent) -> None:
        self.zoom_control.operate_zoom(event)




