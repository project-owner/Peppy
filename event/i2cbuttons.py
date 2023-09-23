# Copyright 2021 Peppy Player peppy.player@gmail.com
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
from util.config import I2C_GPIO_INTERRUPT, I2C_INPUT_ADDRESS, GPIO, BUTTON_LEFT, BUTTON_RIGHT, BUTTON_UP, \
    BUTTON_DOWN, BUTTON_SELECT, BUTTON_VOLUME_UP, BUTTON_VOLUME_DOWN, BUTTON_MUTE, BUTTON_PLAY_PAUSE, BUTTON_NEXT, \
    BUTTON_PREVIOUS, BUTTON_HOME, BUTTON_POWEROFF, I2C

class I2CButtons(object):
    """ This class handles I2C Buttons
        Each button event will be wrapped into user event to simplify event processing
    """
    def __init__(self, config):
        """ Initializer
        
        :param config: configuration object
        """
        self.config = config
        self.i2c_input_address = self.config[I2C][I2C_INPUT_ADDRESS]
        intr = self.config[I2C][I2C_GPIO_INTERRUPT]
        if not self.i2c_input_address or not intr:
            logging.error("Both I2C parameters should be defined: input address and GPIO interrupt pin number")
            return
            
        # init GPIO interrupt
        try:
            import RPi.GPIO as GPIO_LIB
            GPIO_LIB.setmode(GPIO_LIB.BCM)
            GPIO_LIB.setup(intr, GPIO_LIB.IN, pull_up_down=GPIO_LIB.PUD_UP)
            GPIO_LIB.add_event_detect(intr, GPIO_LIB.FALLING, callback=self.handle_i2c_event)
        except ImportError:
            logging.error("Rpi.GPIO not found")
            return

        #I2C init
        try:
            from smbus import SMBus
            self.i2c = SMBus(1)
        except ImportError:
            logging.error("SMBus not found")
            return

        # initialization of the MCP23017 - bidirectional 16-Bit I/O Expander
        self.i2c.write_byte_data(self.i2c_input_address, 0x00, 0xFF)  # set port A as input
        self.i2c.write_byte_data(self.i2c_input_address, 0x01, 0xFF)  # set port B as input
        self.i2c.write_byte_data(self.i2c_input_address, 0x0C, 0xFF)  # init pullup resistors for port A
        self.i2c.write_byte_data(self.i2c_input_address, 0x0D, 0xFF)  # init pullup resistors for port B
        self.i2c.write_byte_data(self.i2c_input_address, 0x04, 0xFF)  # set interrupt for port A
        self.i2c.write_byte_data(self.i2c_input_address, 0x05, 0xFF)  # set interrupt for port B
        self.i2c.write_byte_data(self.i2c_input_address, 0x0A, 0x40)  # connect interrupt A with B (MIRROR = 1)
        self.i2c.write_byte_data(self.i2c_input_address, 0x0B, 0x40)  # connect interrupt B with A (MIRROR = 1)
        # read ports to reset interrupt
        self.i2c.read_byte_data(self.i2c_input_address, 0x12) # read byte from port A
        self.i2c.read_byte_data(self.i2c_input_address, 0x13) # read byte from port B

        self.i2c_buttons = {}
        if self.config[GPIO][BUTTON_LEFT]: self.i2c_buttons[self.config[GPIO][BUTTON_LEFT]] = pygame.K_LEFT
        if self.config[GPIO][BUTTON_RIGHT]: self.i2c_buttons[self.config[GPIO][BUTTON_RIGHT]] = pygame.K_RIGHT
        if self.config[GPIO][BUTTON_UP]: self.i2c_buttons[self.config[GPIO][BUTTON_UP]] = pygame.K_UP
        if self.config[GPIO][BUTTON_DOWN]: self.i2c_buttons[self.config[GPIO][BUTTON_DOWN]] = pygame.K_DOWN
        if self.config[GPIO][BUTTON_SELECT]: self.i2c_buttons[self.config[GPIO][BUTTON_SELECT]] = pygame.K_RETURN
        if self.config[GPIO][BUTTON_VOLUME_UP]: self.i2c_buttons[self.config[GPIO][BUTTON_VOLUME_UP]] = pygame.K_KP_PLUS
        if self.config[GPIO][BUTTON_VOLUME_DOWN]: self.i2c_buttons[self.config[GPIO][BUTTON_VOLUME_DOWN]] = pygame.K_KP_MINUS
        if self.config[GPIO][BUTTON_MUTE]: self.i2c_buttons[self.config[GPIO][BUTTON_MUTE]] = pygame.K_x
        if self.config[GPIO][BUTTON_PLAY_PAUSE]: self.i2c_buttons[self.config[GPIO][BUTTON_PLAY_PAUSE]] = pygame.K_SPACE
        if self.config[GPIO][BUTTON_NEXT]: self.i2c_buttons[self.config[GPIO][BUTTON_NEXT]] = pygame.K_RIGHT
        if self.config[GPIO][BUTTON_PREVIOUS]: self.i2c_buttons[self.config[GPIO][BUTTON_PREVIOUS]] = pygame.K_LEFT
        if self.config[GPIO][BUTTON_HOME]: self.i2c_buttons[self.config[GPIO][BUTTON_HOME]] = pygame.K_HOME
        if self.config[GPIO][BUTTON_POWEROFF]: self.i2c_buttons[self.config[GPIO][BUTTON_POWEROFF]] = pygame.K_END

        self.bits = {
            0b1111111111111111: 0,
            0b1111111111111110: 1,
            0b1111111111111101: 2,
            0b1111111111111011: 3,
            0b1111111111110111: 4,
            0b1111111111101111: 5,
            0b1111111111011111: 6,
            0b1111111110111111: 7,
            0b1111111101111111: 8,
            0b1111111011111111: 9,
            0b1111110111111111: 10,
            0b1111101111111111: 11,
            0b1111011111111111: 12,
            0b1110111111111111: 13,
            0b1101111111111111: 14,
            0b1011111111111111: 15,
            0b0111111111111111: 16
        }
        self.key = None

    def handle_i2c_event(self, _):
        """ Handle I2C interrupt """

        d = {}
        a = self.i2c.read_byte_data(self.i2c_input_address, 0x12)
        b = self.i2c.read_byte_data(self.i2c_input_address, 0x13)

        if a == 255 and b == 255:
            d[KEY_ACTION] = pygame.KEYUP
        else:
            d[KEY_ACTION] = pygame.KEYDOWN
            data = a + (b << 8)
            try:
                bit = self.bits[data]
                self.key = self.i2c_buttons[str(bit)]
            except:
                pass
        
        if self.key != None:
            d[KEY_SUB_TYPE] = SUB_TYPE_KEYBOARD
            d[KEY_KEYBOARD_KEY] = self.key
            event = pygame.event.Event(USER_EVENT_TYPE, **d)
            pygame.event.post(event)
            if d[KEY_ACTION] == pygame.KEYUP:
                self.key = None
