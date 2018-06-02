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

import pygame
from ui.component import Component
from random import randrange
from screensaver.screensaver import Screensaver, PLUGIN_CONFIGURATION
from util.config import SCREEN_RECT, SCREEN_INFO, WIDTH, HEIGHT

VERTICAL_SIZE_PERCENT = "vertical.size.percent"

class Logo(Component, Screensaver):
    """ Logo screensaver plug-in. 
       
    Depending on mode it works the following way
    Radio Mode: 
    After delay it displays the logo image of the current station.
    Audio Files Mode: 
    After delay it displays the current album art (if any).
    If there is no album art then the default CD image will be displayed.    
    The image periodically changes on-screen position. 
    The period in seconds is defined by the variable update_period. 
    """    
    def __init__(self, util):
        """ Initializer
        
        :param util: contains config object
        """ 
        self.config = util.config       
        Component.__init__(self, util)
        plugin_folder = type(self).__name__.lower() 
        Screensaver.__init__(self, plugin_folder)
        self.util = util
        self.bounding_box = self.config[SCREEN_RECT]        
        vertical_size_percent = self.plugin_config_file.getint(PLUGIN_CONFIGURATION, VERTICAL_SIZE_PERCENT)        
        self.logo_size = int((vertical_size_percent * self.bounding_box.h)/100)
        self.r = pygame.Rect(0, 0, self.logo_size, self.logo_size)
        
    def set_image(self, image):
        """ Image setter
        
        :param image: depending on mode either station logo or album art
        """ 
        img = None
        if isinstance(image, tuple):
            img = image[1]
        else:
            img = image
            
        if not img: return
        
        scale_ratio = self.util.get_scale_ratio((self.logo_size, self.logo_size), img)
        scaled_img = self.util.scale_image(img, scale_ratio)
        self.content = ("img", scaled_img)
        
    def refresh(self):
        """ Update image position on screen """
        
        w = self.config[SCREEN_INFO][WIDTH]
        h = self.config[SCREEN_INFO][HEIGHT]
        self.content_x = randrange(1, w - self.r.w)
        self.content_y = randrange(1, h - self.r.h)
        self.clean()
        super(Logo, self).draw()
        self.update()
