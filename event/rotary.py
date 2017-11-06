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
import logging
from threading import RLock
import threading
import time
from util.keys import KEY_SUB_TYPE, SUB_TYPE_KEYBOARD, KEY_ACTION, \
    KEY_KEYBOARD_KEY, USER_EVENT_TYPE

class RotaryEncoder(object):
    """ This class handles Rotary Encoders (RE).
     
    It's based on rotary_class.py by Bob Rathbone:
    http://www.bobrathbone.com/raspberrypi/Raspberry%20Rotary%20Encoders.pdf
    Each RE event will be wrapped into user event to simplify event processing
    """
    CLOCKWISE=1
    ANTICLOCKWISE=2
    BUTTONDOWN=3
    BUTTONUP=4
    ROTARY_JITTER_TOLERANCE = 2
    KEY_DOWN_UP_INTERVAL = 0.1

    rotary_a = 0
    rotary_b = 0
    rotary_c = 0
    last_state = 0
    direction = 0
    
    def __init__(self, pinA, pinB, button, key_increment, key_decrement, key_select):
        """ Initializer
        
        :param pinA: GPIO pin number to increment
        :param pinA: GPIO pin number to decrement
        :param button: GPIO pin number for push-button
        :param key_increment: keyboard key for increment event
        :param key_decrement: keyboard key for decrement event
        :param key_select: keyboard key for selection event
        """
        self.lock = RLock()
        try:
            import RPi.GPIO as GPIO
            self.gpio = GPIO
        except ImportError:
            logging.error("Rpi.GPIO not found")
            return
        
        self.pinA = pinA
        self.pinB = pinB
        self.button = button
        self.key_increment = key_increment 
        self.key_decrement = key_decrement 
        self.key_select = key_select
        self.gpio.setmode(self.gpio.BCM)
        self.gpio.setwarnings(False)
        self.gpio.setup(self.pinA, self.gpio.IN, pull_up_down=self.gpio.PUD_UP)
        self.gpio.setup(self.pinB, self.gpio.IN, pull_up_down=self.gpio.PUD_UP)
        self.gpio.setup(self.button, self.gpio.IN, pull_up_down=self.gpio.PUD_UP)
        self.gpio.add_event_detect(self.pinA, self.gpio.FALLING, callback=self.handle_rotation_event)
        self.gpio.add_event_detect(self.pinB, self.gpio.FALLING, callback=self.handle_rotation_event)
        self.gpio.add_event_detect(self.button, self.gpio.BOTH, callback=self.handle_button_event, bouncetime=200)
        self.increment_counter = 0
        self.decrement_counter = 0

    def handle_rotation_event(self, p):
        """ Callback method for rotation RE events.
        
        Makes required calculations and calls event handler with event defining rotation direction 
        
        :param p: pin
        """        
        if self.gpio.input(self.pinA):
            self.rotary_a = 1
        else:
            self.rotary_a = 0
        
        if self.gpio.input(self.pinB):
            self.rotary_b = 1
        else:
            self.rotary_b = 0

        self.rotary_c = self.rotary_a ^ self.rotary_b
        new_state = self.rotary_a * 4 + self.rotary_b * 2 + self.rotary_c * 1
        delta = (new_state-self.last_state) % 4
        self.last_state = new_state
        event = 0
        
        if delta == 1:
            if self.direction == self.CLOCKWISE:
                event = self.direction
            else:
                self.direction = self.CLOCKWISE
        elif delta == 3:
            if self.direction == self.ANTICLOCKWISE:
                event = self.direction
            else:
                self.direction = self.ANTICLOCKWISE
        
        if event > 0:
            self.handle_event(event)
    
    def handle_button_event(self, button):
        """ Callback method for push-button event.
         
        Calls event handler with event defining button Up or Down state
        
        :param button: pin number of push-button  
        """        
        if self.gpio.input(button):
            event = self.BUTTONUP
        else:
            event = self.BUTTONDOWN
        self.handle_event(event)
        return
    
    def handle_event(self, event):
        """ Event handler for rotation and button events.
        
        Generates two Pygame user event for each RE event. 
        One button down and one button up events.
        
        :param event: the event to handle
        """
        d = {}
        d[KEY_SUB_TYPE] = SUB_TYPE_KEYBOARD
        d[KEY_ACTION] = pygame.KEYDOWN
        d[KEY_KEYBOARD_KEY] = None

        if event == RotaryEncoder.CLOCKWISE:
            logging.debug("Clockwise")
            if self.increment_counter == self.ROTARY_JITTER_TOLERANCE:
                d[KEY_KEYBOARD_KEY] = self.key_increment
                self.increment_counter = 0
                self.decrement_counter = 0                
            else:
                self.increment_counter += 1
                self.decrement_counter = 0
                return
        elif event == RotaryEncoder.ANTICLOCKWISE:
            logging.debug("Anti-Clockwise")
            if self.decrement_counter == self.ROTARY_JITTER_TOLERANCE:
                d[KEY_KEYBOARD_KEY] = self.key_decrement
                self.decrement_counter = 0
                self.increment_counter = 0                
            else:
                self.decrement_counter += 1
                self.increment_counter = 0
                return
        elif event == RotaryEncoder.BUTTONUP:
            d[KEY_KEYBOARD_KEY] = self.key_select
            logging.debug("Button pushed")
        
        with self.lock:
            event = pygame.event.Event(USER_EVENT_TYPE, **d)
            thread = threading.Thread(target=pygame.event.post, args=[event])
            thread.start()
            d[KEY_ACTION] = pygame.KEYUP
            time.sleep(self.KEY_DOWN_UP_INTERVAL)
            event = pygame.event.Event(USER_EVENT_TYPE, **d)
            thread = threading.Thread(target=pygame.event.post, args=[event])
            thread.start()
