# Copyright 2020 Peppy Player peppy.player@gmail.com
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
from util.keys import KEY_SUB_TYPE, SUB_TYPE_KEYBOARD, KEY_ACTION, \
    KEY_KEYBOARD_KEY, USER_EVENT_TYPE

class GpioButton(object):
    """ This class handles GPIO Button
        Each button event will be wrapped into user event to simplify event processing
    """
    def __init__(self, pin, key):
        """ Initializer
        
        :param pin: GPIO pin number
        :param key: keyboard key
        """
        try:
            import RPi.GPIO as GPIO
            self.gpio = GPIO
        except ImportError:
            logging.error("Rpi.GPIO not found")
            return
        
        self.pin = pin
        self.key = key
        self.gpio.setmode(self.gpio.BCM)
        self.gpio.setwarnings(False)
        self.gpio.setup(pin, self.gpio.IN, pull_up_down=self.gpio.PUD_UP)
        self.gpio.add_event_detect(pin, self.gpio.BOTH, callback=self.handle_button_event, bouncetime=50)

    def handle_button_event(self, pin):
        """ Callback method for push-button event.
         
        :param pin: pin number of push-button  
        """
        d = {}
        d[KEY_SUB_TYPE] = SUB_TYPE_KEYBOARD
        d[KEY_KEYBOARD_KEY] = self.key

        if not self.gpio.input(pin):
            d[KEY_ACTION] = pygame.KEYDOWN
        else:
            d[KEY_ACTION] = pygame.KEYUP
            
        event = pygame.event.Event(USER_EVENT_TYPE, **d)
        pygame.event.post(event)
