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

from ui.state import State
from ui.page import Page
from ui.factory import Factory
from ui.menu.menu import Menu, ALIGN_CENTER
from util.keys import H_ALIGN_LEFT, H_ALIGN_RIGHT, H_ALIGN_CENTER, KEY_HOME
from util.fileutil import FOLDER, FOLDER_WITH_ICON, FILE_PLAYLIST, FILE_AUDIO, FILE_RECURSIVE, FILE_IMAGE
from util.config import CURRENT_FOLDER, CURRENT_FILE, CURRENT_TRACK_TIME, AUDIO, MUSIC_FOLDER, \
    CURRENT_FILE_PLAYBACK_MODE, CURRENT_FILE_PLAYLIST, CLIENT_NAME, VLC, FILE_PLAYBACK, \
    CURRENT, MODE, CD_PLAYER, CD_PLAYBACK, CD_DRIVE_NAME, CD_TRACK, MPV, BACKGROUND, MENU_BGR_COLOR, \
    HORIZONTAL_LAYOUT, FONT_HEIGHT_PERCENT, WRAP_LABELS, IMAGE_AREA, PADDING, ALIGN_BUTTON_CONTENT_X, \
    FILE_BROWSER_COLUMNS, FILE_BROWSER_ROWS
from util.cdutil import CdUtil
from ui.layout.buttonlayout import CENTER, LEFT, RIGHT, TOP, BOTTOM

