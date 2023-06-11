# Copyright 2022-2023 Peppy Player peppy.player@gmail.com
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
import pygame
import random

from ui.card.card import Card
from ui.container import Container
from horoscopeutil import HoroscopeUtil, BLUE_THEME, ORANGE_THEME, GREEN_THEME, PINK_THEME, SILVER_THEME, GOLD_THEME
from screensaver.screensaver import Screensaver
from util.config import BACKGROUND, SCREEN_BGR_COLOR, HOROSCOPE, SCREENSAVER, ICONS, LABELS
from itertools import cycle

ZODIAC_SECTION = "Zodiac"
ARIES = "aries"
TAURUS = "taurus"
GEMINI = "gemini"
CANCER = "cancer"
LEO = "leo"
VIRGO = "virgo"
LIBRA = "libra"
SCORPIO = "scorpio"
SAGITTARIUS = "sagittarius"
CAPRICORN = "capricorn"
AQUARIUS = "aquarius"
PISCES = "pisces"

ZODIAC = [ARIES, TAURUS, GEMINI, CANCER, LEO, VIRGO, LIBRA, SCORPIO, SAGITTARIUS, CAPRICORN, AQUARIUS, PISCES]

class Horoscope(Container, Screensaver):
    """ Horoscope screensaver class """
    
    def __init__(self, util=None):
        """ Initializer
        
        :param util: utility object
        """
        self.name = HOROSCOPE
        plugin_folder = type(self).__name__.lower() 
        Screensaver.__init__(self, self.name, util, plugin_folder)
        self.util = util
        self.config = util.config
        self.rect = util.screen_rect
        self.screens = []
        Container.__init__(self, self.util, self.rect, (0, 0, 0))
        self.current_screen = None
        self.icon_folder = os.path.join(os.getcwd(), SCREENSAVER, HOROSCOPE, ICONS)

        self.signs = []
        
        for z in ZODIAC:
            try:
                if self.plugin_config_file.getboolean(ZODIAC_SECTION, z):
                    self.signs.append(z)
            except:
                pass

        self.current_sign_index = 0
        self.horoscope_util = HoroscopeUtil(util, self.signs)
        self.padding = (3, 3, 3, 3)

        bgr_img_num = 4
        self.bgr_images = self.get_bgr_images(bgr_img_num)
        if self.bgr_images != None:
            self.image_indexes = cycle(range(len(self.bgr_images)))

        self.color_theme = [BLUE_THEME, ORANGE_THEME, GREEN_THEME, PINK_THEME, SILVER_THEME, GOLD_THEME]
        self.color_theme_indexes = cycle(range(len(self.color_theme)))

        for s in self.signs:
            self.add_card(s)

        self.screen_indexes = cycle(range(len(self.screens)))

    def get_bgr_images(self, bgr_img_num):
        """ Get background images
        
        :param bgr_img_num: the number of images to get

        :return: list of images
        """
        if bgr_img_num == 0:
            return None

        images = []
        r = random.sample(range(0, bgr_img_num), bgr_img_num)
        bgr = self.util.config[BACKGROUND][SCREEN_BGR_COLOR]
        blur_radius = 4
        for n in r:
            img = self.util.get_background(self.name + "." + str(n), bgr, index=n, blur_radius=blur_radius)
            images.append((img[3], img[2]))

        return images

    def add_card(self, name):
        """ Add card screen
        
        :param name: screen name
        """
        card = Card(name, self.util.screen_rect, name, self.util, icon_name=name, icon_folder=self.icon_folder, lcd=False, 
            show_details=False, padding=self.padding, icon_width=20)
        card.set_visible(False)
        i = next(self.color_theme_indexes)
        card.set_value(colors=self.color_theme[i], bgr_img=self.get_bgr_image())
        self.add_component(card)
        self.screens.append(card)

    def is_ready(self):
        """ Check if screensaver is ready """

        return len(self.signs) > 0

    def start(self):
        """ Start screensaver """
        
        pygame.event.clear()

    def get_bgr_image(self):
        """ Get next background image
        
        :return: background image
        """
        bgr_image = None

        if self.bgr_images != None:
            i = next(self.image_indexes)
            bgr_image = self.bgr_images[i]

        return bgr_image

    def refresh(self):
        """ Refresh screen """

        sign = self.signs[self.current_sign_index]
        h = self.horoscope_util.get_daily_horoscope(self.current_sign_index)

        if h == None:
            return

        self.current_sign_index += 1
        if self.current_sign_index == len(self.signs):
            self.current_sign_index = 0
        
        i = next(self.screen_indexes)
        if self.current_screen != None:
            self.current_screen.set_visible(False)

        self.current_screen = self.screens[i]
        current_date = h["current_date"]

        if self.bgr_images != None:
            i = next(self.image_indexes)
            bgr_image = self.bgr_images[i]
        else:
            bgr_image = None

        i = next(self.color_theme_indexes)

        sign_t = self.config[LABELS][sign]

        self.current_screen.set_value(sign_t, None, colors=self.color_theme[i], value=h["description"], unit=None,
            details=None, timestamp=current_date, bgr_img=bgr_image)
        self.current_screen.set_visible(True)
        self.current_screen.clean_draw_update()

    def set_visible(self, flag):
        pass
