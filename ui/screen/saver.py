# Copyright 2016-2018 Peppy Player peppy.player@gmail.com
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
from ui.screen.screen import Screen
from util.config import COLORS, COLOR_DARK_LIGHT, COLOR_CONTRAST, SCREENSAVER, DELAY
from util.keys import kbd_keys, SCREEN_RECT, LABELS, KEY_HOME, KEY_UP, KEY_DOWN, \
    USER_EVENT_TYPE, SUB_TYPE_KEYBOARD, KEY_PLAY_PAUSE

PERCENT_SAVERS = 60
PERCENT_TOP_HEIGHT = 21.00
PERCENT_TITLE_FONT = 54.00
PERCENT_DELAY_TITLE = 33

class SaverScreen(Screen):
    """ Screensaver Screen """
    
    def __init__(self, util, listeners, voice_assistant):
        """ Initializer
        
        :param util: utility object
        :param listener: screen menu event listener
        """
        self.util = util
        config = util.config
        screen_layout = BorderLayout(config[SCREEN_RECT])
        top = int((config[SCREEN_RECT].h * PERCENT_SAVERS) / 100)
        bottom = config[SCREEN_RECT].h - top
        screen_layout.set_pixel_constraints(top, bottom, 0, 0)
        
        layout = BorderLayout(screen_layout.TOP)
        layout.set_percent_constraints(PERCENT_TOP_HEIGHT, 0, 0, 0)
        
        Screen.__init__(self, util, "", PERCENT_TOP_HEIGHT, voice_assistant, "saver_title", title_layout=layout.TOP)
        factory = Factory(util)
        
        self.bounding_box = config[SCREEN_RECT]
        self.bgr = (0, 0, 0)
                
        self.saver_menu = SaverMenu(util, (0, 0, 0), layout.CENTER)
        self.add_component(self.saver_menu)
        
        d = config[COLORS][COLOR_DARK_LIGHT]
        c = config[COLORS][COLOR_CONTRAST]
        
        font_size = (layout.TOP.h * PERCENT_TITLE_FONT)/100.0
        label = config[LABELS][SCREENSAVER]
        self.screen_title.set_text(label)
        
        layout = BorderLayout(screen_layout.BOTTOM)
        layout.set_percent_constraints(PERCENT_DELAY_TITLE, PERCENT_DELAY_TITLE, 0, 0)
        self.delay_menu = SaverDelayMenu(util, (0, 0, 0), layout.CENTER)
        self.add_component(self.delay_menu)
        
        layout.TOP.y += 1
        layout.TOP.h -= 1
        self.saver_delay_title = factory.create_output_text("saver_delay_title", layout.TOP, d, c, int(font_size))
        label = config[LABELS][DELAY]
        self.saver_delay_title.set_text(label)
        self.add_component(self.saver_delay_title)
        
        buttons = factory.create_home_player_buttons(self, layout.BOTTOM, listeners)
        self.home_button = buttons[0]
        self.player_button = buttons[1]

        self.top_menu_enabled = True

    def handle_event(self, event):
        """ Screensaver screen event handler
        
        :param event: event to handle
        """
        if not self.visible: return
        
        if event.type == USER_EVENT_TYPE and event.sub_type == SUB_TYPE_KEYBOARD and event.action == pygame.KEYUP:
            if event.keyboard_key == kbd_keys[KEY_UP] or event.keyboard_key == kbd_keys[KEY_DOWN]:
                if self.top_menu_enabled:
                    index = self.saver_menu.get_selected_index()                    
                    if event.keyboard_key == kbd_keys[KEY_DOWN] and index <= self.saver_menu.cols - 1:
                        self.saver_menu.handle_event(event)
                    elif event.keyboard_key == kbd_keys[KEY_UP] and index >= self.saver_menu.cols:
                        self.saver_menu.handle_event(event)
                    else:
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
                    else:
                        index += self.saver_menu.cols
                    self.saver_menu.select_by_index(index)
            elif event.keyboard_key == kbd_keys[KEY_HOME]:
                self.home_button.handle_event(event)
            elif event.keyboard_key == kbd_keys[KEY_PLAY_PAUSE]:
                self.player_button.handle_event(event)
            else:
                if self.top_menu_enabled:
                    self.saver_menu.handle_event(event)
                else:
                    self.delay_menu.handle_event(event) 
        else:
            Container.handle_event(self, event)
            
    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        Screen.add_screen_observers(self, update_observer, redraw_observer)
        
        self.saver_menu.add_menu_observers(update_observer, redraw_observer, release=False)
        self.saver_menu.add_move_listener(redraw_observer)
        
        self.delay_menu.add_menu_observers(update_observer, redraw_observer, release=False)
        self.delay_menu.add_move_listener(redraw_observer)
        
        self.add_button_observers(self.home_button, update_observer, redraw_observer, release=False)   
        self.add_button_observers(self.player_button, update_observer, redraw_observer, release=False)
        