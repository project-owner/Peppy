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
from ui.layout.borderlayout import BorderLayout
from event.dispatcher import USER_EVENT_TYPE, SUB_TYPE_KEYBOARD
from ui.factory import Factory
from util.config import SCREEN_RECT, COLOR_LOGO, COLORS, COLOR_WEB_BGR

PERCENT_FOOTER_HEIGHT = 20.00
PERCENT_NAME_LONG_HEIGHT = 10.00
PERCENT_FOOTER_FONT = 26.00

class AboutScreen(Container):
    """ About Screen. Extends Container class """
    
    def __init__(self, util):
        """ Initializer
        
        :param util: utility object
        """        
        self.util = util
        self.config = util.config
        self.color_web_bgr = self.config[COLORS][COLOR_WEB_BGR]
        Container.__init__(self, util, background=self.color_web_bgr)
        self.bounding_box = self.config[SCREEN_RECT]
        self.start_listeners = []
        factory = Factory(util)
        edition = "Rubens Edition"
        
        layout = BorderLayout(self.bounding_box)
        layout.set_percent_constraints(0, PERCENT_FOOTER_HEIGHT, 0, 0)
        release_font_size = (layout.BOTTOM.h * PERCENT_FOOTER_FONT)/100.0
        
        color_logo = self.config[COLORS][COLOR_LOGO]        
        button = factory.create_image_button("peppy", bounding_box=layout.CENTER, bgr=self.color_web_bgr)
        x = layout.CENTER.w/2 - button.components[1].content.get_size()[0]/2
        y = layout.CENTER.h/2 - button.components[1].content.get_size()[1]/2        
        button.components[1].content_x = x
        button.components[1].content_y = y
        self.add_component(button)
        
        layout.BOTTOM.y -= 1
        layout.BOTTOM.h += 1
        release = factory.create_output_text("about-name", layout.BOTTOM, self.color_web_bgr, color_logo, int(release_font_size), full_width=True)
        release.set_text_no_draw(edition)
        self.add_component(release)
    
    def add_listener(self, listener):
        """ Add About Screen event listener
        
        :param listener: event listener
        """
        if listener not in self.start_listeners:
            self.start_listeners.append(listener)
            
    def notify_listeners(self, state):
        """ Notify all About Screen event listeners
        
        :param state: button state
        """
        if not self.visible:
            return
        
        for listener in self.start_listeners:
            listener(state)

    def handle_event(self, event):
        """ About Screen event handler
        
        :param evenr: event to hanle
        """
        if not self.visible: return
        mouse_events = [pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN]        
        
        if (event.type in mouse_events) or (event.type == USER_EVENT_TYPE and event.sub_type == SUB_TYPE_KEYBOARD and event.action == pygame.KEYUP):
            self.notify_listeners(None)
    
    def exit_screen(self):
        """ Complete actions required to save screen state """
        
        self.set_visible(False)
        
    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        self.add_listener(redraw_observer)
