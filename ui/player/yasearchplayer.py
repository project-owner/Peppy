# Copyright 2024 Peppy Player peppy.player@gmail.com
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

import time

from ui.player.fileplayer import FilePlayerScreen
from util.config import *
from util.fileutil import FILE_AUDIO
from util.keys import *
from copy import copy
from ui.state import State
from ui.menu.popup import Popup
from ui.layout.borderlayout import BorderLayout

class YaSearchPlayerScreen(FilePlayerScreen):
    """ YA Stream Player Screen """
    
    def __init__(self, listeners, util, get_current_playlist, volume_control):
        """ Initializer
        
        :param listeners: screen listeners
        :param util: utility object
        :param get_current_playlist: current playlist getter
        :param volume_control: volume control
        """
        self.ya_stream_util = util.ya_stream_util
        FilePlayerScreen.__init__(self, listeners, util, get_current_playlist, volume_control)
        self.center_button.state.name = ""
        self.screen_title.active = True
        self.current_query = None
        self.track_change_listeners = []
        self.current_item_url = None
        self.screen_title.add_press_listener(self.update_title)
        self.screen_title.add_select_listener(self.handle_title_click)

    def set_current(self, state=None):
        """ Set current stream
        
        :param state: button state
        """
        self.config[KEY_YA_STREAM_CURRENT_PLAYER] = KEY_YA_SEARCH_PLAYER

        self.current_item_url = getattr(state, "id", None)
        source = getattr(state, "source", None)
        if source == KEY_HOME or source == GO_PLAYER or source == KEY_BACK or source == INIT or source == RESUME:
            if self.time_control.timer_started or getattr(self, "current_track_index", None) == None:
                return
            state.index = self.current_track_index

        playlist = self.config.get(KEY_YA_STREAM_SEARCH_BROWSER, None)

        if playlist == None:
            return

        loading = False
        self.current_track_index = getattr(state, "index", 0)
        s = playlist[self.current_track_index]

        if source == KEY_YA_STREAM_SEARCH_BROWSER or source == ARROW_BUTTON:
            self.config[YA_STREAM][YA_SEARCH_TIME] = 0
            self.screen_title.visible = False
            self.set_loading()
            loading = True

            url = getattr(s, "url", None)
            if not url:
                self.ya_stream_util.get_search_stream_properties(s, self.bounding_box)

            if source == KEY_YA_STREAM_SEARCH_BROWSER or source == ARROW_BUTTON:
                self.current_query = getattr(s, "search", None)

        if not hasattr(s, "url"):
            self.clean_draw_update()
            if loading:
                self.screen_title.visible = True
                self.reset_loading()
                loading = False
            return

        self.config[KEY_YA_SEARCH_STREAM_INDEX] = s.index
        if hasattr(s, "time"):
            self.config[YA_STREAM][YA_PLAYLIST_TIME] = s.time

        if state != None:
            self.center_button.state.name = s.l_name
            self.center_button.state.url = s.url

        self.screen_title.set_text(s.l_name)

        if getattr(s, "image_path", None) != None and getattr(s, "full_screen_image", None) == None:
            img = self.ya_stream_util.get_thumbnail(s.image_path, 1.0, 1.0, self.bounding_box)
            if img:
                s.full_screen_image = img[1]

        self.set_center_button((s.image_path, s.full_screen_image))
        self.center_button.clean()
        self.center_button.draw()
        
        config_volume_level = int(self.config[PLAYER_SETTINGS][VOLUME])
         
        if s:
            s.volume = config_volume_level
        
        self.set_audio_file(s)

        if self.volume.get_position() != config_volume_level:
            self.volume.set_position(config_volume_level)
            self.volume.update_position()

        if loading:
            self.screen_title.visible = True
            self.reset_loading()
            loading = False

        self.clean()
        self.draw()
        self.update_component = True
        
    def is_valid_mode(self):
        """ Check that current mode is valid mode
        
        :return: True - SA Stream mode is valid
        """
        return True

    def set_current_track_index(self, state):
        """ Set current track index

        :param state: state object representing current track
        """
        if not self.is_valid_mode(): return

        if self.playlist_size == 1:
            self.current_track_index = 0
            return

        self.audio_files = self.ya_stream_util.search_cache.get(self.current_query, None)

        if not self.audio_files:
            self.current_track_index = 0
            return

        if self.current_track_index == None:
            self.current_track_index = self.get_current_track_index(state)

        self.update_component = True

    def get_current_track_index(self, state=None):
        """ Return current track index.
        
        :param state: button state
        
        :return: current track index
        """
        state_id = self.get_id(state["file_name"])
        for i, f in enumerate(self.audio_files):
            link = getattr(f, "url", None)
            if link:
                import urllib.parse
                link = urllib.parse.unquote(link)
                link_id = self.get_id(link)

                if state_id == link_id:
                    return i
        return 0

    def get_id(self, link):
        """ Get stream ID from the link

        :param link: stream link

        :return: stream ID
        """
        token = "&id="
        start = link.find(token)

        if start != -1:
            stop = link.find("&", start + len(token))
        else:
            return None

        id = link[start + len(token): stop]
        return id

    def set_audio_file(self, s=None):
        """ Set new stream
        
        "param s" button state
        """
        state = copy(s)
        state.folder = PODCASTS_FOLDER        
        state.url = s.url
            
        self.config[PLAYER_SETTINGS][PAUSE] = False
        state.mute = self.config[PLAYER_SETTINGS][MUTE]
        state.pause = self.config[PLAYER_SETTINGS][PAUSE]
        state.file_type = FILE_AUDIO
        state.dont_notify = True
        state.source = FILE_AUDIO 
        state.playback_mode = FILE_AUDIO

        source = None
        if s:
            source = getattr(s, "source", None)

        tt = self.config[YA_STREAM].get(YA_SEARCH_TIME, 0)
                    
        if (isinstance(tt, str) and len(tt) != 0) or (isinstance(tt, float) or (source and source == RESUME)) or isinstance(tt, int):
            state.track_time = tt
        
        self.time_control.slider.set_position(0)
            
        if self.center_button and self.center_button.components[1] and self.center_button.components[1].content:
            state.icon_base = self.center_button.components[1].content
        
        if s:
            if self.config[VOLUME_CONTROL][VOLUME_CONTROL_TYPE] == VOLUME_CONTROL_TYPE_PLAYER:
                state.volume = s.volume
            else:
                state.volume = None
            
        self.notify_play_listeners(state)
        self.notify_track_change_listeners(state)

    def change_track(self, track_index):
        """ Change track
        
        :param track_index: track index
        """        
        s = self.audio_files[track_index]
        self.stop_player()
        self.stop_timer()
        time.sleep(0.3)
        s.source = ARROW_BUTTON
        self.config[KEY_YA_SEARCH_STREAM_INDEX] = track_index
        self.set_current(s)

    def start_timer(self):
        """ Start time control timer """
        
        self.time_control.start_timer()

    def get_audio_files(self):
        """ Return the list of audio files in current folder
        
        :return: list of audio files
        """
        pass

    def stop(self):
        self.current_track_index = None
        self.stop_player()
        self.left_button.change_label("0")
        self.right_button.change_label("0")
        self.stop_timer()
        self.time_control.reset()
        self.set_title("")
        self.config[KEY_YA_SEARCH_STREAM_INDEX] = None
        self.config[YA_STREAM][YA_STREAM_NAME] = None
        self.config[YA_STREAM][YA_STREAM_URL] = None
        self.config[YA_STREAM][YA_THUMBNAIL_PATH] = None
        self.audio_files = []

    def add_track_change_listener(self, listener):
        """ Add track change listener

        :param listener: event listener
        """
        if listener not in self.track_change_listeners:
            self.track_change_listeners.append(listener)

    def notify_track_change_listeners(self, state):
        """ Notify all track change listeners

        :param state: button state
        """
        for listener in self.track_change_listeners:
            try:
                listener(state)
            except:
                pass

    def handle_info_popup_selection(self, state):
        """ Handle info menu selection

        :param state: button state
        """
        n = state.name

        if n == CLOCK or n == WEATHER:
            self.start_screensaver(n)
        elif n == LYRICS:
            t = self.screen_title.text
            if t:
                s = State()
                s.album = t
                self.start_screensaver(n, s)
            else:
                self.start_screensaver(n)
    
    def get_info_popup(self, bb):
        """ Create info popup menu

        :param bb: bounding box

        :return: popup menu
        """
        items = []

        items.append(CLOCK)
        items.append(WEATHER)
        items.append(LYRICS)

        if not self.util.connected_to_internet:
            disabled_items = [WEATHER, LYRICS]
        else:
            disabled_items = None       
        
        layout = BorderLayout(bb)
        layout.set_percent_constraints(self.top_height, 0, 0, self.popup_width)
        popup = Popup(items, self.util, layout.RIGHT, self.update_screen, self.handle_info_popup_selection, disabled_items=disabled_items)

        return popup
    
    def update_title(self):
        if self.screen_title.fgr == self.config[COLORS][COLOR_CONTRAST]:
            self.screen_title.fgr = self.config[COLORS][COLOR_BRIGHT]
        else:
            self.screen_title.fgr = self.config[COLORS][COLOR_CONTRAST]

        self.screen_title.set_text({"current_title" : self.screen_title.text}, force=True)
        self.clean()
        self.draw()
        self.update_component = True
    
    def handle_title_click(self):
        """ Add/Remove item to/from the playlist """

        name = self.screen_title.text
        id = self.current_item_url
        self.ya_stream_util.handle_playlist_item(name, id)
        self.update_title()
