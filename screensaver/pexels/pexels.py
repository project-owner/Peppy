# Copyright 2022 Peppy Player peppy.player@gmail.com
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

import requests
import logging
import datetime

from ui.component import Component
from ui.container import Container
from itertools import cycle
from screensaver.screensaver import Screensaver, PLUGIN_CONFIGURATION
from util.config import PEXELS, SCREEN_INFO, WIDTH, HEIGHT, GENERATED_IMAGE
from random import shuffle, randrange

PAGE_SIZE = "page.size"
TOPICS = "topics"
DELAY_MINUTES = 10
PEXELS_URL = "https://api.pexels.com/v1/search"
PEXELS_LABEL = "Photos provided by Pexels"
DEFAULT_TOPICS = "nature, animals, forest, city"
LABEL_COLOR = (220, 220, 220)

class Pexels(Container, Screensaver):
    """ Pexels screensaver plug-in """

    def __init__(self, util):
        """ Initializer
        
        :param util: contains configuration object
        """ 
        self.name = PEXELS
        plugin_folder = type(self).__name__.lower() 
        Screensaver.__init__(self, self.name, util, plugin_folder)
        Container.__init__(self, util, bounding_box=util.screen_rect, background=self.bg[1], content=self.bg[2], image_filename=self.bg[3])
        
        self.util = util
        self.config = util.config
        self.image_util = util.image_util
        self.bounding_box = util.screen_rect
        self.w = self.config[SCREEN_INFO][WIDTH]
        self.h = self.config[SCREEN_INFO][HEIGHT]
        
        self.slides = []
        self.avg_colors = []
        self.page_size = self.plugin_config_file.getint(PLUGIN_CONFIGURATION, PAGE_SIZE)
        self.topics = self.plugin_config_file.get(PLUGIN_CONFIGURATION, TOPICS)

        if len(self.topics) == 0:
            self.topics = DEFAULT_TOPICS
        
        self.topics = [s.strip() for s in self.topics.split(',')]

        self.component = Component(util)
        self.component.name = self.name
        self.add_component(self.component)

        if self.h <= 320:
            self.image_size = "medium"
        else:
            self.image_size = "large"

        self.auth_header = {"Authorization": self.util.k4}
        self.last_loaded = None
        self.images = {}
        self.page = randrange(1, 20)

    def start(self):
        """ Start screensaver """

        now = datetime.datetime.now()

        if self.last_loaded != None:
            if int((now - self.last_loaded).total_seconds()/60) < DELAY_MINUTES:
                return

        self.query_pexels()        
        self.slide_index = cycle(range(self.page_size))
        shuffle(self.slides)
        self.last_loaded = now

    def query_pexels(self):
        """ Get list of photo info from the Pexels web site """

        self.topic_index = randrange(0, len(self.topics))
        parameters = {
            "query": self.topics[self.topic_index],
            "page": self.page,
            "per_page": self.page_size,
            "size": self.image_size,
            "orientation": "landscape" 
        }

        content = None
        try:
            content = requests.get(PEXELS_URL, headers=self.auth_header, params=parameters, timeout=(2, 2))
        except Exception as e:
            logging.debug(e)

        if content == None:
            return None

        j = content.json()
        photos = j["photos"]
        if photos == None or len(photos) == 0:
            return
        pages = int(j["total_results"]/self.page_size)
        self.page = randrange(1, pages)
        self.images = {}
        self.slides = []
        self.avg_colors = []
        self.photographers = []
        for photo in photos:
            self.photographers.append(photo["photographer"])
            url = photo["src"][self.image_size]
            self.slides.append(url)
            hex_color = photo["avg_color"].lstrip("#")
            dec_color = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
            self.avg_colors.append(dec_color)

    def load_image(self, url):
        """ Load image from the Pexels web site
        
        :param url: URL of the image

        :return: tuple with image URL and Surface
        """
        img = self.image_util.load_image_from_url(url)

        if img == None:
            return None

        scale_ratio = self.image_util.get_scale_ratio((self.w, self.h), img[1], fit_all=False)
        im = self.image_util.scale_image(img, scale_ratio)
        return (url, im)

    def refresh(self):
        """ Update image on screen """
        
        if not self.slides:
            self.clean_draw_update()
            return

        i = next(self.slide_index)
        slide = None

        try:
            slide = self.images[self.slides[i]]   
        except:
            slide = self.load_image(self.slides[i])
            if slide != None:
                self.images[self.slides[i]] = slide

        if slide == None:
            self.clean_draw_update()
            return

        component = Component(self.util)
        component.name = GENERATED_IMAGE + PEXELS
        component.content = (component.name, slide[1])
        component.image_filename = slide[0]
        size = component.content[1].get_size()

        if size[0] != self.w or size[1] != self.h:
            component.content_x = int((self.w - size[0])/2)
            component.content_y = int((self.h - size[1])/2)
        else:
            component.content_x = 0
            component.content_y = 0
        
        font = self.util.get_font(12)
        d_x = (size[0] - self.w)/2

        label_size = font.size(PEXELS_LABEL)
        y = size[1] - label_size[1] + 2
        pexels_label = font.render(PEXELS_LABEL, True, LABEL_COLOR)
        if d_x < 0:
            x = 4
        else:
            x = abs(d_x) + 4
        component.content[1].blit(pexels_label, (x, y))

        p = self.photographers[i]
        label_size = font.size(p)
        photographer_label = font.render(p, True, LABEL_COLOR)
        if d_x < 0:
            x = x = size[0] - label_size[0] - 4
        else:
            x = size[0] - (abs(size[0] - self.w)/2) - label_size[0] - 4
        component.content[1].blit(photographer_label, (x, y))
        
        if len(self.components) == 1:
            self.components.append(component)
        else:
            self.components[1] = component

        self.clean_draw_update()
