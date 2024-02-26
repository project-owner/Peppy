# Copyright 2016-2020 Peppy Player peppy.player@gmail.com
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
from ui.container import Container
from random import randrange
from screensaver.screensaver import Screensaver, PLUGIN_CONFIGURATION
from util.config import SCREEN_INFO, WIDTH, HEIGHT, LOGO, GENERATED_IMAGE

VERTICAL_SIZE_PERCENT = "vertical.size.percent"

class Logo(Container, Screensaver):
    """ Logo screensaver plug-in. 
       
    Depending on mode it works the following way
    Radio Mode: 
    After delay it displays the logo image of the current station.
    Audio Files Mode: 
    After delay it displays the current album art (if any).
    If there is no album art then the default CD image will be displayed.    
    The image periodically changes on-screen position. 
    The period in seconds can be defined in the configuration file.
    """    
    def __init__(self, util):
        """ Initializer
        
        :param util: contains config object
        """
        self.name = LOGO
        plugin_folder = type(self).__name__.lower() 
        Screensaver.__init__(self, self.name, util, plugin_folder)
        Container.__init__(self, util, bounding_box=util.screen_rect, background=self.bg[1], content=self.bg[2], image_filename=self.bg[3])

        self.config = util.config
        self.image_util = util.image_util       
        self.util = util
        vertical_size_percent = self.plugin_config_file.getint(PLUGIN_CONFIGURATION, VERTICAL_SIZE_PERCENT)        
        self.logo_size = int((vertical_size_percent * self.bounding_box.h)/100)
        self.r = pygame.Rect(0, 0, self.logo_size, self.logo_size)

        self.component = Component(util)
        self.component.name = GENERATED_IMAGE + self.name
        self.component.image_filename = self.component.name
        self.add_component(self.component)
        
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
        
        scale_ratio = self.image_util.get_scale_ratio((self.logo_size, self.logo_size), img)
        scaled_img = self.image_util.scale_image(img, scale_ratio)

        self.component.content = (self.component.name, scaled_img)

    def update(self, area=None):
        """  Update screensaver """

        pass

    def refresh(self, init=False):
        """ Update image position on screen 

        :param init: initial call
        """        
        w = self.config[SCREEN_INFO][WIDTH]
        h = self.config[SCREEN_INFO][HEIGHT]
        
        dw = w - self.r.w
        if dw <= 0:
            self.component.content_x = 0
        else:
            self.component.content_x = randrange(1, dw)
        
        dh = h - self.r.h
        if dh <= 0:
            self.component.content_y = 0
        else:
            self.component.content_y = randrange(1, dh)
        
        self.clean()
        self.draw()

        if init:
            Component.update(self, self.bounding_box)

        return self.bounding_box
