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

import logging
import time

from util.keys import KEY_POWER_ON, BIT_ADDRESS, KEY_SWITCH

I2C_ADDRESS = 0x20
DELAY_AFTER_SWITCHING = 5

class SwitchUtil(object):
    """ Disk Switch utility class """
    
    def __init__(self, util):
        """ Initializer
        
        :param util: utility object
        """
        self.util = util

        #I2C init
        try:
            from smbus import SMBus
            self.i2c = SMBus(1)
            # Initialize MCP23017 module
            self.i2c.write_byte_data(I2C_ADDRESS, 0x00, 0x00) # set port A as output
            self.i2c.write_byte_data(I2C_ADDRESS, 0x01, 0x00) # set port B as output
            self.i2c.write_byte_data(I2C_ADDRESS, 0x0C, 0xFF) # set all internal pullup resistors for port A
            self.i2c.write_byte_data(I2C_ADDRESS, 0x0D, 0xFF) # set all internal pullup resistors for port B
            self.i2c.write_byte_data(I2C_ADDRESS, 0x12, 0) # switch all off
        except:
            logging.error("SMBus error")
            return

    def switch_power(self):
        """ Switch disk power supply """

        try:
            self.util.config[KEY_SWITCH]
        except Exception as e:
            logging.debug(e)
            return

        bits = 0
        
        for disk in self.util.config[KEY_SWITCH]:
            if not disk: continue
            if disk[KEY_POWER_ON]:
                bits = bits | disk[BIT_ADDRESS]
        
        try:
            self.i2c.write_byte_data(I2C_ADDRESS, 0x12, bits)  # output bits to port A
            time.sleep(DELAY_AFTER_SWITCHING)
        except:
            pass
