from PyQt5.QtGui import QPixmap


class HistoryStack:
    def __init__(self):
        self.history_memory = []

    def add_pix_to_memory(self, pix: QPixmap):
        copied = pix.copy()
        self.history_memory.append(copied)