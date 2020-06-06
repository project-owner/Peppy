# Copyright 2016-2020 Peppy Player peppy.player@gmail.com
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

import logging
import pygame

from ui.component import Component
from ui.container import Container
from ui.slider.slider import Slider
from ui.layout.gridlayout import GridLayout
from ui.layout.borderlayout import BorderLayout
from ui.factory import Factory
from util.keys import KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6, CLASSICAL, \
    JAZZ, POP, ROCK, CONTEMPORARY, FLAT, KEY_HOME, KEY_PLAYER, KEY_PLAY_PAUSE, \
    USER_EVENT_TYPE, SUB_TYPE_KEYBOARD, kbd_keys, KEY_LEFT, KEY_RIGHT, KEY_UP, \
    KEY_DOWN, KEY_PAGE_UP, KEY_PAGE_DOWN
from util.config import BACKGROUND, MENU_BGR_COLOR

class EqualizerMenu(Container):
    """ Equalizer Navigator Menu class """
    
    def __init__(self, util, handle_slider_event, bgr=None, bounding_box=None):
        """ Initializer
        
        :param util: utility object
        :param handle_slider_event: slider event handler
        :param listeners: menu listeners
        :param bgr: menu background
        :param bounding_box: bounding box
        """
        self.labels = ["31", "63", "125", "250", "500", "1k", "2k", "4k", "8k", "16k"]
          
        Container.__init__(self, util)
        name = "equalizermenu"
        self.factory = Factory(util)
        
        self.bounding_box = bounding_box
        self.bounding_box.y += 1
        self.bounding_box.h -= 1
        self.bgr_color = util.config[BACKGROUND][MENU_BGR_COLOR]

        self.eq_layout = BorderLayout(self.bounding_box)
        self.eq_layout.set_percent_constraints(0, 0, 5, 5)
        
        self.bands = 10
        self.sliders = self.add_sliders(handle_slider_event)
        self.current_slider = -1

        self.left_filler = Component(util, self.eq_layout.LEFT)
        self.left_filler.name = name + ".bgr.left"
        self.left_filler.bgr = self.bgr_color
        self.add_component(self.left_filler)

        self.right_filler = Component(util, self.eq_layout.RIGHT)
        self.right_filler.name = name + ".bgr.right"
        self.right_filler.bgr = self.bgr_color
        self.add_component(self.right_filler)
        
        self.SLOW_INCREMENT = 1
        self.FAST_INCREMENT = self.sliders[0].slider.knob_height/2
        
    def add_sliders(self, handle_slider_event):
        
        layout = GridLayout(self.eq_layout.CENTER)
        layout.set_pixel_constraints(1, self.bands, 0, 0)        
        layout.current_constraints = 0
        sliders = []

        for n in range(self.bands):        
            constr = layout.get_next_constraints()        
            s = self.factory.create_equalizer_slider(n, constr, "band", handle_slider_event, self.labels[n], self.bgr_color)
            s.slider.active = False
            s.content = None
            s.slider.content = None
            self.add_component(s)
            sliders.append(s)
        
        return sliders
    
    def set_bands(self, values):
        for n, s in enumerate(self.sliders):
            v = values[n]
            s.slider.set_position(v)
            s.slider.update_position()
            s.set_value(str(v))
            s.slider.set_knob_off()
            self.current_slider = -1
    
    def set_parent_screen(self, scr):
        """ Add parent screen

        :param scr: parent screen
        """
        self.left_filler.parent_screen = scr
        self.right_filler.parent_screen = scr
        for s in self.sliders:
            s.slider.parent_screen = scr
            s.top.parent_screen = scr
            s.bottom.parent_screen = scr

    def handle_event(self, event):
        """ Menu event handler
        
        :param event: menu event
        """
        if not self.visible: return
        
        if event.type == USER_EVENT_TYPE and event.sub_type == SUB_TYPE_KEYBOARD:
            key_events = [kbd_keys[KEY_LEFT], kbd_keys[KEY_RIGHT], kbd_keys[KEY_UP], kbd_keys[KEY_DOWN], kbd_keys[KEY_PAGE_UP], kbd_keys[KEY_PAGE_DOWN]]
            if event.keyboard_key not in key_events:
                return
            
            if event.action == pygame.KEYUP:
                self.key_up(event)
            elif event.action == pygame.KEYDOWN:
                self.key_down(event)                
        else:
            if not self.bounding_box.collidepoint(event.pos):
                return
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                selected_slider = self.current_slider                
                for i, b in enumerate(self.sliders):
                    if b.slider.bounding_box.collidepoint(event.pos):
                        selected_slider = i
                        break
                
                if selected_slider != self.current_slider:
                    self.deactivate_current_slider()
                    self.current_slider = selected_slider

            Container.handle_event(self, event)
            
            if event.type == pygame.MOUSEBUTTONUP:
                slider = self.sliders[self.current_slider].slider
                slider.set_knob_on()
                slider.notify_slide_listeners()

    def key_up(self, event):
        avoided_keys = [kbd_keys[KEY_UP], kbd_keys[KEY_DOWN], kbd_keys[KEY_PAGE_UP], kbd_keys[KEY_PAGE_DOWN]]
        if self.current_slider == -1 and (event.keyboard_key in avoided_keys): return
        
        self.deactivate_current_slider()
        if event.keyboard_key == kbd_keys[KEY_LEFT]:
            if self.current_slider == 0 or self.current_slider == -1:
                self.current_slider = len(self.sliders) - 1
            else:
                self.current_slider -= 1                
        elif event.keyboard_key == kbd_keys[KEY_RIGHT]:
            if self.current_slider == len(self.sliders) - 1:
                self.current_slider = 0
            else:
                self.current_slider += 1
                
        self.activate_slider()

    def key_down(self, event):
        if self.current_slider == -1: return
        
        slider = self.sliders[self.current_slider].slider
        
        if event.keyboard_key == kbd_keys[KEY_UP]:            
            slider.release_action((slider.knob_x, slider.last_knob_position + slider.knob_height/2 - self.SLOW_INCREMENT))
        elif event.keyboard_key == kbd_keys[KEY_DOWN] and event.action == pygame.KEYDOWN:
            slider.release_action((slider.knob_x, slider.last_knob_position + slider.knob_height/2 + self.SLOW_INCREMENT))
        elif event.keyboard_key == kbd_keys[KEY_PAGE_UP] and event.action == pygame.KEYDOWN:
            slider.release_action((slider.knob_x, slider.last_knob_position - self.FAST_INCREMENT))
        elif event.keyboard_key == kbd_keys[KEY_PAGE_DOWN] and event.action == pygame.KEYDOWN:
            slider.release_action((slider.knob_x, slider.last_knob_position + slider.knob_height/2 + self.FAST_INCREMENT))
        
        slider.set_knob_on()              

    def deactivate_current_slider(self):
        if self.current_slider == -1:
            return
        
        slider = self.sliders[self.current_slider].slider
        slider.release_action((slider.knob_x, slider.last_knob_position))
        slider.clean_draw_update()
        
    def activate_slider(self):
        slider = self.sliders[self.current_slider].slider
        slider.press_action()
        slider.clean_draw_update()
    
    def add_menu_observers(self, update_observer, redraw_observer):
        for b in self.sliders:
            b.slider.add_slide_listener(update_observer)
            b.slider.add_knob_listener(update_observer)
            b.slider.add_press_listener(update_observer)
            b.slider.add_motion_listener(update_observer)
            b.web_seek_listener = update_observer
    