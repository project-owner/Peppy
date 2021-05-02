# Copyright 2020-2021 Peppy Player peppy.player@gmail.com
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
from util.config import COLLECTION, COLLECTION_TOPIC, TOPIC_DETAIL
from util.keys import GO_LEFT_PAGE, GO_RIGHT_PAGE, KEY_HOME, KEY_PLAYER, KEY_LIST, KEY_DETAIL

class CollectionBrowserNavigator(Navigator):
    """ Collection browser navigator """

    def __init__(self, util, bounding_box, listeners):
        """ Initializer
        
        :param util: utility object
        :param bounding_box: bounding box
        :param listeners: buttons listeners
        """
        items = []
        self.add_button(items, KEY_HOME, None, [listeners[KEY_HOME]])
        self.add_button(items, COLLECTION, None, [listeners[COLLECTION]])
        self.add_button(items, KEY_LIST, None, [listeners[COLLECTION_TOPIC]])
        self.add_button(items, KEY_DETAIL, None, [listeners[TOPIC_DETAIL]])
        self.add_button(items, KEY_PLAYER, None, [listeners[KEY_PLAYER]])

        arrow_items = []
        self.add_button(arrow_items, None, None, [listeners[GO_LEFT_PAGE]])
        self.add_button(arrow_items, None, None, [listeners[GO_RIGHT_PAGE]])
        
        Navigator.__init__(self, util, bounding_box, "collection.browser.navigator", items, arrow_items)
