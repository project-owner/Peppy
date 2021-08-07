# Copyright 2016-2021 Peppy Player peppy.player@gmail.com
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

import os
import pygame

from ui.page import Page
from ui.layout.borderlayout import BorderLayout
from ui.factory import Factory
from ui.screen.menuscreen import Screen
from util.keys import GO_LEFT_PAGE, GO_RIGHT_PAGE, GO_ROOT, GO_USER_HOME, GO_TO_PARENT, KEY_IMAGE_VIEWER, KEY_PLAYER, \
    KEY_PLAY_FILE, KEY_PAGE_DOWN, KEY_PAGE_UP, USER_EVENT_TYPE, SUB_TYPE_KEYBOARD
from util.config import CURRENT_FOLDER, AUDIO, MUSIC_FOLDER, CURRENT_FILE_PLAYBACK_MODE, FILE_BROWSER_ROWS, \
    FILE_BROWSER_COLUMNS, CURRENT_FILE_PLAYLIST, FILE_PLAYBACK, ALIGN_BUTTON_CONTENT_X, \
    IMAGE_AREA, IMAGE_SIZE, PADDING
from util.fileutil import FILE_AUDIO, FILE_PLAYLIST, FILE_RECURSIVE
from ui.navigator.file import FileNavigator
from ui.menu.filemenu import FileMenu
from ui.state import State
from ui.layout.buttonlayout import TOP

# 480x320
PERCENT_TOP_HEIGHT = 14.0625
PERCENT_BOTTOM_HEIGHT = 16.50

class FileBrowserScreen(Screen):
    """ File Browser Screen """
    
    def __init__(self, util, get_current_playlist, playlist_provider, listeners, voice_assistant):
        """ Initializer
        
        :param util: utility object
        :param listeners: file browser listeners
        """
        self.util = util
        self.config = util.config
        self.factory = Factory(util)
        self.bounding_box = util.screen_rect
        layout = BorderLayout(self.bounding_box)
        layout.set_percent_constraints(PERCENT_TOP_HEIGHT, PERCENT_BOTTOM_HEIGHT, 0, 0)
        Screen.__init__(self, util, "", PERCENT_TOP_HEIGHT, voice_assistant, "file_browser_screen_title", True, layout.TOP)
        current_folder = self.util.file_util.current_folder  
        d = {"current_title" : current_folder}
        
        if self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] == FILE_PLAYLIST:
            f = self.config[FILE_PLAYBACK][CURRENT_FOLDER]
            p = self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYLIST]
            d = f + os.sep + p
        
        self.screen_title.set_text(d)
        
        rows = self.config[FILE_BROWSER_ROWS]
        columns = self.config[FILE_BROWSER_COLUMNS]
        self.filelist = None
        playback_mode = self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE]
        
        if not playback_mode:
            self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] = playback_mode = FILE_AUDIO
        
        button_box = pygame.Rect(0, 0, layout.CENTER.w / columns, layout.CENTER.h / rows)
        if self.config[ALIGN_BUTTON_CONTENT_X] == 'center':
            location = TOP
        else:
            location = self.config[ALIGN_BUTTON_CONTENT_X]
        icon_box = self.factory.get_icon_bounding_box(button_box, location, self.config[IMAGE_AREA], self.config[IMAGE_SIZE], self.config[PADDING])
        icon_box_without_label = self.factory.get_icon_bounding_box(button_box, location, 100, 100, self.config[PADDING], False)

        if playback_mode == FILE_AUDIO or playback_mode == FILE_RECURSIVE:
            folder_content = self.util.load_folder_content(current_folder, rows, columns)
            self.filelist = Page(folder_content, rows, columns)
        elif playback_mode == FILE_PLAYLIST:
            s = State()
            s.folder = self.config[FILE_PLAYBACK][CURRENT_FOLDER]
            s.music_folder = self.config[AUDIO][MUSIC_FOLDER]
            s.file_name = self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYLIST]
            
            pl = self.get_filelist_items(get_current_playlist)
            if len(pl) == 0:            
                pl = self.util.load_playlist(s, playlist_provider, rows, columns, (icon_box.w, icon_box.h))
            else:
                pl = self.util.load_playlist_content(pl, rows, columns, (icon_box.w, icon_box.h))
            self.filelist = Page(pl, rows, columns)
        
        self.file_menu = FileMenu(self.filelist, util, playlist_provider, layout.CENTER, location, icon_box, icon_box_without_label, listeners[KEY_IMAGE_VIEWER])
        self.file_menu.parent_screen = self
        self.file_menu.link_borders = self.link_borders

        self.file_menu.add_change_folder_listener(self.screen_title.set_text)
        self.file_menu.add_play_file_listener(listeners[KEY_PLAY_FILE])
        
        listeners[GO_LEFT_PAGE] = self.file_menu.page_down
        listeners[GO_RIGHT_PAGE] = self.file_menu.page_up
        listeners[GO_USER_HOME] = self.file_menu.switch_to_user_home
        listeners[GO_ROOT] = self.file_menu.switch_to_root
        listeners[GO_TO_PARENT] = self.file_menu.switch_to_parent_folder
        
        self.navigator = FileNavigator(util, layout.BOTTOM, listeners)
        left = str(self.filelist.get_left_items_number())
        right = str(self.filelist.get_right_items_number())
        left_button = self.navigator.get_button_by_name(KEY_PAGE_DOWN)
        right_button = self.navigator.get_button_by_name(KEY_PAGE_UP)
        self.back_button = self.navigator.get_button_by_name(KEY_PLAYER)
        left_button.change_label(left)
        right_button.change_label(right)
        
        self.file_menu.add_left_number_listener(left_button.change_label)
        self.file_menu.add_right_number_listener(right_button.change_label)
        self.add_navigator(self.navigator)
        self.page_turned = False
        self.animated_title = True

        self.file_menu.navigator = self.navigator
        self.add_menu(self.file_menu)
        self.link_borders()
        self.back_button.set_selected(True)

    def get_filelist_items(self, get_current_playlist):
        """ Call player for files in the playlist 
        
        :return: list of files from playlist
        """
        playlist = get_current_playlist()
        files = []
        if playlist:
            for n in range(len(playlist)):
                st = State()
                st.index = st.comparator_item = n
                st.file_type = FILE_AUDIO
                st.file_name = st.url = playlist[n]
                files.append(st)
        return files
    
    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        Screen.add_screen_observers(self, update_observer, redraw_observer)
        
        self.file_menu.add_menu_observers(update_observer, redraw_observer, release=False)        
        self.file_menu.add_change_folder_listener(redraw_observer)
        self.file_menu.add_menu_navigation_listeners(redraw_observer)
        
        self.file_menu.add_left_number_listener(redraw_observer)
        self.file_menu.add_right_number_listener(redraw_observer)       
        
        self.navigator.add_observers(update_observer, redraw_observer)

    def handle_event(self, event):
        """ Handle screen event

        :param event: the event to handle
        """
        if event.type == USER_EVENT_TYPE and event.sub_type == SUB_TYPE_KEYBOARD and (event.action == pygame.KEYUP or event.action == pygame.KEYDOWN):
            menu_selected = self.file_menu.get_selected_index()
            navigator_selected = self.navigator.is_selected()

            if menu_selected != None:
                self.file_menu.handle_event(event)
            elif navigator_selected:
                self.navigator.handle_event(event)
        else:
            Screen.handle_event(self, event)
