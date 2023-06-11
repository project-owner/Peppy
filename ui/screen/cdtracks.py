# Copyright 2016-2023 Peppy Player peppy.player@gmail.com
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

import pygame

from ui.page import Page
from ui.container import Container
from ui.layout.borderlayout import BorderLayout
from ui.factory import Factory
from ui.screen.screen import Screen
from util.keys import GO_LEFT_PAGE, GO_RIGHT_PAGE, KEY_EJECT, KEY_PLAYER, KEY_REFRESH, KEY_PAGE_DOWN, \
    KEY_PAGE_UP, KEY_HOME, KEY_BACK
from util.config import CD_PLAYBACK, CD_DRIVE_ID, CD_TRACK_TIME, CD_DRIVE_NAME, LIST_VIEW_ROWS, \
    LIST_VIEW_COLUMNS, ALIGN_BUTTON_CONTENT_X, IMAGE_AREA, IMAGE_SIZE, PADDING
from util.fileutil import FILE_AUDIO
from ui.navigator.cdtracks import CdTracksNavigator
from ui.menu.filemenu import FileMenu
from ui.menu.menu import ALIGN_LEFT
from ui.state import State
from util.cdutil import CdUtil
from ui.layout.gridlayout import GridLayout
from ui.layout.buttonlayout import TOP

# 480x320
PERCENT_TOP_HEIGHT = 14.0
PERCENT_BOTTOM_HEIGHT = 14.0625

