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
from ui.button.button import Button
from util.keys import USER_EVENT_TYPE, SUB_TYPE_KEYBOARD

class ToggleButton(Button):
    """ Toggle button class (e.g. Shutdown button) """
    
    def __init__(self, util, state):
        """ Initializer
        
        :param util: utility object
        :param states: button states 
        """
        Button.__init__(self, util, state)
        self.pressed = False
        self.cancel_listeners = list()
        
    def handle_event(self, event):
        """ Button event dispatcher
        
        :param event: the event to handle
        """
        if not self.visible:
            return
        
        mouse_events = [pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN]        
        
        if event.type in mouse_events:
            self.mouse_action(event)
        elif event.type == USER_EVENT_TYPE:
            self.user_event_action(event)
            
    def mouse_action(self, event):
        """ Mouse event handler
        
        :param event: the event to handle
        """
        pos = event.pos
        
        if self.bounding_box.collidepoint(pos) and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:            
            self.press_action()
            self.notify_press_listeners(self.state)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.clicked:
            self.release_action(self.state)
        else:
            self.cancel_action()            
    
    def user_event_action(self, event):
        """ User event handler
        
        :param event: the event to handle
        """
        if event.sub_type == SUB_TYPE_KEYBOARD and self.state.keyboard_key == event.keyboard_key:
            self.keyboard_action(event)
        else:
            self.cancel_action()
                
    def keyboard_action(self, event):
        """  Keyboard event handler 
        
        :param event: the event to handle
        """
        if event.action == pygame.KEYDOWN:
            self.press_action()
        elif event.action == pygame.KEYUP:
            self.release_action(self.state)            
                
    def press_action(self):
        """ Button press event handler """
        
        self.set_selected(True)
        self.clicked = True
        self.clean_draw_update()
    
    def release_action(self, state):
        """ Button release event handler """
        
        self.clicked = False
        if self.pressed:
            self.notify_release_listeners(self.state)
        else:
            self.notify_press_listeners(self.state)
        self.pressed = True
        self.clean_draw_update()
    
    def cancel_action(self):
        """ Cancel previous action """
        
        if self.pressed:
            self.set_selected(False)
            self.pressed = False
            self.clean_draw_update()
            self.notify_cancel_listeners(self.state)
   
    def add_cancel_listener(self, listener):
        """ Add cancel event listener
        
        :param listener: event listener
        """
        if listener not in self.cancel_listeners:
            self.cancel_listeners.append(listener)
        
    def notify_cancel_listeners(self, state):
        """ Notify cancel event listeners
        
        :param state: button state
        """
        for listener in self.cancel_listeners:
            listener(state)      
