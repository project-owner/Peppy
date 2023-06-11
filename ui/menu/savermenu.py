# Copyright 2016-2023 Peppy Player peppy.player@gmail.com
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

from ui.menu.menu import Menu
from ui.factory import Factory
from util.keys import GENRE, V_ALIGN_TOP
from util.config import SCREEN_INFO, SCREENSAVER, NAME, ACTIVE_SAVERS, DISABLED_SAVERS, WIDTH, HEIGHT
from ui.layout.buttonlayout import TOP, CENTER

ICON_LOCATION = TOP
BUTTON_PADDING = 10
ICON_AREA = 80
ICON_SIZE = 48
FONT_HEIGHT = 70

class SaverMenu(Menu):
    """ Screensaver Menu class. Extends base Menu class """
    
    def __init__(self, util, bgr=None, bounding_box=None):
        """ Initializer
        
        :param util: utility object
        :param bgr: menu background
        :param bounding_box: bounding box
        """
        self.factory = Factory(util)
        self.config = util.config
        self.screen_w = self.config[SCREEN_INFO][WIDTH]
        self.screen_h = self.config[SCREEN_INFO][HEIGHT]

        items = self.config[ACTIVE_SAVERS]
        rows_num = 2
        cols_num = 4
        length = len(items)
        
        if length == 6 or length == 5:
            rows_num = 2
            cols_num = 3
        elif length == 4:
            rows_num = 2
            cols_num = 2
        elif length == 3:
            rows_num = 1
            cols_num = 3
        elif length == 2:
            rows_num = 1
            cols_num = 2
        elif length == 1:
            rows_num = 1
            cols_num = 1
        elif length == 9:
            rows_num = 3
            cols_num = 3
        elif length == 10:
            rows_num = 2
            cols_num = 5
        elif length == 11 or length == 12:
            rows_num = 3
            cols_num = 4

        m = self.create_saver_menu_button
        label_area = (bounding_box.h / rows_num / 100) * (100 - ICON_AREA)
        font_size = int((label_area / 100) * FONT_HEIGHT)

        if font_size <= 10:
            font_size = 12
        elif font_size > 20:
            font_size = 20

        Menu.__init__(self, util, bgr, bounding_box, rows=rows_num, cols=cols_num, create_item_method=m, font_size=font_size)
        
        disabled_items = self.config[DISABLED_SAVERS]
        current_saver_name = self.config[SCREENSAVER][NAME]
        l = self.get_layout(items)
        bounding_box = l.get_next_constraints()
        box = self.factory.get_icon_bounding_box(bounding_box, ICON_LOCATION, ICON_AREA, ICON_SIZE, BUTTON_PADDING)
        box.w = box.w / 2
        self.savers = util.load_menu(items, GENRE, disabled_items=disabled_items, v_align=V_ALIGN_TOP, bb=box)
        self.set_items(self.savers, 0, self.change_saver, False)
        self.current_saver = self.savers[current_saver_name]
        self.item_selected(self.current_saver)

    def create_saver_menu_button(self, s, constr, action, scale, font_size):
        """ Create Screensaver Menu button

        :param s: button state
        :param constr: scaling constraints
        :param action: button event listener
        :param scale: True - scale images, False - don't scale images
        :param font_size: label font height in pixels

        :return: screensaver menu button
        """
        s.padding = BUTTON_PADDING
        s.image_area_percent = ICON_AREA
        s.v_align = CENTER
        if s.l_name[0].islower():
            s.l_name = s.l_name.capitalize()

        return self.factory.create_menu_button(s, constr, action, scale, font_size=font_size)

    def get_saver_by_index(self, index):
        """ Return screensaver specified by its index
        
        :param index: screensaver index in the map of screensavers
        
        :return: screensaver
        """
        return self.savers[index]

    def change_saver(self, state):
        """ Change screensaver event listener
        
        :param state: button state
        """
        if not self.visible:
            return
        
        self.config[SCREENSAVER][NAME] = state.name        
        self.notify_listeners(state)
        