# Copyright 2016-2018 Peppy Player peppy.player@gmail.com
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

from ui.component import Component
import time
import pygame
from random import randrange
from screensaver.screensaver import Screensaver, PLUGIN_CONFIGURATION
from util.keys import SCREEN_RECT
from util.config import SCREEN_INFO, WIDTH, HEIGHT, COLORS, COLOR_CONTRAST

MILITARY_TIME_FORMAT = "military.time.format"
ANIMATED = "animated"

class Clock(Component, Screensaver):
    """ Clock screensaver plug-in. 
    After delay it displays the digital clock in format HH:MM.
    The clock periodically changes on-screen position. 
    The period in seconds can be defined in the configuration file. 
    """
    def __init__(self, util):
        """ Initializer
        
        :param util: contains configuration object
        """        
        self.config = util.config
        Component.__init__(self, util, bgr=(0, 0, 0))
        plugin_folder = type(self).__name__.lower() 
        Screensaver.__init__(self, plugin_folder)
        self.bounding_box = self.config[SCREEN_RECT]
        
        military_time_format = self.plugin_config_file.getboolean(PLUGIN_CONFIGURATION, MILITARY_TIME_FORMAT)
        if military_time_format:
            self.TIME_FORMAT = "%H:%M"
        else:
            self.TIME_FORMAT = "%I:%M"
        
        self.animated = self.plugin_config_file.getboolean(PLUGIN_CONFIGURATION, ANIMATED)
        if self.animated:
            font_vertical_percent = 20
        else:
            font_vertical_percent = 50
        
        font_size = int((font_vertical_percent * self.bounding_box.h)/100)    
        self.f = util.get_font(font_size)
    
    def refresh(self):
        """ Draw digital clock on screen """
        
        current_time = time.strftime(self.TIME_FORMAT) 
        clock_size = self.f.size(current_time)
        r = pygame.Rect(0, 0, clock_size[0], clock_size[1])
        img = self.f.render(current_time, 1, self.config[COLORS][COLOR_CONTRAST])
        self.content = ("img", img)
        w = self.config[SCREEN_INFO][WIDTH]
        h = self.config[SCREEN_INFO][HEIGHT]
        
        if self.animated:
            self.content_x = randrange(1, w - r.w)
            self.content_y = randrange(1, h - r.h)
        else:
            if r.w > w:
                self.content_x = 0
                self.content_y = 0
            else:                
                self.content_x = (w - r.w)/2
                self.content_y = (h - r.h)/2
            
        self.clean()
        super(Clock, self).draw()
        self.update()
