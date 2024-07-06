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
from util.keys import *
from util.config import NAME
from ui.layout.buttonlayout import TOP, CENTER

ICON_LOCATION = TOP
BUTTON_PADDING = 5
ICON_AREA = 65
ICON_SIZE = 50
FONT_HEIGHT = 60

class YaStreamMenu(Menu):
    """ YA Stream Menu class """

    def __init__(self, util, bgr=None, bounding_box=None, font_size=None):
        """ Initializer

        :param util: utility object
        :param bgr: menu background
        :param bounding_box: bounding box
        :param font_size: labels font size
        """
        self.util = util
        self.factory = Factory(util)
        self.config = util.config
        items = [KEY_SEARCH_BY_NAME, KEY_PLAYLISTS]

        m = self.create_ya_stream_menu_button
        label_area = ((bounding_box.h / 3) / 100) * (100 - ICON_AREA)
        font_size = int((label_area / 100) * FONT_HEIGHT)
        Menu.__init__(self, util, bgr, bounding_box, None, None, create_item_method=m, font_size=font_size)

        l = self.get_layout(items)
        bounding_box = l.get_next_constraints()
        image_box = self.factory.get_icon_bounding_box(bounding_box, ICON_LOCATION, ICON_AREA, ICON_SIZE, BUTTON_PADDING)

        self.menu_topics = self.util.load_menu(items, NAME, [], V_ALIGN_TOP, bb=image_box, labels=["search", "playlist"])
        self.set_items(self.menu_topics, 0, self.change_topic, False)
        self.current_topic = self.menu_topics[items[0]]

        self.item_selected(self.current_topic)

    def create_ya_stream_menu_button(self, s, constr, action, scale, font_size):
        """ Create Collection Main Menu button

        :param s: button state
        :param constr: scaling constraints
        :param action: button event listener
        :param scale: True - scale images, False - don't scale images

        :return: home menu button
        """
        s.padding = BUTTON_PADDING
        s.image_area_percent = ICON_AREA
        s.fixed_height = font_size
        s.v_align = CENTER

        return self.factory.create_menu_button(s, constr, action, scale, font_size=font_size)

    def change_topic(self, state):
        """ Change topic event listener

        :param state: button state
        """
        if not self.visible:
            return
        state.previous_mode = self.current_topic.name
        state.source = "menu"
        self.current_topic = state
        self.notify_listeners(state)
