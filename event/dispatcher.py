# Copyright 2016 Peppy Player peppy.player@gmail.com
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

import logging
from pygame.time import Clock

from ui.menu.stationmenu import StationMenu
from ui.screen.station import StationScreen
from util.config import USAGE, USE_LIRC, USE_ROTARY_ENCODERS 
from util.keys import *

# Maps IR remote control keys to keyboard keys
lirc_keyboard_map = {"options" : pygame.K_m,
                     "power" : pygame.K_END,
                     "home" : pygame.K_HOME,
                     "0" : pygame.K_SPACE,
                     "1" : pygame.K_SPACE,
                     "return" : pygame.K_RETURN,
                     "left" : pygame.K_LEFT,
                     "right" : pygame.K_RIGHT,
                     "up" : pygame.K_UP,
                     "down" : pygame.K_DOWN,
                     "up" : pygame.K_UP,
                     "down" : pygame.K_DOWN,
                     "next" : pygame.K_PAGEUP,
                     "previous" : pygame.K_PAGEDOWN,
                     "mute" : pygame.K_x,
                     "back" : pygame.K_ESCAPE}

class EventDispatcher(object):
    """ Event Dispatcher 
    This class runs two separate event loops:
    - Main event loop which handles mouse, keyboard and user events
    - LIRC event loop which handles LIRC events
    """

    def __init__(self, screensaver_dispatcher, util):
        """ Initializer        
        :param screensaver_dispatcher: reference to screensaver dispatcher used for forwarding events
        :param util: utility object which keeps configuration settings and utility methods        
        """
        self.screensaver_dispatcher = screensaver_dispatcher
        self.config = util.config       
        self.frame_rate = self.config[SCREEN_INFO][FRAME_RATE]
        self.screensaver_dispatcher.frame_rate = self.frame_rate
        self.lirc = None
        self.lirc_thread = None
        self.init_lirc()
        self.init_rotary_encoders()
        self.volume_initialized = False
        self.screensaver_was_running = False        
    
    def set_current_screen(self, current_screen):
        """ Set current screen.        
        All events are applicable for the current screen only. 
        Logo screensaver needs current screen to get the current logo.
        :param current_screen: reference to the current screen
        """
        self.current_screen = current_screen
        self.screensaver_dispatcher.set_current_screen(current_screen)
    
    def init_lirc(self):
        """ LIRC initializer.         
        It's not executed if disabled in config.txt. Starts new thread for IR events handling. 
        """        
        if not self.config[USAGE][USE_LIRC]:
            return
        
        try:
            import pylirc
            self.lirc = pylirc
            self.lirc.init("radio")
            self.lirc.blocking(0)
        except ImportError:
            logging.error("PYLIRC library not found")

    def init_rotary_encoders(self):
        """ Rotary encoders (RE) initializer.        
        This is executed only if RE enabled in config.txt. Two REs are configured this way:
        1. Volume Control: GPIO16 - Volume Up, GPIO26 - Volume Down, GPIO13 - Mute
        2. Tuning: GPIO12 - Move Right, GPIO6 - Move Left, GPIO5 - Select
        RE events will be wrapped into keyboard events with the following assignment:
        Volume Up - '+' key on numeric keypad, Volume Down - '-' key on keypad, Mute - 'x' key         
        """        
        if not self.config[USAGE][USE_ROTARY_ENCODERS]:
            return        
        from event.rotary import RotaryEncoder 
        RotaryEncoder(16, 26, 13, pygame.K_KP_PLUS, pygame.K_KP_MINUS, pygame.K_x)
        RotaryEncoder(12, 6, 5, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RETURN)

    def handle_lirc_event(self, code):
        """ LIRC event handler.        
        To simplify event handling it wraps IR events into user event with keyboard sub-type. 
        For one IR event it generates two events - one for key down and one for key up.
        """
        if self.screensaver_dispatcher.saver_running:
                self.screensaver_dispatcher.cancel_screensaver()
                return        
        d = {}
        d[KEY_SUB_TYPE] = SUB_TYPE_KEYBOARD
        d[KEY_ACTION] = pygame.KEYDOWN
        d[KEY_KEYBOARD_KEY] = None
                
        try:
            d[KEY_KEYBOARD_KEY] = lirc_keyboard_map[code[0]]
            station_screen = isinstance(self.current_screen, StationScreen)
                
            if station_screen and self.current_screen.station_menu.current_mode == StationMenu.STATION_MODE:
                if code[0] == "up":
                    d[KEY_KEYBOARD_KEY] = kbd_keys[KEY_VOLUME_UP]
                elif code[0] == "down":
                    d[KEY_KEYBOARD_KEY] = kbd_keys[KEY_VOLUME_DOWN]
                            
            logging.debug("Received IR key: %s", d[KEY_KEYBOARD_KEY])
        except KeyError:
            logging.debug("Received not supported key: %s", code[0])
            pass
                
        if d[KEY_KEYBOARD_KEY]:
            event = pygame.event.Event(USER_EVENT_TYPE, **d)
            pygame.event.post(event)
            if not self.screensaver_dispatcher.saver_running:
                d[KEY_ACTION] = pygame.KEYUP
                event = pygame.event.Event(USER_EVENT_TYPE, **d)
                pygame.event.post(event)

    def handle_keyboard_event(self, event):
        """ Keyboard event handler.         
        Wraps keyboard events into user event. Exits upon Ctrl-C. 
        Distinguishes key up and key down.        
        :param event: event to handle
        """        
        keys = pygame.key.get_pressed() 
        if keys[pygame.K_LCTRL] and event.key == pygame.K_c: 
            self.shutdown(event)
        elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            if self.screensaver_dispatcher.saver_running:
                self.screensaver_dispatcher.cancel_screensaver()
                return
            self.handle_event(event)
            d = {}
            d[KEY_SUB_TYPE] = SUB_TYPE_KEYBOARD
            d[KEY_ACTION] = event.type
            d[KEY_KEYBOARD_KEY] = event.key
            event = pygame.event.Event(USER_EVENT_TYPE, **d)            
            pygame.event.post(event)
    
    def handle_event(self, event):
        """ Forward event to the current screen and screensaver dispatcher         
        :param event: event to handle
        """        
        self.screensaver_dispatcher.handle_event(event)
        self.current_screen.handle_event(event)
    
    def init_volume(self, volume):
        """ Volume initializer        
        This method will be executed only once upon system startup.
        It assumes that current screen is Station Screen.
        After initialization it removes itself as a listener        
        :param volume: initial volume level
        """        
        if volume == -1 or self.volume_initialized:
            return
        else:
            try:
                v = self.current_screen.volume
                if v:
                    v.set_position(int(volume))
                    v.update_position()
                    self.volume_initialized = True
                    self.player.remove_volume_listener(self.init_volume)
            except:
                pass
    
    def dispatch(self, player, shutdown):
        """ Dispatch events.        
        Runs the main event loop. Redirects events to corresponding handler.
        Distinguishes four types of events:
        - Quit event - when user closes window (Windows only)
        - Keyboard events
        - Mouse events
        - User Events        
        :param player: reference to player object
        "param shutdown: shutdown method to use when user exits
        """        
        self.player = player
        self.shutdown = shutdown
        mouse_events = [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]
        pygame.event.clear()
        self.player.add_volume_listener(self.init_volume)
        self.player.add_player_listener(self.current_screen.screen_title.set_text)
        clock = Clock()        
        
        while 1:
            for event in pygame.event.get():
                s = str(event)
                logging.debug("Received event: %s", s) 
                if event.type == pygame.QUIT:
                    self.shutdown(event) 
                elif (event.type == pygame.KEYDOWN or event.type == pygame.KEYUP) and not self.config[USAGE][USE_LIRC]:
                    self.handle_keyboard_event(event)                                
                elif event.type in mouse_events or event.type == USER_EVENT_TYPE:
                    self.handle_event(event)                    
            if self.lirc != None:
                code = self.lirc.nextcode()
                if code != None:
                    self.handle_lirc_event(code)
            self.current_screen.refresh()
            self.screensaver_dispatcher.refresh()
            clock.tick(self.frame_rate)
            