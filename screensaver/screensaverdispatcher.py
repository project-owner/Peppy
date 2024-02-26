# Copyright 2016-2024 Peppy Player peppy.player@gmail.com
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
import logging

from ui.component import Component
from ui.container import Container
from ui.state import State
from util.keys import USER_EVENT_TYPE
from util.config import *

DELAY_1 = 60
DELAY_3 = 180
DELAY_OFF = 0

WEB_SAVERS = [CLOCK, LOGO, LYRICS, WEATHER, SLIDESHOW, PEXELS, MONITOR, STOCK, HOROSCOPE]

class ScreensaverDispatcher(Component):
    """ Starts and stops screensavers. Handles switching between plug-ins. """
    
    def __init__(self, util, webserver=None):
        """ Initializer
        
        :param util: utility object which contains configuration
        """
        self.util = util
        self.config = util.config
        self.send_json_to_web_ui = webserver.send_json_to_web_ui
        Component.__init__(self, util, None, None, False)
        self.current_image = None
        self.current_volume = 0
        self.start_listeners = []
        self.stop_listeners = []
        self.config[ACTIVE_SAVERS] = self.get_active_savers()
        self.config[DISABLED_SAVERS] = self.set_initial_saver_name()
        self.set_initial_saver_name()
        self.current_screensaver = self.get_screensaver()
        if self.current_screensaver:
            self.update_period = self.current_screensaver.get_update_period()
        self.current_delay = self.get_delay()
        self.current_screen = None
        self.saver_running = False
        self.one_cycle_period = 1000 / self.config[SCREEN_INFO][FRAME_RATE]
        self.counter = 0
        self.delay_counter = 0
        self.previous_saver = None
        self.internally_refreshed = [VUMETER, SPECTRUM]

    def get_active_savers(self):
        """ Get all configured savers

        :return: the list of all selected savers
        """
        items = []

        for k, v in self.config[SCREENSAVER_MENU].items():
            if v: items.append(k)

        return items

    def set_initial_saver_name(self):
        """ Set inital saver name depending on connection and selected savers 

        :return: the list of the disabled savers        
        """
        if not self.util.connected_to_internet:
            disabled_items = [WEATHER, LYRICS, RANDOM, PEXELS, HOROSCOPE, STOCK]
        else:
            disabled_items = []

        items = self.config[ACTIVE_SAVERS]
        if len(items) > 0:
            current_saver_name = items[0]
        else:
            current_saver_name = None

        for s in items:
            if s == self.config[SCREENSAVER][NAME] and s not in disabled_items:
                current_saver_name = s
                break

        self.config[SCREENSAVER][NAME] = current_saver_name

        return disabled_items
    
    def set_current_screen(self, current_screen):
        """ Current screen setter 
        
        :param current_screen: the current screen
        """
        self.current_screen = current_screen
    
    def start_screensaver(self, name=None, state=None):
        """ Starts screensaver 
        
        :param name: screensaver name
        :param state: state object with song info
        """
        if not self.current_screensaver:
            return

        if self.config[DSI_DISPLAY_BACKLIGHT][USE_DSI_DISPLAY] and self.config[DSI_DISPLAY_BACKLIGHT][SCREENSAVER_DISPLAY_POWER_OFF]:
            self.config[BACKLIGHTER].power = False    
        else:
            if self.config[DSI_DISPLAY_BACKLIGHT][USE_DSI_DISPLAY] and self.config[BACKLIGHTER]:
                screensaver_brightness = int(self.config[DSI_DISPLAY_BACKLIGHT][SCREENSAVER_BRIGHTNESS])
                self.config[BACKLIGHTER].brightness = screensaver_brightness

        if name != None: # info
            self.previous_saver = self.config[SCREENSAVER][NAME]
            self.config[SCREENSAVER][NAME] = name
            self.change_saver_type()
            if name == LYRICS:
                if state != None and hasattr(state, "album"):
                    self.current_screensaver.set_song_info(state)
                else:
                    self.current_screensaver.set_song_info(State())

        if self.config[SCREENSAVER][NAME] in WEB_SAVERS:
            s = State()
            s.screen = self.current_screensaver
        else:
            s = None

        if not self.current_screensaver or not self.current_screensaver.is_ready():
            return

        self.current_screen.clean()
        self.current_screen.set_visible(False)
        self.current_screensaver.set_visible(True)
        self.current_screensaver.start_callback = self.notify_start_listeners
        self.current_screensaver.start()

        self.util.run_script(self.config[SCRIPTS][SCRIPT_SCREENSAVER_START])

        if not self.current_screensaver.ready:
            return

        self.current_screensaver.refresh(init=True)
        self.counter = 0
        self.delay_counter = 0    
        self.saver_running = True

        self.notify_start_listeners(s)
            
    def cancel_screensaver(self, event=None):
        """ Stop currently running screensaver. Show current screen. 
        
        :param event: mouse event
        """
        if not self.current_screensaver:
            return

        if self.config[DSI_DISPLAY_BACKLIGHT][USE_DSI_DISPLAY] and self.config[DSI_DISPLAY_BACKLIGHT][SCREENSAVER_DISPLAY_POWER_OFF]:
            self.config[BACKLIGHTER].power = True    
        else:
            if self.config[DSI_DISPLAY_BACKLIGHT][USE_DSI_DISPLAY] and self.config[BACKLIGHTER]:
                screensaver_brightness = int(self.config[DSI_DISPLAY_BACKLIGHT][SCREEN_BRIGHTNESS])
                self.config[BACKLIGHTER].brightness = screensaver_brightness
        
        if getattr(self.current_screensaver, "has_exit_area", False) and not self.current_screensaver.is_exit_clicked(event):
            s = State()
            s.screen = self.current_screensaver
            self.notify_start_listeners(s)
            return

        self.current_screensaver.stop()
        self.current_screensaver.set_visible(False)
        self.current_screen.set_visible(True)
        self.current_screen.clean_draw_update()
        self.saver_running = False
        self.notify_stop_listeners(None)

        if self.previous_saver != None and self.config[SCREENSAVER][NAME] != self.previous_saver:
            self.config[SCREENSAVER][NAME] = self.previous_saver
            self.change_saver_type()
        
        self.previous_saver = None
        self.util.run_script(self.config[SCRIPTS][SCRIPT_SCREENSAVER_STOP])
    
    def change_saver_type(self, state=None):
        """ Change the screensaver type 
        
        :param state: button state which contains new screensaver type
        """        
        self.current_screensaver = self.get_screensaver()
        self.update_period = self.current_screensaver.get_update_period()
        self.current_screensaver.set_image(self.current_image)
        try:
            self.current_screensaver.set_util(self.util)
        except:
            pass
        
    def change_saver_delay(self, state):
        """ Change the delay before screensaver starts
        
        :param state: button state which contains new delay
        """
        self.current_delay = self.get_delay()
        
    def get_screensaver(self):
        """ Return current screensaver """
        
        name = self.config[SCREENSAVER][NAME]
        logging.debug(f"Get screensaver {name}")

        try:
            saver = self.util.load_screensaver(name)
            saver.set_image(self.current_image)
            saver.set_volume(self.current_volume)
            if name == VUMETER:
                saver.set_web(self.send_json_to_web_ui)
            return saver
        except Exception as e:
            logging.debug(e)
    
    def get_delay(self):
        """ Return current delay """
        
        delay = DELAY_OFF
        delay_setting = self.config[SCREENSAVER_DELAY][DELAY]
        if delay_setting == KEY_SCREENSAVER_DELAY_1:
            delay = DELAY_1
        elif delay_setting == KEY_SCREENSAVER_DELAY_3:
            delay = DELAY_3
        return delay
    
    def update(self):
        """ Update screensaver """

        return self.current_screensaver.update()

    def refresh(self):
        """ Refresh screensaver """

        a = None

        if self.saver_running:
            self.counter = self.counter + 1

            if self.current_screensaver.name in self.internally_refreshed:
                return self.current_screensaver.refresh()
            else:
                if int(self.counter * self.one_cycle_period) == self.update_period * 1000:
                    a = self.current_screensaver.refresh()
                    self.counter = 0
                    if self.config[SCREENSAVER][NAME] in WEB_SAVERS:
                        s = State()
                        if isinstance(self.current_screensaver, Component):
                            screen_savers = [WEATHER, CLOCK, LYRICS, LOGO]
                            if self.current_screensaver.name in screen_savers:
                                s.screen = self.current_screensaver
                            else:
                                s.screen = Container(self.util)
                                s.screen.components = [self.current_screensaver]
                        else:
                            s.screen = self.current_screensaver
                        self.notify_start_listeners(s)
                    return a
        else:
            if self.current_delay == 0:
                return a
            self.delay_counter = self.delay_counter + 1
            if int(self.delay_counter * self.one_cycle_period) == self.current_delay * 1000:
                self.start_screensaver()
        return a                
        
    def change_image(self, state):
        """ Set new image on screensaver
        
        :param state: button state which contains new image
        """
        if not self.current_screensaver:
            return

        if self.current_screensaver.name == LYRICS:
            self.current_screensaver.set_song_info(state)

        if getattr(state, "icon_base", None) == None and getattr(state, "full_screen_image", None) == None:
            return
        
        if getattr(state, "full_screen_image", None) != None:            
            self.current_image = state.full_screen_image
        elif getattr(state, "icon_base", None) != None:
            self.current_image = state.icon_base
                
        self.current_screensaver.set_image(self.current_image)
    
    def change_image_folder(self, folder):
        """ Change image folder
        
        :param folder: new folder
        """
        if not self.current_screensaver:
            return

        self.current_screensaver.set_image_folder(folder)
        
    def change_volume(self, volume):
        """ Set new volume level
        
        :param volume: new volume level
        """
        if not self.current_screensaver:
            return

        self.current_volume = volume.position
        self.current_screensaver.set_volume(self.current_volume)
        
        if self.config[USAGE][USE_VU_METER]:
            try:
                vu_meter = self.util.screensaver_cache[VUMETER]
                vu_meter.set_volume(self.current_volume)
            except:
                pass
    
    def handle_event(self, event):
        """ Handle user input events. Stop screensaver if it's running or restart dispatcher.
        
        :param event: input event (e.g. mouse click)
        """
        if event.type == pygame.MOUSEBUTTONUP or event.type == USER_EVENT_TYPE:
            if self.saver_running:               
                self.cancel_screensaver(event)
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
