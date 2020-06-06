# Copyright 2019-2020 Peppy Player peppy.player@gmail.com
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
from ui.factory import Factory
from util.config import BACKGROUND, FOOTER_BGR_COLOR
from util.keys import KEY_HOME, KEY_PLAYER, KEY_PLAY_PAUSE, KEY_BACK, GO_BACK, KEY_DELETE, KEY_VIEW, KEY_PARENT, KEY_SETUP

IMAGE_SIZE = 64

class KeyboardNavigator(Container):
    """ Keyboard screen navigator menu """

    def __init__(self, util, bounding_box, listeners, show_visibility=True):
        """ Initializer

        :param util: utility object
        :param bounding_box: bounding box
        :param listeners: buttons listeners
        """
        Container.__init__(self, util)
        self.factory = Factory(util)
        self.name = "keyboard.navigator"
        self.content = None
        self.content_x = bounding_box.x
        self.content_y = bounding_box.y
        self.menu_buttons = []

        if show_visibility:
            n = 5
        else:
            n = 4
        self.layout = GridLayout(bounding_box)
        self.layout.set_pixel_constraints(1, n, 1, 0)
        self.layout.current_constraints = 0
        self.bgr = util.config[BACKGROUND][FOOTER_BGR_COLOR]

        self.add_button(KEY_HOME, KEY_HOME, listeners[KEY_HOME])
        self.add_button(KEY_BACK, KEY_BACK, listeners[KEY_BACK])
        self.add_button(KEY_DELETE, KEY_PARENT, listeners[KEY_DELETE])
        if n == 5:
            self.add_button(KEY_VIEW, KEY_SETUP, listeners[KEY_VIEW])
        self.add_button(KEY_PLAYER, KEY_PLAY_PAUSE, listeners[KEY_PLAYER])

    def add_button(self, img_name, key, listener):
        """ Add button

        :param img_name: button image name
        :param key: keyboard key
        :param listener: button listener
        """
        c = self.layout.get_next_constraints()
        b = self.factory.create_button(img_name, key, c, listener, self.bgr, image_size_percent=IMAGE_SIZE)
        self.add_component(b)
        self.menu_buttons.append(b)

    def set_parent_screen(self, scr):
        """ Add parent screen

        :param scr: parent screen
        """
        for b in self.menu_buttons:
            b.parent_screen = scr

    def add_observers(self, update_observer, redraw_observer):
        """ Add screen observers

        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        for b in self.menu_buttons:
            self.add_button_observers(b, update_observer, redraw_observer)
