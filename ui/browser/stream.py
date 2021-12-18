# Copyright 2021 Peppy Player peppy.player@gmail.com
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

from ui.browser.radio import RadioBrowserScreen
from util.keys import KEY_STREAM_BROWSER
from util.config import CURRENT, STREAM

class StreamBrowserScreen(RadioBrowserScreen):
    """ Stream Browser Screen """
    
    def __init__(self, util, listeners, voice_assistant, volume_control):
        """ Initializer
        
        :param util: utility object
        :param listeners: screen event listeners
        :param voice_assistant: the voice assistant
        :param volume_control: volume control
        """
        self.util = util
        RadioBrowserScreen.__init__(self, util, listeners, voice_assistant, volume_control)

    def get_page(self):
        """ Get the current page from the playlist

        :return: the page
        """
        playlist = self.util.get_stream_playlist()
        playlist_length = len(playlist)
        self.total_pages = math.ceil(playlist_length / self.page_size)
        
        if self.total_pages == 0:
            self.left_button.change_label("0")
            self.right_button.change_label("0")
            self.set_title()
            return []
        
        if self.current_page == None:
            self.current_page = self.get_page_by_index()

        self.set_title()

        start = (self.current_page - 1) * self.page_size
        end = self.current_page * self.page_size
        return playlist[start : end]

    def get_page_by_index(self):
        """ Get the page by index

        :return: the page
        """
        page = None
        index = self.config[CURRENT][STREAM]
        if index < self.page_size:
            page = 1
        else:
            page = math.ceil(index / self.page_size)
        return page

    def turn_page(self):
        """ Turn page """
        
        page = self.get_page()
        d = self.stations_menu.make_dict(page)
        self.stations_menu.set_items(d, 0, self.change_stream, False)
        index = self.config[CURRENT][STREAM]
        menu_selected = self.stations_menu.select_by_index(index)

        if self.navigator and self.total_pages > 1:
            self.left_button.change_label(str(self.current_page - 1))
            self.right_button.change_label(str(self.total_pages - self.current_page))
        else:
            self.left_button.change_label("0")
            self.right_button.change_label("0")

        for b in self.stations_menu.buttons.values():
            b.parent_screen = self
            b.release_listeners.insert(0, self.handle_favorite)

        self.stations_menu.clean_draw_update()
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
        state.source = KEY_STREAM_BROWSER
        self.config[CURRENT][STREAM] = state.index
        state.name = state.l_name
        self.go_player(state)
        self.set_title()

    def handle_favorite(self, state):
        """ Ignore """
        pass
