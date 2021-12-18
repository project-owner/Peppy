# Copyright 2016-2021 Peppy Player peppy.player@gmail.com
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
from ui.container import Container
from itertools import cycle
from screensaver.screensaver import Screensaver, PLUGIN_CONFIGURATION
from util.config import SCREEN_INFO, WIDTH, HEIGHT, SLIDESHOW
from util.util import PACKAGE_SCREENSAVER
from random import shuffle

DEFAULT_SLIDES_FOLDER = "slides"
CONFIG_SLIDES_FOLDER = "slides.folder"
RANDOM_ORDER = "random"
USE_CACHE = "use.cache"

class Slideshow(Container, Screensaver):
    """ Slideshow screensaver plug-in.
    Depending on mode it works the following way
    Radio Mode:
    After delay it displays the images from the 'slides' folder. 
    Audio Files Mode: 
    After delay it displays the images from the album art folder (if any). 
    If there is no album art folder then images from the 'slides' folder will be displayed.
    The images will be displayed in cycle. 
    The period in seconds can be defined in the configuration file.
    """    
    def __init__(self, util):
        """ Initializer
        
        :param util: contains configuration object
        """ 
        self.name = SLIDESHOW
        plugin_folder = type(self).__name__.lower() 
        Screensaver.__init__(self, self.name, util, plugin_folder)
        Container.__init__(self, util, bounding_box=util.screen_rect, background=self.bg[1], content=self.bg[2], image_filename=self.bg[3])
        
        self.util = util
        self.config = util.config
        self.image_util = util.image_util
        self.bounding_box = util.screen_rect
        self.default_folder = os.path.join(PACKAGE_SCREENSAVER, plugin_folder, DEFAULT_SLIDES_FOLDER)
        self.w = self.config[SCREEN_INFO][WIDTH]
        self.h = self.config[SCREEN_INFO][HEIGHT]
        self.use_cache = self.plugin_config_file.getboolean(PLUGIN_CONFIGURATION, USE_CACHE)
        
        config_slides_folder = self.plugin_config_file.get(PLUGIN_CONFIGURATION, CONFIG_SLIDES_FOLDER)
        if config_slides_folder and os.path.exists(config_slides_folder):
             self.current_folder = config_slides_folder
        else:            
            self.current_folder = self.default_folder

        self.slides = []
        self.image_names = []
        self.random = self.plugin_config_file.getboolean(PLUGIN_CONFIGURATION, RANDOM_ORDER)
        self.component = Component(util)
        self.component.name = self.name
        self.add_component(self.component)
    
    def change_folder(self, folder):
        """ Changes folder and loads slides 
        
        :param folder: images folder 
        """
        self.current_folder = folder
        
        if self.use_cache:
            self.slides = self.image_util.load_scaled_images(folder)
            self.slide_index = cycle(range(len(self.slides)))
        else:
            self.image_names = self.image_util.get_image_names_from_folder(folder)
            self.image_index = cycle(range(len(self.image_names)))

        if self.random:
            shuffle(self.image_names)
            shuffle(self.slides)
        else:
            self.slides.sort()
            self.image_names.sort()

    def refresh(self):
        """ Update image on screen """
        
        if self.use_cache:
            if not self.slides:
                self.change_folder(self.current_folder)
            if not self.slides:
                return
            i = next(self.slide_index)
            slide = self.slides[i]
        else:
            if not self.image_names:
                self.change_folder(self.current_folder)
            if not self.image_names:
                return   
            i = next(self.image_index)
            path = self.image_names[i]
            slide = self.image_util.load_scaled_image(path)

        self.component.content = (slide[0], slide[1])
        self.component.image_filename = slide[0]
        size = self.component.content[1].get_size()
        if size[0] != self.w or size[1] != self.h:
            self.component.content_x = int((self.w - size[0])/2)
            self.component.content_y = int((self.h - size[1])/2)
        else:
            self.component.content_x = 0
            self.component.content_y = 0
        
        self.clean_draw_update()
        
    def set_image_folder(self, state):
        """ Image folder setter 
        
        :param state: state object defining image folder 
        """
        folder = getattr(state, "cover_art_folder", None)
        if not folder:
            folder = self.default_folder
        self.current_folder = folder
        self.slides = []
        self.image_names = []
        self.change_folder(folder)
