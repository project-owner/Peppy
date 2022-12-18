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

import os
import pygame

from ui.page import Page
from ui.layout.borderlayout import BorderLayout
from ui.factory import Factory
from ui.screen.menuscreen import Screen
from util.keys import GO_LEFT_PAGE, GO_RIGHT_PAGE, GO_ROOT, GO_USER_HOME, GO_TO_PARENT, KEY_IMAGE_VIEWER, KEY_PLAYER, \
    KEY_PLAY_FILE, KEY_PAGE_DOWN, KEY_PAGE_UP, USER_EVENT_TYPE, SUB_TYPE_KEYBOARD, KEY_LIST, V_ALIGN_CENTER, \
    H_ALIGN_CENTER
from util.config import CURRENT_FOLDER, AUDIO, MUSIC_FOLDER, CURRENT_FILE_PLAYBACK_MODE, FILE_BROWSER_ROWS, \
    FILE_BROWSER_COLUMNS, CURRENT_FILE_PLAYLIST, FILE_PLAYBACK, ALIGN_BUTTON_CONTENT_X, IMAGE_AREA, IMAGE_SIZE, PADDING, \
    COLORS, COLOR_DARK, SORT_BY_TYPE, ASCENDING, WRAP_LABELS, HORIZONTAL_LAYOUT, HIDE_FOLDER_NAME, ENABLE_FOLDER_IMAGES, \
    SHOW_EMBEDDED_IMAGES, ENABLE_EMBEDDED_IMAGES, ENABLE_IMAGE_FILE_ICON
from util.fileutil import FILE_AUDIO, FILE_PLAYLIST, FILE_RECURSIVE
from ui.navigator.file import FileNavigator
from ui.menu.filemenu import FileMenu
from ui.state import State
from ui.layout.buttonlayout import TOP
from ui.menu.popup import Popup
from ui.menu.menu import ALIGN_CENTER

# 480x320
PERCENT_TOP_HEIGHT = 14.0625
PERCENT_BOTTOM_HEIGHT = 16.50
POPUP_TEXT_HEIGHT = 30

SORT_BY_NAME = "sort.by.name"
ASCENDING = "ascending"
DESCENDING = "descending"
LIST_VIEW = "list.view"
ICON_VIEW = "icon.view"
ELLIPSIS = "ellipsis"
VERTICAL_LAYOUT = "vertical.layout"
DISABLE_FOLDER_IMAGES = "disable.folder.images"
LAYOUT_1 = "1x5"
LAYOUT_2 = "2x5"
LAYOUT_3 = "3x5"
LAYOUT_4 = "4x5"
LAYOUT_5 = "5x2"
LAYOUT_6 = "10x2"
POPUP_ITEMS = [
    SORT_BY_TYPE,
    SORT_BY_NAME,
    LAYOUT_1,
    ASCENDING,
    DESCENDING,
    LAYOUT_2,
    LIST_VIEW,
    ICON_VIEW,
    LAYOUT_3,
    DISABLE_FOLDER_IMAGES,
    ENABLE_FOLDER_IMAGES,
    LAYOUT_4,
    ELLIPSIS,
    WRAP_LABELS,
    LAYOUT_5,
    HORIZONTAL_LAYOUT,
    VERTICAL_LAYOUT,
    LAYOUT_6
]

