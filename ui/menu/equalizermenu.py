# Copyright 2016-2021 Peppy Player peppy.player@gmail.com
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

from ui.component import Component
from ui.container import Container
from ui.layout.gridlayout import GridLayout
from ui.layout.borderlayout import BorderLayout
from ui.factory import Factory
from util.keys import KEY_SELECT, USER_EVENT_TYPE, SUB_TYPE_KEYBOARD, kbd_keys, KEY_LEFT, KEY_RIGHT, KEY_UP, \
    KEY_DOWN, KEY_PAGE_UP, KEY_PAGE_DOWN, SELECT_EVENT_TYPE
from util.config import BACKGROUND, MENU_BGR_COLOR

class EqualizerMenu(Container):
    """ Equalizer Menu class """
    
    def __init__(self, util, handle_slider_event, bounding_box=None):
        """ Initializer
        
        :param util: utility object
        :param handle_slider_event: slider event handler
        :param listeners: menu listeners
        :param bgr: menu background
        :param bounding_box: bounding box
        """
        self.labels = ["31", "63", "125", "250", "500", "1k", "2k", "4k", "8k", "16k"]

        self.util = util 
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

        self.mouse_events = [pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION]   
        
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
            key_events = [kbd_keys[KEY_LEFT], kbd_keys[KEY_RIGHT], kbd_keys[KEY_UP], kbd_keys[KEY_DOWN], kbd_keys[KEY_PAGE_UP], kbd_keys[KEY_PAGE_DOWN], kbd_keys[KEY_SELECT]]
            if event.keyboard_key not in key_events:
                return

            if not self.is_menu_selected():
                return
            
            if event.action == pygame.KEYUP:
                self.key_up(event)
            elif event.action == pygame.KEYDOWN:
                self.key_down(event)
        elif event.type == SELECT_EVENT_TYPE:
            if event.source == self:
                return
            self.handle_select_action(event.x, event.y)               
        elif event.type in self.mouse_events:
            if not self.bounding_box.collidepoint(event.pos):
                return

            Container.handle_event(self, event)            

    def handle_select_action(self, x, y):
        """ Handle select action

        :param x: x coordinate
        :param y: y coordinate
        """
        for index, s in enumerate(self.sliders):
            if s.bounding_box.collidepoint((x - 3, y)):
                s.slider.selected = True
                self.current_slider = index
                self.activate_slider()

    def key_up(self, event):
        """ Handle key up

        :param event: the event to handle
        """
        avoided_keys = [kbd_keys[KEY_UP], kbd_keys[KEY_DOWN], kbd_keys[KEY_PAGE_UP], kbd_keys[KEY_PAGE_DOWN]]
        if self.current_slider == -1 and (event.keyboard_key in avoided_keys): return
        
        self.deactivate_current_slider()
        if event.keyboard_key == kbd_keys[KEY_LEFT]:
            if self.current_slider == 0 or self.current_slider == -1:
                y = self.exit_bottom_y
                slider = self.sliders[len(self.sliders) - 1].slider
                if self.exit_menu(y, event, slider):
                    return
            else:
                self.current_slider -= 1                
        elif event.keyboard_key == kbd_keys[KEY_RIGHT]:
            if self.current_slider == len(self.sliders) - 1:
                y = self.exit_bottom_y
                slider = self.sliders[0].slider
                if self.exit_menu(y, event, slider):
                    return
            else:
                self.current_slider += 1
        elif event.keyboard_key == kbd_keys[KEY_SELECT]:
            if not self.is_menu_selected():
                return
            slider = self.sliders[self.current_slider].slider
            if self.exit_menu(self.exit_bottom_y, event, slider):
                return
                
        self.activate_slider()

    def exit_menu(self, exit_border, event, slider):
        """ Exit menu

        :param exit_border: exit border
        :param event: exit event
        :param slider: the slider
        """
        if exit_border == None or slider == None or event.action != pygame.KEYUP:
            return False
        
        x = int(slider.bounding_box.x + (slider.bounding_box.w / 2))
        y = exit_border
        slider.selected = False
        self.current_slider = -1
        for s in self.sliders:
            s.slider.selected = False
        self.util.post_exit_event(x, y, self)
        if self.redraw_observer:
            self.redraw_observer()
        return True

    def key_down(self, event):
        """ Handle key down

        :param event: the event to handle
        """
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
        """ Deactivate the current slider """

        if self.current_slider == -1:
            return
        
        slider = self.sliders[self.current_slider].slider
        slider.release_action((slider.knob_x, slider.last_knob_position))
        slider.clean_draw_update()
        
    def activate_slider(self):
        """ Activate the current slider """

        slider = self.sliders[self.current_slider].slider
        slider.press_action()
        slider.clean_draw_update()

    def is_menu_selected(self):
        """ Check if menu has selected slider

        :return: True - has selected slider, False - doesn't have
        """
        for s in self.sliders:
            if s.slider.selected:
                return True
        return False
    
    def add_menu_observers(self, update_observer, redraw_observer):
        """ Add menu observer
        
        :param update_observer: observer for updating menu
        :param redraw_observer: observer to redraw the whole screen
        """
        self.redraw_observer = redraw_observer
        for s in self.sliders:
            s.slider.add_slide_listener(update_observer)
            s.slider.add_knob_listener(update_observer)
            s.slider.add_press_listener(update_observer)
            s.slider.add_motion_listener(update_observer)
            s.web_seek_listener = update_observer
    