class FileMenu(Menu):
    """ File Menu class. Extends base Menu class """
    
    def __init__(self, filelist, util, playlist_provider, bounding_box=None, align=ALIGN_CENTER, icon_box=None, icon_box_without_label=None, go_image_viewer=None):
        """ Initializer
        
        :param filelist: file list
        :param util: utility object
        :param bgr: menu background
        :param bounding_box: bounding box
        """
        self.factory = Factory(util)
        self.util = util
        self.cdutil = CdUtil(self.util)
        self.playlist_provider = playlist_provider
        self.config = self.util.config
        self.filelist = filelist
        self.icon_box = icon_box
        self.icon_box_without_label = icon_box_without_label
        self.go_image_viewer = go_image_viewer

        m = self.create_file_menu_button
        self.bounding_box = bounding_box
        bgr = util.config[BACKGROUND][MENU_BGR_COLOR]
        
        r = c = 3
        if filelist:
            r = filelist.rows
            c = filelist.columns

        h = self.config[HORIZONTAL_LAYOUT]
        button_height = (self.bounding_box.h / r) - (self.config[PADDING] * 2)

        if self.config[ALIGN_BUTTON_CONTENT_X] == 'center':
            font_size = int(((100 - self.config[IMAGE_AREA]) / 100) * self.config[FONT_HEIGHT_PERCENT])
        else:
            font_size = int((button_height / 100) * self.config[FONT_HEIGHT_PERCENT])

        Menu.__init__(self, util, bgr, self.bounding_box, r, c, create_item_method=m, align=align, horizontal_layout=h, font_size=font_size)

        self.browsing_history = {}        
        self.left_number_listeners = []
        self.right_number_listeners = []
        self.change_folder_listeners = []
        self.play_file_listeners = []
        self.playlist_size_listeners = []
        self.menu_navigation_listeners = []
        self.page_turned = False
        self.separator = os.sep
        self.empty_state = State()
        url = selection = None
        self.current_folder = self.config[FILE_PLAYBACK][CURRENT_FOLDER]
        folder = self.current_folder

        playback_mode = self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE]
        if playback_mode == FILE_AUDIO or playback_mode == FILE_RECURSIVE:
            if not self.current_folder.endswith(os.sep):
                self.current_folder += os.sep                
                        
            if self.config[CURRENT][MODE] == CD_PLAYER:
                cd_drive_name = self.config[CD_PLAYBACK][CD_DRIVE_NAME]
                track = self.config[CD_PLAYBACK][CD_TRACK]
                url = self.cdutil.get_cd_track_url(cd_drive_name, track)
            else:
                url = self.current_folder + self.config[FILE_PLAYBACK][CURRENT_FILE]                            
        elif playback_mode == FILE_PLAYLIST:
            url = self.config[FILE_PLAYBACK][CURRENT_FILE]
            self.browsing_history[self.current_folder] = 0
            p = self.current_folder + self.separator + self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYLIST]
            self.browsing_history[p] = 0
            folder = p
            self.current_folder = folder
        selection = url
        
        if url and self.filelist:        
            self.filelist.set_current_item_by_url(url)
        
        p_index = self.filelist.current_page_index
        pl = self.filelist.items
        self.change_folder(folder, page_index=p_index, playlist=pl, selected=selection)            
    
    def create_file_menu_button(self, s, constr, action, scale, font_size):
        """ Create File Menu button

        :param s: button state
        :param constr: scaling constraints
        :param action: button event listener
        :param scale: True - scale images, False - don't scale images

        :return: file menu button
        """
        scale = False
        s.padding = self.config[PADDING]
        s.image_area_percent = self.config[IMAGE_AREA]
        label_area_percent = 100 - s.image_area_percent
        if self.config[ALIGN_BUTTON_CONTENT_X] == 'left':
            s.image_location = LEFT
            s.label_location = LEFT
            s.h_align = H_ALIGN_LEFT
        elif self.config[ALIGN_BUTTON_CONTENT_X] == 'right':
            s.image_location = RIGHT
            s.label_location = RIGHT
            s.h_align = H_ALIGN_RIGHT
        elif self.config[ALIGN_BUTTON_CONTENT_X] == 'center':
            s.image_location = TOP
            s.label_location = BOTTOM
            s.h_align = H_ALIGN_CENTER
        s.v_align = CENTER
        s.wrap_labels = self.config[WRAP_LABELS]
        s.fixed_height = font_size

        if s.file_type == FOLDER_WITH_ICON or (s.file_type == FILE_AUDIO and getattr(s, "has_embedded_image", None)):
            scale = True
        if hasattr(s, "show_label"):
            return self.factory.create_menu_button(s, constr, action, scale, label_area_percent=label_area_percent, show_label=s.show_label, font_size=font_size)
        else:
            return self.factory.create_menu_button(s, constr, action, scale, label_area_percent=label_area_percent, font_size=font_size)

    def recursive_change_folder(self, state):
        """ Change recursive folder
        
        :param state: state object
        """
        f = self.util.file_util.get_first_folder_with_audio_files(state.url)
        if f == None:
            self.change_folder(state.url)
            return
        
        self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] = FILE_RECURSIVE
        
        self.config[FILE_PLAYBACK][CURRENT_FOLDER] = f[0]
        state.folder = f[0]
        state.file_name = f[1]
        state.file_type = FILE_AUDIO
        state.url = os.path.join(f[0], f[1])
        self.change_folder(f[0])
        self.handle_file(state)
        
    def select_item(self, state):
        """ Select menu item
        
        :param state: state object defining selected object
        """ 
        if self.visible:
            if state.file_type == FILE_AUDIO or state.file_type == FILE_PLAYLIST:
                self.config[FILE_PLAYBACK][CURRENT_FOLDER] = self.util.file_util.current_folder
                if self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] == FILE_PLAYLIST:
                    if hasattr(state, "file_name") and hasattr(state, "name"):
                        file_name = state.file_name
                        name = state.name
                        index = file_name.rfind(name)
                        if index != -1:
                            folder = file_name[0 : index]
                            if len(folder.strip()) > 0:
                                self.config[FILE_PLAYBACK][CURRENT_FOLDER] = folder
        
        if state.file_type == FOLDER or state.file_type == FOLDER_WITH_ICON:
            if getattr(state, "long_press", False):
                if self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] == FILE_RECURSIVE:
                    self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] = FILE_AUDIO
                    self.change_folder(state.url)
                else:
                    self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYLIST] = state.url
                    self.recursive_change_folder(state)
            else:
                self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] = FILE_AUDIO  
                self.change_folder(state.url)
        elif state.file_type == FILE_AUDIO:
            if getattr(state, "long_press", False) and self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] == FILE_RECURSIVE:
                self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] = FILE_AUDIO
            
            m = getattr(state, "playback_mode", FILE_AUDIO)
            mode = self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] or FILE_AUDIO
            if m == FILE_AUDIO and mode == FILE_AUDIO:
                self.handle_file(state)
            else:
                self.config[FILE_PLAYBACK][CURRENT_FILE] = state.file_name
                self.config[FILE_PLAYBACK][CURRENT_TRACK_TIME] = None
                if not getattr(state, "dont_notify", None):            
                    self.notify_play_file_listeners(state)
                else:
                    n = self.config[AUDIO][CLIENT_NAME]
                    if n == VLC or n == MPV:
                        self.handle_file(state)
            self.handle_border_links()
        elif state.file_type == FILE_PLAYLIST:
            self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] = FILE_PLAYLIST
            i = state.url.rfind(self.separator)
            url = state.url[i + 1:]
            self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYLIST] = url
            state.music_folder = self.config[AUDIO][MUSIC_FOLDER]
            pl = self.util.load_playlist(state, self.playlist_provider, self.filelist.rows, self.filelist.columns, (self.icon_box.w, self.icon_box.h))
            url = state.url
            if pl:
                self.notify_playlist_size_listener(len(pl))
            else:
                url = state.url[0 : i]
            u = getattr(state, "url", None)            
            if u == None:
                state.url = state.folder + os.sep + state.file_name
                url = state.url
                                
            self.change_folder(url, playlist=pl)
        elif state.file_type == FILE_IMAGE:
            self.go_image_viewer(state)
            
        if self.visible:
            self.draw()
   
    def page_up(self, state=None):
        """ Called by page up button
        
        :param state: not used
        """        
        if self.filelist.length <= self.filelist.items_per_page:
            return
        
        self.switch_to_next_page(None)
        
    def page_down(self, state=None):
        """ Called by page down button
        
        :param state: not used
        """        
        if self.filelist.length <= self.filelist.items_per_page:
            return
        
        self.switch_to_previous_page(None)
   
    def handle_file(self, state):
        """ Handle audio file
        
        :param state: state object defining audio file
        """
        
        state.track_time = '0'
        
        if not state.file_name.startswith("cdda:"):
            self.config[FILE_PLAYBACK][CURRENT_FILE] = state.file_name
            self.config[FILE_PLAYBACK][CURRENT_TRACK_TIME] = state.track_time
        
        if self.is_in_filelist(state.file_name):
            b = self.get_button_by_filename(state.file_name)
            if not b:
                self.switch_to_next_page(state)
            else:
                state.comparator_item = b.state.comparator_item
        
        if not self.config[FILE_PLAYBACK][CURRENT_FILE].startswith("cdda:"):
            if not self.config[FILE_PLAYBACK][CURRENT_FOLDER].endswith(os.sep):
                url = self.config[FILE_PLAYBACK][CURRENT_FOLDER] + os.sep + self.config[FILE_PLAYBACK][CURRENT_FILE]
            else:
                url = self.config[FILE_PLAYBACK][CURRENT_FOLDER] + self.config[FILE_PLAYBACK][CURRENT_FILE]
            self.filelist.set_current_item_by_url(url)
        
        mode = getattr(state, "playback_mode", None)
        if mode == None:
            if state.file_type == FILE_AUDIO:
                state.playback_mode = FILE_AUDIO
            else:
                state.playback_mode = FILE_PLAYLIST

        self.item_selected(state)
        if not getattr(state, "dont_notify", None):
            self.notify_play_file_listeners(state)
    
    def update_playlist_menu(self, state):
        """ Update playlist menu
        This is initiated by player
        
        :param state: state object from player defining current playlist file
        """
        if self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] != FILE_PLAYLIST:
            return 
        
        s = State()
        s.dont_notify = True
        
        i = self.util.get_dictionary_value(state, "current_track_id")
        s.track_time = self.util.get_dictionary_value(state, "seek_time", "0")
        self.config[FILE_PLAYBACK][CURRENT_TRACK_TIME] = s.track_time
        
        if i != None:            
            b = self.get_button_by_index_in_page(int(i) - 1)
            if not b:
                self.switch_to_next_page(s)
            s.comparator_item = int(i) 
            
        name = self.util.get_dictionary_value(state, "Track")
        
        if not name:
            name = self.util.get_dictionary_value(state, "file_name")
        
        if name != None:
            self.config[FILE_PLAYBACK][CURRENT_FILE] = name
        
        self.item_selected(state)
    
    def get_comparator(self, state):
        """ Return comparator object from state
        
        :param state: state object containing comparator item
        """
        try:
            p = state["Pos"]
            return int(p)
        except:
            pass
        
        try:
            s_comp = getattr(state, "comparator_item", None)
            if s_comp != None:
                return s_comp
        except:
            pass
        
        s_name = None
        
        if isinstance(state, dict):
            try:
                s_name = state["file_name"]
            except:
                pass
        elif isinstance(state, State):
            s_name = getattr(state, "file_name", None)
        
        for button in self.buttons.values():            
            b_name = getattr(button.state, "file_name", None)
            if s_name and b_name and s_name == button.state.file_name:
                return button.state.comparator_item
        return None
    
    def set_current_folder(self, folder):
        """ Current folder setter
        
        :param folder: new current folder
        """
        self.current_folder = folder
    
    def set_filelist(self, filelist):
        """ Set filelist
        
        :param filelist: the filelist to set
        """
        self.filelist = filelist        
    
    def init_page(self, index):
        """ Page initializer
        
        :param index: new current page index
        """
        url = self.config[FILE_PLAYBACK][CURRENT_FILE]
        if self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] == FILE_AUDIO:  
            url = self.config[FILE_PLAYBACK][CURRENT_FOLDER] + os.sep + self.config[FILE_PLAYBACK][CURRENT_FILE]
            
        if url:
            self.filelist.set_current_item_by_url(url)
            
        self.filelist.current_page_index = index        
        page = self.filelist.get_current_page()
        self.set_page(self.filelist.current_item_index_in_page, page)
        
        if not self.filelist.current_item:
            self.filelist.current_page_index = index

    def set_page(self, index_on_page, page, align=ALIGN_CENTER):
        """ Page setter
        
        :param index_on_page: current item index on page
        :param page: current page content
        """
        if page == None: return
        
        self.add_icons(page)

        self.set_items(self.make_dict(page), index_on_page, self.select_item)

        for b in self.buttons.values():
            b.parent_screen = self.parent_screen

        self.draw() 

    def add_icons(self, page):
        """ Add icons to all page items

        :param page: page items
        """
        self.util.image_util.add_file_icon(page, self.icon_box, self.icon_box_without_label)

    def switch_to_next_page(self, state):
        """ Switch to the next page
        
        :param state: button state
        """
        if len(self.filelist.items) == 0:
            return
        self.turn_page(state, self.filelist.next_page())
            
    def switch_to_previous_page(self, state):
        """ Switch to the previous page
        
        :param state: button state
        """
        if len(self.filelist.items) == 0:
            return        
        self.turn_page(state, self.filelist.previous_page())
        
    def turn_page(self, state, page):
        """ Change current page
        
        :param state: state object defining current item on page
        :param page: new page content
        """
        self.set_page(self.filelist.current_item_index, page)
        if getattr(state, "url", None):
            self.filelist.set_current_item_by_url(state.url)
        if self.visible:
            self.item_selected(self.filelist.current_item)        
        self.update_buttons()
        if not getattr(state, "dont_notify", None):
            self.draw()            
        self.page_turned = True
        
        f = self.current_folder
        
        if f[-1] == self.separator:
            f = f[:-1]

        self.browsing_history[f] = self.filelist.current_page_index
        self.handle_border_links()
    
    def handle_border_links(self):
        """ Handle border links and menu/navigator selection """

        if hasattr(self, "link_borders"):
            self.link_borders()

        if hasattr(self, "navigator"):
            if self.get_selected_item() != None:
                self.navigator.unselect()
            else:
                if not self.navigator.is_selected():
                    b = self.navigator.get_button_by_name(KEY_HOME)
                    b.set_selected(True)
                    b.clean_draw_update()

    def switch_to_root(self, state):
        """ Switch to the root folder
        
        :param state: not used state object
        """
        self.switch_folder(self.util.file_util.ROOT)
            
    def switch_to_user_home(self, state):
        """ Switch to the user home folder
        
        :param state: not used state object
        """
        self.switch_folder(self.util.file_util.USER_HOME)  
    
    def switch_folder(self, folder):
        """ Switch to folder
        
        :param folder: folder to switch to
        """
        self.switch_file_playback_mode()
        self.change_folder(folder)
    
    def switch_file_playback_mode(self):
        if self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] == FILE_PLAYLIST:
            self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] = FILE_AUDIO
    
    def switch_to_parent_folder(self, state):
        """ Switch to the parent folder
        
        :param state: not used state object
        """
        if self.current_folder == self.separator:
            return
        
        self.switch_file_playback_mode()
        
        if self.current_folder and self.current_folder[-1] == self.separator:
            self.current_folder = self.current_folder[:-1]

        tmp = self.current_folder    
        
        sep_index = self.current_folder.rfind(self.separator)
        self.browsing_history.pop(self.current_folder, None)
        
        folder = self.current_folder
        page_index = 0 
        selected_item = tmp
        
        if sep_index == -1: return
        
        if sep_index != 0:
            folder = self.current_folder[0:sep_index]
            
            if len(self.browsing_history) == 0:
                page_index = -1
            else:
                page_index = self.browsing_history.get(folder, 0)
        elif sep_index == 0:
            folder = self.separator            
            try:
                page_index = self.browsing_history[folder]
            except:
                pass
            
        try:
            self.change_folder(folder, page_index, selected=selected_item)
        except:
            pass
                    
        if self.filelist.length != 0 and tmp != None:
            self.filelist.set_current_item_by_url(tmp)
            self.unselect()
            i = self.filelist.current_item_index
            self.select_by_index(i)
            if hasattr(self, "navigator") and self.get_selected_item() != None:
                self.navigator.unselect()
    
    def change_folder(self, folder, page_index=0, playlist=None, selected=None):
        """ Change folder
        
        :param folder: new folder name
        :param page_index: new page index
        :param playlist: playlist content
        """
        if not folder:
            if self.config[AUDIO][MUSIC_FOLDER]:
                folder = self.config[AUDIO][MUSIC_FOLDER]
            else:
                folder = self.util.file_util.current_folder        
        
        self.current_folder = folder
        self.selected_index = None
        
        folder_content = playlist

        columns = self.config[FILE_BROWSER_COLUMNS]
        rows = self.config[FILE_BROWSER_ROWS]

        if not folder_content and self.config[CURRENT][MODE] != CD_PLAYER:
            folder_content = self.util.load_folder_content(folder, rows, columns)
            
        if not folder_content:
            self.buttons = {}
            self.components = []            
        self.filelist = Page(folder_content, rows, columns)

        if selected:
            self.filelist.set_current_item_by_url(selected)
            page_index = self.filelist.current_item_page_index

        self.browsing_history[folder] = page_index 
        self.init_page(page_index)
        self.notify_change_folder_listeners(folder)
        self.update_buttons()
        self.page_turned = True

        self.handle_border_links()               
    
    def update_buttons(self):
        """ Update left/right buttons """
        
        left = str(self.filelist.get_left_items_number())
        right = str(self.filelist.get_right_items_number())        
        self.notify_left_number_listeners(left)
        self.notify_right_number_listeners(right)    
            
    def get_button_by_index_in_page(self, index):
        """ Return the button by its index on page
        
        :param index: button index
        :return: the button
        """
        for button in self.buttons.values():
            if button.state.comparator_item == index:
                return button
        return None
    
    def get_button_by_filename(self, file_name):
        """ Return the button by its file name
        
        :param file_name: file name
        :return: the button
        """
        for button in self.buttons.values():
            if button.state.file_name == file_name:
                return button
        return None
    
    def is_in_filelist(self, file_name):
        """ Check that file is in the current file list
        
        :param file_name: file name
        :return: True - in file list, False- not in file list
        """
        if not self.filelist.items:
            return False

        for item in self.filelist.items:
            if item.file_name == file_name:
                return True
        return False
    
    def get_button_by_index(self, index):
        """ Return the button by its index on page
        
        :param index: button index
        :return: the button
        """
        for button in self.buttons.values():
            if button.state.index == index:
                return button
        return None
    
    def draw(self):
        """ Draw menu """
        
        self.clean()
        super(FileMenu, self).draw()        
        self.update()
     
    def add_left_number_listener(self, listener):
        """ Add left button event listener
        
        :param listener: event listener
        """
        if listener not in self.left_number_listeners:
            self.left_number_listeners.append(listener)     
 
    def notify_left_number_listeners(self, index):
        """ Notify left number button listeners
        
        :param index: file index
        """
        for listener in self.left_number_listeners:
            listener(index)
            
    def add_right_number_listener(self, listener):
        """ Add right button event listener
        
        :param listener: event listener
        """
        if listener not in self.right_number_listeners:
            self.right_number_listeners.append(listener)     
 
    def notify_right_number_listeners(self, index):
        """ Notify right number button listeners
        
        :param index: file index
        """
        for listener in self.right_number_listeners:
            listener(index)
            
    def add_change_folder_listener(self, listener):
        """ Add change folder event listener
        
        :param listener: event listener
        """
        if listener not in self.change_folder_listeners:
            self.change_folder_listeners.append(listener)     
 
    def notify_change_folder_listeners(self, state):
        """ Notify change folder listeners
        
        :param state: state object defining new folder
        """
        for listener in self.change_folder_listeners:
            listener(state)
            
    def add_play_file_listener(self, listener):
        """ Add play file event listener
        
        :param listener: event listener
        """
        if listener not in self.play_file_listeners:
            self.play_file_listeners.append(listener)     
 
    def notify_play_file_listeners(self, state):
        """ Notify play file listeners
        
        :param state: state object defining file
        """
        for listener in self.play_file_listeners:
            listener(state)
            
    def add_playlist_size_listener(self, listener):
        """ Add playlist size event listener
        
        :param listener: event listener
        """
        if listener not in self.playlist_size_listeners:
            self.playlist_size_listeners.append(listener)     
 
    def notify_playlist_size_listener(self, size):
        """ Notify playlist size listeners
        
        :param size: playlist size
        """
        for listener in self.playlist_size_listeners:
            listener(size)
            
    def add_menu_navigation_listeners(self, listener):
        """ Add menu navigation event listener
        
        :param listener: event listener
        """
        if listener not in self.menu_navigation_listeners:
            self.menu_navigation_listeners.append(listener)     
 
    def notify_menu_navigation_listeners(self, state):
        """ Notify menu navigation listeners """
        
        for listener in self.menu_navigation_listeners:
            listener(state)
            