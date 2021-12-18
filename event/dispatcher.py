# Copyright 2016-2021 Peppy Player peppy.player@gmail.com
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

import os
import logging
import pygame
from pygame.time import Clock
from util.config import BUTTON_TYPE, USAGE, USE_LIRC, USE_ROTARY_ENCODERS, SCREEN_INFO, \
    FRAME_RATE, SHOW_MOUSE_EVENTS, FLIP_TOUCH_XY, WIDTH, HEIGHT, MULTI_TOUCH, GPIO, ROTARY_VOLUME_UP, ROTARY_VOLUME_DOWN, ROTARY_VOLUME_MUTE, \
    ROTARY_NAVIGATION_LEFT, ROTARY_NAVIGATION_RIGHT, ROTARY_NAVIGATION_SELECT, ROTARY_JITTER_FILTER, USE_BUTTONS, \
    BUTTON_LEFT, BUTTON_RIGHT, BUTTON_UP, BUTTON_DOWN, BUTTON_SELECT, BUTTON_VOLUME_UP, BUTTON_VOLUME_DOWN, \
    BUTTON_MUTE, BUTTON_PLAY_PAUSE, BUTTON_NEXT, BUTTON_PREVIOUS, BUTTON_HOME, BUTTON_POWEROFF
from util.keys import SELECT_EVENT_TYPE, kbd_keys, KEY_SUB_TYPE, SUB_TYPE_KEYBOARD, KEY_ACTION, KEY_KEYBOARD_KEY, USER_EVENT_TYPE, \
    VOICE_EVENT_TYPE, KEY_END, REST_EVENT_TYPE, KEY_VOLUME_UP, KEY_VOLUME_DOWN, KEY_MUTE, IMAGE_VIEWER_SCREEN, KEY_PLAY_PAUSE, KEY_PAGE_UP, \
    KEY_PAGE_DOWN
from event.gpiobutton import GpioButton
from event.i2cbuttons import I2CButtons

HOLD_BUTTON_SCREENS = [IMAGE_VIEWER_SCREEN]

# Maps IR remote control keys to keyboard keys
lirc_keyboard_map = {"options": pygame.K_m,
                     "power": pygame.K_END,
                     "home": pygame.K_HOME,
                     "pause": pygame.K_SPACE,
                     "play": pygame.K_SPACE,
                     "ok": pygame.K_RETURN,
                     "left": pygame.K_LEFT,
                     "right": pygame.K_RIGHT,
                     "up": pygame.K_UP,
                     "down": pygame.K_DOWN,
                     "next": pygame.K_PAGEUP,
                     "previous": pygame.K_PAGEDOWN,
                     "next_page": pygame.K_KP_PLUS,
                     "previous_page": pygame.K_KP_MINUS,
                     "mute": pygame.K_x,
                     "back": pygame.K_ESCAPE,
                     "setup": pygame.K_s,
                     "root": pygame.K_r,
                     "parent": pygame.K_p,
                     "audio": pygame.K_a,
                     "0": pygame.K_0,
                     "1": pygame.K_1,
                     "2": pygame.K_2,
                     "3": pygame.K_3,
                     "4": pygame.K_4,
                     "5": pygame.K_5,
                     "6": pygame.K_6,
                     "7": pygame.K_7,
                     "8": pygame.K_8,
                     "9": pygame.K_9}

