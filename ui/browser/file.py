# Copyright 2016-2024 Peppy Player peppy.player@gmail.com
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
from util.keys import *
from util.config import *
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

LEFT = "left"
ASCENDING = "ascending"
DESCENDING = "descending"
LIST_VIEW = "list.view"
ICON_VIEW = "icon.view"
ELLIPSIS = "ellipsis"
VERTICAL_LAYOUT = "vertical.layout"
SHOW_FOLDER_NAME = "show.folder.name"
DISABLE_FOLDER_IMAGES = "disable.folder.images"
POPUP_ITEMS = [
    ASCENDING,
    DESCENDING,
    "",
    LIST_VIEW,
    ICON_VIEW,
    "",
    SHOW_FOLDER_NAME,
    HIDE_FOLDER_NAME,
    "",
    DISABLE_FOLDER_IMAGES,
    ENABLE_FOLDER_IMAGES,
    "",
    ELLIPSIS,
    WRAP_LABELS,
    "",
    HORIZONTAL_LAYOUT,
    VERTICAL_LAYOUT,
    ""
]

class FileBrowserScreen(Screen):
    """ File Browser Screen """
    
    def __init__(self, util, get_current_playlist, playlist_provider, listeners):
        """ Initializer
        
        :param util: utility object
        :param get_current_playlist: function to get current playlist
        :param playlist_provider: playlist provider
        :param listeners: file browser listeners
        """
        self.util = util
        self.config = util.config
        self.factory = Factory(util)
        self.bounding_box = util.screen_rect

        layout = BorderLayout(self.bounding_box)
        layout.set_percent_constraints(PERCENT_TOP_HEIGHT, PERCENT_BOTTOM_HEIGHT, 0, 0)
        Screen.__init__(self, util, "", PERCENT_TOP_HEIGHT, "file_browser_screen_title", True, layout.TOP)
        current_folder = self.util.file_util.current_folder  
        d = {"current_title" : current_folder}
        
        if self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] == FILE_PLAYLIST:
            f = self.config[FILE_PLAYBACK][CURRENT_FOLDER]
            p = self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYLIST]
            d = f + os.sep + p
        
        self.screen_title.set_text(d)
        
        rows = self.config[LIST_VIEW_ROWS]
        columns = self.config[LIST_VIEW_COLUMNS]
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
            s.music_folder = self.config[MUSIC_FOLDER]
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
        listeners[GO_PLAYLISTS] = self.file_menu.switch_to_playlists
        listeners[GO_USER_HOME] = self.file_menu.switch_to_user_home
        listeners[GO_ROOT] = self.file_menu.switch_to_root
        listeners[GO_TO_PARENT] = self.file_menu.switch_to_parent_folder
        listeners[KEY_LIST] = self.show_popup
        
        self.navigator = FileNavigator(util, layout.BOTTOM, listeners)
        self.update_navigator()
        self.add_navigator(self.navigator)
        self.page_turned = False
        self.animated_title = True

        self.file_menu.navigator = self.navigator
        self.add_menu(self.file_menu)
        self.link_borders()
        self.back_button.set_selected(True)

        self.sort_popup = self.get_popup()
        self.add_component(self.sort_popup)

        if self.filelist and hasattr(self.filelist, "current_item_index_in_page"):
            self.file_menu.select_menu_item(self.filelist.current_item_index_in_page)

    def update_navigator(self):
        """ Update Navigator """

        left = str(self.file_menu.filelist.get_left_items_number())
        right = str(self.file_menu.filelist.get_right_items_number())
        left_button = self.navigator.get_button_by_name(KEY_PAGE_DOWN)
        right_button = self.navigator.get_button_by_name(KEY_PAGE_UP)
        self.back_button = self.navigator.get_button_by_name(KEY_PLAYER)
        left_button.change_label(left)
        right_button.change_label(right)
        self.file_menu.add_left_number_listener(left_button.change_label)
        self.file_menu.add_right_number_listener(right_button.change_label)

    def get_location(self):
        """ Button content location

        :return: the location
        """
        if self.config[ALIGN_BUTTON_CONTENT_X] == CENTER:
            location = TOP
        else:
            location = self.config[ALIGN_BUTTON_CONTENT_X]
        return location

    def get_boxes(self):
        """ Get icon bounding boxes

        :return: tuple with icon boxes w/ and w/o label
        """
        if self.config[ALIGN_BUTTON_CONTENT_X] == CENTER:
            rows = self.config[ICON_VIEW_ROWS]
            cols = self.config[ICON_VIEW_COLUMNS]
        else:
            rows = self.config[LIST_VIEW_ROWS]
            cols = self.config[LIST_VIEW_COLUMNS]

        button_box = pygame.Rect(0, 0, self.menu_bb.w / cols, self.menu_bb.h / rows)
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

    def get_view_type(self):
        """ Get view type

        :return: ICON_VIEW or LIST_VIEW
        """
        if self.config[ALIGN_BUTTON_CONTENT_X] == CENTER:
            return ICON_VIEW
        else:
            return LIST_VIEW

    def get_popup_items(self):
        """ Get popup items depending on resolution and view type

        :param return: list of popup items
        """
        screen_width = self.config[SCREEN_INFO][WIDTH]
        view_type = self.get_view_type()

        if screen_width <= 320: # small 320x240
            if view_type == LIST_VIEW:
                layout = ["1x4", "2x4", "1x5", "2x5", "1x6", "2x6"]
            else:
                layout = ["2x1", "3x1", "4x1", "4x2", "5x2", "6x3"]
        elif 800 >= screen_width > 480: # large 800x480
            if view_type == LIST_VIEW:
                layout = ["1x5", "2x5", "1x6", "2x6", "1x7", "2x7"]
            else:
                layout = ["3x1", "5x2", "6x2", "7x3", "8x3", "9x4"]
        elif 1280 >= screen_width > 800: # wide 1280x400
            if view_type == LIST_VIEW:
                layout = ["2x5", "3x5", "2x6", "3x6", "2x7", "3x7"]
            else:
                layout = ["5x1", "6x1", "10x2", "11x2", "14x3", "16x3"]
        else: # the rest e.g. 480x320
            if view_type == LIST_VIEW:
                layout = ["1x5", "2x5", "1x6", "2x6", "1x7", "2x7"]
            else:
                layout = ["2x1", "3x1", "5x2", "6x2", "6x3", "7x3"]

        for i, n in enumerate(layout):
            POPUP_ITEMS[2 + i * 3] = n

        return POPUP_ITEMS

    def get_popup(self):
        """ Get file browser popup

        :return: popup
        """
        layout = BorderLayout(self.bounding_box)
        layout.set_percent_constraints(PERCENT_TOP_HEIGHT, 0, 0, 0)
        layout_left = layout.CENTER
        popup = Popup(
            self.get_popup_items(),
            self.util,
            layout_left,
            self.update_screen,
            self.handle_popup_selection,
            bgr=self.config[COLORS][COLOR_DARK],
            default_selection=ASCENDING,
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
        self.update_component = True

    def handle_popup_selection(self, state):
        """ Handle playback order menu selection

        :param state: button state
        """
        if state.name == ASCENDING:
            self.config[ASCENDING] = True
        elif state.name == DESCENDING:
            self.config[ASCENDING] = False
        elif state.name == LIST_VIEW:
            self.set_list_view()
        elif state.name == ICON_VIEW:
            self.set_icon_view()
        elif state.name == SHOW_FOLDER_NAME:
            self.config[HIDE_FOLDER_NAME] = False
            self.update_popup_items()
        elif state.name == HIDE_FOLDER_NAME:
            self.config[HIDE_FOLDER_NAME] = True
            self.update_popup_items()
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
            self.set_rows_columns(state)

        self.file_menu.font_size = self.file_menu.get_font_size()
        icon_box, icon_box_without_label = self.get_boxes()
        self.file_menu.icon_box = icon_box
        self.file_menu.icon_box_without_label = icon_box_without_label

        self.file_menu.change_folder(self.file_menu.current_folder)
        self.sort_popup.set_visible(False)
        self.update_navigator()
        self.update_component = True

    def update_popup_items(self):
        """ Update popup items """

        popup_items = self.get_popup_items()
        for i, n in enumerate(self.sort_popup.menu.components):
            if n.state.name[0].isdigit():
                n.components[2].text = n.state.name = n.state.l_name = n.state.l_genre = n.state.genre = n.state.comparator_item = popup_items[i]
                n.set_label()
        self.update_component = True

    def set_list_view(self):
        """ Set List View """

        self.config[ALIGN_BUTTON_CONTENT_X] = LEFT
        self.config[FONT_HEIGHT_PERCENT] = 38
        self.config[IMAGE_AREA] = 18
        self.config[ENABLE_FOLDER_IMAGES] = self.config[ENABLE_EMBEDDED_IMAGES] = self.config[ENABLE_IMAGE_FILE_ICON] = False
        self.file_menu.cols = self.config[LIST_VIEW_COLUMNS]
        self.file_menu.rows = self.config[LIST_VIEW_ROWS]
        self.update_popup_items()

    def set_icon_view(self):
        """ Set Icon View """

        self.config[ALIGN_BUTTON_CONTENT_X] = CENTER
        self.config[FONT_HEIGHT_PERCENT] = 60
        self.config[IMAGE_AREA] = 84
        self.config[ENABLE_FOLDER_IMAGES] = self.config[ENABLE_EMBEDDED_IMAGES] = self.config[ENABLE_IMAGE_FILE_ICON] = True
        self.file_menu.cols = self.config[ICON_VIEW_COLUMNS]
        self.file_menu.rows = self.config[ICON_VIEW_ROWS]
        self.update_popup_items()

    def set_rows_columns(self, state):
        """ Set Rows/Columns

        :param state: button state which includes rows and columns
        """
        numbers = state.name.split("x")
        view_type = self.get_view_type()

        if view_type == LIST_VIEW:
            self.file_menu.cols = self.config[LIST_VIEW_COLUMNS] = int(numbers[0])
            self.file_menu.rows = self.config[LIST_VIEW_ROWS] = int(numbers[1])
        else:
            self.file_menu.cols = self.config[ICON_VIEW_COLUMNS] = int(numbers[0])
            self.file_menu.rows = self.config[ICON_VIEW_ROWS] = int(numbers[1])

        if self.file_menu.rows == 1:
            if not getattr(self, "was_increased", False):
                self.file_menu.bb.h += 1
                self.was_increased = True
        else:
            if getattr(self, "was_increased", False):
                self.file_menu.bb.h -= 1
                self.was_increased = False

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
        if event.type == pygame.MOUSEMOTION:
            return

        if self.sort_popup.visible:
            self.sort_popup.handle_event(event)
            self.update_component = True
            return

        if event.type == USER_EVENT_TYPE and event.sub_type == SUB_TYPE_KEYBOARD and (event.action == pygame.KEYUP or event.action == pygame.KEYDOWN):
            menu_selected = self.file_menu.get_selected_index()
            navigator_selected = self.navigator.is_selected()

            if event.keyboard_key in kbd_num_keys.keys() and navigator_selected and event.action == pygame.KEYUP:
                self.navigator.unselect()
                menu_selected = 0

            if menu_selected != None:
                self.file_menu.handle_event(event)
            elif navigator_selected:
                self.navigator.handle_event(event)
        else:
            Screen.handle_event(self, event)

    def update_screen(self):
        """ Update the screen """

        self.update_component = True
        self.update_web_observer()

    def refresh(self):
        """ Refresh current screen """

        if self.update_component or self.screen_title.update_component:
            if self.sort_popup.visible:
                self.sort_popup.clean()
                self.sort_popup.draw()
            else:
                self.clean()
                self.draw()

            self.update(self.bounding_box)
            self.update_component = False
            if self.screen_title.update_component:
                self.screen_title.update_component = False

        if self.screen_title.animate:
            a = self.screen_title.refresh()
            self.screen_title.draw()
            self.screen_title.update(a)    

        return None
