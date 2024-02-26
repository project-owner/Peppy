# Copyright 2019-2024 Peppy Player peppy.player@gmail.com
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
from util.keys import KEY_HOME, KEY_PLAYER, KEY_PLAY_PAUSE, KEY_DISCONNECT, KEY_REFRESH, KEY_BLUETOOTH_REMOVE
from util.config import WIFI, BLUETOOTH, USAGE, USE_BLUETOOTH, BLUETOOTH_SINK

class NetworkNavigator(Navigator):
    """ Network Navigator """

    def __init__(self, util, bounding_box, listeners):
        """ Initializer
        
        :param util: utility object
        :param bounding_box: bounding box
        :param listeners: buttons listeners
        """
        config = util.config
        items = []
        self.add_button(items, KEY_HOME, None, [listeners[KEY_HOME]])

        self.add_button(items, KEY_REFRESH, None, [listeners[KEY_REFRESH]])
        self.add_button(items, WIFI, None, [listeners[WIFI]])
        self.add_button(items, KEY_DISCONNECT, None, [listeners[KEY_DISCONNECT]])
        if config[USAGE][USE_BLUETOOTH]:
            self.add_button(items, BLUETOOTH, None, [listeners[BLUETOOTH]])
            self.add_button(items, KEY_BLUETOOTH_REMOVE, None, [listeners[KEY_BLUETOOTH_REMOVE]])

        self.add_button(items, KEY_PLAYER, KEY_PLAY_PAUSE, [listeners[KEY_PLAYER]])

        Navigator.__init__(self, util, bounding_box, "network.navigator", items, None)
