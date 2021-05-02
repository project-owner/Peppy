# Copyright 2016-2021 Peppy Player peppy.player@gmail.com
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
from util.keys import KEY_HOME, KEY_PLAYER, CLASSICAL, JAZZ, POP, ROCK, CONTEMPORARY, FLAT

class EqualizerNavigator(Navigator):
    """ Equalizer navigator """

    def __init__(self, util, bounding_box, listeners, presets_listener):
        """ Initializer
        
        :param util: utility object
        :param bounding_box: bounding box
        :param listeners: home and player buttons listeners
        :param presets_listener: presets buttons listeners
        """
        items = []
        self.add_button(items, KEY_HOME, None, [listeners[KEY_HOME]])

        presets = [CLASSICAL, JAZZ, POP, ROCK, CONTEMPORARY, FLAT]
        for preset in presets:
            self.add_button(items, preset, None, [presets_listener])

        self.add_button(items, KEY_PLAYER, None, [listeners[KEY_PLAYER]])

        Navigator.__init__(self, util, bounding_box, "equalizer.navigator", items, None)
