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

SORT_ALPHABETIC = "abc"
SORT_NUMERIC = "num"

class BrowserNavigator(Navigator):
    """ Radio Browser navigator menu """
    
    def __init__(self, util, bounding_box, listeners, name):
        """ Initializer
        
        :param util: utility object
        :param bounding_box: bounding box
        :param listeners: buttons listeners
        :param name: navigator name
        """
        items = []
        self.add_button(items, KEY_BACK, KEY_BACK, [listeners[KEY_BACK]])
        self.add_button(items, KEY_HOME, KEY_HOME, [listeners[KEY_HOME]])
        self.add_button(items, KEY_SEARCH, KEY_SELECT, [listeners[KEY_SEARCH_BY_SCREEN]])
        self.add_button(items, KEY_SORT_ABC, KEY_PAGE_UP, [listeners[SORT_ALPHABETIC]])
        self.add_button(items, KEY_SORT_NUM, KEY_PAGE_DOWN, [listeners[SORT_NUMERIC]])
        self.add_button(items, KEY_PLAYER, KEY_PARENT, [listeners[KEY_PLAYER]])

        arrow_items = []
        self.add_button(arrow_items, None, None, [listeners[GO_LEFT_PAGE]])
        self.add_button(arrow_items, None, None, [listeners[GO_RIGHT_PAGE]])
        
        Navigator.__init__(self, util, bounding_box, name, items, arrow_items)
