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
from ui.button.button import Button
from util.keys import USER_EVENT_TYPE, SUB_TYPE_KEYBOARD, REST_EVENT_TYPE

class MultiStateButton(Button):
    """ Multi-state button class (e.g. Play/Pause button) """
    
    def __init__(self, util, states):
        """ Initializer
        
        :param util: utility object
        :param states: button states 
        """
        self.states = states
        self.index = 0
        self.state = states[self.index]
        for s in states:
            s.event_origin = self
        self.name = self.state.name
        self.start_listeners = dict()
        Button.__init__(self, util, self.state)        
    
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
        elif event.type == REST_EVENT_TYPE:
            self.rest_event_action(event)
        
    def mouse_action(self, event):
        """ Mouse event handler
        
        :param event: the event to handle
        """
        pos = event.pos        
        if self.bounding_box.collidepoint(pos) and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:            
            self.press_action()
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.clicked:
            self.release_action()

    def user_event_action(self, event):
        """ User event handler
        
        :param event: the event to handle
        """
        if event.sub_type == SUB_TYPE_KEYBOARD and self.state.keyboard_key == event.keyboard_key:
            if event.action == pygame.KEYDOWN:
                self.press_action()
            elif event.action == pygame.KEYUP:
                self.release_action()

    def press_action(self):
        """ Button press event handler """
        
        if not self.press_listeners:
            return

        self.set_selected(True)
        self.clicked = True
        super(MultiStateButton, self).clean_draw_update()
        self.notify_press_listeners(self.state)

    def release_action(self):
        """ Button release event handler """
        
        if not self.start_listeners and not self.release_listeners:
            return

        self.set_selected(False)
        self.clicked = False
        self.notify_listeners(self.state)            
        self.index += 1
        if self.index == len(self.states):
            self.index = 0    
        self.state = self.states[self.index]
        self.set_selected(False)
        super(MultiStateButton, self).clean_draw_update()
        self.notify_release_listeners(self.state)
        
    def draw_default_state(self, state):
        """ Draw default button state without action """
        
        if self.index == 0:
            return
        
        self.index = 0
        self.state = self.states[self.index]
        self.clicked = False
        self.set_selected(False)
        super(MultiStateButton, self).clean_draw_update()

    def draw_state(self, index):
        """ Draw state defined by index without action 
        
        :param index: state index
        """

        if self.index == index:
            return

        self.index = index
        self.state = self.states[self.index]
        self.clicked = False
        self.set_selected(False)
        super(MultiStateButton, self).clean_draw_update()

    def add_listener(self, name, listener):
        """ Add button event listeners
        
        :param listeners: event listeners
        """
        self.start_listeners[name].append(listener)

    def add_listeners(self, listeners):
        """ Add button event listeners
        
        :param listeners: event listeners
        """
        self.start_listeners = listeners

    def notify_listeners(self, state):
        """ Notify event listeners
        
        :param state: button state
        """
        if not self.start_listeners:
            return

        listeners = self.start_listeners[state.name]
        for listener in listeners:
            listener()
