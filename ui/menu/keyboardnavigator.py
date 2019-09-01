# Copyright 2019 Peppy Player peppy.player@gmail.com
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
from util.config import COLORS, COLOR_DARK_LIGHT
from util.keys import KEY_HOME, KEY_PLAYER, KEY_PLAY_PAUSE, KEY_BACK, GO_BACK, KEY_DELETE, KEY_VIEW, KEY_PARENT, KEY_SETUP

class KeyboardNavigator(Container):
    """ Keyboard screen navigator menu """

    def __init__(self, util, bounding_box, listeners):
        """ Initializer

        :param util: utility object
        :param bounding_box: bounding box
        :param listeners: buttons listeners
        """
        Container.__init__(self, util)
        self.factory = Factory(util)
        self.name = "keyboard.navigator"
        self.content = bounding_box
        self.content_x = bounding_box.x
        self.content_y = bounding_box.y
        self.menu_buttons = []

        layout = GridLayout(bounding_box)
        layout.set_pixel_constraints(1, 5, 1, 0)
        layout.current_constraints = 0
        image_size = 64
        bgr = util.config[COLORS][COLOR_DARK_LIGHT]

        constr = layout.get_next_constraints()
        self.home_button = self.factory.create_button(KEY_HOME, KEY_HOME, constr, listeners[KEY_HOME], bgr,
                                                      image_size_percent=image_size)
        self.add_component(self.home_button)
        self.menu_buttons.append(self.home_button)

        constr = layout.get_next_constraints()
        self.back = self.factory.create_button(KEY_BACK, KEY_BACK, constr, listeners[KEY_BACK], bgr,
                                                   image_size_percent=image_size)
        self.add_component(self.back)
        self.menu_buttons.append(self.back)

        constr = layout.get_next_constraints()
        self.delete = self.factory.create_button(KEY_DELETE, KEY_PARENT, constr, listeners[KEY_DELETE], bgr,
                                               image_size_percent=image_size)
        self.add_component(self.delete)
        self.menu_buttons.append(self.delete)

        constr = layout.get_next_constraints()
        self.delete = self.factory.create_button(KEY_VIEW, KEY_SETUP, constr, listeners[KEY_VIEW], bgr,
                                                 image_size_percent=image_size)
        self.add_component(self.delete)
        self.menu_buttons.append(self.delete)

        constr = layout.get_next_constraints()
        self.player_button = self.factory.create_button(KEY_PLAYER, KEY_PLAY_PAUSE, constr, listeners[KEY_PLAYER], bgr,
                                                        image_size_percent=image_size)
        self.add_component(self.player_button)
        self.menu_buttons.append(self.player_button)

    def add_observers(self, update_observer, redraw_observer):
        """ Add screen observers

        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        for b in self.menu_buttons:
            self.add_button_observers(b, update_observer, redraw_observer)
