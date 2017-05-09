# Copyright 2016-2017 Peppy Player peppy.player@gmail.com
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
from ui.factory import Factory
from ui.layout.borderlayout import BorderLayout
from ui.menu.savermenu import SaverMenu
from ui.menu.saverdelaymenu import SaverDelayMenu
from ui.component import Component
from util.keys import kbd_keys, KEY_SCREENSAVER, KEY_SCREENSAVER_DELAY, COLOR_DARK_LIGHT, \
    COLOR_CONTRAST, SCREEN_RECT, LABELS, COLORS, KEY_HOME, KEY_UP, KEY_DOWN, \
    USER_EVENT_TYPE, SUB_TYPE_KEYBOARD

PERCENT_TOP_HEIGHT = 26.00
PERCENT_TITLE_FONT = 54.00

class SaverScreen(Container):
    """ Screensaver Screen. Extends Container class """
    
    def __init__(self, util, listener):
        """ Initializer
        
        :param util: utility object
        :param listener: screen menu event listener
        """
        Container.__init__(self, util)
        factory = Factory(util)
        self.util = util
        config = util.config
        self.bounding_box = config[SCREEN_RECT]
        self.bgr = (0, 0, 0)
        
        screen_layout = BorderLayout(config[SCREEN_RECT])
        top = bottom = int(config[SCREEN_RECT].h/2)
        screen_layout.set_pixel_constraints(top, bottom, 0, 0)
        
        layout = BorderLayout(screen_layout.TOP)
        layout.set_percent_constraints(PERCENT_TOP_HEIGHT, 0, 0, 0)
                
        self.saver_menu = SaverMenu(util, (0, 0, 0), layout.CENTER)
        self.add_component(self.saver_menu)
        
        d = config[COLORS][COLOR_DARK_LIGHT]
        c = config[COLORS][COLOR_CONTRAST]
        
        font_size = (layout.TOP.h * PERCENT_TITLE_FONT)/100.0
        self.saver_title = factory.create_output_text("saver_title", layout.TOP, d, c, int(font_size))
        label = config[LABELS][KEY_SCREENSAVER]
        self.saver_title.set_text(label) 
        self.add_component(self.saver_title)
        
        layout = BorderLayout(screen_layout.BOTTOM)
        layout.set_percent_constraints(PERCENT_TOP_HEIGHT, PERCENT_TOP_HEIGHT, 0, 0)
        self.delay_menu = SaverDelayMenu(util, (0, 0, 0), layout.CENTER)
        self.add_component(self.delay_menu)
        
        self.saver_delay_title = factory.create_output_text("saver_delay_title", layout.TOP, d, c, int(font_size))
        label = config[LABELS][KEY_SCREENSAVER_DELAY]
        self.saver_delay_title.set_text(label)
        self.add_component(self.saver_delay_title)
        
        layout.BOTTOM.h = screen_layout.BOTTOM.h - (layout.TOP.h + layout.CENTER.h) - 2
        layout.BOTTOM.y = screen_layout.TOP.h + screen_layout.BOTTOM.h - layout.BOTTOM.h - 1
        layout.BOTTOM.x += 1
        layout.BOTTOM.w -= 2
        self.home_button = factory.create_button(KEY_HOME, KEY_HOME, layout.BOTTOM, listener, d, 8)        
        self.add_component(self.home_button)
        
        self.top_menu_enabled = True

    def get_bounding_box(self, name, comp):
        """ Return Screensaver menu bounding box
        
        :param name: screensaver name 
        :param menu: screensaver menu
        
        :return: screensaver menu bounding box
        """
        c = Component(self.util)
        c.name = name
        c.content = comp.bounding_box
        c.bgr = c.fgr = (0, 0, 0)
        c.content_x = c.content_y = 0
        return c

    def get_clickable_rect(self):
        """ Return the list of rectangles which includes bounding boxes for screensaver and delay menus. 
        
        :return: list of rectangles
        """
        d = []
        d.append(self.get_bounding_box("clickable_rect_1", self.saver_menu))
        d.append(self.get_bounding_box("clickable_rect_2", self.delay_menu))
        d.append(self.get_bounding_box("clickable_rect_3", self.home_button))
        return d
    
    def handle_event(self, event):
        """ Screensaver screen event handler
        
        :param event: event to handle
        """
        if not self.visible: return
        
        if event.type == USER_EVENT_TYPE and event.sub_type == SUB_TYPE_KEYBOARD and event.action == pygame.KEYUP:
            if event.keyboard_key == kbd_keys[KEY_UP] or event.keyboard_key == kbd_keys[KEY_DOWN]:
                if self.top_menu_enabled:
                    index = self.saver_menu.get_selected_index()
                    self.top_menu_enabled = False
                    self.delay_menu.unselect()
                    s = len(self.delay_menu.delays)
                    if index > (s - 1):
                        index = s - 1
                    self.delay_menu.select_by_index(index)
                else:
                    index = self.delay_menu.get_selected_index()
                    self.top_menu_enabled = True
                    self.saver_menu.unselect()
                    s = len(self.delay_menu.delays)
                    if index == (s - 1):
                        index = len(self.saver_menu.savers) - 1
                    self.saver_menu.select_by_index(index)
            elif event.keyboard_key == kbd_keys[KEY_HOME]:
                self.home_button.handle_event(event)
            else:
                if self.top_menu_enabled:
                    self.saver_menu.handle_event(event)
                else:
                    self.delay_menu.handle_event(event) 
        else:
            Container.handle_event(self, event)
            
    def exit_screen(self):
        """ Complete actions required to save screen state """
        
        self.set_visible(False)    