class EventDispatcher(object):
    """ Event Dispatcher  
       
    This class runs two separate event loops:
    - Main event loop which handles mouse, keyboard and user events
    - LIRC event loop which handles LIRC events
    """

    def __init__(self, screensaver_dispatcher, util, volume_control):
        """ Initializer      
          
        :param screensaver_dispatcher: reference to screensaver dispatcher used for forwarding events
        :param util: utility object which keeps configuration settings and utility methods
        :param volume_control: volume control object       
        """
        self.screensaver_dispatcher = screensaver_dispatcher
        self.config = util.config
        self.volume_control = volume_control
        self.frame_rate = self.config[SCREEN_INFO][FRAME_RATE]
        self.screen_width = self.config[SCREEN_INFO][WIDTH]
        self.screen_height = self.config[SCREEN_INFO][HEIGHT]
        self.flip_touch_xy = self.config[SCREEN_INFO][FLIP_TOUCH_XY]
        self.multi_touch = self.config[SCREEN_INFO][MULTI_TOUCH]
        self.show_mouse_events = self.config[SHOW_MOUSE_EVENTS]
        self.screensaver_dispatcher.frame_rate = self.frame_rate
        self.lirc = None
        self.lirc_thread = None
        self.init_lirc()
        self.init_buttons()
        self.init_rotary_encoders()
        self.volume_initialized = False
        self.screensaver_was_running = False
        self.run_dispatcher = True
        self.mouse_events = [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]
        self.user_events = [USER_EVENT_TYPE, VOICE_EVENT_TYPE, REST_EVENT_TYPE]
        self.multi_touch_screen = None
        self.mts_state = [False for _ in range(10)]
        self.move_enabled = False
        self.poweroff_flag = 0

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
        
        Starts new thread for IR events handling.        
        It's not executed if IR remote was disabled in config.txt.         
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
              
        This is executed only if RE enabled in config.txt.
        RE events will be wrapped into keyboard events.
        """
        if not self.config[GPIO][USE_ROTARY_ENCODERS]:
            return
        
        volume_up = self.config[GPIO][ROTARY_VOLUME_UP]
        volume_down = self.config[GPIO][ROTARY_VOLUME_DOWN]
        mute = self.config[GPIO][ROTARY_VOLUME_MUTE]
        move_left = self.config[GPIO][ROTARY_NAVIGATION_LEFT]
        move_right = self.config[GPIO][ROTARY_NAVIGATION_RIGHT]
        select = self.config[GPIO][ROTARY_NAVIGATION_SELECT]
        jitter_filter = self.config[GPIO][ROTARY_JITTER_FILTER]

        from event.rotary import RotaryEncoder

        if volume_up and volume_down and mute and jitter_filter:
            try:
                RotaryEncoder(int(volume_up), int(volume_down), int(mute), pygame.K_KP_PLUS, pygame.K_KP_MINUS, pygame.K_x, int(jitter_filter))
            except Exception as e:
                logging.debug(e)

        if move_right and move_left and select and jitter_filter:
            try:
                RotaryEncoder(int(move_right), int(move_left), int(select), pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RETURN, int(jitter_filter))
            except Exception as e:
                logging.debug(e)

    def init_buttons(self):
        """ GPIO buttons initializer.  
              
        This is executed only if buttons were enabled in config.txt.
        Button events will be wrapped into keyboard events.
        """
        if not self.config[GPIO][USE_BUTTONS] or not self.config[GPIO][BUTTON_TYPE]:
            return

        if self.config[GPIO][BUTTON_TYPE] == "GPIO":
            self.init_gpio_buttons()
        elif self.config[GPIO][BUTTON_TYPE] == "I2C":
            self.i2c_buttons = I2CButtons(self.config)

    def init_gpio_buttons(self):
        """ Initializae GPIO buttons """

        self.init_gpio_button(self.config[GPIO][BUTTON_LEFT], pygame.K_LEFT)
        self.init_gpio_button(self.config[GPIO][BUTTON_RIGHT], pygame.K_RIGHT)
        self.init_gpio_button(self.config[GPIO][BUTTON_UP], pygame.K_UP)
        self.init_gpio_button(self.config[GPIO][BUTTON_DOWN], pygame.K_DOWN)
        self.init_gpio_button(self.config[GPIO][BUTTON_SELECT], pygame.K_RETURN)
        self.init_gpio_button(self.config[GPIO][BUTTON_VOLUME_UP], pygame.K_KP_PLUS)
        self.init_gpio_button(self.config[GPIO][BUTTON_VOLUME_DOWN], pygame.K_KP_MINUS)
        self.init_gpio_button(self.config[GPIO][BUTTON_MUTE], pygame.K_x)
        self.init_gpio_button(self.config[GPIO][BUTTON_PLAY_PAUSE], pygame.K_SPACE)
        self.init_gpio_button(self.config[GPIO][BUTTON_NEXT], pygame.K_PAGEUP)
        self.init_gpio_button(self.config[GPIO][BUTTON_PREVIOUS], pygame.K_PAGEDOWN)
        self.init_gpio_button(self.config[GPIO][BUTTON_HOME], pygame.K_HOME)
        self.init_gpio_button(self.config[GPIO][BUTTON_POWEROFF], pygame.K_END)

    def init_gpio_button(self, pin, key):
        """ Initialize GPIO button

        :param pin: GPIO pin number
        :param key: keyboard key
        """
        if pin:
            try:
                GpioButton(int(pin), key)
            except Exception as e:
                logging.debug(e)

    def handle_lirc_event(self, code):
        """ LIRC event handler. 
               
        To simplify event handling it wraps IR events into user event with keyboard sub-type. 
        For one IR event it generates two events - one for key down and one for key up.
        
        :param code: IR code
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
            if code[0] == "power":
                if self.poweroff_flag == 1:
                    self.shutdown()
                else:
                    self.poweroff_flag = 1
            else:
                self.poweroff_flag = 0

            logging.debug("Received IR key: %s", d[KEY_KEYBOARD_KEY])
        except KeyError:
            logging.debug("Received not supported key: %s", code[0])
            pass

        if d[KEY_KEYBOARD_KEY]:
            event = pygame.event.Event(USER_EVENT_TYPE, **d)
            event.source = "lirc"
            pygame.event.post(event)
            d[KEY_ACTION] = pygame.KEYUP
            event = pygame.event.Event(USER_EVENT_TYPE, **d)
            event.source = "lirc"
            pygame.event.post(event)

    def handle_keyboard_event(self, event):
        """ Keyboard event handler. 
                
        Wraps keyboard events into user event. Exits upon Ctrl-C. 
        Distinguishes key up and key down.
                
        :param event: event to handle
        """
        keys = pygame.key.get_pressed()

        if (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]) and event.key == pygame.K_c:
            self.shutdown(event)
        elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            if self.screensaver_dispatcher.saver_running:
                if event.type == pygame.KEYUP:
                    self.screensaver_dispatcher.cancel_screensaver(event)
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
        if self.screensaver_dispatcher.saver_running:
            self.screensaver_was_running = True
        else:
            self.screensaver_was_running = False
        self.screensaver_dispatcher.handle_event(event)

        if not self.screensaver_was_running:
            self.current_screen.handle_event(event)

    def hold_button(self, events):
        """ Handle hold mouse and keyboard buttons. Different from long press
        
        :param events: vents list

        :return: True - event was handled, False - event was not handled
        """
        mouse_pressed = pygame.mouse.get_pressed()
        if (events == None or len(events) == 0) and mouse_pressed and mouse_pressed[0] == True:
            self.pressed_mouse_button += 1
            if self.pressed_mouse_button > 5:
                event = pygame.event.Event(pygame.MOUSEBUTTONDOWN)
                event.pos = self.last_pos
                event.button = 1
                self.handle_event(event)
                event = pygame.event.Event(pygame.MOUSEBUTTONUP)
                event.pos = self.last_pos
                event.button = 1
                self.handle_event(event)
                return True
        else:
            self.pressed_mouse_button = 0

        if events and len(events) == 2 and events[0].type == USER_EVENT_TYPE and events[0].sub_type == 0 \
            and events[0].action == 2 and events[0].keyboard_key == 13 and events[1].type == pygame.KEYDOWN and events[1].key == 13:
            d = {}
            d[KEY_SUB_TYPE] = SUB_TYPE_KEYBOARD
            d[KEY_ACTION] = pygame.KEYDOWN
            d[KEY_KEYBOARD_KEY] = 13
            event = pygame.event.Event(USER_EVENT_TYPE, **d)
            pygame.event.post(event)
            d[KEY_ACTION] = pygame.KEYUP
            event = pygame.event.Event(USER_EVENT_TYPE, **d)
            pygame.event.post(event)
            return True

        return False

    def handle_single_touch(self):
        """ Handle single touch events """
        
        events = pygame.event.get()

        if self.current_screen and hasattr(self.current_screen, "name") and self.current_screen.name in HOLD_BUTTON_SCREENS:
            if self.hold_button(events):
                return

        for event in events:
            source = getattr(event, "source", None)
            if source != "browser" and self.flip_touch_xy and event.type in self.mouse_events:  # not browser event
                x, y = event.pos
                new_x = self.screen_width - x - 1
                new_y = self.screen_height - y - 1
                event.pos = (new_x, new_y)
            s = str(event)
            if self.show_mouse_events:
                logging.debug("Received event: %s", s)
            if event.type == pygame.QUIT:
                self.shutdown(event)
            elif (event.type == pygame.KEYDOWN or event.type == pygame.KEYUP) and source != "lirc":
                self.handle_keyboard_event(event)
            elif event.type in self.mouse_events or event.type in self.user_events:
                if hasattr(event, "pos"):
                    self.last_pos = event.pos
                self.handle_poweroff(event)
                self.handle_volume(event)
                self.handle_event(event)
            elif event.type == SELECT_EVENT_TYPE:
                self.handle_event(event)

    def get_event(self, event_type, x, y):
        """ Prepare event

        :param event_type: event type
        :param x: X coordinate
        :param y: Y coordinate
        :return: event
        """
        event = pygame.event.Event(event_type)
        event.pos = (x, y)
        event.button = 1
        return event

    def handle_multi_touch(self):
        """ Handle multi-touch events """

        for touch in self.multi_touch_screen.poll():
            if self.mts_state[touch.slot] != touch.valid:
                if touch.valid: # pressed
                    self.handle_event(self.get_event(pygame.MOUSEBUTTONDOWN, touch.x, touch.y))
                    self.move_enabled = True
                else: # released
                    self.handle_event(self.get_event(pygame.MOUSEBUTTONUP, touch.x, touch.y))
                    self.move_enabled = False
                self.mts_state[touch.slot] = touch.valid
            else:
                if self.move_enabled and touch.valid: # move
                    self.handle_event(self.get_event(pygame.MOUSEMOTION, touch.x, touch.y))

        for event in pygame.event.get():
            s = str(event)
            source = getattr(event, "source", None)

            if self.show_mouse_events:
                logging.debug("Received event: %s", s)

            if event.type == pygame.QUIT:
                self.shutdown(event)
            elif (event.type == pygame.KEYDOWN or event.type == pygame.KEYUP) and source != "lirc":
                self.handle_keyboard_event(event)
            elif event.type in self.user_events:
                self.handle_poweroff(event)
                self.handle_volume(event)
                self.handle_event(event)
            elif (event.type in self.mouse_events) and source == "browser":
                self.poweroff_flag = 0
                self.handle_event(event)

    def handle_poweroff(self, event):
        """ Handle poweroff hardware button

        :param event: event object
        """
        if event.type == USER_EVENT_TYPE and hasattr(event, "action") and event.action == pygame.KEYUP:
            k = getattr(event, "keyboard_key", None)
            if k and k == kbd_keys[KEY_END]:
                if self.poweroff_flag == 1:
                    self.shutdown(event)
                else:
                    self.poweroff_flag = 1
            else:
                self.poweroff_flag = 0

        if event.type == pygame.MOUSEBUTTONUP:
            self.poweroff_flag = 0

    def handle_volume(self, event):
        """ Handle volume control through rotary encoder

        :param event: event object
        """
        if event.type in self.mouse_events:
            return

        if event.type == USER_EVENT_TYPE and hasattr(event, "action") and event.action == pygame.KEYUP:
            k = getattr(event, "keyboard_key", None)
            if not k: return

            if k == kbd_keys[KEY_VOLUME_UP]:
                self.volume_control.increase_volume()
            elif k == kbd_keys[KEY_VOLUME_DOWN]:
                self.volume_control.decrease_volume()
            elif k == kbd_keys[KEY_MUTE]:
                self.volume_control.mute(event)
            elif k == kbd_keys[KEY_PLAY_PAUSE]:
                self.volume_control.play_pause(event)
            elif k == kbd_keys[KEY_PAGE_UP] or k == kbd_keys[KEY_PAGE_DOWN]:
                self.volume_control.previous_next(event)

    def get_handler(self):
        """ Get either single or multi touch handler

        :return: event handler
        """
        handler = None
        if self.multi_touch:
            try:
                from event.ft5406peppy import Touchscreen
                self.multi_touch_screen = Touchscreen()
                handler = self.handle_multi_touch
            except Exception as e:
                logging.debug("%s", str(e))
        else:
            handler = self.handle_single_touch

        if not handler:
            os._exit(0)
        else:
            return handler

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
        handler = self.get_handler()
        pygame.event.clear()
        clock = Clock()

        while self.run_dispatcher:
            handler()
            if self.lirc != None:
                code = self.lirc.nextcode()
                if code != None:
                    self.handle_lirc_event(code)
            self.current_screen.refresh()
            self.screensaver_dispatcher.refresh()
            clock.tick(self.frame_rate)
