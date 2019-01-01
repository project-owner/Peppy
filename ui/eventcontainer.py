# Copyright 2018 Peppy Player peppy.player@gmail.com
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
import time

import threading
from threading import RLock, Thread
from ui.state import State
from ui.container import Container
from util.keys import USER_EVENT_TYPE, SUB_TYPE_KEYBOARD, VOICE_EVENT_TYPE
from util.config import USAGE, USE_LONG_PRESS_TIME

class EventContainer(Container):
    """ Base class for containers with additional event handling """
    
    lock = RLock()
    
    def __init__(self, util, bb, bgr=(0, 0, 0, 0)):
        """ Initializer
        
        :param util: utility object
        :param bb: bounding box
        :param bgr: background color
        """        
        self.util = util
        self.config = self.util.config
        Container.__init__(self, util)
        self.press_listeners = []
        self.release_listeners = []
        self.label_listeners = []
        self.area_listeners = []
        self.bounding_box = bb
        self.bgr = bgr
        self.selected = None
        self.press_time = 0
        self.enabled = True
        self.LONG_PRESS_TIME = self.config[USAGE][USE_LONG_PRESS_TIME]
        self.keep_sending = False
        self.press_thread = None        
                
    def add_press_listener(self, listener):
        """ Add button press listener
        
        :param listener: press button listener
        """
        if listener not in self.press_listeners:
            self.press_listeners.append(listener)
        
    def notify_press_listeners(self, state=None):
        """ Notify button press listeners
        
        :param state: button state
        """
        for listener in self.press_listeners:
            listener(state)
            
    def add_release_listener(self, listener):
        """ Add button release listener
        
        :param listener: release button listener
        """
        if listener not in self.release_listeners:
            self.release_listeners.append(listener)
        
    def notify_release_listeners(self, state=None):
        """ Notify button release listeners
        
        :param state: button state
        """
        for listener in self.release_listeners:
            listener(state)
    
    def add_area_listener(self, listener):
        """ Add area listener
        
        :param listener: area listener
        """
        if listener not in self.area_listeners:
            self.area_listeners.append(listener)
        
    def notify_area_listeners(self, state):
        """ Notify area listeners
        
        :param state: button state
        """
        for listener in self.area_listeners:
            if not listener[0].collidepoint(state.pos):
                continue
            listener[1](state)
                                
    def handle_event(self, event):
        """ Handle button event
        
        :param event: the event to handle
        """
        if not self.visible:
            return
        
        mouse_events = [pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN]        
        
        if event.type in mouse_events:            
            self.mouse_action(event)
        elif event.type == USER_EVENT_TYPE:
            self.user_event_action(event)
        elif event.type == VOICE_EVENT_TYPE:
            self.voice_event_action(event)
    
    def mouse_action(self, event):
        """ Mouse event dispatcher
        
        :param event: the event to handle
        """
        self.pos = event.pos
        
        if not self.bounding_box.collidepoint(self.pos):
            return
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.press_action()            
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.clicked:
            self.release_action(event)
    
    def user_event_action(self, event):
        """ User event dispatcher
        
        :param event: the event to handle
        """
        key = getattr(self.state, "keyboard_key", None)
        if event.sub_type == SUB_TYPE_KEYBOARD and key and key == event.keyboard_key:
            if event.action == pygame.KEYDOWN:
                self.press_action()
            elif event.action == pygame.KEYUP:
                self.release_action()
                
    def voice_event_action(self, event):
        """ Voice event dispatcher
        
        :param event: the event to handle
        """
        commands = getattr(self.state, "voice_commands", None)
        if commands and event.voice_command in commands:
            self.press_action()
            self.release_action()  
        
    def press_action(self):
        """ Press button event handler """
        
        if not self.enabled:
            return
        
        self.clicked = True
        self.clean_draw_update()
        self.notify_press_listeners()
        
        self.press_time = pygame.time.get_ticks()
        
        self.keep_sending = False
        time.sleep(0.12)
        self.keep_sending = True
        self.press_thread = Thread(target=self.keep_sending_event)                
        self.press_thread.start()
        state = State()
        state.pos = self.pos
        self.notify_area_listeners(state)
    
    def keep_sending_event(self):
        """ Keep sending event when button was kept pressed """
        
        state = State()
        state.pos = self.pos
        time.sleep(0.5)
        while self.keep_sending:
            self.notify_area_listeners(state)
            time.sleep(0.1)
    
    def release_action(self, event):
        """ Release button event handler """
         
        if not self.enabled:
            return
        
        self.clicked = False
        self.clean_draw_update()
        release_time = pygame.time.get_ticks()
        time_pressed = release_time - self.press_time
        state = State()
        
        if time_pressed >= self.LONG_PRESS_TIME:
            state.long_press = True
        else:
            state.long_press = False
            
        self.notify_release_listeners(state)
        with self.lock:
            self.keep_sending = False
        self.timer.cancel()
        self.timer.join()       
