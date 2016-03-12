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

from ui.component import Component
import time
import pygame
from random import randrange
from screensaver.screensaver import Screensaver
from util.keys import COLORS, SCREEN_RECT, SCREEN_INFO, WIDTH, HEIGHT, COLOR_CONTRAST

class Clock(Component, Screensaver):
    """ Clock screensaver plug-in. 
    After delay it displays the digital clock in format HH:MM.
    The clock periodically changes on-screen position. 
    The period is defined by the variable update_period 
    """
    
    def __init__(self, util):
        """ Initializer
        
        :param util: contains config object
        """
        self.config = util.config
        Component.__init__(self, util, bgr=(0, 0, 0))
        self.bounding_box = self.config[SCREEN_RECT]
        self.TIME_FORMAT = "%I:%M"
        font_size = int((60 * self.bounding_box.h)/320)
        self.f = util.get_font(font_size)
        self.update_period = 4
    
    def refresh(self):
        """ Draw digital clock on screen """
        current_time = time.strftime(self.TIME_FORMAT) 
        clock_size = self.f.size(current_time)
        r = pygame.Rect(0, 0, clock_size[0], clock_size[1])
        self.content = self.f.render(current_time, 1, self.config[COLORS][COLOR_CONTRAST])
        w = self.config[SCREEN_INFO][WIDTH]
        h = self.config[SCREEN_INFO][HEIGHT]
        self.content_x = randrange(1, w - r.w)
        self.content_y = randrange(1, h - r.h)
        self.clean()
        super(Clock, self).draw()
        self.update()
