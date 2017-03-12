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

import os

from ui.component import Component
from itertools import cycle
from screensaver.screensaver import Screensaver
from util.config import SCREEN_RECT, SCREEN_INFO, WIDTH, HEIGHT

class Slideshow(Component, Screensaver):
    """ Slideshow screensaver plug-in.
    Depending on mode it works the following way
    Radio Mode:
    After delay it displays the image from the 'slides' folder. 
    Audio Files Mode: 
    After delay it displays the images from the album art folder (if any). 
    If there is no album art folder then images from the 'slides' folder will be displayed.
    The images will be displayed in cycle. 
    The delay period between images is defined by the variable update_period 
    """    
    def __init__(self, util):
        """ Initializer
        
        :param util: contains configuration object
        """ 
        Component.__init__(self, util)
        self.util = util
        self.config = util.config
        self.bounding_box = self.config[SCREEN_RECT]
        self.default_folder = os.path.join("screensaver", "slideshow", "slides")
        self.current_folder = self.default_folder
        self.update_period = 6
        self.slides = []
    
    def change_folder(self, folder):
        """ Changes folder and prepares slides 
        
        :param state: state object defining image folder 
        """
        self.current_folder = folder
        self.slides = self.util.load_screensaver_images(folder)
        self.w = self.config[SCREEN_INFO][WIDTH]
        self.h = self.config[SCREEN_INFO][HEIGHT]
        l = []
        for slide in self.slides:
            width = slide[1].get_size()[0]
            height = slide[1].get_size()[1]
            
            if width == self.w and height == self.h:
                l.append(slide)
            else:
                scale_ratio = self.util.get_scale_ratio((self.w, self.h), slide[1])
                img = self.util.scale_image(slide[1], scale_ratio)
                t = (slide[0], img)
                l.append(t)
        self.slides = l
        self.indexes = cycle(range(len(self.slides)))
        
    def refresh(self):
        """ Update image on screen """
        
        if not self.slides:
            self.change_folder(self.current_folder)
          
        i = next(self.indexes)
        slide = self.slides[i]
        self.content = (slide[0], slide[1])
        self.image_filename = slide[0]
        size = self.content[1].get_size()
        if size[0] != self.w or size[1] != self.h:
            self.content_x = int((self.w - size[0])/2)
            self.content_y = int((self.h - size[1])/2)
        else:
            self.content_x = 0
            self.content_y = 0
        self.clean()
        super(Slideshow, self).draw()
        self.update()
        
    def set_image_folder(self, state):
        """ Image folder setter 
        
        :param state: state object defining image folder 
        """
        folder = getattr(state, "cover_art_folder", None)
        if not folder:
            folder = self.default_folder
        self.current_folder = folder
        self.slides = []
