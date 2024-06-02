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

from ui.screen.screen import Screen, PERCENT_TOP_HEIGHT
from ui.menu.catalogmenu import CatalogMenu, NEW_ALBUM, BEST_SELLER, GENRE, ARTIST, ALBUM, TRACK
from ui.navigator.catalog import CatalogNavigator
from util.config import CATALOG
from util.keys import *

class CatalogScreen(Screen):
    """ Catalog Screen """

    def __init__(self, util, listeners):
        """ Initializer

        :param util: utility object
        :param listener: screen menu event listener
        """
        Screen.__init__(self, util, CATALOG, PERCENT_TOP_HEIGHT)

        self.menu = CatalogMenu(util, (0, 0, 0, 0), self.layout.CENTER, font_size=self.font_size)
        self.menu.buttons[NEW_ALBUM].add_release_listener(listeners[KEY_CATALOG_NEW_ALBUMS])
        self.menu.buttons[BEST_SELLER].add_release_listener(listeners[KEY_CATALOG_BESTSELLERS])
        self.menu.buttons[GENRE].add_release_listener(listeners[KEY_CATALOG_GENRES])
        self.menu.buttons[ARTIST].add_release_listener(listeners[KEY_CATALOG_ARTISTS])
        self.menu.buttons[ALBUM].add_release_listener(listeners[KEY_CATALOG_ALBUMS])
        self.menu.buttons[TRACK].add_release_listener(listeners[KEY_CATALOG_TRACK])
        self.add_menu(self.menu)

        self.navigator = CatalogNavigator(util, self.layout.BOTTOM, listeners)
        self.add_navigator(self.navigator)

        self.link_borders()       

    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers

        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        Screen.add_screen_observers(self, update_observer, redraw_observer)

        self.menu.add_menu_observers(update_observer, redraw_observer)
        self.navigator.add_observers(update_observer, redraw_observer)
