# Copyright 2020 Peppy Player peppy.player@gmail.com
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
from ui.menu.collectiontrackmenu import CollectionTrackMenu, TRACK_ROWS, TRACK_COLUMNS, TRACKS_PER_PAGE, LABEL_HEIGHT_PERCENT
from util.keys import KEY_CHOOSE_TRACK, LABELS, KEY_PLAY_COLLECTION
from ui.page import Page
from ui.layout.gridlayout import GridLayout
from ui.state import State
from util.config import COLORS, COLOR_DARK, FILE_NOT_FOUND, COLLECTION, COLLECTION_PLAYBACK, COLLECTION_FOLDER, COLLECTION_FILE
from ui.menu.collectionbrowsernavigator import CollectionBrowserNavigator

class CollectionBrowserScreen(MenuScreen):
    """ Collection Browser screen """
    
    def __init__(self, util, listeners, voice_assistant):
        """ Initializer
        
        :param util: utility object
        :param listeners: screen listeners
        :param voice_assistant: voice assistant
        """ 
        self.util = util
        self.config = util.config
        MenuScreen.__init__(self, util, listeners, TRACK_ROWS, TRACK_COLUMNS, voice_assistant, [TRACK_ROWS, TRACK_COLUMNS], self.turn_page)
        
        self.track_menu = CollectionTrackMenu(util, self.next_page, self.previous_page, self.set_title, self.reset_title, self.go_to_page, 
            listeners[KEY_PLAY_COLLECTION], (0, 0, 0), self.menu_layout)
        self.set_menu(self.track_menu)
        self.current_playlist = []
        self.total_pages = 0
        self.current_folder = None  
        
        self.navigator = CollectionBrowserNavigator(util, self.layout.BOTTOM, listeners)
        self.navigator.left_button.change_label(str(0))
        self.navigator.right_button.change_label(str(self.total_pages))
        self.components.append(self.navigator)
        self.animated_title = True
    
    def set_current(self, state):
        """ Set current screen
        
        :param state: button state object
        """
        folder = self.config[COLLECTION_PLAYBACK][COLLECTION_FOLDER]
        if self.current_folder != folder:
            self.current_folder = folder
        else:
            return

        self.current_playlist = self.util.get_audio_files_in_folder(self.current_folder, False)

        if not self.current_folder or not self.current_playlist:
            self.screen_title.set_text(self.config[LABELS][FILE_NOT_FOUND])
            return
        
        index = 0
        for i, t in enumerate(self.current_playlist):
            if t.file_name == self.config[COLLECTION_PLAYBACK][COLLECTION_FILE]:
                index = i
                break

        self.total_pages = 0       
        self.track_menu.current_page_num = ""
        self.track_menu.selected_index = index
        
        page = Page(self.current_playlist, TRACK_ROWS, TRACK_COLUMNS)
        page.set_current_item(index)
        self.track_menu.current_page = self.current_page = page.current_page_index + 1
        
        self.turn_page()        
        
    def turn_page(self):
        """ Turn book tracks page """
        
        self.total_pages = math.ceil(len(self.current_playlist) / TRACKS_PER_PAGE)
        self.track_menu.set_tracks(self.current_playlist, self.current_page)
        
        left = self.current_page - 1
        right = self.total_pages - self.current_page
        
        if right < 0:
            right = 0
        
        self.navigator.left_button.change_label(str(left))
        self.navigator.right_button.change_label(str(right))
        self.screen_title.set_text(self.current_folder)

        index_on_page = self.track_menu.selected_index % TRACKS_PER_PAGE        
        self.track_menu.select_by_index(index_on_page)
        self.track_menu.clean_draw_update()

    def set_tracks(self, tracks, page):
        """ Set tracks in menu
        
        :param tracks: list of tracks
        :param page: page number
        """
        if tracks == None:
            return
        self.tracks = tracks
        items = {}
        start_index = TRACKS_PER_PAGE * (page - 1)
        end_index = start_index + TRACKS_PER_PAGE
        
        layout = GridLayout(self.menu_layout)
        layout.set_pixel_constraints(TRACK_ROWS, TRACK_COLUMNS, 1, 1)
        constr = layout.get_next_constraints()        
        fixed_height = int((constr.h * LABEL_HEIGHT_PERCENT)/100.0)
         
        for i, a in enumerate(self.tracks[start_index : end_index]):
            state = State()
            state.name = a["title"]
            state.l_name = state.name
            state.bgr = self.config[COLORS][COLOR_DARK]
            state.img_x = None
            state.img_y = None
            state.auto_update = True
            state.show_bgr = True
            state.show_img = False
            state.show_label = True
            state.comparator_item = state.name
            state.index = i
            state.fixed_height = fixed_height
            state.file_name = a["file_name"]
            items[state.name] = state
        self.track_menu.set_items(items, 0, self.site_select_track, False)

    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        self.navigator.add_observers(update_observer, redraw_observer)
        self.track_menu.add_menu_observers(update_observer, redraw_observer, release=False)
