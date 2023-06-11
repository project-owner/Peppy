# Copyright 2020-2023 Peppy Player peppy.player@gmail.com
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
import time

from ui.state import State
from ui.player.fileplayer import FilePlayerScreen
from util.config import COLLECTION, FILE_NOT_FOUND, PLAYER_SETTINGS, VOLUME, LABELS, PAUSE, MUTE, BASE_FOLDER, \
    COLLECTION_PLAYBACK, COLLECTION_FOLDER, COLLECTION_TRACK_TIME, COLLECTION_FILE, VOLUME_CONTROL, VOLUME_CONTROL_TYPE, \
    VOLUME_CONTROL_TYPE_PLAYER, COLLECTION_URL
from util.fileutil import FILE_AUDIO
from util.keys import RESUME, ARROW_BUTTON, INIT, KEY_BACK

class CollectionPlayerScreen(FilePlayerScreen):
    """ Collection Player Screen """
    
    def __init__(self, listeners, util, get_current_playlist, volume_control):
        """ Initializer
        
        :param listeners: screen listeners
        :param util: utility object
        :param get_current_playlist: current playlist getter
        :param volume_control: volume control
        """
        FilePlayerScreen.__init__(self, listeners, util, get_current_playlist, volume_control)
        self.file_util = util.file_util
        self.center_button.state.name = ""       

    def set_current(self, new_track=False, state=None):
        """ Set current file
        
        :param new_track: True - new audio file
        :param state: button state
        """
        if getattr(state, "source", None) == KEY_BACK:
            return

        if not hasattr(state, "url") or not self.file_util.is_file_available(state.url):
            self.screen_title.set_text(self.config[LABELS][FILE_NOT_FOUND])
            state.url = None

        state.full_screen_image = self.set_audio_file_image(state.url)

        if not state.url:
            return
                        
        config_volume_level = int(self.config[PLAYER_SETTINGS][VOLUME])
        if state:
            state.volume = config_volume_level
            
        self.set_audio_file(new_track, state)
        
        if self.volume.get_position() != config_volume_level:
            self.volume.set_position(config_volume_level)
            self.volume.update_position()

    def is_valid_mode(self):
        """ Check that current mode is valid mode
        
        :return: True - collection player mode is valid
        """
        return True
    
    def get_current_track_index(self, state=None):
        """ Return current track index.
        
        :param state: button state
        
        :return: current track index
        """
        index = 0

        for f in self.audio_files:
            try:
                if f.file_name == state["file_name"]:
                    index = f.index
                    break
            except:
                pass

        return index

    def set_audio_file(self, new_track, s=None):
        """ Set new audio file
        
        :param new_track: True - new audio file
        "param s" button state object
        """
        state = State()
        state.playback_mode = FILE_AUDIO
        self.current_folder = s.folder
        state.folder = self.current_folder
        state.file_name = s.file_name
        state.url = s.url
        
        if state.folder[-1] == os.sep:
            state.folder = state.folder[:-1]

        state.full_screen_image = self.set_audio_file_image(state.url.replace('\"', ""), state.folder)
        self.config[PLAYER_SETTINGS][PAUSE] = False
        state.mute = self.config[PLAYER_SETTINGS][MUTE]
        state.pause = self.config[PLAYER_SETTINGS][PAUSE]
        self.play_button.draw_default_state(None)
        state.file_type = FILE_AUDIO
        state.dont_notify = True
        
        folder = self.config[COLLECTION_PLAYBACK][COLLECTION_FOLDER]
        self.audio_files = self.util.get_audio_files_in_folder(folder, False, False)
        source = None
        if s:
            source = getattr(s, "source", None)

        tt = 0.0

        if new_track and hasattr(s, "source") and s.source != INIT:
            tt = 0.0
        else:        
            tt = self.config[COLLECTION_PLAYBACK][COLLECTION_TRACK_TIME]
                    
        if (isinstance(tt, str) and len(tt) != 0) or (isinstance(tt, float) or (source and source == RESUME)) or isinstance(tt, int):
            state.track_time = tt
        
        if self.show_time_control:
            self.time_control.slider.set_position(0)
            
        if self.center_button and self.center_button.components[1] and self.center_button.components[1].content:
            state.icon_base = self.center_button.components[1].content
        
        if self.center_button and hasattr(s, "index"):
            self.center_button.state.index = s.index
        else:
            self.center_button.state.index = 0

        if s:
            if self.config[VOLUME_CONTROL][VOLUME_CONTROL_TYPE] == VOLUME_CONTROL_TYPE_PLAYER:
                state.volume = s.volume
            else:
                state.volume = None
                            
        if getattr(s, "full_screen_image", None) != None:
             state.full_screen_image = s.full_screen_image
        
        song_name = self.get_song_name(s)
        if song_name != None:
            state.album = song_name

        self.notify_play_listeners(state)

    def change_track(self, track_index):
        """ Change track
        
        :param track_index: index track
        """
        self.config[COLLECTION_PLAYBACK][COLLECTION_FILE] = self.get_filename(track_index)
        self.stop_timer()
        time.sleep(0.3)
        s = State()
        s.playlist_track_number = track_index
        s.index = track_index
        s.source = ARROW_BUTTON
        s.file_name = self.get_filename(track_index)

        folder = self.current_folder
        if not folder.endswith(os.sep):
            folder += os.sep
        s.folder = os.path.join(self.config[COLLECTION][BASE_FOLDER], folder)
        s.url = os.path.join(s.folder, s.file_name)
        self.config[COLLECTION_PLAYBACK][COLLECTION_URL] = s.url
        
        self.set_current(True, s)
        