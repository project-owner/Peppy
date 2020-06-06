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
import logging

from datetime import datetime
from ui.component import Component
from ui.container import Container
from ui.flipclock.digit import Digit
from util.config import COLOR_DARK, COLORS, TIMER, BACKGROUND, MENU_BGR_COLOR

class Clock(Container):
    """ Base class for the flip clock """
    
    def __init__(self, util, name, time_key, digits, bb, gap, icon_size, timer_lock, clock_change_callback, change_codes):
        """ Initializer
        
        :param util: utility object
        :param name: component name
        :param time_key: key of the clock time in configuration
        :param digits: images of the clock digits 0-9
        :param bb: clock bounding box
        :param gap: gap between hours and minutes
        :param icon_size: size of the button icon size
        :param timer_lock: lock object
        :param clock_change_callback: callback function
        :param change_codes: codes for increment and decrement for hours and minutes 
        """        
        self.util = util
        self.name = name
        self.timer_lock = timer_lock
        self.clock_change_callback = clock_change_callback
        self.config = self.util.config
        Container.__init__(self, util)
        self.content = None
        self.clock_bb = bb
        self.bounding_box = bb.LEFT
        size = digits[0][1].get_size()
        self.digit_w = size[0]
        self.digit_h = size[1]        
        separator = util.image_util.get_flipclock_separator(self.digit_h / 3)
        self.shift_x = 2
        border_x = bb.RIGHT.x
        self.change_codes = change_codes
        self.change_listeners = []
        
        r = pygame.Rect(bb.x, bb.y + 1, border_x, bb.h - 1)
        c = Component(self.util, r, bb=bb)
        c.name = name + ".bgr"
        c.bgr = self.config[BACKGROUND][MENU_BGR_COLOR]
        self.add_component(c)
        
        size = separator[1].get_size()
        w = size[0]
        h = size[1]
        c = Component(self.util)
        c.name = name + ".separator"
        c.content = separator
        separator_x = (border_x / 2) - (w / 2)
        separator_y = bb.y + (bb.h/2) - (h/2)
        c.content_x = separator_x
        c.content_y = separator_y
        self.add_component(c)
        
        self.time_key = time_key
        current_time = datetime.now().strftime("%H%M") 
        try:
            self.time = self.config[TIMER][time_key]
        except:
            self.time = current_time
            
        if len(self.time.strip()) == 0:
            self.time = current_time
            with self.timer_lock:
                self.config[TIMER][self.time_key] = self.time
        
        h1_x = separator_x - (self.digit_w*2) - w
        h1_n = name + ".h1"
        self.h1 = self.add_digit(digits, int(self.time[0]), h1_x, self.increment_hours, self.decrement_hours, h1_n)
        
        h2_x = separator_x - self.digit_w - w
        h2_n = name + ".h2"
        self.h2 = self.add_digit(digits, int(self.time[1]), h2_x, self.increment_hours, self.decrement_hours, h2_n)
        
        m1_x = separator_x + w * 2
        m1_n = name + ".m1"
        self.m1 = self.add_digit(digits, int(self.time[2]), m1_x, self.increment_minutes, self.decrement_minutes, m1_n)
        
        m2_x = separator_x + self.digit_w + w * 2
        m2_n = name + ".m2"
        self.m2 = self.add_digit(digits, int(self.time[3]), m2_x, self.increment_minutes, self.decrement_minutes, m2_n)
        
        key_height = self.digit_h
        self.top_image = util.image_util.get_flipclock_key("key-top.png", key_height)
        self.bottom_image = util.image_util.get_flipclock_key("key-bottom.png", key_height)  
        self.top_image_on = util.image_util.get_flipclock_key("key-top-on.png", key_height)
        self.bottom_image_on = util.image_util.get_flipclock_key("key-bottom-on.png", key_height)  
        
        y = self.clock_bb.y + (self.clock_bb.h/2) - (self.digit_h/2)
        self.h_top = self.add_key(h2_x, y, h2_n + ".top.key", self.top_image)
        self.m_top = self.add_key(m2_x, y, m2_n + ".top.key", self.top_image)
        
        y = self.clock_bb.y + (self.clock_bb.h/2) - (self.digit_h/2) + self.digit_h - self.bottom_image[1].get_size()[1]
        self.h_bottom = self.add_key(h2_x, y, h2_n + ".bottom.key", self.bottom_image)
        self.m_bottom = self.add_key(m2_x, y, m2_n + ".bottom.key", self.bottom_image)
        
        self.selected_key = None
        
    def add_digit(self, digits, digit, x, increment, decrement, name):
        """ Add clock digit
        
        :param digits: clock digits 0-9
        :param digit: the digit
        :param x: digit x coordinate
        :param increment: increment function
        :param decrement: decrement function
        :param name: component name
        """       
        y = self.clock_bb.y + (self.clock_bb.h/2) - (self.digit_h/2)
        bb = pygame.Rect(x, y, self.digit_w, self.digit_h)
        d = Digit(self.util, digits, digit, bb, increment, decrement, name)
        self.add_component(d)
        return d
    
    def add_key(self, x, y, name, key):
        """ Add the key indicating current focus position
        
        :param x: x coordinate
        :param y: y coordinate
        :param name: component name
        :param key: key image
        """
        size = key[1].get_size()
        w = size[0]
        h = size[1]
        
        cont = Container(self.util)
        cont.bgr = cont.fgr = (0, 0, 0, 0)
        cont.name = name + ".cont"
        c = Component(self.util)
        c.name = name
        c.content = key[1]
        c.bgr = c.fgr = (0, 0, 0, 0)
        c.content_x = x - w/2
        c.content_y = y
        c.image_filename = key[0] 
        c.bounding_box = pygame.Rect(0, 0, w, h)
        cont.bounding_box = pygame.Rect(c.content_x, c.content_y, w, h)
        
        cont.add_component(c)
        self.add_component(cont)
        return cont
    
    def select_key(self, key):
        """ Select key
        
        :param key: key image
        """
        self.reset_key()

        if "top" in key.name:
            key.components[0].content = self.top_image_on[1]
            key.components[0].image_filename = self.top_image_on[0]
        elif "bottom" in key.name:
            key.components[0].content = self.bottom_image_on[1]
            key.components[0].image_filename = self.bottom_image_on[0]

        self.selected_key = key
        self.selected_key.content = None
        self.selected_key.clean_draw_update()
    
    def set_key_position(self, position):
        """ Set key position
        
        :param position: position to set
        """
        if position not in self.change_codes:
            return
        
        if position == self.change_codes[0]:
            self.select_key(self.h_top)
        elif position == self.change_codes[1]:
            self.select_key(self.m_top)
        elif position == self.change_codes[2]:
            self.select_key(self.h_bottom)
        elif position == self.change_codes[3]:
            self.select_key(self.m_bottom)
    
    def reset_key(self):
        """ Reset current key """
        
        if self.selected_key == None:
            return

        if "top" in self.selected_key.name:
            self.selected_key.components[0].content = self.top_image[1]
            self.selected_key.components[0].image_filename = self.top_image[0]
        else:
            self.selected_key.components[0].content = self.bottom_image[1]
            self.selected_key.components[0].image_filename = self.bottom_image[0]

        self.selected_key.clean_draw_update()
    
    def increment_hours(self, state=None):
        """ Increment hours
        
        :param state: button state object
        """
        current_hours = int(self.time[0:2])
        current_minutes = int(self.time[2:])
        
        if current_hours == 23 and current_minutes != 0:
            current_minutes = 0
            h = current_hours + 1
            self.change_minutes(0)        
        elif current_hours == 24:
            h = 0
        else:
            h = current_hours + 1
        
        self.set_key_position(self.change_codes[0])
        self.change_hours(h, current_minutes)
        self.notify_change_listeners(self.change_codes[0])
        
    def decrement_hours(self, state=None):
        """ Decrement hours
        
        :param state: button state object
        """
        current_hours = int(self.time[0:2])
        current_minutes = int(self.time[2:])
        
        if current_hours == 0:
            current_minutes = 0
            h = 24
            self.change_minutes(0)           
        else:
            h = current_hours - 1
        
        self.set_key_position(self.change_codes[2])
        self.change_hours(h, current_minutes)
        self.notify_change_listeners(self.change_codes[2])
        
    def change_hours(self, h, m):
        """ Change hours
        
        :param h: hours
        :param m: minutes
        """
        s = format(h, '02d')
        self.h1.set_digit(int(s[0]))
        self.h2.set_digit(int(s[1]))
        self.time = s + format(m, '02d')
        with self.timer_lock:
            self.config[TIMER][self.time_key] = self.time
        self.clock_change_callback()
        
    def increment_minutes(self, state=None):
        """ Increment minutes
        
        :param state: button state object
        """
        current_minutes = int(self.time[2:])
        current_hours = int(self.time[0:2])
        
        if current_hours == 24:
            return
        
        if current_minutes == 59:
            m = 0
        else:
            m = current_minutes + 1
        
        self.set_key_position(self.change_codes[1])
        self.change_minutes(m)
        self.notify_change_listeners(self.change_codes[1])
        
    def decrement_minutes(self, state=None):
        """ Decrement minutes
        
        :param state: button state object
        """
        current_minutes = int(self.time[2:])
        current_hours = int(self.time[0:2])
        
        if current_hours == 24:
            return
        
        if current_minutes == 0:
            m = 59
        else:
            m = current_minutes - 1
        
        self.set_key_position(self.change_codes[3])
        self.change_minutes(m)
        self.notify_change_listeners(self.change_codes[3])
        
    def change_minutes(self, m):
        """ Change minutes
        
        :param m: minutes
        """
        s = format(m, '02d')
        self.m1.set_digit(int(s[0]))
        self.m2.set_digit(int(s[1]))
        self.time = self.time[0:2] + s
        with self.timer_lock:
            self.config[TIMER][self.time_key] = self.time
        self.clock_change_callback()
    
    def add_change_listener(self, listener):
        """ Add change listener
        
        :param listener: the listener
        """
        if listener not in self.change_listeners:
            self.change_listeners.append(listener)
            
    def notify_change_listeners(self, change_code):
        """ Notify change listeners
        
        :param change_code: change code
        """
        for listener in self.change_listeners:
            listener(change_code)
        
    def add_menu_observers(self, update_observer, redraw_observer=None):
        """ Add menu observer
        
        :param update_observer: observer for updating menu
        :param redraw_observer: observer to redraw the whole screen
        """
        self.h1.add_release_listener(redraw_observer)
        self.h2.add_release_listener(redraw_observer)
        self.m1.add_release_listener(redraw_observer)
        self.m2.add_release_listener(redraw_observer)
        