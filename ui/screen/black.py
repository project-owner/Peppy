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

import pygame

from ui.container import Container
from event.dispatcher import USER_EVENT_TYPE, SUB_TYPE_KEYBOARD

class BlackScreen(Container):
    """ Black Screen. Displayed in sleeping mode """
    
    def __init__(self, util):
        """ Initializer
        
        :param util: utility object
        """        
        self.util = util
        self.config = util.config
        Container.__init__(self, util, background=(0, 0, 0))
        self.bounding_box = util.screen_rect
        self.start_listeners = []
               
    def add_listener(self, listener):
        """ Add screen event listener
        
        :param listener: event listener
        """
        if listener not in self.start_listeners:
            self.start_listeners.append(listener)
            
    def notify_listeners(self, state):
        """ Notify screen event listeners
        
        :param state: button state
        """
        if not self.visible:
            return
        
        for listener in self.start_listeners:
            listener(state)

    def handle_event(self, event):
        """ Screen event handler
        
        :param evenr: event to hanle
        """
        if not self.visible: return
        
        if (event.type == pygame.MOUSEBUTTONUP) or (event.type == USER_EVENT_TYPE and event.sub_type == SUB_TYPE_KEYBOARD and event.action == pygame.KEYUP):
            self.notify_listeners(None)
    
    def exit_screen(self):
        """ Complete actions required to save screen state """
        
        self.set_visible(False)
        