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
from util.keys import GO_LEFT_PAGE, GO_RIGHT_PAGE, KEY_HOME, KEY_PLAYER, KEY_PLAY_PAUSE, \
    KEY_KEYBOARD_KEY, KEY_SEARCH, KEY_ARCHIVE_ITEMS, KEY_LIST, KEY_BACK, KEY_ENTER_QUERY
from util.config import LABELS

MAXIMUM_QUERY_TEXT_LENGTH = 256

class ArchiveFilesNavigator(Navigator):
    """ Archive browser navigator menu """
    
    def __init__(self, util, bounding_box, listeners, name="archive.navigator"):
        """ Initializer
        
        :param util: utility object
        :param bounding_box: bounding box
        :param listeners: buttons listeners
        """
        items = []
        self.config = util.config
        self.go_keyboard = listeners[KEY_KEYBOARD_KEY]
        self.go_archive_items = listeners[KEY_ARCHIVE_ITEMS]
        self.add_button(items, KEY_HOME, KEY_HOME, [listeners[KEY_HOME]])
        self.add_button(items, KEY_BACK, KEY_BACK, [listeners[KEY_BACK]])
        self.add_button(items, KEY_LIST, None, [listeners[KEY_ARCHIVE_ITEMS]])
        self.add_button(items, KEY_SEARCH, None, [self.pre_keyboard])
        self.add_button(items, KEY_PLAYER, KEY_PLAY_PAUSE, [listeners[KEY_PLAYER]])

        arrow_items = []
        self.add_button(arrow_items, None, None, [listeners[GO_LEFT_PAGE]])
        self.add_button(arrow_items, None, None, [listeners[GO_RIGHT_PAGE]])
        
        Navigator.__init__(self, util, bounding_box, name, items, arrow_items)

    def pre_keyboard(self, state=None):
        """ Set state parameters and go to Keyboard screen

        :param state: button state
        """
        state.visibility = False
        state.callback = self.go_archive_items
        state.title = self.config[LABELS][KEY_ENTER_QUERY]
        self.go_keyboard(state, max_text_length=MAXIMUM_QUERY_TEXT_LENGTH)
