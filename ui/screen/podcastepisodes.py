# Copyright 2019-2021 Peppy Player peppy.player@gmail.com
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
from ui.menu.menu import ALIGN_CENTER
from util.keys import KEY_PLAYER, KEY_BACK, FILE_BUTTON, V_ALIGN_TOP, H_ALIGN_LEFT, KEY_PAGE_DOWN, KEY_PAGE_UP
from ui.menu.multipagemenu import MultiPageMenu
from ui.navigator.episode import EpisodeNavigator
from util.podcastsutil import STATUS_AVAILABLE, STATUS_LOADING, STATUS_LOADED, MENU_ROWS_EPISODES, \
    MENU_COLUMNS_EPISODES, PAGE_SIZE_EPISODES
from ui.layout.buttonlayout import LEFT, CENTER
from util.config import COLORS, COLOR_BRIGHT, COLOR_MEDIUM, COLOR_CONTRAST, BACKGROUND, MENU_BGR_COLOR, \
    PODCASTS, PODCAST_EPISODE_NAME
from ui.button.episodebutton import EpisodeButton

# 480x320
PERCENT_TOP_HEIGHT = 14.0
PERCENT_BOTTOM_HEIGHT = 14.0625

ICON_AREA = 12
FONT_HEIGHT = 24

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
        self.bounding_box = util.screen_rect
        self.layout = BorderLayout(self.bounding_box)
        self.layout.set_percent_constraints(PERCENT_TOP_HEIGHT, PERCENT_BOTTOM_HEIGHT, 0, 0)

        d = [MENU_ROWS_EPISODES, MENU_COLUMNS_EPISODES]
        MenuScreen.__init__(self, util, listeners, MENU_ROWS_EPISODES, MENU_COLUMNS_EPISODES, voice_assistant, d, self.turn_page, page_in_title=False)
        
        if hasattr(state, "podcast_url"):            
            podcast_url = state.podcast_url
            self.title = self.podcasts_util.summary_cache[podcast_url].name
        else:
            self.title = state.name
        
        self.total_pages = PAGE_SIZE_EPISODES * 2
        self.episodes = []
        self.navigator = EpisodeNavigator(self.util, self.layout.BOTTOM, listeners, self.total_pages)
        self.add_navigator(self.navigator)        
        self.current_page = 1
        self.current_item = None

        m = self.create_episode_menu_button
        font_size = int(((self.menu_layout.h / MENU_ROWS_EPISODES) / 100) * FONT_HEIGHT)
        self.episodes_menu = MultiPageMenu(util, self.next_page, self.previous_page, self.set_title, self.reset_title, 
            self.go_to_page, m, MENU_ROWS_EPISODES, MENU_COLUMNS_EPISODES, None, (0, 0, 0, 0), self.menu_layout, align=ALIGN_CENTER, font_size=font_size)
        self.set_menu(self.episodes_menu)
        
        self.save_episode_listeners = []
        self.animated_title = True
    
    def create_episode_menu_button(self, s, constr, action, scale, font_size):
        """ Create podcast episode menu button

        :param s: button state
        :param constr: scaling constraints
        :param action: button event listener
        :param scale: True - scale images, False - don't scale images
        :param font_size: label font height in pixels

        :return: genre menu button
        """
        s.bounding_box = constr
        s.img_x = None
        s.img_y = None
        s.auto_update = True
        s.show_bgr = True
        s.show_img = True
        s.show_label = True
        s.image_location = LEFT
        s.label_location = CENTER
        s.label_area_percent = 30
        s.image_size_percent = 0.12
        s.text_color_normal = self.config[COLORS][COLOR_BRIGHT]
        s.text_color_selected = self.config[COLORS][COLOR_CONTRAST]
        s.text_color_disabled = self.config[COLORS][COLOR_MEDIUM]
        s.text_color_current = s.text_color_normal
        s.scale = scale
        s.source = "episode_menu"
        s.v_align = V_ALIGN_TOP
        s.h_align = H_ALIGN_LEFT
        s.v_offset = (constr.h/100) * 5
        s.bgr = self.config[BACKGROUND][MENU_BGR_COLOR]
        s.image_area_percent = ICON_AREA
        s.fixed_height = font_size

        button = EpisodeButton(self.util, s)
        button.add_release_listener(action)
        if not getattr(s, "enabled", True):
            button.set_enabled(False)
        elif getattr(s, "icon_base", False) and not getattr(s, "scaled", False):
            button.components[1].content = s.icon_base
        button.scaled = scale
        return button

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
            pass
            filelist.current_page_index = self.current_page - 1
            index = -1
        else:            
            if getattr(state, "status", None) == STATUS_LOADED:
                if hasattr(state, "original_url") and len(state.original_url.strip()) > 0:
                    filelist.set_current_item_by_url(state.original_url)
                else:
                    filelist.set_current_item_by_file_name(state.file_name)
            else:
                filelist.set_current_item_by_url(state.url)
            
            index = filelist.current_item_index            

        self.current_item = self.config[PODCASTS][PODCAST_EPISODE_NAME]        
        self.current_page = filelist.current_page_index + 1
        
        page = filelist.get_current_page()
        d = self.episodes_menu.make_dict(page)
        self.episodes_menu.set_items(d, filelist.current_page_index, self.select_episode, False)
        self.set_title(self.current_page)
        self.episodes_menu.unselect()
        self.episodes_menu.select_by_index(index)
        
        for b in self.episodes_menu.buttons.values():
            b.parent_screen = self

        self.navigator.get_button_by_name(KEY_PAGE_DOWN).change_label(str(filelist.get_left_items_number()))
        self.navigator.get_button_by_name(KEY_PAGE_UP).change_label(str(filelist.get_right_items_number()))
        self.episodes_menu.clean_draw_update()
        
        if hasattr(self, "update_observer"):
            self.episodes_menu.add_menu_observers(self.update_observer, self.redraw_observer)

        self.link_borders()

        menu_selected = self.menu.get_selected_index()
        if menu_selected == None:
            if self.current_item == None or len(self.current_item) == 0:
                self.menu.select_by_index(0)
                item = self.menu.get_selected_item()
                if item != None:
                    self.current_item = item.state.name

        for b in self.menu.buttons.values():
            b.parent_screen = self
            if self.current_item == b.state.name:
                self.menu.select_by_index(b.state.index)
                self.navigator.unselect()
                return
    
    def select_episode(self, state):
        """ Select podacst episode
        
        :param state: button state
        """
        if getattr(state, "long_press", None) == True:
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
            self.current_item = state.name
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

    def handle_event(self, event):
        """ Handle screen event

        :param event: the event to handle
        """
        self.handle_event_common(event)

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
        