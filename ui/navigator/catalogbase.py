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

from ui.navigator.navigator import Navigator
from util.keys import *

class CatalogBaseNavigator(Navigator):
    """ Catalog base navigator menu """

    def __init__(self, util, bounding_box, listeners, name="archive.navigator", custom_nav_button=None):
        """ Initializer

        :param util: utility object
        :param bounding_box: bounding box
        :param listeners: buttons listeners
        """
        items = []
        self.config = util.config
        self.add_button(items, KEY_HOME, KEY_HOME, [listeners[KEY_HOME]])
        self.add_button(items, KEY_BACK, KEY_BACK, [listeners[KEY_BACK]])
        self.add_button(items, KEY_CATALOG, None, [listeners[KEY_CATALOG]])

        if custom_nav_button:
            custom_button_name, custom_button_listener = custom_nav_button
            self.add_button(items, custom_button_name, None, [custom_button_listener], source=custom_button_name)

        self.add_button(items, KEY_PLAYER, KEY_PLAY_PAUSE, [listeners[KEY_PLAYER]], KEY_BACK)

        arrow_items = []
        self.add_button(arrow_items, None, None, [listeners[GO_LEFT_PAGE]])
        self.add_button(arrow_items, None, None, [listeners[GO_RIGHT_PAGE]])

        Navigator.__init__(self, util, bounding_box, name, items, arrow_items)
