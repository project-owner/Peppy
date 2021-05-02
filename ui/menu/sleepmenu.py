# Copyright 2018-2021 Peppy Player peppy.player@gmail.com
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

from pygame import Rect

from ui.container import Container
from ui.layout.gridlayout import GridLayout
from ui.factory import Factory
from util.config import TIMER, SLEEP, SLEEP_TIME, POWEROFF
from util.keys import kbd_keys, KEY_END, KEY_SETUP
from ui.flipclock.clock import Clock

class SleepMenu(Container):
    """ Sleep menu """
    
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
        self.name = SLEEP + "_" + POWEROFF
        self.config = self.util.config
        self.factory = Factory(util)
        sleep_icon_size = 0.64
        poweroff_icon_size = 0.56
        Container.__init__(self, util, bb.CENTER)
        border_x = bb.RIGHT.x
        c = GridLayout(Rect(border_x + 1, bb.y + 1, bb.w - border_x, bb.h - 1))
        c.set_pixel_constraints(2, 1)
        self.bgr = (0, 0, 0, 0)
        
        self.sleep_selected = self.config[TIMER][SLEEP] 
        self.poweroff_selected = self.config[TIMER][POWEROFF]
        
        self.clock = Clock(self.util, SLEEP, SLEEP_TIME, digits, bb, timer_lock, clock_change_callback, change_codes)
        self.add_component(self.clock)
        
        s = c.get_next_constraints()
        self.sleep_button = self.add_button(SLEEP, s, kbd_keys[KEY_SETUP], self.sleep_selected, sleep_icon_size, listener)
        n = c.get_next_constraints()
        h = bb.h - s.height - 2
        r = Rect(n.x, n.y + 1, n.w, h)
        self.poweroff_button = self.add_button(POWEROFF, r, kbd_keys[KEY_END], self.poweroff_selected, poweroff_icon_size, listener)
        self.bounding_box = bb.CENTER
    
    def add_button(self, name, layout, kbd_key, switch_on, icon_size, listener):
        """ Add button
        
        :param name: component name
        :param layout: button layout
        :param kbd_key: keyboard key assigned to the button
        :param switch_on: flag showing if button is selected
        :param icon_size: button icon size
        :param listener: button listener
        """
        d = {}
        d["name"] = name
        d["bounding_box"] = layout
        d["keyboard_key"] = kbd_key
        d["image_size_percent"] = icon_size
        
        button = self.factory.create_timer_button(**d)
        button.add_release_listener(listener)
        button.set_selected(switch_on)
        self.add_component(button)
        
        return button
    
    def set_parent_screen(self, scr):
        """ Add parent screen

        :param scr: parent screen
        """
        self.sleep_button.set_parent_screen(scr)
        self.poweroff_button.set_parent_screen(scr)

    def add_menu_observers(self, update_observer, redraw_observer=None):
        """ Add menu observer
        
        :param update_observer: observer for updating menu
        :param redraw_observer: observer to redraw the whole screen
        """
        
        self.clock.add_menu_observers(update_observer, redraw_observer)
        self.sleep_button.add_release_listener(redraw_observer)
        self.poweroff_button.add_release_listener(redraw_observer)
        
