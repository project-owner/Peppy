# Copyright 2016-2020 Peppy Player peppy.player@gmail.com
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

from ui.screen.menuscreen import MenuScreen
from ui.menu.booknavigator import BookNavigator
from ui.menu.booktrackmenu import BookTrackMenu, TRACK_ROWS, TRACK_COLUMNS
from util.keys import KEY_CHOOSE_TRACK, LABELS
from ui.page import Page

PAGE_SIZE = TRACK_ROWS * TRACK_COLUMNS

class BookTrack(MenuScreen):
    """ Book tracks screen """
    
    def __init__(self, util, listeners, site_select_track, voice_assistant, d):
        """ Initializer
        
        :param util: utility object
        :param listeners: screen listeners
        :param site_select_track: callback
        :param d: dictionary with menu button flags 
        """ 
        self.util = util
        MenuScreen.__init__(self, util, listeners, TRACK_ROWS, TRACK_COLUMNS, voice_assistant, d, self.turn_page)
        self.title = self.config[LABELS][KEY_CHOOSE_TRACK]
        self.screen_title.set_text(self.title)
        self.site_select_track = site_select_track
        
        self.track_menu = BookTrackMenu(util, self.next_page, self.previous_page, self.set_title, self.reset_title, self.go_to_page, site_select_track, None, self.menu_layout)
        self.set_menu(self.track_menu)
        self.current_playlist = []
        self.total_pages = math.ceil(len(self.current_playlist) / PAGE_SIZE)        
        
        self.navigator = BookNavigator(util, self.layout.BOTTOM, listeners, d[4])
        self.add_component(self.navigator)
        self.navigator.left_button.change_label(str(0))
        self.navigator.right_button.change_label(str(self.total_pages))
        
    def set_current(self, state):
        """ Set current screen
        
        :param state: button state object
        """ 
        if self.current_playlist == state.playlist:
            return
        
        self.total_pages = 0       
        self.track_menu.current_page_num = ""
        self.track_menu.selected_index = state.current_track_index
        
        self.current_playlist = state.playlist
        
        page = Page(self.current_playlist, TRACK_ROWS, TRACK_COLUMNS)
        page.set_current_item(state.current_track_index)
        self.track_menu.current_page = self.current_page = page.current_page_index + 1
        
        self.turn_page()        
        
    def turn_page(self):
        """ Turn book tracks page """
        
        self.total_pages = math.ceil(len(self.current_playlist) / PAGE_SIZE)
        self.track_menu.set_tracks(self.current_playlist, self.current_page)
        
        left = self.current_page - 1
        right = self.total_pages - self.current_page
        
        if right < 0:
            right = 0
        
        self.navigator.left_button.change_label(str(left))
        self.navigator.right_button.change_label(str(right))
        self.set_title(self.current_page)
        
        for b in self.track_menu.buttons.values():
            b.parent_screen = self

        index_on_page = self.track_menu.selected_index % PAGE_SIZE        
        self.track_menu.select_by_index(index_on_page)
        self.track_menu.clean_draw_update()
        
    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        self.navigator.add_observers(update_observer, redraw_observer)
        self.track_menu.add_menu_observers(update_observer, redraw_observer, release=False)
