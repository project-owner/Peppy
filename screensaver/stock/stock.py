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

import pygame
import time
import random

from ui.state import State
from ui.card.card import CHANGE_PERCENT, CHANGE_VALUE, ICON_LABEL, LABEL, Card, DETAILS, BLACK, VALUE, \
    UNIT, COLOR_THEME, TREND
from ui.container import Container
from stockutil import StockUtil
from screensaver.screensaver import Screensaver, PLUGIN_CONFIGURATION
from util.config import BACKGROUND, SCREEN_BGR_COLOR, STOCK
from itertools import cycle

TIME_FORMAT = "%H:%M:%S"
VALUE_HEIGHT = 45

class Stock(Container, Screensaver):
    """ Stock screensaver class """
    
    def __init__(self, util=None):
        """ Initializer
        
        :param util: utility object
        """
        self.name = STOCK
        plugin_folder = type(self).__name__.lower() 
        Screensaver.__init__(self, self.name, util, plugin_folder)
        self.util = util
        self.rect = util.screen_rect
        self.screens = []
        Container.__init__(self, self.util, self.rect, BLACK)
        self.current_screen = None
        self.padding = (2, 2, 2, 2)
        self.tickers = None
        self.LOADING = "....."

        t = self.plugin_config_file.get(PLUGIN_CONFIGURATION, "ticker")
        if t == None or len(t.strip()) == 0:
            return

        bgr_img_num = 6
        self.bgr_images = self.get_bgr_images(bgr_img_num)
        if self.bgr_images != None:
            self.image_indexes = cycle(range(len(self.bgr_images)))

        self.tickers = t.split(",")
        self.tickers = list(map(str.strip, self.tickers))
        self.stock_util = StockUtil(util, self.set_values, self.tickers)

        for ticker in self.tickers:
            self.add_card(ticker)

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
        br = 4
        for n in r:
            img = self.util.get_background(self.name + "." + str(n), bgr, index=n, blur_radius=br)
            images.append((img[3], img[2]))

        return images

    def add_card(self, name):
        """ Add card screen
        
        :param cache_name: icon cache name
        :param name: screen name
        :param icon_name: icon name
        """
        card = Card(name, self.util.screen_rect, name, self.util, icon_name=None, lcd=False, 
            show_details=True, padding=self.padding, value_height=VALUE_HEIGHT)
        card.set_visible(False)
        card.set_value(colors=self.stock_util.get_color_theme(), bgr_img=self.get_bgr_image())
        self.add_component(card)
        self.screens.append(card)

    def is_ready(self):
        """ Check if screensaver is ready """

        return True

    def start(self):
        """ Start screensaver """
        
        self.stock_util.start_callback = self.update_web
        pygame.event.clear()

    def update_web(self):
        """ Update web clients from thread """

        s = State()
        s.screen = self
        self.start_callback(s)

    def stop(self):
        """ Stop screensaver """

        self.stock_util.stop_thread()

    def get_bgr_image(self):
        """ Get the next background image
        
        :return: background image
        """
        bgr_image = None

        if self.bgr_images != None:
            i = next(self.image_indexes)
            bgr_image = self.bgr_images[i]

        return bgr_image

    def set_values(self, values):
        """ Set screen values
        
        :param values: screen values
        """
        if values == None:
            self.current_screen.set_label(self.current_screen.name)
            self.current_screen.set_visible(True)
            self.current_screen.clean_draw_update()
            return    

        timestamp = time.strftime(TIME_FORMAT)
        self.current_screen.set_value(values[LABEL], values[ICON_LABEL], colors=values[COLOR_THEME], 
            value=values[VALUE], unit=values[UNIT], details=values[DETAILS], trend=values[TREND], 
            timestamp=timestamp, bgr_img=self.get_bgr_image(), change_value=values[CHANGE_VALUE], change_percent=values[CHANGE_PERCENT])

        self.current_screen.set_visible(True)
        self.current_screen.clean_draw_update()

    def refresh(self):
        """ Refresh screen """

        if self.tickers == None:
            return
        
        i = next(self.screen_indexes)
        if self.current_screen != None:
            self.current_screen.set_visible(False)
        self.current_screen = self.screens[i]
        
        self.stock_util.get_stock_info(self.current_screen.name)

        if self.current_screen.label == None:
            label = self.current_screen.name + " " + self.LOADING
        else:
            label = self.current_screen.label
            if not self.current_screen.label.endswith(self.LOADING):
                label = self.current_screen.label + " " + self.LOADING

        self.current_screen.set_label(label)

        self.current_screen.set_visible(True)
        self.current_screen.clean_draw_update()

    def set_visible(self, flag):
        pass
