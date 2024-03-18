# Copyright 2016-2024 PeppyMeter peppy.player@gmail.com
# 
# This file is part of PeppyMeter.
# 
# PeppyMeter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# PeppyMeter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with PeppyMeter. If not, see <http://www.gnu.org/licenses/>.

import pygame
import os
import sys
import logging

from meterutil import MeterUtil
from pygame.time import Clock
from vumeter import Vumeter
from datasource import DataSource, SOURCE_NOISE, SOURCE_PIPE
from serialinterface import SerialInterface
from i2cinterface import I2CInterface
from pwminterface import PWMInterface
from httpinterface import HTTPInterface
from websocketinterface import WebsocketInterface
from screensavermeter import ScreensaverMeter
from configfileparser import *

class Peppymeter(ScreensaverMeter):
    """ Peppy Meter class """
    
    def __init__(self, util=None, standalone=False):
        """ Initializer
        
        :param util: utility object
        :param standalone: True - standalone version, False - part of Peppy player
        """
        ScreensaverMeter.__init__(self)
        if util:
            self.util = util
            meter_folder = str(util.screen_rect.w) + "x" + str(util.screen_rect.h)
        else:
            self.util = MeterUtil()
            meter_folder = None
            
        try:
            self.use_vu_meter = self.util.config[USAGE][USE_VU_METER]
        except:
            self.use_vu_meter = False

        self.name = "peppymeter"
        
        base_path = "."
        if __package__:
            pkg_parts = __package__.split(".")
            if len(pkg_parts) > 0:
                base_path = os.path.join(os.getcwd(), "screensaver", self.name)
        
        parser = ConfigFileParser(base_path, meter_folder)
        self.util.meter_config = parser.meter_config
        self.outputs = {}
        
        if standalone:
            if self.util.meter_config[USE_LOGGING]:
                log_handlers = []
                try:
                    log_handlers.append(logging.StreamHandler(sys.stdout))
                    log_handlers.append(logging.FileHandler(filename="peppymeter.log", mode='w'))
                    logging.basicConfig(
                        level=logging.NOTSET,
                        format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
                        handlers=log_handlers
                    )
                except:
                    pass
            else:
                logging.disable(logging.CRITICAL)
        
        # no VU Meter support for Windows
        if "win" in sys.platform and self.util.meter_config[DATA_SOURCE][TYPE] == SOURCE_PIPE:
            self.util.meter_config[DATA_SOURCE][TYPE] = SOURCE_NOISE
        
        self.data_source = DataSource(self.util)
        if self.use_vu_meter == True:
            self.data_source.start_data_source()
        
        if self.util.meter_config[OUTPUT_DISPLAY]:
            self.meter = self.output_display(self.data_source)
            
        if self.util.meter_config[OUTPUT_SERIAL]:
            self.outputs[OUTPUT_SERIAL] = SerialInterface(self.util.meter_config, self.data_source)
            
        if self.util.meter_config[OUTPUT_I2C]:
            self.outputs[OUTPUT_I2C] = I2CInterface(self.util.meter_config, self.data_source)
            
        if self.util.meter_config[OUTPUT_PWM]:
            self.outputs[OUTPUT_PWM] = PWMInterface(self.util.meter_config, self.data_source)

        if self.util.meter_config[OUTPUT_HTTP]:
            self.outputs[OUTPUT_HTTP] = HTTPInterface(self.util.meter_config, self.data_source)

        if self.util.meter_config[OUTPUT_WEBSOCKET]:
            self.outputs[OUTPUT_WEBSOCKET] = WebsocketInterface(self.util.meter_config, self.data_source)

        self.start_interface_outputs()
        w = self.util.meter_config[SCREEN_INFO][WIDTH] = util.config[SCREEN_INFO][WIDTH]
        h = self.util.meter_config[SCREEN_INFO][HEIGHT] = util.config[SCREEN_INFO][HEIGHT]
        self.util.meter_config[SCREEN_RECT] = pygame.Rect(0, 0, w, h)
        self.clock = Clock()
        self.random_meter_interval = self.util.meter_config[RANDOM_METER_INTERVAL]
    
    def set_web(self, send_json):
        try:
            self.outputs[OUTPUT_WEBSOCKET].send_json = send_json    
        except:
            pass

    def output_display(self, data_source):
        """ Initialize display
        
        :data_source: data source
        :return: graphical VU Meter
        """
        meter = Vumeter(self.util, data_source)         
        self.current_image = None
        self.update_period = meter.get_update_period()
        
        return meter
    
    def init_display(self):
        """ Initialize display """

        screen_w = self.util.meter_config[SCREEN_INFO][WIDTH]
        screen_h = self.util.meter_config[SCREEN_INFO][HEIGHT]
        depth = self.util.meter_config[SCREEN_INFO][DEPTH]
        
        os.environ["SDL_FBDEV"] = "/dev/fb1"
        os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"
        os.environ["SDL_MOUSEDRV"] = "TSLIB"
        
        if "win" not in sys.platform:
            pygame.display.init()
            pygame.mouse.set_visible(False)
        else:            
            pygame.init()
            pygame.display.set_caption("Peppy Meter")
            
        self.util.pygame_screen = pygame.display.set_mode((screen_w, screen_h), pygame.DOUBLEBUF, depth)
    
    def start_interface_outputs(self):
        """ Start writing to interfaces """
        
        for v in self.outputs.values():
            v.start_writing()

    def start(self):
        """ Start VU meter. This method called by Peppy Meter to start meter """
        
        pygame.event.clear()
        if not (self.util.meter_config[DATA_SOURCE][TYPE] == SOURCE_PIPE and self.use_vu_meter == True):
            self.data_source.start_data_source()
        self.meter.start()
        pygame.display.update(self.util.meter_config[SCREEN_RECT])

        for v in self.outputs.values():
            v.start_writing()

    def stop(self):
        """ Stop meter animation. """ 

        if not self.use_vu_meter:
            for v in self.outputs.values():
                v.stop_writing()

            self.data_source.stop_data_source()

        self.meter.stop()

    def update(self):
        """ Update screensaver """

        return self.meter.run()

    def refresh(self, init=False):
        """ Refresh meter. Used to switch from one random meter to another. 
        
        :param init: initial call
        """
        return self.meter.refresh()
    
    def set_volume(self, volume):
        """ Set volume level.
        
        :param volume: new volume level
        """
        self.data_source.volume = volume
    
    def exit(self):
        """ Exit program """
        
        for v in self.outputs.values():
            v.stop_writing()

        pygame.quit()            
        os._exit(0)

    def set_visible(self, flag):
        """ Set visible/invisible flag.
        
        :param flag: True - visible, False - invisible
        """
        pass
