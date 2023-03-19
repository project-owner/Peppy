# Copyright 2016-2023 Peppy Player peppy.player@gmail.com
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
from util.keys import kbd_keys, USER_EVENT_TYPE, SELECT_EVENT_TYPE, KEY_SELECT, SUB_TYPE_KEYBOARD

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
            k = event.keyboard_key
            if k in self.key_events and self.selected and event.action == pygame.KEYUP:
                self.cancel_action()
                self.handle_exit(k)
            else:
                self.user_event_action(event)
        elif event.type == SELECT_EVENT_TYPE:
            self.select_action(event.x, event.y)
            
    def mouse_action(self, event):
        """ Mouse event handler
        
        :param event: the event to handle
        """
        pos = event.pos
        
        if self.bounding_box.collidepoint(pos) and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:            
            self.press_action()
            self.notify_press_listeners(self.state)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.clicked:
            self.release_action(False)
        else:
            self.cancel_action()            
    
    def user_event_action(self, event):
        """ User event handler
        
        :param event: the event to handle
        """
        if event.sub_type == SUB_TYPE_KEYBOARD and self.state.keyboard_key == event.keyboard_key:
            self.keyboard_action(event)

        k = event.keyboard_key
        if self.selected and event.action == pygame.KEYUP:
            if k in self.key_events:
                self.cancel_action()
                self.handle_exit(k)
            elif k == kbd_keys[KEY_SELECT]:
                if self.pressed:
                    self.release_action()    
                else:
                    self.pressed = True
 
    def keyboard_action(self, event):
        """  Keyboard event handler 
        
        :param event: the event to handle
        """
        if event.action == pygame.KEYDOWN:
            self.press_action()
        elif event.action == pygame.KEYUP:
            self.release_action()            
                
    def press_action(self):
        """ Button press event handler """
        
        self.set_selected(True)
        self.clicked = True
        self.clean_draw_update()
    
    def release_action(self, unselect=True):
        """ Release button event handler
        
        :param unselect: unselect flag
        """
        self.clicked = False

        if unselect:
            self.set_selected(False)
        else:
            self.set_selected(True)

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
