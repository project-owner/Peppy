# Copyright 2016-2024 Peppy Player peppy.player@gmail.com
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
import time
import pygame
import pygame.freetype
import logging

from random import randrange
from ui.component import Component
from ui.container import Container
from screensaver.screensaver import Screensaver, PLUGIN_CONFIGURATION
from util.config import SCREEN_INFO, WIDTH, HEIGHT, COLORS, CLOCK, GENERATED_IMAGE, FONT_KEY
from util.util import PACKAGE_SCREENSAVER

TYPE = "type"
FONT = "font"
IMAGE = "image"
MILITARY_TIME_FORMAT = "military.time.format"
ANIMATED = "animated"
CLOCK_SIZE = "clock.size"
FONT_NAME = "font.name"
IMAGE_FOLDER = "image.folder"
SHOW_SECONDS = "show.seconds"
MULTI_COLOR = "multi.color"
COLOR = "color"
HORIZONTAL_ADVANCE_X = 4
COLOR_KEYS = [
    "hour.1", "hour.2", "hour.separator", "minute.1", "minute.2", "minute.separator", "second.1", "second.2"
]

class Clock(Container, Screensaver):
    """ Clock screensaver plug-in.

    After delay it displays the clock either in format HH:MM or HH:MM:SS.
    The clock periodically changes on-screen position. 
    The period in seconds can be defined in the configuration file.
    """
    def __init__(self, util):
        """ Initializer
        
        :param util: contains configuration object
        """
        self.name = CLOCK
        self.util = util
        self.image_util = util.image_util
        self.config = util.config
        config_class = util.config_class
        plugin_folder = type(self).__name__.lower()
        Screensaver.__init__(self, self.name, util, plugin_folder)
        Container.__init__(self, util, bounding_box=util.screen_rect, background=self.bg[1], content=self.bg[2], image_filename=self.bg[3])
        
        military_time_format = self.plugin_config_file.getboolean(PLUGIN_CONFIGURATION, MILITARY_TIME_FORMAT)
        self.show_seconds = self.plugin_config_file.getboolean(PLUGIN_CONFIGURATION, SHOW_SECONDS)
        self.multi_color = self.plugin_config_file.getboolean(PLUGIN_CONFIGURATION, MULTI_COLOR)
        self.type = self.plugin_config_file.get(PLUGIN_CONFIGURATION, TYPE)
        self.clock_width_percent = self.plugin_config_file.getint(PLUGIN_CONFIGURATION, CLOCK_SIZE)
        image_folder = self.plugin_config_file.get(PLUGIN_CONFIGURATION, IMAGE_FOLDER)
        self.images_folder = os.path.join(PACKAGE_SCREENSAVER, plugin_folder, image_folder)
        self.screen_width = self.config[SCREEN_INFO][WIDTH]
        self.screen_height = self.config[SCREEN_INFO][HEIGHT]
        color = self.plugin_config_file.get(PLUGIN_CONFIGURATION, COLOR)
        self.color = config_class.get_color_tuple(color)

        if military_time_format:
            if self.show_seconds:
                self.TIME_FORMAT = "%H:%M:%S"
            else:
                self.TIME_FORMAT = "%H:%M"
        else:
            if self.show_seconds:
                self.TIME_FORMAT = "%I:%M:%S"
            else:
                self.TIME_FORMAT = "%I:%M"
        
        self.animated = self.plugin_config_file.getboolean(PLUGIN_CONFIGURATION, ANIMATED)

        if self.type == FONT:
            self.init_font_clock()
        elif self.type == IMAGE:
            self.init_image_clock()

        self.component = Component(util)
        self.component.name = GENERATED_IMAGE + self.name
        self.component.image_filename = self.component.name
        self.add_component(self.component)

        self.component.content_x = None
        self.component.content_y = None
        self.counter = 0

        self.colors = []
        for key in COLOR_KEYS:
            color = self.plugin_config_file.get(COLORS, key)
            color_tuple = config_class.get_color_tuple(color)
            self.colors.append(color_tuple)

    def get_update_period(self):
        """ Return screensaver update period """

        if self.show_seconds:
            return 1
        else:
            return self.update_period

    def init_font_clock(self):
        """ Font Clock initializer """

        try:
            font_name = self.plugin_config_file.get(PLUGIN_CONFIGURATION, FONT_NAME)
            if not font_name:
                font_name = self.util.config[FONT_KEY]
            font_filename = os.path.join(FONT, font_name)
            pygame.freetype.init()

            self.font = pygame.freetype.Font(font_filename)

            self.font.size = 60

            if self.show_seconds:
                text_sample = "23:45:08"
            else:
                text_sample = "23:45"

            metrics = self.font.get_metrics(text_sample)
            text_width = 0
            for m in metrics:
                text_width += m[4]

            w = self.config[SCREEN_INFO][WIDTH]
            self.font.size = (60 * w) / text_width
            self.font.size = (self.font.size * self.clock_width_percent) / 100

            self.font.origin = True
            rect = self.font.get_rect(text_sample)
            self.baseline = rect.y
        except Exception as e:
            logging.debug(e)

    def get_font_clock(self, current_time):
        """ Font Clock getter

        :param current_time: current time

        :return: the tuple with image and its bounding box
        """
        metrics = self.font.get_metrics(current_time)
        rect = self.font.get_rect(current_time)
        img = pygame.Surface((rect.size[0] + 6, rect.size[1] + 6), pygame.SRCALPHA, 32)
        x = 0

        for (idx, (letter, metric)) in enumerate(zip(current_time, metrics)):
            color = self.colors[idx]
            self.font.render_to(img, (x, self.baseline), letter, fgcolor=color)
            x += metric[HORIZONTAL_ADVANCE_X]

        if self.multi_color:
            image = img
        else:
            image = self.font.render(current_time, fgcolor=self.color)[0]

        r = image.get_rect()
        self.set_max(r)

        return (image, r)

    def init_image_clock(self):
        """ Image Clock initializer """

        self.images = self.image_util.load_images_from_folder(self.images_folder)
        self.images.sort(key=lambda tup: tup[0])
        digit_image_size = self.images[0][1].get_size()
        colon_image_size = self.images[10][1].get_size()

        if self.show_seconds:
            clock_w = (digit_image_size[0] * 6) + (colon_image_size[0] * 2)
        else:
            clock_w = (digit_image_size[0] * 4) + colon_image_size[0]

        required_w = (self.config[SCREEN_INFO][WIDTH] * self.clock_width_percent) / 100
        k = required_w / clock_w
        scaled_image_size = (int(digit_image_size[0] * k), int(digit_image_size[1] * k))
        scaled_colon_size = (int(colon_image_size[0] * k), int(colon_image_size[1] * k))

        for n in range(10):
            self.images[n] = self.image_util.scale_image(self.images[n][1], scaled_image_size)

        self.images[10] = self.image_util.scale_image(self.images[10][1], scaled_colon_size)

        self.digit_w = self.images[0].get_size()[0]
        digit_h = self.images[0].get_size()[1]
        self.colon_w = self.images[10].get_size()[0]

        if self.show_seconds:
            clock_w = (self.digit_w * 6) + (self.colon_w * 2)
        else:
            clock_w = (self.digit_w * 4) + self.colon_w

        self.image_clock_size = (clock_w, digit_h)

    def get_image_clock(self, current_time):
        """ Image Clock getter

        :param current_time: current time

        :return: the tuple with image and its bounding box
        """
        img = pygame.Surface((self.image_clock_size[0], self.image_clock_size[1]), pygame.SRCALPHA, 32)
        x = 0

        for i, n in enumerate(current_time):
            if n == ":":
                img.blit(self.images[10], (x, 0))
                x += self.colon_w
            else:
                img.blit(self.images[int(n)], (x, 0))
                x += self.digit_w

        r = img.get_rect()
        self.set_max(r)

        return (img, r)

    def set_max(self, rect):
        """ Set maximum x and y coordinates
        
        :param rect: image bounding box
        """
        self.max_x = abs(self.screen_width - rect.w)
        self.max_y = abs(self.screen_height - rect.h)

        if self.max_x <= 1: self.max_x = 2
        if self.max_y <= 1: self.max_y = 2

    def update(self, area=None):
        """  Update screensaver """

        pass

    def refresh(self, init=False):
        """ Draw the clock on screen 
        
        :param init: initial call
        """
        current_time = time.strftime(self.TIME_FORMAT)
        self.clean()

        if self.type == FONT:
            img, rect = self.get_font_clock(current_time)
        elif self.type == IMAGE:
            img, rect = self.get_image_clock(current_time)

        self.component.content = (self.component.name, img)
        
        if self.animated:
            x = randrange(1, self.max_x)
            y = randrange(1, self.max_y)

            if self.show_seconds:
                if self.counter == 0:
                    self.component.content_x = x
                    self.component.content_y = y
                self.counter += 1
                if self.counter == self.update_period:
                    self.counter = 0
            else:
                self.component.content_x = x
                self.component.content_y = y
        else:
            if self.component.content_x == None and self.component.content_y == None:
                self.component.content_x = (self.screen_width - rect.w)/2
                self.component.content_y = (self.screen_height - rect.h)/2
        
        self.draw()

        if init:
            Component.update(self, self.bounding_box)

        return self.bounding_box
