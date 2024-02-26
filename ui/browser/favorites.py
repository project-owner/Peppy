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

from ui.browser.search import RadioSearchScreen, MENU_ROWS, MENU_COLUMNS, PAGE_SIZE
from ui.factory import Factory
from util.keys import *
from util.config import *

class FavoritesScreen(RadioSearchScreen):
    """ Radio Browser Favorites Screen """
    
    def __init__(self, util, listeners, state):
        """ Initializer
        
        :param util: utility object
        :param listeners: screen event listeners
        :param state: initial state
        """
        self.util = util
        self.config = util.config
        self.radio_browser_util = util.radio_browser
        self.factory = Factory(util)
        rows = MENU_ROWS
        columns = MENU_COLUMNS
        self.page_size = rows * columns
        self.go_player = listeners[KEY_PLAYER]
        self.listeners = listeners
        self.bgr_color = self.util.config[COLORS][COLOR_DARK]
        RadioSearchScreen.__init__(self, util, listeners, state)
        if not self.config.get(KEY_RADIO_BROWSER_FAVORITES, None):
            self.config[KEY_RADIO_BROWSER_FAVORITES] = self.radio_browser_util.load_favorites(self.bgr_color)
        self.DEFAULT_TITLE = self.config[LABELS]["favorites"]
        self.load_page(state)

    def load_page(self, state):
        """ Load page items
        
        :param state: button state
        """
        self.title = self.DEFAULT_TITLE
        self.screen_title.set_text(self.title)
        self.menu_items = self.get_items()
        self.turn_page()
        self.clean_draw_update()

    def get_items(self):
        """ Get favorite items
        
        :return: favorites playlist
        """
        playlist = self.config.get(KEY_RADIO_BROWSER_FAVORITES, None)
        if playlist:
            self.total_pages = math.ceil(len(playlist) / PAGE_SIZE)
            if self.config[RADIO_BROWSER][FAVORITE_STATION_NAME]: 
                self.title = self.config[RADIO_BROWSER][FAVORITE_STATION_NAME]
            else:
                self.title = self.DEFAULT_TITLE
            return playlist
        else:
            self.title = self.DEFAULT_TITLE
            self.total_pages = 0
            return None
    
    def get_page(self):
        """ Get the current page from the playlist

        :return: the page
        """
        if self.total_pages == 0:
            self.left_button.change_label("0")
            self.right_button.change_label("0")
            self.set_title()
            return []
        
        if self.current_page == None:
            self.current_page = 1

        self.set_title()

        start = (self.current_page - 1) * self.page_size
        end = self.current_page * self.page_size
        playlist = self.config[KEY_RADIO_BROWSER_FAVORITES]
        self.menu_items = playlist[start : end]

        return self.menu_items

    def change_item(self, state):
        """ Change item

        :param state: state object
        """
        self.util.config[RADIO_BROWSER][FAVORITE_STATION_NAME] = state.name
        self.util.config[RADIO_BROWSER][FAVORITE_STATION_ID] = state.id
        self.util.config[RADIO_BROWSER][FAVORITE_STATION_LOGO] = state.image_path
        self.util.config[RADIO_BROWSER][FAVORITE_STATION_URL] = state.url
        self.title = state.name
        self.screen_title.set_text(self.title)
        state.source = KEY_FAVORITES
        self.go_player(state)

    def select_current_menu_item(self):
        """ Select current menu item """

        self.browser_menu.unselect()
        id = self.config[RADIO_BROWSER][FAVORITE_STATION_ID]
        for b in self.browser_menu.buttons.values():
            if b.state.id == id:
                b.set_selected(True)
                self.navigator.unselect()
                break
        
        if not self.navigator.is_selected() and not self.browser_menu.is_selected():
            self.back_button.set_selected(True)

    def get_page_by_index(self, index):
        """ Get the page by index

        :param index: page index

        :return: the page
        """
        if index < PAGE_SIZE:
            page = 1
        else:
            page = math.ceil(index / PAGE_SIZE)
        return page

    def set_current(self, state):
        """ Set as a current screen
        
        :param state: button state
        """
        source = getattr(state, "source", None)
        if source == None or source == KEY_BACK:
            return
        
        elif source == KEY_RADIO_BROWSER_PLAYER:
            playlist = self.config.get(KEY_RADIO_BROWSER_FAVORITES, None)
            if playlist:
                if self.radio_browser_util.is_favorite(state):
                    s = state
                else:
                    index = state.index
                    if state.index >= len(playlist):
                        index -= 1
                    self.current_page = self.get_page_by_index(index + 1)
                    s = playlist[index]
            else:
                s = None
            self.load_page(s)
            self.select_current_menu_item()
