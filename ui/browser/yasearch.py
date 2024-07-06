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

from ui.browser.yaplaylist import YaPlaylistScreen, YA_STREAM, YA_STREAM_ID
from ui.navigator.yasearch import YaSearchNavigator
from util.keys import *

class YaSearchScreen(YaPlaylistScreen):
    """ YA Stream Search Browser Screen """
    
    def __init__(self, util, listeners):
        """ Initializer
        
        :param util: utility object
        :param listeners: screen event listeners
        :param volume_control: volume control
        """
        YaPlaylistScreen.__init__(self, util, listeners)
        self.components.remove(self.navigator)
        self.navigator = YaSearchNavigator(self.util, self.layout.BOTTOM, listeners, "ya.search.navigator")
        self.add_navigator(self.navigator)
        self.left_button = self.navigator.get_button_by_name(KEY_PAGE_DOWN)
        self.right_button = self.navigator.get_button_by_name(KEY_PAGE_UP)
        self.player_button = self.navigator.get_button_by_name(KEY_PLAYER)
        self.current_query = ""

    def set_current(self, state):
        """ Set current state
        
        :param state: button state
        """
        skip = ["file.button", "back", "playlist", "search", KEY_SEARCH_BY_NAME]
        query = getattr(state, KEY_CALLBACK_VAR, None)

        source = getattr(state, "source", None)
        if source in skip and query == None:
            return
        
        if query == self.current_query:
            return

        self.screen_title.set_text(query)
        page = self.get_page(query)
        self.turn_page(page)

    def get_page(self, query=None):
        """ Get the current page from the playlist

        :return: the page
        """
        loading = False

        if query != None and query != self.current_query:
            self.screen_title.visible = False
            self.set_loading()
            self.current_page = 1
            self.current_query = query
            loading = True
        else:
            query = self.current_query

        playlist = self.ya_stream_util.search(query)
        self.config[KEY_YA_SEARCH_STREAM_INDEX] = 0

        if loading:
            self.reset_loading()
            self.screen_title.visible = True

        playlist_length = len(playlist)
        self.total_pages = math.ceil(playlist_length / self.page_size)
        
        if self.total_pages == 0:
            self.left_button.change_label("0")
            self.right_button.change_label("0")
            return []
        
        if self.current_page == None:
            self.current_page = self.get_page_by_id()

        start = (self.current_page - 1) * self.page_size
        end = self.current_page * self.page_size

        self.config[KEY_YA_STREAM_SEARCH_BROWSER] = playlist

        return playlist[start : end]

    def turn_page(self, page=None):
        """ Turn page """

        if page == None:
            page = self.get_page()

        d = self.ya_stream_menu.make_dict(page)
        self.ya_stream_menu.set_items(d, 0, self.change_stream, False)

        index = self.config.get(KEY_YA_SEARCH_STREAM_INDEX, 0)
        menu_selected = self.ya_stream_menu.select_by_index(index)

        if self.navigator and self.total_pages > 1:
            self.left_button.change_label(str(self.current_page - 1))
            self.right_button.change_label(str(self.total_pages - self.current_page))
        else:
            self.left_button.change_label("0")
            self.right_button.change_label("0")

        for b in self.ya_stream_menu.buttons.values():
            b.parent_screen = self

        self.ya_stream_menu.clean_draw_update()
        if menu_selected:
            self.navigator.unselect()

        self.link_borders()
        navigator_selected = self.navigator.is_selected()

        if (len(page) == 0 or (not menu_selected and not navigator_selected)) and self.navigator:
            self.navigator.unselect()
            self.player_button.set_selected(True)
            self.player_button.clean_draw_update()

    def change_stream(self, state):
        """ Change stream

        :param state: state object
        """
        state.source = KEY_YA_STREAM_SEARCH_BROWSER
        state.name = state.l_name
        state.time = "0.0"

        self.go_player(state)

    def handle_track_change(self, state):
        """ Handle track change event

        :param state: event state object
        """
        if getattr(state, "index", None) == None:
            return

        page_start_index = (self.current_page - 1) * self.page_size
        page_end_index = self.current_page * self.page_size - 1
        length = len(self.ya_stream_util.search(self.current_query))

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

        for button in self.ya_stream_menu.buttons.values():
            if button.state.index == state.index:
                button.set_selected(True)
                self.ya_stream_menu.selected_index = state.index
                self.navigator.unselect()
            else:
                button.set_selected(False)
            
            if self.ya_stream_menu.visible:
                button.clean()
                button.draw()

        self.update_component = True
