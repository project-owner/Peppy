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

from ui.component import Component
from util.keys import USER_EVENT_TYPE
from util.config import SCREEN_INFO, FRAME_RATE, SCREENSAVER, NAME, DELAY, \
    KEY_SCREENSAVER_DELAY_1, KEY_SCREENSAVER_DELAY_3

DELAY_1 = 60
DELAY_3 = 180
DELAY_OFF = 0

class ScreensaverDispatcher(Component):
    """ Starts and stops screensavers. Handles switching between plug-ins. """
    
    def __init__(self, util):
        """ Initializer
        
        :param util: utility object which contains configuration
        """
        self.util = util
        self.config = util.config
        Component.__init__(self, util, None, None, False)
        self.current_image = None
        self.current_volume = 0
        self.start_listeners = []
        self.stop_listeners = []
        self.current_screensaver = self.get_screensaver()
        self.update_period = self.current_screensaver.get_update_period()
        self.current_delay = self.get_delay()
        self.current_screen = None
        self.saver_running = False
        self.one_cycle_period = 1000 / self.config[SCREEN_INFO][FRAME_RATE]
        self.counter = 0
        self.delay_counter = 0
    
    def set_current_screen(self, current_screen):
        """ Current screen setter 
        
        :param current_screen: the current screen
        """
        self.current_screen = current_screen
    
    def start_screensaver(self):
        """ Starts screensaver """
        
        if self.current_screen.visible:
            self.notify_start_listeners(None)
        self.current_screen.clean()
        self.current_screen.set_visible(False)
        self.current_screensaver.start()
        self.current_screensaver.refresh()
        self.counter = 0
        self.delay_counter = 0    
        self.saver_running = True
            
    def cancel_screensaver(self):
        """ Stop currently running screensaver. Show current screen. """
        
        self.current_screensaver.stop()
        self.current_screen.set_visible(True)
        self.current_screen.clean_draw_update()
        self.saver_running = False
        self.notify_stop_listeners(None)
    
    def change_saver_type(self, state):
        """ Change the screensaver type 
        
        :param state: button state which contains new screensaver type
        """
        self.current_screensaver = self.get_screensaver()
        self.update_period = self.current_screensaver.get_update_period()
        self.current_screensaver.set_image(self.current_image)
        
    def change_saver_delay(self, state):
        """ Change the delay before screensaver starts
        
        :param state: button state which contains new delay
        """
        self.current_delay = self.get_delay()
        
    def get_screensaver(self):
        """ Return current screensaver """
        
        name = self.config[SCREENSAVER][NAME]
        saver = self.util.load_screensaver(name)

        try:
            saver.set_image(self.current_image)
            saver.set_volume(self.current_volume)
        except:
            pass
        return saver
    
    def get_delay(self):
        """ Return current delay """
        
        delay = DELAY_OFF
        delay_setting = self.config[SCREENSAVER][DELAY]
        if delay_setting == KEY_SCREENSAVER_DELAY_1:
            delay = DELAY_1
        elif delay_setting == KEY_SCREENSAVER_DELAY_3:
            delay = DELAY_3
        return delay
    
    def refresh(self):
        """ Refresh screensaver """
        
        if self.saver_running:
            self.counter = self.counter + 1
            if int(self.counter * self.one_cycle_period) == self.update_period * 1000:
                self.current_screensaver.refresh()
                self.counter = 0
        else:
            if self.current_delay == 0:
                return
            self.delay_counter = self.delay_counter + 1
            if int(self.delay_counter * self.one_cycle_period) == self.current_delay * 1000:
                self.start_screensaver()                
        
    def change_image(self, state):
        """ Set new image on screensaver
        
        :param state: button state which contains new image
        """ 
        if getattr(state, "icon_base", None) == None and getattr(state, "full_screen_image", None) == None:
            return
        
        if getattr(state, "full_screen_image", None) != None:            
            self.current_image = state.full_screen_image
        elif getattr(state, "icon_base", None) != None:
            self.current_image = state.icon_base
                
        self.current_screensaver.set_song_info(state)
        self.current_screensaver.set_image(self.current_image)
    
    def change_image_folder(self, folder):
        """ Change image folder
        
        :param folder: new folder
        """  
        self.current_screensaver.set_image_folder(folder)
        
    def change_volume(self, volume):
        """ Set new volume level
        
        :param volume: new volume level
        """        
        self.current_volume = volume.position
        self.current_screensaver.set_volume(self.current_volume)
    
    def handle_event(self, event):
        """ Handle user input events. Stop screensaver if it's running or restart dispatcher.
        
        :param event: input event (e.g. mouse click)
        """
        if event.type == pygame.MOUSEBUTTONUP or event.type == USER_EVENT_TYPE:
            if self.saver_running:               
                self.cancel_screensaver()
            else:
                self.delay_counter = 0                
                
    def add_start_listener(self, listener):
        """ Add start screensaver event listener
        
        :param listener: start screensaver event listener
        """
        if listener not in self.start_listeners:
            self.start_listeners.append(listener)
            
    def notify_start_listeners(self, state):
        """ Notify start screensaver event listeners
        
        :param state: button state
        """
        for listener in self.start_listeners:
            listener(state)
            
    def add_stop_listener(self, listener):
        """ Add stop screensaver event listener
        
        :param listener: stop screensaver event listener
        """
        if listener not in self.stop_listeners:
            self.stop_listeners.append(listener)
            
    def notify_stop_listeners(self, state):
        """ Notify stop screensaver event listeners
        
        :param state: button state
        """
        for listener in self.stop_listeners:
            listener(state)
                
