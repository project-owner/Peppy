# Copyright 2018 Peppy Player peppy.player@gmail.com
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
import math
import time
import logging
import sys
import os

from ui.component import Component
from ui.container import Container
from random import randrange
from screensaver.screensaver import Screensaver, PLUGIN_CONFIGURATION
from util.config import SCREEN_INFO, WIDTH, HEIGHT
from threading import Thread
from util.util import PACKAGE_SCREENSAVER
from itertools import cycle

PIPE_POLLING_INTERVAL = "pipe.polling.interval"
MAX_VALUE = "max.value"
PIPE_NAME = "pipe.name"
SIZE = "size"
UPDATE_UI_INTERVAL = "update.ui.interval"
DEFAULT_IMAGES_FOLDER = "images"
AMPLIFIER = "amplifier"

class Spectrum(Container, Screensaver):
    """ Spectrum Analyzer screensaver plug-in. """
        
    def __init__(self, util):
        """ Initializer
        
        :param util: contains config object and utility functions
        """ 
        self.config = util.config
        self.bounding_box = util.screen_rect
        bgr = (0, 0, 0)
        Container.__init__(self, util, self.bounding_box, bgr)
        plugin_folder = type(self).__name__.lower() 
        Screensaver.__init__(self, plugin_folder)
        self.util = util        
        self.run_flag = False
        self.run_datasource = False
        
        self.pipe_name = self.plugin_config_file.get(PLUGIN_CONFIGURATION, PIPE_NAME)
        self.pipe_polling_interval = self.plugin_config_file.getfloat(PLUGIN_CONFIGURATION, PIPE_POLLING_INTERVAL)
        self.max_value = self.plugin_config_file.getint(PLUGIN_CONFIGURATION, MAX_VALUE)
        self.size = self.plugin_config_file.getint(PLUGIN_CONFIGURATION, SIZE)
        self.update_ui_interval = self.plugin_config_file.getfloat(PLUGIN_CONFIGURATION, UPDATE_UI_INTERVAL)
        self.amplifier = self.plugin_config_file.getfloat(PLUGIN_CONFIGURATION, AMPLIFIER)
        
        self.bar_heights = [0] * self.size
        self.pipe_size = 4 * self.size
        
        self.fifth = self.bounding_box.h / 5
        self.unit = (self.fifth * 2) / self.max_value
        self.bar_max_height = int(self.unit * self.max_value * self.amplifier)
        width = int(self.bounding_box.w - self.fifth * 2)
        self.bar_width = int(math.floor(width) / self.size) 
        
        base_line_1 = self.bounding_box.h - (self.fifth * 1.8)
        base_line_2 = self.bounding_box.h - (self.fifth * 3.0)
        base_line_3 = self.bounding_box.h - (self.fifth * 1.0)        
        self.base_line = [base_line_1, base_line_2, base_line_3] 

        self.indexes = cycle(range(3))
        self.pipe = None
        
        self.init_images()
        self.init_container()       

        if "win" in sys.platform:
            self.windows = True
            self.update_ui_interval = 0.1
        else:
            self.windows = False
            thread = Thread(target=self.open_pipe)
            thread.start()
    
    def init_container(self):
        """ Initialize container """
        
        c = Component(self.util)
        self.add_component(c)
        for r in range(self.size):
            c = Component(self.util)
            self.add_component(c)
            c = Component(self.util)
            self.add_component(c)        
    
    def init_images(self):
        """ Initialize lists of images """
        
        bgr_name = ["bgr-1.png", "bgr-2.png", "bgr-3.png"]
        bar_names = ["bar-1.png", "bar-2.png", "bar-3.png"]
        reflection_names = ["reflection-1.png", "reflection-2.png", "reflection-3.png"]
        
        self.bgr = self.load_images(bgr_name, (self.bounding_box.w, self.bounding_box.h))
        self.bar = self.load_images(bar_names, (self.bar_width - 1, self.bar_max_height))
        self.reflection = self.load_images(reflection_names, (self.bar_width - 1, self.bar_max_height))
    
    def load_images(self, names, bb):
        """ Load images specified by names
        
        :param names: image names
        :param bb: image bounding box
        """
        images = []
        plugin_folder = type(self).__name__.lower()
        
        for n in names:
            img = self.util.load_image(os.path.join(PACKAGE_SCREENSAVER, plugin_folder, DEFAULT_IMAGES_FOLDER, n))
            scaled_image = self.util.scale_image(img, bb)
            images.append(scaled_image)
            
        return images   
            
    def start(self):
        """ Start spectrum thread. """ 
        
        self.index = 0
        self.set_background()        
        self.set_bars()
        self.set_reflections()
        
        self.run_flag = True
        self.start_data_source()
        thread = Thread(target=self.update_ui)
        thread.start()
        pygame.event.clear()
    
    def set_background(self):
        """ Set background image """
        
        c = self.components[0]
        c.content = ("", self.bgr[self.index])

        w = self.config[SCREEN_INFO][WIDTH]
        h = self.config[SCREEN_INFO][HEIGHT]
        size = c.content[1].get_size()
        
        if size[0] < w:
            c.content_x = int((w - size[0])/2)
            c.content_y = int((h - size[1])/2)
    
    def set_bars(self):
        """ Set spectrum bars  """
        
        for r in range(self.size):
            c = self.components[r + 1]
            x = int(self.fifth + (r * self.bar_width) + self.bar_width)
            c.content_x = x
            c.content_y = self.base_line[self.index]
            w = self.bar_width - 1
            c.content = ("", self.bar[self.index])
            c.bounding_box = pygame.Rect(0, 0, w, 0)
            
    def set_reflections(self):
        """ Set reflection bars """
        
        for r in range(self.size):
            c = self.components[r + 1 + self.size]
            x = int(self.fifth + (r * self.bar_width) + self.bar_width)
            c.content_x = x
            c.content_y = self.base_line[self.index]
            w = self.bar_width - 1
            c.content = ("", self.reflection[self.index])
            c.bounding_box = pygame.Rect(0, 0, w, 0)
    
    def refresh(self):
        """ Update spectrum """
        
        self.index = next(self.indexes)
        self.set_background()        
        self.set_bars()
        self.set_reflections()
            
    def stop(self):
        """ Stop spectrum thread. """ 
        
        self.run_flag = False
        self.run_datasource = False
        if self.pipe:
            os.close(self.pipe)
            self.pipe = None
    
    def open_pipe(self):
        """ Open named pipe  """
        
        try:            
            self.pipe = os.open(self.pipe_name, os.O_RDONLY | os.O_NONBLOCK)
        except Exception as e:
            logging.debug("Cannot open named pipe: " + self.pipe_name)
            logging.debug(e)
            
    def start_data_source(self):
        """ Start data source thread. """ 
               
        self.run_datasource = True
        thread = Thread(target=self.get_data)
        thread.start()
        
    def get_data(self):
        """ Data Source Thread method. """ 
               
        while self.run_datasource:
            self.set_values()
            time.sleep(self.pipe_polling_interval)
    
    def set_values(self):
        """ Get signal from the named pile and update spectrum bars. """ 
               
        if self.windows:
            data = []
            mask = 0b11111111
            for r in range(self.size):
                v = int((randrange(0, int(self.max_value * 0.5))))
                data.append(v & mask);
                data.append((v >> 8) & mask);
                data.append((v >> 16) & mask);
                data.append((v >> 24) & mask);            
        else:
            try:
                if self.pipe == None:
                    self.open_pipe()
                    
                if self.pipe == None:
                    return
    			
                data = os.read(self.pipe, self.pipe_size)
            except Exception as e:
                logging.debug(e)
                return
            
        length = len(data)
        if length == 0:
            return
            
        words = int(length / 4);
            
        for m in range(words):
            v1 = data[4 * m] + (data[4 * m + 1] << 8) + (data[4 * m + 2] << 16) + (data[4 * m + 3] << 24)
            if m == 0 and words > 1:
                t = m + 1
                v2 = data[4 * t] + (data[4 * t + 1] << 8) + (data[4 * t + 2] << 16) + (data[4 * t + 3] << 24)
                v1 = (v1 + v2) / 2
            if m > 0 and m < (words - 2) and words > 2:
                t = m - 1
                v2 = data[4 * t] + (data[4 * t + 1] << 8) + (data[4 * t + 2] << 16) + (data[4 * t + 3] << 24)
                t = m + 1
                v3 = data[4 * t] + (data[4 * t + 1] << 8) + (data[4 * t + 2] << 16) + (data[4 * t + 3] << 24)
                v1 = (v1 + v2 + v3) / 3
            if m == (words - 1) and words > 1:
                t = m - 1
                v2 = data[4 * t] + (data[4 * t + 1] << 8) + (data[4 * t + 2] << 16) + (data[4 * t + 3] << 24)
                v1 = (v1 + v2) / 2
                
            h = int(v1 * self.unit * self.amplifier)            
            i = m + 1
            
            comp = self.components[i]
            comp.bounding_box.h = h
            comp.bounding_box.y = self.bar_max_height - h
            comp.content_y = int(self.base_line[self.index] - self.bar_max_height + comp.bounding_box.y)
            
            comp = self.components[i + self.size]
            comp.bounding_box.h = h
            comp.bounding_box.y = 0
            comp.content_y = int(self.base_line[self.index] + 2)
                
    def update_ui(self):
        """ Update UI Thread method. """ 
               
        while self.run_flag:
            self.clean_draw_update()            
            time.sleep(self.update_ui_interval)
