# Copyright 2021 Peppy Player peppy.player@gmail.com
# 
# This file is part of Peppy Player.
# 
# Peppy Player is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Peppy Player is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Peppy Player. If not, see <http://www.gnu.org/licenses/>.

import os
from util.keys import KEY_SWITCH, NAME, KEY_POWER_ON
import time

from ui.factory import Factory
from ui.menu.menu import Menu
from ui.layout.buttonlayout import TOP
from ui.button.imagebutton import ImageButton
from threading import Thread

ICON_LOCATION = TOP
BUTTON_PADDING = 5
ICON_AREA = 70
ICON_SIZE = 70
FONT_HEIGHT = 58

SWITCH_OFF_DELAY = 3

class SwitchMenu(Menu):
    """ Switch Menu class """
    
    def __init__(self, util, bgr=None, bounding_box=None):
        """ Initializer
        
        :param util: utility object
        :param bgr: menu background
        :param bounding_box: bounding box
        """
        self.util = util
        self.factory = Factory(util)
        self.folder = os.path.join(os.getcwd(), KEY_SWITCH)
        d = util.config[KEY_SWITCH]
        d_num = len(d)

        if d_num == 0:
            rows_num = 0
            cols_num = 0
        if d_num == 1:
            rows_num = 1
            cols_num = 1
        elif d_num == 2:
            rows_num = 1
            cols_num = 2
        elif d_num == 3:
            rows_num = 1
            cols_num = 3
        elif d_num == 4:
            rows_num = 2
            cols_num = 2
        elif d_num == 5 or d_num == 6:
            rows_num = 2
            cols_num = 3
        elif d_num == 7 or d_num == 8:
            rows_num = 2
            cols_num = 4

        m = self.create_switch_menu_button

        label_area = (bounding_box.h / rows_num / 100) * (100 - ICON_AREA)
        font_size = int((label_area / 100) * FONT_HEIGHT)
        Menu.__init__(self, util, bgr, bounding_box, rows=rows_num, cols=cols_num, create_item_method=m, font_size=font_size)
        self.config = self.util.config
        
        self.disks = self.util.load_disk_switch_menu(d)

        layout = self.get_layout(d)        
        button_rect = layout.constraints[0]
        label_area = (button_rect.h / 100) * (100 - ICON_AREA)
        self.font_size = int((label_area / 100) * FONT_HEIGHT)

        self.set_items(self.disks, 0, self.switch_disk, False, fill=True)
        self.select_by_index(0)

    def create_switch_menu_button(self, state, bb, action=None, scale=None, font_size=None):
        """ Create switch menu button
        
        :param state: button state
        :param bb: bounding box
        :param action: event listener
        
        :return: switch menu button
        """
        return ImageButton(self.util, state, self.folder, bb, action)

    def switch_disk(self, state):
        """ Switch disk on/off
        
        :param state: button state
        """
        name = getattr(state, "name", None)
        if not self.visible or not name:
            return

        button = self.get_selected_item()
        if button:
            button.switch_button()

        for disk in self.util.config[KEY_SWITCH]:
            if state.name == disk[NAME]:
                disk[KEY_POWER_ON] = state.button_on
                if state.button_on:
                    thread = Thread(target=self.switch_on, args=[state])
                else:
                    thread = Thread(target=self.switch_off, args=[state])
                thread.start()

    def switch_on(self, state):
        """ Switch on thread function

        :param state: button state
        """
        self.notify_listeners(state)
        self.util.switch_util.switch_power()

    def switch_off(self, state):
        """ Switch off thread function

        :param state: button state
        """
        self.notify_listeners(state)
        time.sleep(SWITCH_OFF_DELAY)
        self.util.switch_util.switch_power()
        