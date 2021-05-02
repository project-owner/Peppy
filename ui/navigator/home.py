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

from util.config import LANGUAGE, SCREENSAVER, EQUALIZER, HOME_NAVIGATOR, TIMER, HOME_SCREENSAVER, \
    HOME_BACK, HOME_LANGUAGE, ABOUT, NETWORK
from ui.navigator.navigator import Navigator
from util.keys import KEY_PLAYER, KEY_ABOUT, KEY_BACK, KEY_PLAYER

class HomeNavigator(Navigator):
    """ Home Navigator """
    
    def __init__(self, util, bounding_box, listeners):
        """ Initializer
        
        :param util: utility object
        :param bounding_box: bounding box
        :param listeners: buttons listeners
        """
        items = []

        if util.config[HOME_NAVIGATOR][HOME_BACK]:
            self.add_button(items, KEY_BACK, None, [listeners[KEY_BACK]])

        if util.is_screensaver_available() and util.config[HOME_NAVIGATOR][HOME_SCREENSAVER]:
            self.add_button(items, SCREENSAVER, None, [listeners[SCREENSAVER]])

        if util.config[HOME_NAVIGATOR][HOME_LANGUAGE]:
            self.add_button(items, LANGUAGE, None, [listeners[LANGUAGE]])

        if util.config[HOME_NAVIGATOR][EQUALIZER]:
            self.add_button(items, EQUALIZER, None, [listeners[EQUALIZER]])

        if util.config[HOME_NAVIGATOR][TIMER]:
            self.add_button(items, TIMER, None, [listeners[TIMER]])

        if util.config[HOME_NAVIGATOR][NETWORK]:
            self.add_button(items, NETWORK, None, [listeners[NETWORK]])

        if util.config[HOME_NAVIGATOR][KEY_PLAYER]:
            self.add_button(items, KEY_PLAYER, None, [listeners[KEY_PLAYER]])

        if util.config[HOME_NAVIGATOR][ABOUT]:
            self.add_button(items, KEY_ABOUT, None, [listeners[KEY_ABOUT]])

        if len(items) == 0:
            return

        Navigator.__init__(self, util, bounding_box, "home.navigator", items, None)
