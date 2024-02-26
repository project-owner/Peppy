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

from ui.component import Component
from ui.card.card import ICON_LABEL, LABEL, Card
from ui.container import Container
from monitorutil import MonitorUtil, BLACK, COLOR_THEMES, CPU, MEMORY, DISKS, PEPPY, PEPPY_ICON_NAME, \
    DISKS_ICON_NAME, COLOR_THEME, VALUE, UNIT, DETAILS
from ui.card.dashboard import Dashboard
from screensaver.screensaver import Screensaver
from util.config import BACKGROUND, SCREEN_BGR_COLOR, MONITOR
from itertools import cycle

TIME_FORMAT = "%H:%M:%S"

class Monitor(Container, Screensaver):
    """ Monitor screensaver class """
    
    def __init__(self, util=None):
        """ Initializer
        
        :param util: utility object
        """
        self.name = MONITOR
        plugin_folder = type(self).__name__.lower() 
        Screensaver.__init__(self, self.name, util, plugin_folder)
        self.util = util
        self.config = util.config
        self.rect = util.screen_rect
        self.screens = []
        self.color_theme_indexes = cycle(range(len(COLOR_THEMES)))
        Container.__init__(self, self.util, self.rect, BLACK)
        self.current_screen = None
        self.monitor_util = MonitorUtil(util)
        self.padding = (3, 3, 3, 3)

        bgr_img_num = 0
        self.bgr_images = self.get_bgr_images(bgr_img_num)
        if self.bgr_images != None:
            self.image_indexes = cycle(range(len(self.bgr_images)))

        dashboard_content = []
        dashboard_content.append((CPU, CPU, (3, 3, 2, 3)))
        dashboard_content.append((MEMORY, MEMORY, (2, 3, 3, 3)))
        dashboard_content.append((DISKS, DISKS_ICON_NAME, (3, 3, 2, 3)))
        dashboard_content.append((PEPPY, PEPPY_ICON_NAME, (2, 3, 3, 3)))

        self.dashboard = Dashboard(self.util, 2, 2, dashboard_content)
        self.dashboard.set_visible(False)
        self.add_component(self.dashboard)
        self.screens.append(self.dashboard)

        self.add_card(CPU, CPU)
        self.add_card(MEMORY, MEMORY)
        self.add_card(DISKS, DISKS, DISKS_ICON_NAME)
        self.add_card(PEPPY, PEPPY, PEPPY_ICON_NAME)

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

    def add_card(self, cache_name, name, icon_name=None):
        """ Add card screen
        
        :param cache_name: icon cache name
        :param name: screen name
        :param icon_name: icon name
        """
        if icon_name:
            i_name = icon_name
        else:
            i_name = name

        card = Card(cache_name, self.util.screen_rect, name, self.util, icon_name=i_name, lcd=True, 
            show_details=True, padding=self.padding)
        card.set_visible(False)
        self.add_component(card)
        self.screens.append(card)

    def is_ready(self):
        """ Check if screensaver is ready """

        return True

    def start(self):
        """ Start screensaver """
        
        self.screen_indexes = cycle(range(len(self.screens)))
        pygame.event.clear()

    def update(self, area=None):
        """  Update screensaver """

        pass

    def refresh(self, init=False):
        """ Refresh screen 

        :param init: initial call
        """
        i = next(self.screen_indexes)
        if self.current_screen != None:
            self.current_screen.set_visible(False)
        self.current_screen = self.screens[i]
        timestamp = time.strftime(TIME_FORMAT)

        if self.bgr_images != None:
            i = next(self.image_indexes)
            bgr_image = self.bgr_images[i]
        else:
            bgr_image = None

        if isinstance(self.current_screen, Card):
            if self.current_screen.name == CPU:
                values = self.monitor_util.get_cpu_values()
            elif self.current_screen.name == MEMORY:
                values = self.monitor_util.get_memory_values()
            elif self.current_screen.name == DISKS:
                values = self.monitor_util.get_disks_values()
            elif self.current_screen.name == PEPPY:
                values = self.monitor_util.get_peppy_values()
            
            self.current_screen.set_value(values[LABEL], values[ICON_LABEL],
                colors=values[COLOR_THEME], value=values[VALUE], unit=values[UNIT], 
                details=values[DETAILS], timestamp=timestamp, bgr_img=bgr_image)
            self.current_screen.set_visible(True)
            self.current_screen.clean()
            self.current_screen.draw()

            if init:
                Component.update(self, self.current_screen.bounding_box)

            return self.current_screen.bounding_box
        else:
            dashboard_values = self.monitor_util.get_dashboard_values()
            self.content = bgr_image
            self.dashboard.set_values(dashboard_values, bgr_image)
            self.dashboard.set_visible(True)
            self.dashboard.clean_draw_update()

            self.dashboard.clean()
            self.dashboard.draw()

            if init:
                Component.update(self, self.dashboard.bounding_box)

            return self.dashboard.bounding_box

    def set_visible(self, flag):
        pass