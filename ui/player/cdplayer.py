# Copyright 2016-2021 Peppy Player peppy.player@gmail.com
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
from util.keys import *
from util.config import *
from util.fileutil import FILE_AUDIO, FILE_PLAYLIST
from util.cdutil import CdUtil
from ui.player.fileplayer import FilePlayerScreen

class CdPlayerScreen(FilePlayerScreen):
    """ File Player Screen """
    
    def __init__(self, listeners, util, get_current_playlist, voice_assistant, volume_control):
        """ Initializer
        
        :param listeners: screen listeners
        :param util: utility object
        :param get_current_playlist: current playlist getter
        :param voice_assistant:   voice assistant
        :param volume_control: volume control
        """
        self.util = util
        self.config = util.config
        self.cdutil = CdUtil(util)
        self.cd_album = None

        FilePlayerScreen.__init__(self, listeners, util, get_current_playlist, voice_assistant, volume_control)
        
    def get_audio_files(self):
        """ Return the list of audio files in current folder
        
        :return: list of audio files
        """
        files = []
        af = getattr(self, "audio_files", None)
        if af == None:
            cd_drive_name = self.config[CD_PLAYBACK][CD_DRIVE_NAME]
            files = self.cdutil.get_cd_tracks_summary(cd_drive_name)
        else:
            return self.audio_files

        return files
    
    def get_current_track_index(self, state=None):
        """ Return current track index.
        In case of files goes through the file list.
        In case of playlist takes track index from the state object.
        
        :param state: button state

        :return: current track index
        """
        mode = self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE]       
        if state and mode == FILE_PLAYLIST:
            try:
                n = state["Track"]
                if n: return int(n) - 1
            except:
                pass

        cmp = int(self.config[CD_PLAYBACK][CD_TRACK]) - 1

        for f in self.audio_files:
            if f.index == cmp:
                return f.index
        return 0
    
    def change_track(self, track_index):
        """ Change track
        
        :param track_index: index track
        """
        self.stop_timer()
        time.sleep(0.3)
        s = State()

        s.playlist_track_number = track_index
        s.index = track_index
        s.source = ARROW_BUTTON
        s.file_name = self.get_filename(track_index)
        
        if self.cd_album != None:
            s.album = self.cd_album

        self.set_current(True, s)
    
    def is_valid_mode(self):
        return True
    
    def set_current_track_index(self, state):
        """ Set current track index
        
        :param state: state object representing current track
        """
        if not self.is_valid_mode(): return
        
        if getattr(state, "cd_track_id", None):
            self.config[CD_PLAYBACK][CD_TRACK] = state["cd_track_id"]
        
        self.current_track_index = 0
        
        if self.playlist_size == 1:            
            return
        
        if not self.audio_files:
            self.audio_files = self.get_audio_files()            
            if not self.audio_files: return
        
        i = self.get_current_track_index(state)
        self.current_track_index = i
        
    def eject_cd(self, state):
        """ Eject CD
        
        :param state: button state object
        """
        self.audio_files = []
        self.screen_title.set_text(" ")
        self.update_arrow_button_labels(state)
        if self.show_time_control:
            self.time_control.reset()
        self.cd_album = None
        self.set_cd_album_art_image()
    
    def set_current(self, new_track=False, state=None):
        """ Set current file or playlist
        
        :param new_track: True - new audio file
        :param state: button state
        """
        self.cd_album = getattr(state, "album", None)
        
        if getattr(state, "source", None) != INIT:
            state.full_screen_image = self.set_cd_album_art_image()
            state.image_base = self.center_button.components[1].content
                        
        config_volume_level = int(self.config[PLAYER_SETTINGS][VOLUME])
        if state:
            if self.config[VOLUME_CONTROL][VOLUME_CONTROL_TYPE] == VOLUME_CONTROL_TYPE_PLAYER:
                state.volume = config_volume_level
            else:
                state.volume = None
            
        self.set_audio_file(new_track, state)
        
        if self.volume.get_position() != config_volume_level:
            self.volume.set_position(config_volume_level)
            self.volume.update_position()
    
    def set_cd_album_art_image(self):
        """ Set CD album art image """
        
        img_tuple = self.image_util.get_cd_album_art(self.cd_album, self.bounding_box)
        if img_tuple == None:
            return None
        self.set_center_button(img_tuple)
        self.center_button.clean_draw_update()
        
        return img_tuple[1]
            
    def set_audio_file(self, new_track, s=None):
        """ Set new audio file
        
        :param new_track: True - new audio file
        "param s" button state object
        """
        state = State()
        
        if s:
            state.playback_mode = getattr(s, "playback_mode", FILE_AUDIO)
            state.playlist_track_number = getattr(s, "playlist_track_number", None)
            if getattr(s, "source", None) != INIT:
                image_base = getattr(s, "image_base", None)
                if image_base != None:
                    state.image_base = image_base
        else:
            m = self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE]
            if m:
                state.playback_mode = m
            else:
                state.playback_mode = FILE_AUDIO
        
        state.file_name = s.file_name
        state.url = getattr(s, "url", s.file_name)
        parts = s.file_name.split()
        self.config[CD_PLAYBACK][CD_DRIVE_NAME] = parts[0][len("cdda:///"):]
        id = self.cdutil.get_cd_drive_id_by_name(self.config[CD_PLAYBACK][CD_DRIVE_NAME]) 
        self.config[CD_PLAYBACK][CD_DRIVE_ID] = int(id)
        self.config[CD_PLAYBACK][CD_TRACK] = int(parts[1].split("=")[1])             

        self.config[PLAYER_SETTINGS][PAUSE] = False
        state.mute = self.config[PLAYER_SETTINGS][MUTE]
        state.pause = self.config[PLAYER_SETTINGS][PAUSE]
        self.play_button.draw_default_state(None)
        state.file_type = FILE_AUDIO
        state.dont_notify = True
        state.source = FILE_AUDIO        
        self.audio_files = self.get_audio_files()            
        source = None

        if s:
            source = getattr(s, "source", None)

        if new_track:
            tt = 0.0
        else:        
            tt = self.config[CD_PLAYBACK][CD_TRACK_TIME] 
                    
        if (isinstance(tt, str) and len(tt) != 0) or (isinstance(tt, float) or (source and source == RESUME)) or isinstance(tt, int):
            state.track_time = tt
        
        if self.show_time_control:
            self.time_control.slider.set_position(0)
            
        if self.center_button and self.center_button.components[1] and self.center_button.components[1].content:
            state.icon_base = self.center_button.components[1].content
        
        if s and hasattr(s, "volume"):
            state.volume = s.volume
            
        if s and getattr(s, "source", None) == INIT:
            try:
                self.cd_album = self.util.cd_titles[self.config[CD_PLAYBACK][CD_DRIVE_NAME]]
                self.set_cd_album_art_image()
                state.image_base = self.center_button.components[1].content
            except:
                self.cd_album = None
                
        if getattr(s, "full_screen_image", None) != None:
             state.full_screen_image = s.full_screen_image
        
        song_name = self.get_song_name(s)
        if song_name != None:
            state.album = song_name

        self.notify_play_listeners(state)

    def get_song_name(self, state):
        """ Get song name in the format: Artist - Song name
        
        :param state: state object
        """
        album = getattr(state, "album", None)
        if album == None:
            return None
        
        artist = album
        if "/" in album:
            artist = album.split("/")[0].strip()
        
        if artist == None or len(artist) == 0:
            return None
        
        name = getattr(state, "l_name", None)
        file_name = getattr(state, "file_name", None)
        if name == None:
            if file_name == None:
                return None
            else:
                if file_name.startswith("cdda:"):
                    id = int(file_name.split("=")[1].strip())
                    name = self.audio_files[id - 1].name
                else:
                    name = file_name
        
        pos = name.find(".")
        if pos != -1:
            tokens = name.split(".")
            if tokens[0].strip().isdigit():
                name = name[pos + 1:].strip()
        
        if name == None or len(name) == 0:
            return None
        else:
            return artist + " - " + name    
