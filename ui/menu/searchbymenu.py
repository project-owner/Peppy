# Copyright 2024 Peppy Player peppy.player@gmail.com
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

from ui.factory import Factory
from ui.menu.menu import Menu
from ui.layout.buttonlayout import TOP
from ui.layout.buttonlayout import TOP, CENTER
from util.keys import *

ICON_LOCATION = TOP
BUTTON_PADDING = 0
ICON_AREA = 70
ICON_SIZE = 54
FONT_HEIGHT = 48

class SearchByMenu(Menu):
    """ Radio Browser Search By Menu class """

    def __init__(self, util, bgr=None, bounding_box=None):
        """ Initializer

        :param util: utility object
        :param bgr: menu background
        :param bounding_box: bounding box
        """
        self.util = util
        self.factory = Factory(util)
        self.config = util.config

        self.bb = bounding_box
        self.horizontal_layout = True
        self.rows = 2
        self.cols = 2
        items = [KEY_SEARCH_BY_COUNTRY, KEY_SEARCH_BY_LANGUAGE, KEY_SEARCH_BY_GENRE, KEY_SEARCH_BY_NAME]
        layout = self.get_layout(items)
        bounding_box = layout.get_next_constraints()
        box = self.factory.get_icon_bounding_box(bounding_box, ICON_LOCATION, ICON_AREA, ICON_SIZE, BUTTON_PADDING)
        cell_bb = bounding_box

        m = self.create_menu_button
        label_area = (cell_bb.h / 100) * (100 - ICON_AREA)
        font_size = int((label_area / 100) * FONT_HEIGHT)
        Menu.__init__(self, util, bgr, self.bb, self.rows, self.cols, create_item_method=m, font_size=font_size)
        labels = ["country", "language", "genre", "name"]
        self.items = util.load_menu(items, None, disabled_items=None, v_align=V_ALIGN_TOP, bb=box, labels=labels)
        self.set_items(self.items, 0, self.change_item, False)
        self.current_item = self.items[KEY_SEARCH_BY_COUNTRY]
        self.item_selected(self.current_item)

    def create_menu_button(self, s, constr, action, scale, font_size):
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

    def change_item(self, state):
        """ Change mode event listener

        :param state: button state
        """
        if not self.visible:
            return
        self.notify_listeners(state)
