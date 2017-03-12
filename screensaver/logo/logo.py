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

import pygame
from ui.component import Component
from random import randrange
from screensaver.screensaver import Screensaver
from util.config import SCREEN_RECT, SCREEN_INFO, WIDTH, HEIGHT

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
        self.bounding_box = self.config[SCREEN_RECT]
        self.logo_size = int((100 * self.bounding_box.h)/320)
        self.r = pygame.Rect(0, 0, self.logo_size, self.logo_size)
        self.update_period = 4
        
    def set_image(self, image):
        """ Image setter
        
        :param image: depending on mode either station logo or album art
        """ 
        a = pygame.Surface((self.logo_size, self.logo_size), flags=pygame.SRCALPHA)
        img = None
        if isinstance(image, tuple):
            img = image[1]
        else:
            img = image
            
        if not img: return
        
        scaled_img = pygame.transform.smoothscale(img, (self.logo_size, self.logo_size), a)
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
