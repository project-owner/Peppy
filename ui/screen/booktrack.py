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
from ui.menu.booktrackmenu import BookTrackMenu, TRACK_ROWS, TRACK_COLUMNS
from util.keys import KEY_CHOOSE_TRACK, LABELS

PAGE_SIZE = TRACK_ROWS * TRACK_COLUMNS

class BookTrack(MenuScreen):
    """ Book tracks screen """
    
    def __init__(self, util, listeners, site_select_track, d):
        """ Initializer
        
        :param util: utility object
        :param listeners: screen listeners
        :param site_select_track: callback
        :param d: dictionary with menu button flags 
        """ 
        self.util = util
        MenuScreen.__init__(self, util, listeners, TRACK_ROWS, TRACK_COLUMNS, d, self.turn_page)
        self.title = self.config[LABELS][KEY_CHOOSE_TRACK]
        self.screen_title.set_text(self.title)        
        self.track_menu = BookTrackMenu(util, self.next_page, self.previous_page, self.set_title, self.reset_title, self.go_to_page, site_select_track, (0, 0, 0), self.menu_layout)
        self.set_menu(self.track_menu)
        self.current_playlist = []
        self.total_pages = math.ceil(len(self.current_playlist) / PAGE_SIZE)
        self.track_menu.set_tracks(self.current_playlist, self.current_page)        
        self.navigator.left_button.change_label(str(0))
        self.navigator.right_button.change_label(str(self.total_pages))
    
    def set_current(self, state):
        """ Set current screen
        
        :param state: button state object
        """ 
        if self.current_playlist == state.playlist:
            return
        
        self.total_pages = 0       
        self.track_menu.current_page = self.current_page = 1
        self.track_menu.current_page_num = ""
        self.track_menu.selected_index = 0
        
        self.current_playlist = state.playlist
        self.turn_page()        
        
    def turn_page(self):
        """ Turn book tracks page """
        
        self.total_pages = math.ceil(len(self.current_playlist) / PAGE_SIZE)
        self.track_menu.set_tracks(self.current_playlist, self.current_page)        
        self.track_menu.clean_draw_update()
        
        left = self.current_page - 1
        right = self.total_pages - self.current_page
        
        if right < 0:
            right = 0
        
        self.navigator.left_button.change_label(str(left))
        self.navigator.right_button.change_label(str(right))
        self.set_title(self.current_page)
        self.track_menu.select_by_index(self.track_menu.selected_index)
        
