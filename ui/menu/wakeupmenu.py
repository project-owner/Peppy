# Copyright 2018-2020 Peppy Player peppy.player@gmail.com
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

import pygame

from ui.container import Container
from ui.layout.borderlayout import BorderLayout
from ui.button.button import Button
from ui.factory import Factory
from util.config import COLOR_DARK, COLORS, TIMER, WAKE_UP, WAKE_UP_TIME
from util.keys import kbd_keys, KEY_BACK, LABELS
from ui.flipclock.clock import Clock

class WakeUpMenu(Container):
    """ Wake up menu """
    
    def __init__(self, util, bb, gap, digits, listener, timer_lock, clock_change_callback, change_codes):
        """ Initializer
        
        :param util: utility object
        :param bb: menu bounding box
        :param gap: gap between hours and minutes
        :param digits: clock digits 0-9
        :param listener: the listener
        :param timer_lock: lock object
        :param clock_change_callback: callback function
        :param change_codes: change codes
        """   
        self.util = util
        self.name = WAKE_UP
        self.config = self.util.config
        self.factory = Factory(util)
        icon_size = 0.43
        Container.__init__(self, util, bb.CENTER)
        self.bgr = (0, 0, 0, 0)
        
        self.clock = Clock(self.util, WAKE_UP, WAKE_UP_TIME, digits, bb, gap, icon_size, timer_lock, clock_change_callback, change_codes)
        self.add_component(self.clock)
        
        border_x = bb.RIGHT.x
        d = {}
        d["name"] = WAKE_UP
        d["bounding_box"] = pygame.Rect(border_x + 1, bb.y + 1, bb.w - border_x, bb.h - 1)
        d["keyboard_key"] = kbd_keys[KEY_BACK]
        d["image_size_percent"] = icon_size
        
        switch_on = self.config[TIMER][WAKE_UP]
        self.button_selected = switch_on
        self.button = self.factory.create_timer_button(**d)
        self.button.set_selected(switch_on)
        self.button.add_release_listener(listener)
        
        self.add_component(self.button)

    def set_parent_screen(self, scr):
        """ Add parent screen

        :param scr: parent screen
        """
        self.button.set_parent_screen(scr)

    def add_menu_observers(self, update_observer, redraw_observer=None):
        """ Add menu observer
        
        :param update_observer: observer for updating menu
        :param redraw_observer: observer to redraw the whole screen
        """
        
        self.clock.add_menu_observers(update_observer, redraw_observer)
        self.button.add_release_listener(redraw_observer)        
