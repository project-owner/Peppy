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

import pygame
import logging
from threading import RLock
import time
from datetime import timedelta
from util.keys import KEY_SUB_TYPE, SUB_TYPE_KEYBOARD, KEY_ACTION, \
    KEY_KEYBOARD_KEY, USER_EVENT_TYPE

class RotaryEncoder(object):
    """ This class handles Rotary Encoders (RE).
     
    It's based on rotary_class.py by Bob Rathbone:
	https://bobrathbone.com/raspberrypi/documents/Raspberry%20Rotary%20Encoders.pdf
    Each RE event will be wrapped into user event to simplify event processing
    """
    CLOCKWISE=1
    ANTICLOCKWISE=2
    BUTTONDOWN=3
    BUTTONUP=4
    KEY_DOWN_UP_INTERVAL = 0.05

    rotary_a = 0
    rotary_b = 0
    rotary_c = 0
    last_state = 0
    direction = 0
    
    def __init__(self, pin_a, pin_b, button, key_increment, key_decrement, key_select, jitter_filter):
        """ Initializer
        
        :param pin_a: GPIO pin number to increment in format <chip>/pin, e.g. "gpiochip0/11"
        :param pin_a: GPIO pin number to decrement in format <chip>/pin
        :param button: GPIO pin number for push-button in format <chip>/pin
        :param key_increment: keyboard key for increment event
        :param key_decrement: keyboard key for decrement event
        :param key_select: keyboard key for selection event
        :param jitter_filter: jitter filter 0-no filter, 2 - two clicks before event
        """
        self.lock = RLock()
        try:
            import gpiod
            self.gpiod = gpiod
        except ImportError:
            logging.error("Failed to import gpiod module")
            return
        from .gpiomon import GPIOMon
        self.GPIOMon = GPIOMon
        
        self.gpiochip_a, self.pin_a = self.parse_pin(pin_a)
        self.gpiochip_b, self.pin_b = self.parse_pin(pin_b)
        self.gpiochip_button, self.button = self.parse_pin(button)
        self.key_increment = key_increment 
        self.key_decrement = key_decrement 
        self.key_select = key_select
        self.jitter_filter = jitter_filter

        self.gpiomon_a = self.GPIOMon(
            dev_name=f"/dev/{self.gpiochip_a}",
            lines=self.pin_a,
            settings=self.gpiod.LineSettings(
                edge_detection=self.gpiod.line.Edge(self.gpiod.line.Edge.FALLING),
                bias=self.gpiod.line.Bias(self.gpiod.line.Bias.PULL_UP),
            ),
            handler=self.handle_rotation_event,
            args=(self.gpiochip_a, pin_a)
        )
        self.gpiomon_b = self.GPIOMon(
            dev_name=f"/dev/{self.gpiochip_b}",
            lines=self.pin_b,
            settings=self.gpiod.LineSettings(
                edge_detection=self.gpiod.line.Edge(self.gpiod.line.Edge.FALLING),
                bias=self.gpiod.line.Bias(self.gpiod.line.Bias.PULL_UP),
            ),
            handler=self.handle_rotation_event,
            args=(self.gpiochip_b, pin_b)
        )
        self.gpiomon_button = self.GPIOMon(
            dev_name=f"/dev/{self.gpiochip_b}",
            lines=self.pin_b,
            settings=self.gpiod.LineSettings(
                edge_detection=self.gpiod.line.Edge(self.gpiod.line.Edge.BOTH),
                bias=self.gpiod.line.Bias(self.gpiod.line.Bias.PULL_UP),
                debounce_period=timedelta(milliseconds=200),
            ),
            handler=self.handle_button_event,
        )

        self.increment_counter = 0
        self.decrement_counter = 0

    @staticmethod
    def parse_pin(pin):
        raw = pin.split("/")
        if len(raw) < 2:
            return 'gpiochip0', int(pin)
        return raw[0], int(raw[1])

    def handle_rotation_event(self, e, gpiochip, pin):
        """ Callback method for rotation RE events.
        
        Makes required calculations and calls event handler with event defining rotation direction 
        
        :param e: gpiod event
        :param gpiochip: GPIO chip
        :param pin: GPIO pin number
        """
        if gpiochip == self.gpiochip_a and pin == self.pin_a:
            self.rotary_a = 0
        else:
            self.rotary_a = 1

        if gpiochip == self.gpiochip_b and pin == self.pin_b:
            self.rotary_b = 0
        else:
            self.rotary_b = 1

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
    
    def handle_button_event(self, e):
        """ Callback method for push-button event.
         
        Calls event handler with event defining button Up or Down state
        
        :param button: pin number of push-button  
        """
        if e.event_type == self.gpiod.EdgeEvent.Type.RISING_EDGE:
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
            if self.increment_counter == self.jitter_filter:
                d[KEY_KEYBOARD_KEY] = self.key_increment
                self.increment_counter = 0
                self.decrement_counter = 0                
            else:
                self.increment_counter += 1
                self.decrement_counter = 0
                return
        elif event == RotaryEncoder.ANTICLOCKWISE:
            logging.debug("Anti-Clockwise")
            if self.decrement_counter == self.jitter_filter:
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
            if d[KEY_KEYBOARD_KEY] == None:
                return

            event = pygame.event.Event(USER_EVENT_TYPE, **d)
            pygame.event.post(event)
            logging.debug("Event-1 posted: " + str(event))

            d[KEY_ACTION] = pygame.KEYUP
            time.sleep(self.KEY_DOWN_UP_INTERVAL)
            event = pygame.event.Event(USER_EVENT_TYPE, **d)
            pygame.event.post(event)
            logging.debug("Event-2 posted: " + str(event))
