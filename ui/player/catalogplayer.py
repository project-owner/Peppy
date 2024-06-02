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

from ui.state import State
from ui.player.fileplayer import FilePlayerScreen
from util.config import *
from util.fileutil import FILE_AUDIO
from util.keys import ARROW_BUTTON, CATALOG_TRACKS, KEY_INFO
from util.streamingservice import ALBUM_IMAGE_LARGE
from util.config import CLOCK, WEATHER, LYRICS

class CatalogPlayerScreen(FilePlayerScreen):
    """ Catalog Player Screen """

    def __init__(self, listeners, util, volume_control):
        """ Initializer

        :param listeners: screen listeners
        :param util: utility object
        :param volume_control: volume control
        """
        self.archive_util = util.archive_util
        self.image_util = util.image_util
        FilePlayerScreen.__init__(self, listeners, util, self.get_audio_files, volume_control)
        self.center_button.state.name = ""
        self.screen_title.active = True
        self.CATALOG_LABEL = util.config[LABELS][CATALOG]
        self.screen_title.set_text(self.CATALOG_LABEL)
        self.track_change_listeners = []
        self.item = None
        self.logo = None

    def set_current(self, state=None):
        """ Set current item

        :param state: button state
        """
        source = getattr(state, "source", None)

        if source == "back" or source == "go player" or source == "resume":
            return

        try:
            url = getattr(state, ALBUM_IMAGE_LARGE, None)
            if url:
                img = self.image_util.load_image_from_url(url)
                self.set_center_button(img)
        except:
            pass

        config_volume_level = int(self.config[PLAYER_SETTINGS][VOLUME])

        if state:
            state.volume = config_volume_level

        self.audio_files = self.get_audio_files()
        self.set_audio_file(state)
        self.current_track_index = state.index

        if self.volume.get_position() != config_volume_level:
            self.volume.set_position(config_volume_level)
            self.volume.update_position()

        self.update_component = True

    def is_valid_mode(self):
        """ Check that current mode is valid mode

        :return: True - valid mode
        """
        return True

    def set_current_track_index(self, state):
        """ Callabck from player

        :param state: state object representing current track
        """
        pass

    def get_current_track_index(self, state=None):
        """ Return file index.

        :param state: button state

        :return: file index
        """
        if getattr(state, "index", None):
            return state.index
        return 0

    def set_audio_file(self, s=None):
        """ Set audio file

        "param s" button state
        """
        state = State()

        try:      
            state.url = s.url
        except:
            return

        self.config[PLAYER_SETTINGS][PAUSE] = False
        state.mute = self.config[PLAYER_SETTINGS][MUTE]
        state.pause = self.config[PLAYER_SETTINGS][PAUSE]
        state.file_type = FILE_AUDIO
        state.dont_notify = True
        state.source = FILE_AUDIO 
        state.playback_mode = s.playback_mode
        state.index = s.index
        state.track_time = 0
        self.time_control.slider.set_position(0)

        self.set_title(s)

        if self.center_button:
            self.center_button.state.index = s.index
            if self.center_button.components[1] and self.center_button.components[1].content:
                state.icon_base = self.center_button.components[1].content

        if s:
            if self.config[VOLUME_CONTROL][VOLUME_CONTROL_TYPE] == VOLUME_CONTROL_TYPE_PLAYER:
                state.volume = s.volume
            else:
                state.volume = None

        if getattr(s, "full_screen_image", None) != None:
             state.full_screen_image = s.full_screen_image

        self.play_button.draw_default_state(None)
        self.notify_play_listeners(state)
        self.notify_track_change_listeners(state)

    def set_title(self, current_item, title=None):
        """ Set screen title

        :param current_item: the current button state object
        """
        if title != None:
            t = title
        else:
            t = getattr(current_item, "artist name", "") + " - " + current_item.name
        d = {"current_title" : t}
        flag = self.screen_title.active
        self.enable_player_screen(True)
        self.screen_title.set_text(d)
        self.enable_player_screen(flag)

    def stop(self):
        self.current_track_index = None
        self.stop_player()
        self.left_button.change_label("0")
        self.right_button.change_label("0")
        self.stop_timer()
        self.time_control.reset()
        self.set_title(None, title="")
        self.config[CATALOG_TRACKS] = []
        self.audio_files = []

    def change_track(self, track_index):
        """ Change track

        :param track_index: track index
        """
        if self.audio_files and track_index >= len(self.audio_files):
            self.stop()
            return

        s = self.audio_files[track_index]
        self.stop_player()
        self.stop_timer()
        s.file = track_index
        time.sleep(0.3)
        s.source = ARROW_BUTTON
        self.set_current(s)

    def start_timer(self):
        """ Start time control timer """

        self.time_control.start_timer()

    def get_audio_files(self):
        """ Return the list of audio files in current folder

        :return: list of audio files
        """
        try:
            return self.config[CATALOG_TRACKS]
        except:
            pass
        return []

    def handle_info_popup_selection(self, state):
        """ Handle info menu selection

        :param state: button state
        """
        n = state.name

        if n == CLOCK or n == WEATHER:
            self.start_screensaver(n)
        elif n == LYRICS:
            a = None
            try:
                a = self.screen_title.text
            except:
                pass
            if a != None:
                s = State()
                s.album = a
                self.start_screensaver(n, s)
            else:
                self.start_screensaver(n)
        else:
            self.listeners[KEY_INFO](state)

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
