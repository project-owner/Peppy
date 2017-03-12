# Copyright 2016-2017 Peppy Player peppy.player@gmail.com
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

from ui.state import State
from ui.page import Page
from ui.factory import Factory
from ui.menu.menu import Menu
from util.keys import kbd_keys, CURRENT, USER_EVENT_TYPE, SUB_TYPE_KEYBOARD, KEY_LEFT, KEY_RIGHT, \
    KEY_UP, KEY_DOWN, KEY_SELECT
from util.fileutil import FOLDER, FOLDER_WITH_ICON, FILE_PLAYLIST, FILE_AUDIO
from util.config import CURRENT_FOLDER, CURRENT_FILE, CURRENT_TRACK_TIME, AUDIO, MUSIC_FOLDER

class FileMenu(Menu):
    """ File Menu class. Extends base Menu class """
    
    def __init__(self, filelist, util, playlist_provider, bgr=None, bounding_box=None):
        """ Initializer
        
        :param filelist: file list
        :param util: utility object
        :param bgr: menu background
        :param bounding_box: bounding box
        """ 
        self.factory = Factory(util)
        self.util = util
        self.playlist_provider = playlist_provider
        self.config = self.util.config
        self.filelist = filelist
        m = self.factory.create_file_menu_button
        self.bounding_box = bounding_box
        Menu.__init__(self, util, bgr, self.bounding_box, filelist.rows, filelist.columns, create_item_method=m)
        
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

        url = self.config[CURRENT][CURRENT_FOLDER] + os.sep + self.config[CURRENT][CURRENT_FILE]
        self.filelist.set_current_item_by_url(url)
        self.change_folder(self.config[CURRENT][CURRENT_FOLDER], self.filelist.current_page_index)
        
        if not self.config[CURRENT][CURRENT_FOLDER] and not self.config[CURRENT][CURRENT_FILE]:
            self.select_first_item()
        
    def select_item(self, state):
        """ Select menu item
        
        :param state: state object defining selected object
        """        
        if self.visible and (state.file_type == FILE_AUDIO or state.file_type == FILE_PLAYLIST):
            self.config[CURRENT][CURRENT_FOLDER] = self.util.file_util.current_folder
        
        if state.file_type == FOLDER or state.file_type == FOLDER_WITH_ICON:         
            self.change_folder(state.url)
            self.select_item_on_page(0)
        elif state.file_type == FILE_AUDIO:
            m = getattr(state, "playback_mode", None)
            if m != None:                
                if m == FILE_AUDIO:
                    self.handle_file(state)
                elif m == FILE_PLAYLIST:
                    self.handle_playlist_file(state)
            else:
                self.handle_file(state)
            
        if self.visible:
            self.draw()
   
    def handle_event(self, event):
        """ File menu event handler
        
        :param event: event to handle
        """
        if not self.visible: return
        
        if event.type == USER_EVENT_TYPE and event.sub_type == SUB_TYPE_KEYBOARD and event.action == pygame.KEYUP:
            if event.keyboard_key == kbd_keys[KEY_LEFT]:
                if (self.filelist.current_item_index_in_page == 0 and self.filelist.current_item_index != 0) or self.filelist.current_item_index == 0:
                    if self.filelist.length <= self.filelist.items_per_page:
                        self.select_item_on_page(self.filelist.length - 1)
                    else:
                        self.turn_page_left()
                else:
                    self.select_item_on_page(self.filelist.current_item_index - 1) 
            elif event.keyboard_key == kbd_keys[KEY_RIGHT]:
                if self.filelist.current_item_index == self.filelist.length - 1 or self.filelist.current_item_index_in_page == self.filelist.items_per_page - 1:
                    if self.filelist.length <= self.filelist.items_per_page:
                        self.select_item_on_page(0)
                    else:
                        self.turn_page_right()
                else:
                    self.select_item_on_page(self.filelist.current_item_index + 1) 
            elif event.keyboard_key == kbd_keys[KEY_UP] or event.keyboard_key == kbd_keys[KEY_DOWN]:
                Menu.handle_event(self, event)
                self.filelist.set_current_item(self.selected_index)
                self.notify_menu_navigation_listeners(self.empty_state)
            elif event.keyboard_key == kbd_keys[KEY_SELECT]:
                Menu.handle_event(self, event)
        else:
            Menu.handle_event(self, event)

    def page_up(self, state=None):
        """ Called by page up button
        
        :param state: not used
        """        
        if self.filelist.length <= self.filelist.items_per_page:
            return
        
        self.switch_to_next_page(None)
        self.select_item_on_page(self.filelist.current_page_index * self.filelist.items_per_page)
        
    def page_down(self, state=None):
        """ Called by page down button
        
        :param state: not used
        """        
        if self.filelist.length <= self.filelist.items_per_page:
            return
        
        self.switch_to_previous_page(None)
        self.select_item_on_page(self.filelist.current_page_index * self.filelist.items_per_page)
   
    def turn_page_left(self, state=None):
        """ Turn page left
        
        :param state: not used
        """
        if self.filelist.length <= self.filelist.items_per_page:
            return
        
        self.switch_to_previous_page(None)
        if self.filelist.current_item_index == 0:
            self.select_item_on_page(self.filelist.length - 1)
        elif self.filelist.current_item_index_in_page == 0 and self.filelist.current_item_index != 0:
            self.select_item_on_page(self.filelist.current_item_index - 1)
        else:
            self.select_item_on_page(self.filelist.current_page_index * self.filelist.items_per_page)
   
    def turn_page_right(self, state=None):
        """ Turn page right
        
        :param state: not used
        """        
        if self.filelist.length <= self.filelist.items_per_page:
            return
        
        self.switch_to_next_page(None)
        if self.filelist.current_item_index == self.filelist.length - 1:
            self.select_item_on_page(0)
        elif self.filelist.current_item_index_in_page == self.filelist.items_per_page - 1:
            self.select_item_on_page(self.filelist.current_item_index + 1)
        else:
            self.select_item_on_page(self.filelist.current_page_index * self.filelist.items_per_page)
   
    def select_item_on_page(self, selected_index):
        """ Select item on page
        
        :param selected_index: index of the selected item
        """
        if self.filelist.length == 0: return
        self.filelist.set_current_item(selected_index)
        self.unselect()
        self.select_by_index(selected_index)
        self.notify_menu_navigation_listeners(self.empty_state) 
   
    def handle_file(self, state):
        """ Handle audio file
        
        :param state: state object defining audio file
        """
        self.config[CURRENT][CURRENT_FILE] = state.file_name
        state.track_time = '0'
        self.config[CURRENT][CURRENT_TRACK_TIME] = state.track_time
        
        if self.is_in_filelist(state.file_name):
            b = self.get_button_by_filename(state.file_name)
            if not b:
                self.switch_to_next_page(state)
            else:
                state.comparator_item = b.state.comparator_item        
        
        url = self.config[CURRENT][CURRENT_FOLDER] + os.sep + self.config[CURRENT][CURRENT_FILE]
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
    
    def get_comparator(self, state):
        """ Return comparator object from state
        
        :param state: state object containing comparator item
        """
        try:
            p = state["Pos"]
            return int(p)
        except:
            pass
        
        s_comp = getattr(state, "comparator_item", None)
        if s_comp:
            return s_comp
        for button in self.buttons.values():
            s_name = getattr(state, "file_name", None)
            b_name = getattr(button.state, "file_name", None)
            if s_name and b_name and state.file_name == button.state.file_name:
                return button.state.comparator_item
        return None
    
    def load_playlist(self, state):
        """ Handle playlist
        
        :param state: state object defining playlist 
        """       
        state.music_folder = self.config[AUDIO][MUSIC_FOLDER]
        n = getattr(state, "file_name", None)
        if n != None:
            self.config[CURRENT][FILE_AUDIO] = n
        else:
            state.file_name = self.config[CURRENT][FILE_AUDIO]
        p = self.playlist_provider(state)
        
        if not p:
            return

        play_list = []
        
        for i, n in enumerate(p):
            s = State()
            s.index = i
            s.playlist_track_number = i
            s.file_name = n
            s.file_type = FILE_AUDIO
            s.url = state.folder + os.sep + n
            s.playback_mode = FILE_PLAYLIST
            play_list.append(s)
        self.notify_playlist_size_listener(len(p))
        u = getattr(state, "url", None)
        if u == None:
            state.url = state.folder + os.sep + state.file_name                
        self.change_folder(state.url, playlist=play_list)
    
    def handle_playlist_file(self, state):
        """ Handle playlist file
        
        :param state: state object defining playlist file
        """
        i = getattr(state, "index", None)
        state.track_time = '0'
        self.config[CURRENT][CURRENT_TRACK_TIME] = state.track_time
        if i != None:            
            b = self.get_button_by_index_in_page(i)
            if not b:
                self.switch_to_next_page(state)

        state.comparator_item = i 
        self.item_selected(state)
        n = getattr(state, "dont_notify", None)
        name = getattr(state, "file_name", None)
        if name != None:
            m = name.rfind("/")
            self.config[CURRENT][CURRENT_FILE] = state.file_name[m + 1:]
        
        if not n:            
            self.notify_play_file_listeners(state)
        
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
        url = self.config[CURRENT][CURRENT_FOLDER] + os.sep + self.config[CURRENT][CURRENT_FILE]
        self.filelist.set_current_item_by_url(url)
        self.filelist.current_page_index = index        
        page = self.filelist.get_current_page()
        self.set_page(self.filelist.current_item_index_in_page, page)
        
        if not self.filelist.current_item:
            self.select_first_item()
        else:
            self.item_selected(self.filelist.current_item)

    def set_page(self, index_on_page, page):
        """ Page setter
        
        :param index_on_page: current item index on page
        :param page: current page content
        """
        if page == None: return
        self.set_items(self.make_dict(page), index_on_page, self.select_item) 

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
        
        f = self.util.file_util.current_folder
        if f[-1] == self.separator:
            f = f[:-1]

        self.browsing_history[f] = self.filelist.current_page_index
    
    def switch_to_root(self, state):
        """ Switch to the root folder
        
        :param state: not used state object
        """
        self.change_folder(self.util.file_util.ROOT)
        self.select_first_item()     
            
    def switch_to_user_home(self, state):
        """ Switch to the user home folder
        
        :param state: not used state object
        """
        self.change_folder(self.util.file_util.USER_HOME)
        self.select_first_item()  
    
    def switch_to_parent_folder(self, state):
        """ Switch to the parent folder
        
        :param state: not used state object
        """
        
        if self.current_folder[-1] == self.separator:
            self.current_folder = self.current_folder[:-1]

        tmp = self.current_folder    
        
        sep_index = self.current_folder.rfind(self.separator)
        self.browsing_history.pop(self.current_folder, None)
        
        folder = self.current_folder
        page_index = 0 
        selected_item = None       
        
        if sep_index == -1: return
        
        if sep_index != 0:
            folder = self.current_folder[0:sep_index]
            
            if len(self.browsing_history) == 0:
                page_index = -1
                selected_item = tmp
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
        folder_content = self.util.load_folder_content(folder, self.filelist.rows, self.filelist.columns, self.bounding_box)
        if not folder_content:
            self.buttons = {}
            self.components = []            
        self.filelist = Page(folder_content, self.filelist.rows, self.filelist.columns)
        
        if page_index == -1 and selected:
            self.filelist.set_current_item_by_url(selected)
            page_index = self.filelist.current_page_index
        
        self.browsing_history[folder] = page_index             
        self.init_page(page_index)
        self.notify_change_folder_listeners(folder)
        self.update_buttons()
        self.draw()
        self.page_turned = True                 
    
    def select_first_item(self, state=None):
        """ Select the first item in menu """
        
        if self.filelist.length == 0: return
        
        self.filelist.set_current_item(0)
        self.unselect()
        self.select_by_index(0)
    
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
        self.select_by_index(self.selected_index)        
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
