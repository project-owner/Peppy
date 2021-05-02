# Copyright 2019-2021 Peppy Player peppy.player@gmail.com
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
from util.keys import KEY_HOME, KEY_PLAYER, KEY_BACK, KEY_DELETE, KEY_VIEW

class KeyboardNavigator(Navigator):
    """ Collection browser navigator """

    def __init__(self, util, bounding_box, listeners, show_visibility=True):
        """ Initializer
        
        :param util: utility object
        :param bounding_box: bounding box
        :param listeners: buttons listeners
        :param show_visibility: True - show visibility icon, False - don't show
        """
        items = []
        self.add_button(items, KEY_HOME, None, [listeners[KEY_HOME]])
        self.add_button(items, KEY_BACK, None, [listeners[KEY_BACK]])
        self.add_button(items, KEY_DELETE, None, [listeners[KEY_DELETE]])
        if show_visibility:
            self.add_button(items, KEY_VIEW, None, [listeners[KEY_VIEW]])
        self.add_button(items, KEY_PLAYER, None, [listeners[KEY_PLAYER]])

        Navigator.__init__(self, util, bounding_box, "keyboard.navigator", items, None)
