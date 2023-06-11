# Copyright 2020-2023 Peppy Player peppy.player@gmail.com
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
from util.keys import V_ALIGN_TOP, KEY_AUDIO_FOLDER, KEY_FILE
from util.config import NAME, COLLECTION, COLLECTION_MENU, SHOW_NUMBERS, \
    COLLECTION_PLAYBACK, COLLECTION_TOPIC
from util.collector import GENRE, ARTIST, ALBUM, TITLE, DATE, TYPE, COMPOSER, FOLDER, FILENAME
from ui.layout.buttonlayout import TOP, CENTER

ICON_LOCATION = TOP
BUTTON_PADDING = 5
ICON_AREA = 65
ICON_SIZE = 70
FONT_HEIGHT = 50

class CollectionMenu(Menu):
    """ Collection Menu class """

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
        dbutil = util.get_db_util()
        self.stats = dbutil.get_collection_summary()
        suffix = []
        items = []
        item_list = [GENRE, ARTIST, COMPOSER, ALBUM, TITLE, DATE, FOLDER, FILENAME, TYPE]

        for n, i in enumerate(item_list):
            if self.stats and self.config[COLLECTION][SHOW_NUMBERS]:
                suffix.append(self.stats[i])

            if i == FOLDER and self.config[COLLECTION_MENU][FOLDER]:
                items.append(KEY_AUDIO_FOLDER)
            elif i == FILENAME and self.config[COLLECTION_MENU][FILENAME]:
                items.append(KEY_FILE)
            elif self.config[COLLECTION_MENU][i]:
                items.append(i)

        m = self.create_collection_main_menu_button
        label_area = ((bounding_box.h / 3) / 100) * (100 - ICON_AREA)
        font_size = int((label_area / 100) * FONT_HEIGHT)
        Menu.__init__(self, util, bgr, bounding_box, None, None, create_item_method=m, font_size=font_size)
        
        if not items:
            return

        l = self.get_layout(items)
        bounding_box = l.get_next_constraints()
        image_box = self.factory.get_icon_bounding_box(bounding_box, ICON_LOCATION, ICON_AREA, ICON_SIZE, BUTTON_PADDING)

        self.topics = self.util.load_menu(items, NAME, [], V_ALIGN_TOP, bb=image_box, suffix=suffix)
        self.set_items(self.topics, 0, self.change_topic, False)

        topic = self.config[COLLECTION_PLAYBACK][COLLECTION_TOPIC]
        if topic:
            for k in self.topics.keys():
                if k == topic:
                    self.current_topic = self.topics[k]
                    break
        else:
            self.current_topic = self.topics[items[0]]

        self.item_selected(self.current_topic)

    def create_collection_main_menu_button(self, s, constr, action, scale, font_size):
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
