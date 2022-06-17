from PyQt5.QtGui import QPixmap
from dataclasses import dataclass
import pprint
from power_editor.image_editor import ImageEditor
# when we load pix from history stack we should not append it to history stack right away
# on any new action with pixmap -> append new action to history_memory


@dataclass(frozen=True)
class HistoryStamp:
    pixmap: QPixmap
    rotation: int
    brightness: int
    gamma: int
    blur: int
    grey: bool
    serialized: dict


class HistoryStack:
    staging_step = 0

    def __init__(self):
        self.__history_stack = []
        self._current_step = 0
        self._current_stamp = object
        self.stack_empty = True
        self.__history_limit = False

    def add_pix_to_memory(self, pix: QPixmap, editor: ImageEditor, all_items):

        history_stamp = HistoryStamp(pix.copy(),
                                     editor.last_custom_rot,
                                     editor.last_brightness,
                                     editor.last_gamma,
                                     editor.last_blur,
                                     editor.grey,
                                     all_items)
        self.__prepare_stack_for_a_stamp(history_stamp)

    def __prepare_stack_for_a_stamp(self, new_stamp):
        self.__clear_irrelevant_history()
        self.__history_stack.append(new_stamp)
        self.__refresh_current_step()
        pp = pprint.PrettyPrinter(indent=4)
        print(f'all stack : {pp.pprint(self.__history_stack)}')
        # pp.pprint(self.__history_stack[:self._current_step])
        print(f'current step {self._current_step} len {len(self.__history_stack)}')

    def clear_history(self):
        self.__history_stack.clear()

    def __clear_irrelevant_history(self):
        self.__history_stack = self.__history_stack[:self._current_step + 1]

    def __refresh_current_step(self):
        self._current_step = len(self.__history_stack) - 1
        self.reassign_steps()

    def restore_from_history(self, forward: bool):
        if forward:
            self.__travel_forward()
        else:
            self.__travel_back()

    def retrieve_stamp(self):
        if not self.stack_empty and not self.__history_limit:
            self._current_stamp = self.__history_stack[self._current_step]
            return self._current_stamp
        return False

    def __travel_forward(self):
        if self.__history_stack:
            self._current_step += 1
            self.reassign_steps()
            self.stack_empty = False

    def __travel_back(self):
        if self.__history_stack:
            self._current_step -= 1
            self.reassign_steps()
            print(f'travelled back, current step: {self._current_step}')
            self.stack_empty = False

    def reassign_steps(self):
        if self._current_step < self.staging_step:
            self._current_step = self.staging_step
            self.__history_limit = True
        elif self._current_step > len(self.__history_stack) - 1:
            self._current_step = len(self.__history_stack) - 1
            self.__history_limit = True
        else:
            self.__history_limit = False
