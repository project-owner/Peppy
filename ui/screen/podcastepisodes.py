# Copyright 2019 Peppy Player peppy.player@gmail.com
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

from ui.layout.borderlayout import BorderLayout
from ui.factory import Factory
from ui.page import Page
from ui.screen.menuscreen import MenuScreen
from ui.menu.menu import ALIGN_MIDDLE
from util.keys import SCREEN_RECT, KEY_PLAYER, KEY_BACK, FILE_BUTTON
from util.config import COLORS, COLOR_DARK_LIGHT
from ui.menu.multipagemenu import MultiPageMenu
from ui.menu.episodenavigator import EpisodeNavigator
from util.podcastsutil import STATUS_AVAILABLE, STATUS_LOADING, STATUS_LOADED, MENU_ROWS_EPISODES, \
    MENU_COLUMNS_EPISODES, PAGE_SIZE_EPISODES

# 480x320
PERCENT_TOP_HEIGHT = 14.0
PERCENT_BOTTOM_HEIGHT = 14.0625

class PodcastEpisodesScreen(MenuScreen):
    """ Podcast Episodes Screen """
    
    def __init__(self, util, listeners, voice_assistant, state):
        """ Initializer
        
        :param util: utility object
        :param listeners: file browser listeners
        :param voice_assistant: voice assistant
        :param state: button state
        """
        self.util = util
        self.config = util.config
        self.podcasts_util = util.get_podcasts_util()
        self.listeners = listeners
        self.factory = Factory(util)
        self.bounding_box = self.config[SCREEN_RECT]
        self.layout = BorderLayout(self.bounding_box)
        self.layout.set_percent_constraints(PERCENT_TOP_HEIGHT, PERCENT_BOTTOM_HEIGHT, 0, 0)

        d = [MENU_ROWS_EPISODES, MENU_COLUMNS_EPISODES]
        MenuScreen.__init__(self, util, listeners, MENU_ROWS_EPISODES, MENU_COLUMNS_EPISODES, voice_assistant, d, self.turn_page, page_in_title=False)
        
        if hasattr(state, "podcast_url"):            
            podcast_url = state.podcast_url
            self.title = self.podcasts_util.summary_cache[podcast_url].name
        else:
            self.title = state.name
        
        m = self.factory.create_episode_menu_button
        self.episodes_menu = MultiPageMenu(util, self.next_page, self.previous_page, self.set_title, self.reset_title, self.go_to_page, m, MENU_ROWS_EPISODES, MENU_COLUMNS_EPISODES, None, (0, 0, 0), self.menu_layout, align=ALIGN_MIDDLE)
        self.set_menu(self.episodes_menu)
        
        self.total_pages = PAGE_SIZE_EPISODES * 2
        self.episodes = []
        self.navigator = EpisodeNavigator(self.util, self.layout.BOTTOM, listeners, self.config[COLORS][COLOR_DARK_LIGHT], self.total_pages)
        self.components.append(self.navigator)        
        self.current_page = 1
        
        self.save_episode_listeners = []
    
    def set_current(self, state):
        """ Set current state
        
        :param state: button state
        """
        if not self.util.connected_to_internet and len(self.episodes) == 0 and not hasattr(state, "url"):
            return
            
        if state.name == KEY_BACK or (getattr(state, "source", None) == FILE_BUTTON and len(self.episodes) != 0):
            self.episodes_menu.clean_draw_update()
            return
        
        if getattr(state, "podcast_url", None) != None:
            self.episodes = self.podcasts_util.get_episodes(state.podcast_url)
            if len(self.episodes) != 0:
                self.total_pages = math.ceil(len(self.episodes) / PAGE_SIZE_EPISODES)
                self.turn_page(state)
                return

        self.set_loading(self.title)
        if state.name != self.title or len(self.episodes) == 0:
            self.title = state.name
            if self.util.connected_to_internet:
                self.episodes = self.podcasts_util.get_episodes(state.url)
            else:
                self.episodes = self.podcasts_util.get_episodes_from_disk(state.url)
                
        self.total_pages = math.ceil(len(self.episodes) / PAGE_SIZE_EPISODES)
                            
        self.turn_page(state)
        self.reset_loading()
    
    def turn_page(self, state=None):
        """ Turn screen page
        
        :param state: button state
        """
        filelist = Page(self.episodes, MENU_ROWS_EPISODES, MENU_COLUMNS_EPISODES)
        
        if state == None:
            filelist.current_page_index = self.current_page - 1
            index = filelist.current_page_index * PAGE_SIZE_EPISODES
        else:            
            if getattr(state, "status", None) == STATUS_LOADED:
                if hasattr(state, "original_url") and len(state.original_url.strip()) > 0:
                    filelist.set_current_item_by_url(state.original_url)
                else:
                    filelist.set_current_item_by_file_name(state.file_name)
            else:
                filelist.set_current_item_by_url(state.url)
            index = filelist.current_item_index            
        
        self.current_page = filelist.current_page_index + 1
        
        page = filelist.get_current_page()
        d = self.episodes_menu.make_dict(page)
        self.episodes_menu.set_items(d, filelist.current_page_index, self.select_episode, False)
        self.set_title(self.current_page)
        self.episodes_menu.unselect()
        self.episodes_menu.select_by_index(index)
        
        self.navigator.left_button.change_label(str(filelist.get_left_items_number()))
        self.navigator.right_button.change_label(str(filelist.get_right_items_number()))
        self.episodes_menu.clean_draw_update()
        
        if hasattr(self, "update_observer"):
            self.episodes_menu.add_menu_observers(self.update_observer, self.redraw_observer)
    
    def select_episode(self, state):
        """ Select podacst episode
        
        :param state: button state
        """
        if state.long_press == True:
            if state.status == STATUS_LOADED:
                self.podcasts_util.delete_episode(state)
                if not self.util.connected_to_internet:
                    for i, c in enumerate(self.episodes):
                        if c.name == state.name:
                            del self.episodes[i]
                            break
                    if len(self.episodes) == 0:
                        self.title = " "
                        self.set_title(0)
                    self.turn_page(state)
                else:
                    state.icon_base = state.event_origin.components[1].content = self.podcasts_util.available_icon
                    state.status = STATUS_AVAILABLE
            elif state.status == STATUS_AVAILABLE:
                if self.podcasts_util.is_podcast_folder_available():                
                    state.icon_base = state.event_origin.components[1].content = self.podcasts_util.loading_icon
                    state.status = STATUS_LOADING
                    self.add_save_episode_listener(state) 
                    self.podcasts_util.save_episode(state, self.notify_save_episode_listeners)                              
            self.clean_draw_update()     
        else:
            podcast_player = self.listeners[KEY_PLAYER]
            podcast_player(state)                    

    def add_save_episode_listener(self, listener):
        """ Add save episode listener
        
        :param listener: event listener
        """
        if listener not in self.save_episode_listeners:
            self.save_episode_listeners.append(listener)
            
    def notify_save_episode_listeners(self):
        """ Notify all save episode listeners """
        
        for index, listener in enumerate(self.save_episode_listeners):
            listener.icon_base = listener.event_origin.components[1].content = self.podcasts_util.loaded_icon
            listener.status = STATUS_LOADED
            self.clean_draw_update()
            if hasattr(self, "redraw_observer"):
                self.redraw_observer()
            del self.save_episode_listeners[index]

    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        MenuScreen.add_screen_observers(self, update_observer, redraw_observer)
        self.update_observer = update_observer
        self.redraw_observer = redraw_observer
        self.add_loading_listener(redraw_observer)
        self.navigator.add_observers(self.update_observer, self.redraw_observer)
        