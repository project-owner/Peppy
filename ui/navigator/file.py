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
from util.keys import GO_BACK, GO_LEFT_PAGE, GO_RIGHT_PAGE, GO_ROOT, GO_USER_HOME, GO_TO_PARENT, \
    KEY_HOME, KEY_PLAYER, KEY_PLAY_FILE, KEY_ROOT, KEY_PARENT, KEY_USER_HOME, KEY_SWITCH
from util.config import USE_SWITCH

class FileNavigator(Navigator):
    """ File browser navigator menu """
    
    def __init__(self, util, bounding_box, listeners):
        """ Initializer
        
        :param util: utility object
        :param bounding_box: bounding box
        :param listeners: buttons listeners
        """
        items = []
        self.add_button(items, KEY_HOME, None, [listeners[KEY_HOME]])
        self.add_button(items, KEY_USER_HOME, None, [listeners[GO_USER_HOME]])
        self.add_button(items, KEY_ROOT, None, [listeners[GO_ROOT]])
        self.add_button(items, KEY_PARENT, None, [listeners[GO_TO_PARENT]])
        if util.config[USE_SWITCH] and util.config[KEY_SWITCH]:
            self.add_button(items, KEY_SWITCH, None, [listeners[KEY_SWITCH]])    
        self.add_button(items, KEY_PLAYER, None, [listeners[GO_BACK], listeners[KEY_PLAY_FILE]])

        arrow_items = []
        self.add_button(arrow_items, None, None, [listeners[GO_LEFT_PAGE]])
        self.add_button(arrow_items, None, None, [listeners[GO_RIGHT_PAGE]])
        
        Navigator.__init__(self, util, bounding_box, "file.navigator", items, arrow_items)