class FileBrowserScreen(Screen):
    """ File Browser Screen """
    
    def __init__(self, util, get_current_playlist, playlist_provider, listeners, voice_assistant):
        """ Initializer
        
        :param util: utility object
        :param get_current_playlist: function to get current playlist
        :param playlist_provider: playlist provider
        :param listeners: file browser listeners
        :param voice_assistant: voice assistant
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

        self.menu_bb = layout.CENTER
        
        icon_box, icon_box_without_label = self.get_boxes()

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
        
        location = self.get_location()
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
        listeners[KEY_LIST] = self.show_popup
        
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

        self.sort_popup = self.get_popup()
        self.add_component(self.sort_popup)

    def get_location(self):
        """ Button content location

        :return: the location
        """
        if self.config[ALIGN_BUTTON_CONTENT_X] == 'center':
            location = TOP
        else:
            location = self.config[ALIGN_BUTTON_CONTENT_X]
        return location

    def get_boxes(self):
        """ Get icon bounding boxes

        :return: tuple with icon boxes w/ and w/o label
        """
        button_box = pygame.Rect(0, 0, self.menu_bb.w / self.config[FILE_BROWSER_COLUMNS], self.menu_bb.h / self.config[FILE_BROWSER_ROWS])
        location = self.get_location()
        icon_box = self.factory.get_icon_bounding_box(button_box, location, self.config[IMAGE_AREA], self.config[IMAGE_SIZE], self.config[PADDING])
        icon_box_without_label = self.factory.get_icon_bounding_box(button_box, location, 100, 100, self.config[PADDING], False)

        return (icon_box, icon_box_without_label)

    def get_filelist_items(self, get_current_playlist):
        """ Call player for files in the playlist 
        
        :param get_current_playlist: function to get the current playlist
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

    def get_popup(self):
        """ Get file browser popup

        :return: popup
        """
        layout = BorderLayout(self.bounding_box)
        layout.set_percent_constraints(PERCENT_TOP_HEIGHT, 0, 0, 0)
        layout_left = layout.CENTER
        popup = Popup(
            POPUP_ITEMS,
            self.util,
            layout_left,
            self.update_screen,
            self.handle_popup_selection,
            bgr=self.config[COLORS][COLOR_DARK],
            default_selection=SORT_BY_TYPE,
            align=ALIGN_CENTER,
            h_align=H_ALIGN_CENTER,
            v_align=V_ALIGN_CENTER,
            show_image=False,
            show_label=True,
            label_text_height=POPUP_TEXT_HEIGHT,
            popup_selector=self.handle_popup_selection,
            columns=3,
            wrap_lines=True,
            column_weights=[40, 40, 20]
        )
        return popup

    def show_popup(self, state):
        """ Show popup """

        self.sort_popup.set_visible(True)
        self.clean_draw_update()

    def handle_popup_selection(self, state):
        """ Handle playback order menu selection

        :param state: button state
        """
        if state.name == SORT_BY_NAME:
            self.config[SORT_BY_TYPE] = False
        elif state.name == SORT_BY_TYPE:
            self.config[SORT_BY_TYPE] = True
        elif state.name == ASCENDING:
            self.config[ASCENDING] = True
        elif state.name == DESCENDING:
            self.config[ASCENDING] = False
        elif state.name == LIST_VIEW:
            self.config[HIDE_FOLDER_NAME] = self.config[ENABLE_FOLDER_IMAGES] = self.config[SHOW_EMBEDDED_IMAGES] = self.config[ENABLE_EMBEDDED_IMAGES] = self.config[ENABLE_IMAGE_FILE_ICON] = False
        elif state.name == ICON_VIEW:
            self.config[HIDE_FOLDER_NAME] = self.config[ENABLE_FOLDER_IMAGES] = self.config[SHOW_EMBEDDED_IMAGES] = self.config[ENABLE_EMBEDDED_IMAGES] = self.config[ENABLE_IMAGE_FILE_ICON] = True
        elif state.name == ENABLE_FOLDER_IMAGES:
            self.config[ENABLE_FOLDER_IMAGES] = True
        elif state.name == DISABLE_FOLDER_IMAGES:
            self.config[ENABLE_FOLDER_IMAGES] = False
        elif state.name == WRAP_LABELS:
            self.config[WRAP_LABELS] = True
        elif state.name == ELLIPSIS:
            self.config[WRAP_LABELS] = False
        elif state.name == HORIZONTAL_LAYOUT:
            self.config[HORIZONTAL_LAYOUT] = self.file_menu.horizontal_layout = True
        elif state.name == VERTICAL_LAYOUT:
            self.config[HORIZONTAL_LAYOUT] = self.file_menu.horizontal_layout = False
        else:
            numbers = state.name.split("x")
            self.file_menu.cols = self.config[FILE_BROWSER_COLUMNS] = int(numbers[0])
            self.file_menu.rows = self.config[FILE_BROWSER_ROWS] = int(numbers[1])

        icon_box, icon_box_without_label = self.get_boxes()
        self.file_menu.icon_box = icon_box
        self.file_menu.icon_box_without_label = icon_box_without_label

        self.file_menu.change_folder(self.file_menu.current_folder)
        self.sort_popup.set_visible(False)
        self.clean_draw_update()

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

        self.sort_popup.add_menu_observers(update_observer, redraw_observer)

    def handle_event(self, event):
        """ Handle screen event

        :param event: the event to handle
        """
        if self.sort_popup.visible:
            self.sort_popup.handle_event(event)
            return

        if event.type == USER_EVENT_TYPE and event.sub_type == SUB_TYPE_KEYBOARD and (event.action == pygame.KEYUP or event.action == pygame.KEYDOWN):
            menu_selected = self.file_menu.get_selected_index()
            navigator_selected = self.navigator.is_selected()

            if menu_selected != None:
                self.file_menu.handle_event(event)
            elif navigator_selected:
                self.navigator.handle_event(event)
        else:
            Screen.handle_event(self, event)

    def update_screen(self):
        """ Update the screen """

        self.clean_draw_update()
        self.update_web_observer()
