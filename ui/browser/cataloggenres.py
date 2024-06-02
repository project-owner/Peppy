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

import math

from ui.browser.catalogbase import CatalogBase
from util.keys import KEY_DETAILS, CATALOG_GENRES
from ui.layout.buttonlayout import LEFT

# 480x320
PERCENT_TOP_HEIGHT = 14.0625
PERCENT_BOTTOM_HEIGHT = 14.0625

ICON_LOCATION = LEFT
BUTTON_PADDING = 5
ICON_AREA = 0
ICON_SIZE = 0
FONT_HEIGHT = 16

MENU_ROWS = 5
MENU_COLUMNS = 2
MENU_PAGE_SIZE = MENU_ROWS * MENU_COLUMNS

class CatalogGenres(CatalogBase):
    """ Catalog Genres Screen """
    
    def __init__(self, util, mode, listeners, title):
        """ Initializer

        :param util: utility object
        :param mode: browser mode
        :param listeners: screen event listeners
        :param title: screen title
        """
        CatalogBase.__init__(self, util, mode, listeners, title)
        self.go_genre_artists = listeners[KEY_DETAILS]
        self.album_change_listeners = []

    def set_current(self, state):
        """ Set current state

        :param state: button state
        """
        if getattr(state, "source", None) == "resume" or getattr(state, "source", None) == "back":
            return

        if self.album_menu.buttons and getattr(state, "id", None) == None:
            return

        self.current_page = 1
        self.set_loading(None)
        self.turn_page()
        self.reset_loading()

    def get_page(self, page):
        """ Get the current page from the playlist

        :return: the page
        """
        self.total_pages = 0
        searcher = self.get_service_searcher()
        items = searcher()

        if items:
            self.config[CATALOG_GENRES] = items
            self.total_pages = math.ceil(len(items) / self.page_size)
            start = (self.current_page - 1) * self.page_size
            stop = start + self.page_size
            return items[start : stop]
        else:
            self.total_pages = 0
            self.config[CATALOG_GENRES] = []
            self.left_button.change_label("0")
            self.right_button.change_label("0")
            return []

    def change_item(self, state):
        """ Change item

        :param state: state object
        """
        state.source = self.mode
        state.name = state.l_name
        self.go_genre_artists(state)

    def handle_track_change(self, state):
        """ Handle track change event

        :param state: event state object
        """
        if getattr(state, "index", None) == None:
            return

        page_start_index = (self.current_page - 1) * self.page_size
        page_end_index = self.current_page * self.page_size - 1
        length = len(self.config[CATALOG_GENRES])

        if state.index == 0 and self.current_page != 1:
            self.current_page = 1
            self.turn_page()
        elif state.index == length - 1 and self.current_page != self.total_pages:
            self.current_page = self.total_pages
            self.turn_page()
        elif state.index > page_end_index:
            self.current_page += 1
            self.turn_page()
        elif state.index < page_start_index:
            self.current_page -= 1
            self.turn_page()    

        for button in self.album_menu.buttons.values():
            if button.state.index == state.index:
                button.set_selected(True)
                self.album_menu.selected_index = state.index
            else:
                button.set_selected(False)
            
            if self.album_menu.visible:
                button.clean_draw()

        self.update_component = True

    def add_album_change_listener(self, listener):
        """ Add album change listener

        :param listener: event listener
        """
        if listener not in self.album_change_listeners:
            self.album_change_listeners.append(listener)

    def notify_album_change_listeners(self):
        """ Notify all album change listeners """

        for listener in self.album_change_listeners:
            try:
                listener()
            except:
                pass
