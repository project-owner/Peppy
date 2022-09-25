# Copyright 2016-2022 Peppy Player peppy.player@gmail.com
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
from util.util import IMAGE_ABC, IMAGE_NEW_BOOKS, IMAGE_BOOK_GENRE, IMAGE_PLAYER
from util.keys import GO_BACK, GO_LEFT_PAGE, GO_RIGHT_PAGE, GO_ROOT, GO_USER_HOME, GO_TO_PARENT, GO_PLAYER, \
    KEY_HOME, KEY_BACK, KEY_PLAY_FILE, BOOK_NAVIGATOR_BACK, BOOK_NAVIGATOR

class BookNavigator(Navigator):
    """ Book navigator """

    def __init__(self, util, bounding_box, listeners, language_url=None):
        """ Initializer
        
        :param util: utility object
        :param bounding_box: bounding box
        :param listeners: buttons listeners
        :param language_url: language URL
        """
        items = []
        self.add_button(items, KEY_HOME, None, [listeners[KEY_HOME]])

        if language_url == None:
            self.add_button(items, IMAGE_ABC, None, [listeners[GO_USER_HOME]])

        self.add_button(items, IMAGE_NEW_BOOKS, None, [listeners[GO_ROOT]])

        if language_url == None or language_url == "": # English-USA or Russian
            self.add_button(items, IMAGE_BOOK_GENRE, None, [listeners[GO_TO_PARENT]])

        self.add_button(items, IMAGE_PLAYER, None, [listeners[GO_PLAYER]], source=BOOK_NAVIGATOR)
        self.add_button(items, KEY_BACK, None, [listeners[GO_BACK]], source=BOOK_NAVIGATOR_BACK)
        
        arrow_items = []
        self.add_button(arrow_items, None, None, [listeners[GO_LEFT_PAGE]])
        self.add_button(arrow_items, None, None, [listeners[GO_RIGHT_PAGE]])

        Navigator.__init__(self, util, bounding_box, "book.navigator", items, arrow_items)
        self.back_button = self.get_button_by_name(KEY_BACK)
        try:
            self.back_button.add_release_listener(listeners[KEY_PLAY_FILE])
        except:
            pass
