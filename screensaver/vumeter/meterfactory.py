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

from screensaver.vumeter.meter import Meter
from screensaver.vumeter.maskfactory import MaskFactory
from screensaver.vumeter.needlefactory import NeedleFactory
from screensaver.vumeter.configfileparser import *

class MeterFactory(object):
    """ Meter creation factory """
    
    def __init__(self, util, meter_config, data_source):
        """ Initializer
        
        :param util: utility class
        :param meter_config: configuration dictionary
        :param data_source: the source of audio data
        """
        self.util = util
        self.meter_config = meter_config
        self.data_source = data_source
        
    def create_meter(self):
        """ Dispatcher method """ 
               
        meter_name = self.meter_config[METER]
        meter_config_section = self.meter_config[meter_name]
        if meter_config_section[METER_TYPE] == TYPE_LINEAR:
            return self.create_linear_meter(meter_name)
        elif meter_config_section[METER_TYPE] == TYPE_CIRCULAR:
            return self.create_circular_meter(meter_name)
        
    def create_linear_meter(self, name):
        """ Create linear method
        
        :param name: meter name
        """
        config = self.meter_config[name]
        
        if config[CHANNELS] == 2:
            left_channel_queue = self.data_source.left_channel
            right_channel_queue = self.data_source.right_channel
            meter = Meter(self.util, TYPE_LINEAR, self.meter_config[IMAGE_FOLDER_NAME], config[UI_REFRESH_PERIOD], left_channel_queue, right_channel_queue)
            meter.channels = 2
            meter.left_x = config[LEFT_X]
            meter.left_y = config[LEFT_Y]
            meter.right_x = config[RIGHT_X]
            meter.right_y = config[RIGHT_Y]            
        else:
            mono_channel_queue = self.data_source.mono_channel
            meter = Meter(self.util, TYPE_LINEAR, self.meter_config[IMAGE_FOLDER_NAME], config[UI_REFRESH_PERIOD], mono_channel_queue)
            meter.x = config[MONO_X]
            meter.y = config[MONO_Y]
        
        meter.positions_regular = config[POSITION_REGULAR]
        meter.step_width_regular = config[STEP_WIDTH_REGULAR]
        if POSITION_OVERLOAD in config:
            meter.positions_overload = config[POSITION_OVERLOAD]
            meter.step_width_overload = config[STEP_WIDTH_OVERLOAD]
        else:
            meter.positions_overload = 0
            meter.step_width_overload = 0
        meter.total_steps = meter.positions_regular + meter.positions_overload + 1
        meter.step = 100/meter.total_steps
        
        meter.add_background(config[BGR_FILENAME])
        
        if config[CHANNELS] == 2:
            meter.add_channel(config[INDICATOR_FILENAME], meter.left_x, meter.left_y)
            meter.add_channel(config[INDICATOR_FILENAME], meter.right_x, meter.right_y)
        else:
            meter.add_channel(config[INDICATOR_FILENAME], meter.x, meter.y)
        
        meter.add_foreground(config[FGR_FILENAME])
        
        factory = MaskFactory()
        meter.masks = factory.create_masks(meter.positions_regular, meter.positions_overload, meter.step_width_regular, meter.step_width_overload)
        
        return meter

    def create_circular_meter(self, name):
        """ Create circular meter
        
        :param name: meter name
        """
        config = self.meter_config[name]
        
        if config[CHANNELS] == 2:
            left_channel_queue = self.data_source.left_channel
            right_channel_queue = self.data_source.right_channel
            meter = Meter(self.util, TYPE_CIRCULAR, self.meter_config[IMAGE_FOLDER_NAME], config[UI_REFRESH_PERIOD], left_channel_queue, right_channel_queue)
            meter.channels = 2
        else:
            mono_channel_queue = self.data_source.mono_channel
            meter = Meter(self.util, TYPE_CIRCULAR, self.meter_config[IMAGE_FOLDER_NAME], config[UI_REFRESH_PERIOD], mono_channel_queue=mono_channel_queue)

        meter.steps_per_degree = config[STEPS_PER_DEGREE]                 
        start_angle = config[START_ANGLE]
        stop_angle = config[STOP_ANGLE]
        meter.incr = (abs(start_angle) + abs(stop_angle)) / 100
        meter.add_background(config[BGR_FILENAME])
        needle = meter.load_image(config[INDICATOR_FILENAME])[1]
        
        factory = NeedleFactory(needle, config, meter.origin_x, meter.origin_y)
        meter.needle_sprites = factory.needle_sprites
        
        if config[CHANNELS] == 2:
            meter.left_needle_rects = factory.left_needle_rects
            meter.right_needle_rects = factory.right_needle_rects
            meter.left_needle_rects = factory.left_needle_rects     
            s = meter.needle_sprites[0]
            r = meter.left_needle_rects[0]
            meter.add_image(s, 0, 0, r)
            r = meter.right_needle_rects[0]
            meter.add_image(s, 0, 0, r)
        else:
            meter.mono_needle_rects = factory.mono_needle_rects     
            s = meter.needle_sprites[0]
            r = meter.mono_needle_rects[0]
            meter.add_image(s, 0, 0, r)
        
        if config[FGR_FILENAME]:
            meter.add_foreground(config[FGR_FILENAME])
        
        return meter      
        
        