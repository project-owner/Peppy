# Copyright 2023 Peppy Player peppy.player@gmail.com
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
from util.keys import GO_LEFT_PAGE, GO_RIGHT_PAGE, KEY_HOME, KEY_SHUTDOWN, KEY_END, KEY_VOLUME_DOWN, KEY_VOLUME_UP, KEY_MUTE

class JukeboxNavigator(Navigator):
    """ Jukebox navigator """
    
    def __init__(self, util, bounding_box, listeners, name="jukebox.navigator"):
        """ Initializer
        
        :param util: utility object
        :param bounding_box: bounding box
        :param listeners: buttons listeners
        """
        items = []
        self.add_button(items, KEY_HOME, KEY_HOME, [listeners[KEY_HOME]])
        self.add_button(items, KEY_SHUTDOWN, KEY_END, [listeners[KEY_SHUTDOWN]])
        self.add_button(items, "volume-mute", KEY_MUTE, [listeners[KEY_MUTE]])
        self.add_button(items, "volume-down", KEY_VOLUME_DOWN, [listeners[KEY_VOLUME_DOWN]])
        self.add_button(items, "volume-up", KEY_VOLUME_UP, [listeners[KEY_VOLUME_UP]])

        arrow_items = []
        self.add_button(arrow_items, None, None, [listeners[GO_LEFT_PAGE]])
        self.add_button(arrow_items, None, None, [listeners[GO_RIGHT_PAGE]])
        
        Navigator.__init__(self, util, bounding_box, name, items, arrow_items)
