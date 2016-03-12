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

import pygame
from ui.component import Component
from random import randrange
from screensaver.screensaver import Screensaver
from util.config import SCREEN_RECT, SCREEN_INFO, WIDTH, HEIGHT

class Logo(Component, Screensaver):
    """ Logo screensaver plug-in. 
    After delay it displays the logo image of the current station.
    The logo periodically changes on-screen position. 
    The period is defined by the variable update_period 
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
        
    def set_image(self, logo):
        """ Set new station logo image
        
        :param logo: new station logo image
        """
        a = pygame.Surface((self.logo_size, self.logo_size), flags=pygame.SRCALPHA)
        self.content = pygame.transform.smoothscale(logo[1], (self.logo_size, self.logo_size), a)
        
    def refresh(self):
        """ Draw station logo image on screen """
        w = self.config[SCREEN_INFO][WIDTH]
        h = self.config[SCREEN_INFO][HEIGHT]
        self.content_x = randrange(1, w - self.r.w)
        self.content_y = randrange(1, h - self.r.h)
        self.clean()
        super(Logo, self).draw()
        self.update()
