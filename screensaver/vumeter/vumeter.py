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

from random import randrange
import time
import copy

from util.keys import LINUX_PLATFORM
from screensaver.vumeter.datasource import DataSource
from screensaver.vumeter.meterfactory import MeterFactory
from screensaver.screensaver import Screensaver
from screensaver.vumeter.configfileparser import ConfigFileParser
from screensaver.vumeter.configfileparser import METER, METER_NAMES, RANDOM_METER_INTERVAL, DATA_SOURCE, TYPE
from screensaver.vumeter.datasource import SOURCE_NOISE
from util.config import AUDIO, SERVER_COMMAND

class Vumeter(Screensaver):
    """ VU Meter plug-in. """
    
    def __init__(self, util):
        """ Initializer
        
        :param util: utility class
        """
        self.util = util
        self.update_period = 1
        self.meter = None
        self.USE_VOLUME = False
        
        parser = ConfigFileParser(util)
        self.meter_config = parser.meter_config
        self.meter_names = self.meter_config[METER_NAMES]
        self.random_meter_interval = self.meter_config[RANDOM_METER_INTERVAL]
        
        # no VU Meter support for Windows and mplayer at the moment
        if not util.config[LINUX_PLATFORM] or "mplayer" in util.config[AUDIO][SERVER_COMMAND]:
            self.meter_config[DATA_SOURCE][TYPE] = SOURCE_NOISE
        
        self.data_source = DataSource(self.meter_config)
        self.random_meter = False
        
        if self.meter_config[METER] == "random":
            self.random_meter = True
            self.random_meter_names = copy.copy(self.meter_names)            
            
        self.meter = None
        self.current_volume = 100.0
        self.seconds = 0
    
    def get_meter(self):
        """ Creates meter using meter factory. """
               
        if self.meter and not self.random_meter:
            return self.meter
        
        if self.random_meter:
            if len(self.random_meter_names) == 0:
                self.random_meter_names = copy.copy(self.meter_names)
            i = randrange(0, len(self.random_meter_names))     
            self.meter_config[METER] = self.random_meter_names[i]
            del self.random_meter_names[i]
            
        factory = MeterFactory(self.util, self.meter_config, self.data_source)
        return factory.create_meter()        
    
    def set_volume(self, volume):
        """ Set volume level 
        
        :param volume: new volume level
        """
        if self.USE_VOLUME:
            self.current_volume = volume        
    
    def start(self):
        """ Start data source and meter animation. """
                
        self.data_source.start_data_source()
        self.meter = self.get_meter()
        self.meter.set_volume(self.current_volume)
        self.meter.start()
    
    def stop(self):
        """ Stop data source and meter animation. """ 
               
        self.data_source.stop_data_source()
        self.meter.stop()
    
    def refresh(self):
        """ Refresh meter. Used to update random meter. """ 
               
        if self.random_meter and self.seconds == self.random_meter_interval:
            self.seconds = 0
            self.stop()
            time.sleep(0.2) # let threads stop
            self.start()
        self.seconds += 1
        pass
