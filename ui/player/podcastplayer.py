# Copyright 2019-2023 Peppy Player peppy.player@gmail.com
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
from util.config import PLAYER_SETTINGS, VOLUME, PODCASTS, PODCASTS_FOLDER, PODCAST_EPISODE_TIME, \
    MUTE, PAUSE, PODCAST_URL, PODCAST_EPISODE_NAME, PODCAST_EPISODE_URL, VOLUME_CONTROL, VOLUME_CONTROL_TYPE, \
    VOLUME_CONTROL_TYPE_PLAYER
from util.fileutil import FILE_AUDIO
from util.keys import RESUME, ARROW_BUTTON, INIT, KEY_HOME
from util.podcastsutil import STATUS_LOADED

class PodcastPlayerScreen(FilePlayerScreen):
    """ Podcast Player Screen """
    
    def __init__(self, listeners, util, get_current_playlist, volume_control):
        """ Initializer
        
        :param listeners: screen listeners
        :param util: utility object
        :param get_current_playlist: current playlist getter
        :param volume_control: volume control
        """
        self.podcasts_util = util.get_podcasts_util()
        FilePlayerScreen.__init__(self, listeners, util, get_current_playlist, volume_control)
        self.center_button.state.name = ""
        self.screen_title.active = True

    def set_current_screen(self, state):
        """ Set as a current screen

        :param state: state object
        """
        source = getattr(state, "source", None)
        if source == "episode_menu":
            self.set_current(state=state, new_track=True)
        elif source == RESUME or source == KEY_HOME:
            s = State()
            s.name = self.config[PODCASTS][PODCAST_EPISODE_NAME]
            s.url = self.config[PODCASTS][PODCAST_EPISODE_URL]
            s.podcast_url = self.config[PODCASTS][PODCAST_URL]

            try:
                s.podcast_image_url = self.podcasts_util.summary_cache[s.podcast_url].episodes[0].podcast_image_url
            except:
                pass

            if not hasattr(s, "podcast_image_url"):
                try:
                    self.set_loading()
                    info = self.podcasts_util.get_podcast_info(None, s.podcast_url)
                    s.podcast_image_url = info.image_name
                    self.reset_loading()
                except:
                    self.reset_loading()

            try:
                s.status = self.podcasts_util.get_episode_status(s.podcast_url, s.url)
            except:
                pass

            if self.util.connected_to_internet:
                s.online = True
            else:
                s.online = False
            self.set_current(state=s)
        else:
            self.set_current(state=state)

    def set_current(self, new_track=False, state=None):
        """ Set current file or playlist
        
        :param new_track: True - new audio file
        :param state: button state
        """
        if not state.url:
            return

        self.config[PODCASTS][PODCAST_EPISODE_NAME] = state.name
        self.config[PODCASTS][PODCAST_URL] = state.podcast_url
        if hasattr(state, "file_name"):
            self.config[PODCASTS][PODCAST_EPISODE_URL] = state.file_name
        elif hasattr(state, "url"):
            self.config[PODCASTS][PODCAST_EPISODE_URL] = state.url

        if getattr(state, "source", None) == INIT:
            self.set_loading()
            self.podcasts_util.init_playback(state)
            self.reset_loading()

        if state != None:
            self.center_button.state.name = state.name
            self.center_button.state.podcast_url = state.podcast_url
            self.center_button.state.url = state.url

        self.screen_title.set_text(state.name)
        
        img = self.podcasts_util.get_podcast_image(state.podcast_image_url, 1.0, 1.0, self.bounding_box, state.online)
        state.full_screen_image = img[1]
        self.set_center_button(img)
        
        config_volume_level = int(self.config[PLAYER_SETTINGS][VOLUME])
         
        if state:
            state.volume = config_volume_level
             
        self.set_audio_file(new_track, state)
        
        if self.volume.get_position() != config_volume_level:
            self.volume.set_position(config_volume_level)
            self.volume.update_position()
        
        self.audio_files = None
        self.update_component = True

    def get_audio_files(self):
        """ Return the list of files
        
        :return: list of audio files
        """
        current_podcast_url = self.config[PODCASTS][PODCAST_URL]
        episodes = []

        try:
            if not self.podcasts_util.summary_cache:
                state = State()
                state.podcast_url = self.config[PODCASTS][PODCAST_URL]
                state.url = self.config[PODCASTS][PODCAST_EPISODE_URL]
                self.podcasts_util.init_playback(state)

            current_podcast = self.podcasts_util.summary_cache[current_podcast_url]
            episodes = current_podcast.episodes
        except:
            pass
        return episodes

    def is_valid_mode(self):
        """ Check that current mode is valid mode
        
        :return: True - podcasts mode is valid
        """
        return True
    
    def set_current_track_index(self, state):
        """ Set current track index

        :param state: state object representing current track
        """
        if not self.is_valid_mode(): return

        self.current_track_index = 0

        if self.playlist_size == 1:
            return

        if not self.audio_files:
            self.audio_files = self.get_audio_files()
            if not self.audio_files: return

        self.current_track_index = self.get_current_track_index(state)
        self.update_component = True

    def get_current_track_index(self, state=None):
        """ Return current track index.
        
        :param state: button state
        
        :return: current track index
        """
        for f in self.audio_files:
            if f.file_name.startswith("http:") or f.file_name.startswith("https:"):
                filename = f.file_name.split("/")[-1]
            else:    
                filename = f.file_name.split("\\")[-1]
            
            try:
                if filename and filename == state["file_name"]:
                    return f.index
            except:
                pass
        return 0

    def set_audio_file(self, new_track, s=None):
        """ Set new audio file
        
        :param new_track: True - new file
        "param s" button state
        """
        state = State()
        state.folder = PODCASTS_FOLDER
        
        if s.status == STATUS_LOADED:
            state.url = s.file_name
            state.original_url = s.url
        else:
            state.url = s.url
            
        self.config[PLAYER_SETTINGS][PAUSE] = False
        state.mute = self.config[PLAYER_SETTINGS][MUTE]
        state.pause = self.config[PLAYER_SETTINGS][PAUSE]
        state.file_type = FILE_AUDIO
        state.dont_notify = True
        state.source = FILE_AUDIO 
        state.playback_mode = FILE_AUDIO
        state.status = s.status
        if hasattr(s, "file_name"):      
            state.file_name = s.file_name
        source = None
        if s:
            source = getattr(s, "source", None)

        if new_track:
            tt = 0.0
        else:        
            tt = self.config[PODCASTS][PODCAST_EPISODE_TIME]
                    
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
            
        if getattr(s, "full_screen_image", None) != None:
             state.full_screen_image = s.full_screen_image
        
        self.notify_play_listeners(state)

    def change_track(self, track_index):
        """ Change track
        
        :param track_index: track index
        """        
        s = self.audio_files[track_index]
        self.stop_timer()
        time.sleep(0.3)
        s.source = ARROW_BUTTON
        self.set_current(True, s)

    def start_timer(self):
        """ Start time control timer """
        
        self.time_control.start_timer()
        