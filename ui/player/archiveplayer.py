# Copyright 2023 Peppy Player peppy.player@gmail.com
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
from util.config import PLAYER_SETTINGS, VOLUME, PODCASTS_FOLDER, MUTE, PAUSE, VOLUME_CONTROL, VOLUME_CONTROL_TYPE, \
    VOLUME_CONTROL_TYPE_PLAYER, ARCHIVE, ITEM, FILE, FILE_TIME, LABELS, ARCHIVE
from util.fileutil import FILE_AUDIO
from util.keys import RESUME, ARROW_BUTTON, KEY_ARCHIVE_FILES_BROWSER, KEY_HOME, GO_PLAYER, KEY_BACK, INIT, KEY_ARCHIVE_FILES, \
    KEY_ARCHIVE_TITLE, KEY_ARCHIVE_ITEMS_BROWSER

class ArchivePlayerScreen(FilePlayerScreen):
    """ Archive Player Screen """
    
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
        self.screen_title.set_text(self.config[LABELS][ARCHIVE])
        self.item = None
        self.logo = None
        self.ARCHIVE_LABEL = util.config[LABELS][ARCHIVE]

    def set_current(self, state=None):
        """ Set current item
        
        :param state: button state
        """
        source = getattr(state, "source", None)
        if source == INIT and state.item:
            self.time_control.reset()
            item = self.archive_util.get_item(state.item)
            self.logo = self.archive_util.get_item_logo_url(item)
            files = self.archive_util.get_item_files(item)
            metadata = self.archive_util.get_item_metadata(item)
            self.config[KEY_ARCHIVE_FILES] = files
            file = self.archive_util.get_file(int(state.file), files)
            self.config[KEY_ARCHIVE_TITLE] = metadata.title
        elif source == ARROW_BUTTON or source == KEY_ARCHIVE_FILES_BROWSER:
            file = state
            self.config[ARCHIVE][FILE] = state.index
        elif source == KEY_ARCHIVE_ITEMS_BROWSER:
            self.set_loading(None)

            item = self.archive_util.get_item(state.identifier)
            self.logo = self.archive_util.get_item_logo_url(item)
            files = self.archive_util.get_item_files(item)
            metadata = self.archive_util.get_item_metadata(item)
            self.config[KEY_ARCHIVE_FILES] = files
            file = self.archive_util.get_file(0, files)
            self.config[KEY_ARCHIVE_TITLE] = metadata.title
            self.config[ARCHIVE][ITEM] = state.identifier
            self.config[ARCHIVE][FILE] = 0
            self.current_track_index = 0

            self.reset_loading()

        elif source == RESUME:
            try:
                files = self.config[KEY_ARCHIVE_FILES]
                file = self.archive_util.get_file(self.config[ARCHIVE][FILE], files)
                state.file_time = self.config[ARCHIVE][FILE_TIME]
            except:
                file = None
        elif source == KEY_HOME or source == GO_PLAYER or source == KEY_BACK:
            return
        
        self.audio_files = self.get_audio_files()

        if hasattr(state, "file_time"):
            self.config[ARCHIVE][FILE_TIME] = state.file_time
        else:
            self.config[ARCHIVE][FILE_TIME] = 0

        title = None
        try:
            title = self.config[KEY_ARCHIVE_TITLE]
        except:
            pass

        if state != None and title and file:
            self.center_button.state.name = self.center_button.state.l_name = title
            self.center_button.state.url = file.url
            state.url = file.url
            state.index = file.index
            self.screen_title.set_text(file.title)
        else:
            self.screen_title.set_text(self.ARCHIVE_LABEL)

        if self.logo != None:
            img_url = self.util.encode_url(self.logo)
            img = self.image_util.get_thumbnail(img_url, 1.0, 1.0, self.bounding_box)
            if img:
                state.full_screen_image = img[1]
            else:
                image_tuple = self.image_util.get_audio_file_icon("", self.center_button.bounding_box)
                state.full_screen_image = image_tuple[1]
                self.logo = image_tuple[0]
        else:
            image_tuple = self.image_util.get_audio_file_icon("", self.center_button.bounding_box)
            state.full_screen_image = image_tuple[1]
            self.logo = image_tuple[0]

        try:
            self.set_center_button((self.logo, state.full_screen_image))
        except:
            pass

        self.center_button.clean_draw_update()
        
        config_volume_level = int(self.config[PLAYER_SETTINGS][VOLUME])
         
        if state:
            state.volume = config_volume_level
        
        self.set_audio_file(state)

        if source == KEY_ARCHIVE_FILES_BROWSER or source == ARROW_BUTTON or source == INIT:
            self.clean_draw_update()

        if self.volume.get_position() != config_volume_level:
            self.volume.set_position(config_volume_level)
            self.volume.update_position()
        
    def is_valid_mode(self):
        """ Check that current mode is valid mode
        
        :return: True - valid mode
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

    def get_current_track_index(self, state=None):
        """ Return file index.
        
        :param state: button state
        
        :return: file index
        """
        for f in self.audio_files:
            link = getattr(f, "url", None)
            if link:
                import urllib.parse
                link = urllib.parse.unquote(link)
                if state["file_name"] in link:
                    return f.index
        return 0

    def set_audio_file(self, s=None):
        """ Set audio file
        
        "param s" button state
        """
        state = State()
        state.folder = PODCASTS_FOLDER

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
        state.playback_mode = FILE_AUDIO
        state.index = s.index

        if hasattr(s, "file_name"):      
            state.file_name = s.file_name
        source = None
        if s:
            source = getattr(s, "source", None)

        tt = self.config[ARCHIVE][FILE_TIME]
                    
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

    def set_current_track_index(self, state):
        """ Set current track index
        
        :param state: state object representing current track
        """
        self.current_track_index = 0
        
        if self.playlist_size == 1:            
            return
        
        if not self.audio_files:
            self.audio_files = self.get_audio_files()            
            if not self.audio_files: return
        
        self.current_track_index = int(self.config[ARCHIVE][FILE])

    def change_track(self, track_index):
        """ Change track
        
        :param track_index: track index
        """        
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
            return self.config[KEY_ARCHIVE_FILES]
        except:
            pass
        return []