class CdTracksScreen(Screen):
    """ File Browser Screen """
    
    def __init__(self, util, listeners, state):
        """ Initializer
        
        :param util: utility object
        :param listeners: file browser listeners
        """
        self.util = util
        self.config = util.config
        self.cdutil = CdUtil(util)
        self.factory = Factory(util)
        self.bounding_box = util.screen_rect
        self.layout = BorderLayout(self.bounding_box)
        self.layout.set_percent_constraints(PERCENT_TOP_HEIGHT, PERCENT_BOTTOM_HEIGHT, 0, 0)
        Screen.__init__(self, util, "", PERCENT_TOP_HEIGHT, "cd_tracks_screen_title", True, self.layout.TOP)
        self.current_cd_drive_name = self.config[CD_PLAYBACK][CD_DRIVE_NAME]
        self.current_cd_drive_id = self.config[CD_PLAYBACK][CD_DRIVE_ID]
        self.filelist = self.get_filelist()

        rows = self.config[LIST_VIEW_ROWS]
        columns = self.config[LIST_VIEW_COLUMNS]
        button_box = pygame.Rect(0, 0, self.layout.CENTER.w / columns, self.layout.CENTER.h / rows)
        if self.config[ALIGN_BUTTON_CONTENT_X] == 'center':
            location = TOP
        else:
            location = self.config[ALIGN_BUTTON_CONTENT_X]
        icon_box = self.factory.get_icon_bounding_box(button_box, location, self.config[IMAGE_AREA], self.config[IMAGE_SIZE], self.config[PADDING])
        icon_box_without_label = self.factory.get_icon_bounding_box(button_box, location, 100, 100, self.config[PADDING], False)
        
        self.file_menu = FileMenu(self.filelist, util, None, self.layout.CENTER, location, icon_box, icon_box_without_label)

        self.go_cd_player = listeners[KEY_PLAYER]
        self.file_menu.add_play_file_listener(self.play_track)       
        self.add_menu(self.file_menu)
         
        listeners[GO_LEFT_PAGE] = self.file_menu.page_down
        listeners[GO_RIGHT_PAGE] = self.file_menu.page_up
        listeners[KEY_EJECT] = self.eject_cd
        listeners[KEY_REFRESH] = self.refresh_tracks
        connected_cd_drives = self.cdutil.get_cd_drives_number()
        self.navigator = CdTracksNavigator(util, self.layout.BOTTOM, listeners, connected_cd_drives)
        self.add_navigator(self.navigator)

        self.file_menu.add_left_number_listener(self.navigator.get_button_by_name(KEY_PAGE_DOWN).change_label)
        self.file_menu.add_right_number_listener(self.navigator.get_button_by_name(KEY_PAGE_UP).change_label)
        self.file_menu.update_buttons()        
        self.page_turned = False
        self.animated_title = True
        
    def play_track(self, state):
        """ Set config and go to player
        
        :param state: state object with track info
        """
        self.config[CD_PLAYBACK][CD_DRIVE_ID] = self.current_cd_drive_id
        self.config[CD_PLAYBACK][CD_DRIVE_NAME] = self.current_cd_drive_name
        self.config[CD_PLAYBACK][CD_TRACK_TIME] = "0"
        
        if self.current_cd_drive_name != self.screen_title.text:
            state.album = self.screen_title.text
        
        self.go_cd_player(state)
    
    def get_filelist(self):
        """ Return CD tracks
        
        :return: page with CD tracks
        """
        rows = 5
        columns = 2
        
        layout = GridLayout(self.layout.CENTER)
        layout.set_pixel_constraints(rows, columns, 1, 1)
        constr = layout.get_next_constraints()        
        fixed_height = int((constr.h * 35)/100.0)
        
        tracks = self.cdutil.get_cd_tracks(rows, columns, fixed_height, self.current_cd_drive_name)
        if tracks == None: 
            tracks = []
        return Page(tracks, rows, columns)
    
    def set_current(self, state):
        """ Set current CD drive
        
        :param state: state object with drive info
        """
        if state.name == KEY_BACK:
            return

        if not self.current_cd_drive_name or (getattr(state, "name", None) and self.current_cd_drive_name != state.name):
            change_menu = False
            if not self.current_cd_drive_name:
                self.current_cd_drive_name = self.cdutil.get_default_cd_drive()[1]
                change_menu = True
            elif state.name != "cd":
                self.current_cd_drive_name = state.name
                change_menu = True
            
            name = self.current_cd_drive_name
            tracks = len(self.file_menu.filelist.items)
            empty = self.cdutil.is_drive_empty(name)
            if name and empty != 1 and tracks == 0:
                change_menu = True
                
            if change_menu:
                id = self.cdutil.get_cd_drive_id_by_name(self.current_cd_drive_name)
                self.current_cd_drive_id = id
                self.file_menu.selected_index = 0
                self.set_file_menu()

            if self.file_menu.get_selected_item() == None:
                if not self.navigator.is_selected():
                    self.navigator.get_button_by_name(KEY_HOME).set_selected(True)
            else:
                self.navigator.unselect()

            self.set_screen_title()

    def set_screen_title(self):  
        """ Set screen title """
          
        title = drive_name = self.current_cd_drive_name
        try:
            title = self.util.cd_titles[drive_name]
            if "/" in title:
                title = title.replace("/", "-")
            if "[" in title:
                i = title.find("[")
                title = title[0:i]
            if "," in title:
                i = title.find(",")
                title = title[0:i]
        except:
            pass
        self.screen_title.set_text(title)
    
    def eject_cd(self, state):
        """ Eject CD
        
        :param state: state object with drive info
        """
        if len(str(self.current_cd_drive_id)) == 0:
            return
        
        del self.util.cd_track_names_cache[self.current_cd_drive_id]
        if state == None or getattr(state, "no_physical_eject", None) == None:
            self.cdutil.eject_cd(int(self.current_cd_drive_id))
        self.util.cd_titles[self.current_cd_drive_name] = self.current_cd_drive_name
        self.file_menu.selected_index = 0
        self.set_file_menu()
        self.set_screen_title()

    def refresh_tracks(self, state):
        """ Refresh tracks menu
        
        :param state: not used
        """
        name = self.current_cd_drive_name
        if name and self.cdutil.is_drive_empty(name):
            s = State()
            s.no_physical_eject = True
            self.eject_cd(s)
        
        self.set_file_menu()  
        self.set_screen_title()       
    
    def set_file_menu(self):
        """ Set file menu """
        
        filelist = self.get_filelist()
        self.file_menu.filelist = filelist
        self.file_menu.update_buttons()
        page = filelist.get_current_page()
        self.file_menu.set_page(filelist.current_item_index_in_page, page)

        for b in self.file_menu.buttons.values():
            b.parent_screen = self

        self.link_borders()
        
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
    
    def handle_event(self, event):
        """ Handle screen event

        :param event: the event to handle
        """
        if not self.visible or event.type == pygame.MOUSEMOTION:
            return

        mouse_events = [pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN]

        if event.type in mouse_events:
            clicked_menu_item = self.file_menu.get_clicked_menu_button(event.pos[0], event.pos[1])
            navigator_selected = False
            if not self.navigator.is_empty():
                if clicked_menu_item != None:
                    self.navigator.unselect()
                else:
                    for b in self.navigator.components:
                        if b.bounding_box.collidepoint(event.pos):
                            navigator_selected = True
                        else:
                            b.set_selected(False)
                            b.clean_draw_update()
            if navigator_selected:
                self.file_menu.unselect()

        Container.handle_event(self, event)
        self.link_borders()
        self.redraw_observer()

    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        self.redraw_observer= redraw_observer

        Screen.add_screen_observers(self, update_observer, redraw_observer)        
        self.file_menu.add_menu_observers(update_observer, redraw_observer=None, release=False)        
        self.file_menu.add_change_folder_listener(redraw_observer)
        self.file_menu.add_menu_navigation_listeners(redraw_observer)
        
        self.file_menu.add_left_number_listener(redraw_observer)
        self.file_menu.add_right_number_listener(redraw_observer) 
                       
        self.navigator.add_observers(update_observer, redraw_observer)
