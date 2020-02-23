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

import time
import pygame


from random import randrange
from ui.component import Component
from ui.container import Container
from screensaver.screensaver import Screensaver, PLUGIN_CONFIGURATION
from util.config import SCREEN_INFO, WIDTH, HEIGHT, COLORS, COLOR_CONTRAST, CLOCK, GENERATED_IMAGE

MILITARY_TIME_FORMAT = "military.time.format"
ANIMATED = "animated"

class Clock(Container, Screensaver):
    """ Clock screensaver plug-in. 
    After delay it displays the digital clock in format HH:MM.
    The clock periodically changes on-screen position. 
    The period in seconds can be defined in the configuration file. 
    """
    def __init__(self, util):
        """ Initializer
        
        :param util: contains configuration object
        """
        Container.__init__(self, util, util.screen_rect, (0, 0, 0))
        self.config = util.config
        plugin_folder = type(self).__name__.lower() 
        Screensaver.__init__(self, plugin_folder)
        self.bounding_box = util.screen_rect
        self.name = CLOCK
        
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

        self.component = Component(util)
        self.component.name = GENERATED_IMAGE + self.name
        self.component.image_filename = self.component.name
        self.add_component(self.component)
    
    def refresh(self):
        """ Draw digital clock on screen """
        
        current_time = time.strftime(self.TIME_FORMAT) 
        clock_size = self.f.size(current_time)
        r = pygame.Rect(0, 0, clock_size[0], clock_size[1])

        img = self.f.render(current_time, 1, self.config[COLORS][COLOR_CONTRAST])
        self.component.content = (self.component.name, img)
        w = self.config[SCREEN_INFO][WIDTH]
        h = self.config[SCREEN_INFO][HEIGHT]
        
        if self.animated:
            self.component.content_x = randrange(1, w - r.w)
            self.component.content_y = randrange(1, h - r.h)
        else:
            if r.w > w:
                self.component.content_x = 0
                self.component.content_y = 0
            else:                
                self.component.content_x = (w - r.w)/2
                self.component.content_y = (h - r.h)/2

        self.clean_draw_update()
