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

import pygame

from ui.button.button import Button
from util.keys import H_ALIGN_RIGHT
from util.config import COLOR_MEDIUM, COLORS, COLOR_CONTRAST, COLOR_BRIGHT, BACKGROUND, MENU_BGR_COLOR
from util.util import V_ALIGN_CENTER
from ui.state import State

BAR_HEIGHT_PERCENT = 22

class ImageButton(Button):
    """ Image button with two states: On/Off """
    
    def __init__(self, util, state, folder, bb, action):
        """ Initializer
        
        :param util: utility object
        :param state: button state
        :param folder: image folder
        :param bb: button bounding box
        :param action: event listener
        """
        self.folder = folder
        self.util = util
        self.config = util.config
        bgr = self.config[BACKGROUND][MENU_BGR_COLOR]
        
        self.state = self.get_image_button_state(bgr, state.index, state.name, state.filename, bb, action, state.button_on, BAR_HEIGHT_PERCENT)
        self.state.bit_address = state.bit_address
        Button.__init__(self, util, self.state)
        if state.button_on:
            self.state.button_on = True
            self.state.icon_base = self.state.state_on_image
        else:
            self.state.button_on = False
            self.state.icon_base = self.state.state_off_image

        self.components[1].content = self.state.icon_base
        self.components[1].content_x = self.state.bounding_box.x
        self.components[1].content_y = self.state.bounding_box.y
        
        self.show_label = True
        x = self.state.bounding_box.x
        y = self.state.bounding_box.y
        w = self.state.bounding_box.w
        h = self.state.bounding_box.h
        self.state.h_align = H_ALIGN_RIGHT
        
        bar_height = (h / 100) * BAR_HEIGHT_PERCENT
        self.add_label(self.state, pygame.Rect(x, y + h - bar_height, w, bar_height))

    def get_image_button_state(self, bgr, index, name, filename, bb, action, on_off, bar_height):
        """ Create image button state

        :param bgr: button background
        :param index: button index
        :param name: state name
        :param filename: the image filename
        :param bb: button bounding box
        :param action: button action
        :param on_off: True - button ON, False - button OFF
        :param bar_height: bottom bar height

        :return: button state
        """
        s = State()
        s.button_on = on_off
        s.index = index
        s.name = s.l_name = name
        s.filename = filename
        s.bounding_box = bb
        s.bgr = bgr
        s.action = action
        s.img_x = None
        s.img_y = None
        s.auto_update = True
        s.image_align_v = V_ALIGN_CENTER
        s.show_bgr = True
        s.show_img = True
        s.label_text_height = 60
        s.text_color_normal = self.config[COLORS][COLOR_BRIGHT]
        s.text_color_selected = self.config[COLORS][COLOR_CONTRAST]
        s.text_color_disabled = self.config[COLORS][COLOR_MEDIUM]
        s.text_color_current = s.text_color_normal
        s.folder = self.folder
        self.util.image_util.set_button_images(s, bar_height)

        return s

    def switch_button(self):
        """ Switch button state """

        if self.state.button_on:
            self.state.button_on = False
            self.state.icon_base = self.state.state_off_image
        else:
            self.state.button_on = True
            self.state.icon_base = self.state.state_on_image

        self.components[1].content = self.state.icon_base
        self.clean_draw_update()

    def mouse_action(self, event):
        """ Mouse event handler
        
        :param event: the event to handle
        """
        pos = event.pos        
        if self.bounding_box.collidepoint(pos) and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:            
            self.press_action()
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.release_action()

    def press_action(self):
        """ Button press event handler """
        
        if not self.press_listeners:
            return

        self.set_selected(True)
        self.notify_press_listeners(self.state)

    def release_action(self):
        """ Button release event handler """
        
        if not self.release_listeners:
            return

        self.notify_release_listeners(self.state)
