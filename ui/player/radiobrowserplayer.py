# Copyright 2023-2024 Peppy Player peppy.player@gmail.com
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
import math

from ui.player.radioplayer import RadioPlayerScreen, PERCENT_GENRE_IMAGE_AREA
from util.keys import *
from util.config import *
from copy import copy
from util.util import FOLDER_ICONS, FILE_DEFAULT_STATION
from util.radiobrowser import PAGE_SIZE

class RadioBrowserPlayerScreen(RadioPlayerScreen):
    """ The Stream Player Screen """
    
    def __init__(self, util, listeners, volume_control=None):
        """ Initializer
        
        :param util: utility object
        :param listeners: screen event listeners
        :param volume_control: the volume control
        """
        self.util = util
        self.config = util.config
        self.radio_browser_util = util.radio_browser
        self.bounding_box = util.screen_rect
        self.image_util = util.image_util
        self.listeners = listeners
        self.bgr_color = self.util.config[COLORS][COLOR_DARK]
        self.current_state = None
        self.favorites_mode = False

        RadioPlayerScreen.__init__(self, util, listeners, volume_control)
        self.config[KEY_RADIO_BROWSER_FAVORITES] = self.radio_browser_util.load_favorites(self.bgr_color)
        self.shutdown_button.release_listeners.insert(0, self.radio_browser_util.save_favorites)
        self.screen_title.add_select_listener(self.handle_favorite)
        self.total_items = 0
    
    def set_custom_button(self):
        """ Set the custom buttom """
        pass

    def set_center_button(self):
        """ Set the center button """
        pass

    def set_current(self, state=None, redraw=True):
        """ Set the current screen state

        :param state: the state object
        """
        src = getattr(state, "source", None)
        s = None

        if src == KEY_BACK or src == GO_PLAYER:
            return
        elif src == KEY_FAVORITES or src == INIT or src == KEY_HOME:
            favorites = self.config[KEY_RADIO_BROWSER_FAVORITES]

            if favorites:
                self.playlist = favorites
                self.favorites_mode = True
                favorite = self.radio_browser_util.get_favorite(self.bgr_color)
                if favorite:
                    s = copy(favorite)
                    self.total_items = len(self.playlist)
                else:
                    s = None
                    self.total_items = 0
            else:
                if hasattr(state, "url"):
                    s = copy(state)
                else:
                    s = self.current_state
                if not hasattr(s, "image_path") and hasattr(s, "default_icon_path"):
                    s.image_path = s.default_icon_path

            if src == KEY_HOME:
                self.play()
        elif src == KEY_SEARCH_BROWSER:
            self.favorites_mode = False
            s = copy(state)
        else:
            s = copy(state)

        if s != None:
            s.bounding_box = self.get_center_button_bounding_box()
            s.default_icon_path = os.path.join(os.getcwd(), FOLDER_ICONS, FILE_DEFAULT_STATION)
            self.current_state = s

            if self.center_button and self.center_button.state.url != s.url:
                different_url = True
            else:
                different_url = False

            if self.favorites_mode:
                self.radio_browser_util.set_favorite_config(s)
        else:
            self.clean_center_button()
            self.update_arrow_button_labels()
            self.set_title("")
            self.stop_player()
            if self.favorites_mode:
                self.radio_browser_util.set_favorite_config(None)
            self.update_component = True
            return

        if self.center_button == None:
            self.center_button = self.get_center_button(s)
            self.current_button = self.center_button
            self.add_component(self.center_button)
            # Swap positions to avoid popup outside events
            self.components.insert(len(self.components) - 2, self.components.pop(len(self.components) - 1))
            self.play()
        else:
            if different_url:
                button = self.get_center_button(s)
                self.center_button.state = button.state
                self.center_button.components = button.components
                self.play()

        search_by = getattr(state, "search_by", None)

        if search_by != None and len(search_by) != 0 and src != KEY_FAVORITES:
            items = self.radio_browser_util.get_stations_page(s.search_by, s.search_item)
            self.playlist = self.radio_browser_util.get_states_from_items(items, self.bgr_color, s.search_by, s.search_item)
            self.total_items = self.radio_browser_util.get_items_num(s.search_by, s.search_item)

        self.set_player_custom_button(copy(state))
        self.set_player_center_button(s, redraw=redraw)

        if search_by != None and len(search_by) != 0 and src != KEY_FAVORITES and not self.favorites_mode:
            self.radio_browser_util.mark_favorites({"b": self.center_button})

        self.update_component = True

    def set_player_custom_button(self, state):
        """ Set player custom button

        :param state: button state
        """
        search_by = getattr(state, "search_by", None)
        source = getattr(state, "source", None)

        if source == KEY_HOME:
            return

        if source == KEY_FAVORITES or search_by == None or len(search_by) == 0:
            search_by = KEY_FAVORITES
        else:
            if self.config.get(RADIO_BROWSER_SEARCH_BY, None) != None:
                search_by = self.config[RADIO_BROWSER_SEARCH_BY]
            else:
                search_by = getattr(state, "search_by", "default")
            
        button = self.factory.create_button(
            search_by,
            KEY_MENU,
            self.custom_button_layout,
            self.listeners[KEY_SEARCH_BY_SCREEN],
            None,
            image_size_percent=PERCENT_GENRE_IMAGE_AREA)
        
        if self.custom_button == None:
            self.custom_button = button
            self.right_panel.add_component(self.custom_button)

        self.custom_button.components = button.components
        self.custom_button.state = button.state
        if self.home_button.selected:
            self.current_button = self.home_button    
        else:
            self.custom_button.set_selected(True)
            self.current_button = self.custom_button

        self.update_component = True

    def set_player_center_button(self, state, redraw=True):
        """ Set player center button

        :param state: button state
        :param redraw: redraw flag
        """
        self.current_index = state.index
        self.add_icon(state)        
        button = self.get_center_button(state)
        button.state.id = state.id
        button.state.search_by = getattr(state, "search_by", None)
        button.state.search_item = button.state.callback_var = getattr(state, "search_item", None)
        button.state.source = KEY_RADIO_BROWSER_PLAYER
        self.center_button.state = button.state
        self.center_button.components = button.components
        
        self.center_button.selected = True
        self.center_button.release_listeners = []

        if self.favorites_mode:
            listener = self.listeners[KEY_FAVORITES_SCREEN]
            self.add_star_icon()
        else:
            listener = self.listeners[KEY_SEARCH_BROWSER]
        self.center_button.add_release_listener(listener)

        img = self.center_button.components[1]
        if img:
            self.logo_button_content = (img.image_filename, img.content, img.content_x, img.content_y)

        self.set_background()

        self.update_arrow_button_labels()
        self.set_title(self.current_state)
        self.config[RADIO_BROWSER_SEARCH_STATION_ID] = state.id
        self.center_button.set_selected(False)
        self.link_borders()

        if redraw:
            self.update_component = True

    def add_icon(self, state):
        self.current_state = state
        self.current_state.bounding_box = self.get_center_button_bounding_box()
        if hasattr(state, "image_path") and len(state.image_path) > 0:
            if state.image_path.startswith(GENERATED_IMAGE):
                image_path = getattr(state, "default_icon_path", None)
            else:
                image_path = state.image_path

            if self.image_util.image_cache.get(image_path, None) == None:
                img = self.image_util.load_image_from_url(image_path)
                if img:
                    self.image_util.image_cache[image_path] = img[1]
                    state.icon_base = img
                else:
                    self.util.add_icon(state)       
            else:
                img = (image_path, self.image_util.image_cache[image_path])
        else:
            self.util.add_icon(state)
        
    def set_title(self, current_item):
        """ Set screen title

        :param current_item: the current button state object
        """
        d = {"current_title" : getattr(current_item, "l_name", "")}
        flag = self.screen_title.active
        self.enable_player_screen(True)
        self.screen_title.set_text(d)
        self.enable_player_screen(flag)
        self.update_component = True

    def update_arrow_button_labels(self):
        """ Update arrow buttons state """

        if self.total_items == 0:
            left = right = "0"
        else:    
            left = str(self.current_index)
            right = str(self.total_items - self.current_index - 1)

        self.left_button.change_label(left)
        self.right_button.change_label(right)
        self.update_component = True

    def get_state_by_index(self, index):
        if index > self.playlist[len(self.playlist) - 1].index or index < self.playlist[0].index:
            # offset = int((index / PAGE_SIZE) * PAGE_SIZE)
            f = math.floor(index / PAGE_SIZE)
            offset = f * PAGE_SIZE
            search_by= self.config[RADIO_BROWSER_SEARCH_BY]
            search_item = self.config[RADIO_BROWSER_SEARCH_ITEM]
            items = self.radio_browser_util.get_stations_page(search_by, search_item, offset=offset)
            self.playlist = self.radio_browser_util.get_states_from_items(items, self.bgr_color, search_by, search_item)

        for s in self.playlist:
            if s.index == index:
                return s
        return None
    
    def set_current_item(self, index):
        pass

    def go_left(self, state):
        playlist_size = self.total_items

        if playlist_size == 0 or self.current_index == 0:
            return

        self.current_index -= 1
        self.change_item()
        if self.favorites_mode:
            s = self.playlist[self.current_index]
            self.radio_browser_util.set_favorite_config(s)

        self.update_component = True

    def go_right(self, state):
        playlist_size = self.total_items

        if playlist_size == 0:
            return

        if self.current_index == playlist_size - 1:
            self.current_index = 0
        else:
            self.current_index += 1

        self.change_item()
        if self.favorites_mode:
            s = self.playlist[self.current_index]
            self.radio_browser_util.set_favorite_config(s)

        self.update_component = True

    def update_center_button(self):
        """ Set album art background """

        current_state = self.get_state_by_index(self.current_index)
        s = copy(current_state)
        self.set_player_center_button(s)
        self.set_title(s)
        self.set_background()
        self.update_component = True

        if self.radio_browser_util.is_favorite(s) and len(self.center_button.components) == 3:
            self.add_star_icon()

    def handle_favorite(self):
        """ Add/Remove station to/from the favorites """

        state = self.center_button.state

        if self.radio_browser_util.is_favorite(state):
            index = state.index
            current_screen = self.config.get(CURRENT_SCREEN, None)
            if current_screen == KEY_RADIO_BROWSER_PLAYER:
                self.radio_browser_util.remove_favorite(state)
            if not self.favorites_mode:
                if self.center_button and len(self.center_button.components) == 4:
                    del self.center_button.components[3]
                    self.center_button.clean()
                    self.center_button.draw()
                    self.update_component = True
                return

            self.playlist = self.config.get(KEY_RADIO_BROWSER_FAVORITES, None)
            if not self.playlist:
                self.radio_browser_util.set_favorite_config(None)
                self.set_current(None)
                return

            if index >= len(self.playlist):
                index -= 1  

            s = self.get_state_by_index(index)
            self.set_current(s, redraw=False)
            self.total_items = len(self.playlist)
            self.update_arrow_button_labels()
        else:
            if isinstance(state.icon_base, tuple):
                state.image_path = state.icon_base[0]
            self.radio_browser_util.add_favorite(state)
            if self.center_button and len(self.center_button.components) == 3 and not self.favorites_mode:
                self.radio_browser_util.mark_favorites({"b": self.center_button})
        
        self.update_component = True
