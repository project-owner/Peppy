# Copyright 2020 Peppy Player peppy.player@gmail.com
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

from ui.container import Container
from ui.layout.gridlayout import GridLayout
from ui.layout.borderlayout import BorderLayout
from ui.factory import Factory
from util.config import USAGE, USE_WEB, LABELS, COLORS, COLOR_DARK_LIGHT, COLLECTION, COLLECTION_TOPIC, TOPIC_DETAIL
from util.collector import GENRE, ARTIST, ALBUM, TITLE, DATE, TYPE, COMPOSER
from util.keys import GO_LEFT_PAGE, GO_RIGHT_PAGE, KEY_HOME, KEY_PLAYER, KEY_PLAY_PAUSE, KEY_BACK, KEY_LIST, \
    KEY_DETAIL, KEY_NAVIGATOR, KEY_PARENT, KEY_MENU, KEY_SETUP

IMAGE_SIZE_PERCENT = 58
PERCENT_ARROW_WIDTH = 16.0

class CollectionBrowserNavigator(Container):
    """ Topic detail navigator """

    def __init__(self, util, bounding_box, listeners):
        """ Initializer

        :param util: utility object
        :param bounding_box: bounding box
        :param listeners: buttons listeners
        """
        Container.__init__(self, util)
        self.factory = Factory(util)
        self.name = "collection.navigator"
        self.content = bounding_box
        self.content_x = bounding_box.x
        self.content_y = bounding_box.y
        self.listeners = listeners
        self.menu_buttons = []
        self.config = util.config
        self.use_web = self.config[USAGE][USE_WEB]
        self.bgr = util.config[COLORS][COLOR_DARK_LIGHT]
        self.arrow_layout = BorderLayout(bounding_box)
        self.arrow_layout.set_percent_constraints(0, 0, PERCENT_ARROW_WIDTH, PERCENT_ARROW_WIDTH)
        self.update_observer = None
        self.redraw_observer = None
        self.menu_buttons = []

        constr = self.arrow_layout.LEFT
        self.left_button = self.factory.create_page_down_button(constr, "0", 40, 100)
        self.left_button.add_release_listener(self.listeners[GO_LEFT_PAGE])
        self.add_component(self.left_button)
        self.menu_buttons.append(self.left_button)

        constr = self.arrow_layout.RIGHT
        self.right_button = self.factory.create_page_up_button(constr, "0", 40, 100)
        self.right_button.add_release_listener(self.listeners[GO_RIGHT_PAGE])
        self.add_component(self.right_button)
        self.menu_buttons.append(self.right_button)

        layout = GridLayout(self.arrow_layout.CENTER)
        layout.set_pixel_constraints(1, 5, 1, 0)
        layout.current_constraints = 0

        self.add_button(KEY_HOME, KEY_HOME, layout, self.listeners[KEY_HOME])
        self.add_button(COLLECTION, KEY_PARENT, layout, self.listeners[COLLECTION])
        self.add_button(KEY_LIST, KEY_MENU, layout, self.listeners[COLLECTION_TOPIC])
        self.add_button(KEY_DETAIL, KEY_SETUP, layout, self.listeners[TOPIC_DETAIL])
        self.add_button(KEY_PLAYER, KEY_PLAY_PAUSE, layout, self.listeners[KEY_PLAYER])

        if self.use_web and self.update_observer != None:
            self.add_observers(self.update_observer, self.redraw_observer)

    def add_button(self, img_name, key, layout, listener):
        """ Add button to the navigator

        :param img_name: button image name
        :param key: keyboard key
        :param layout: button layout
        :param listener: button listener
        """
        c = layout.get_next_constraints()
        b = self.factory.create_button(img_name, key, c, listener, self.bgr, source=KEY_NAVIGATOR, image_size_percent=IMAGE_SIZE_PERCENT)
        self.add_component(b)
        self.menu_buttons.append(b)

    def add_observers(self, update_observer, redraw_observer):
        """ Add screen observers

        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        if self.update_observer == None:
            self.update_observer = update_observer
            self.redraw_observer = redraw_observer

        for b in self.menu_buttons:
            self.add_button_observers(b, update_observer, redraw_observer)
