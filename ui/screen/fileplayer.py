# Copyright 2016-2018 Peppy Player peppy.player@gmail.com
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
import logging

from ui.state import State
from ui.container import Container
from ui.layout.borderlayout import BorderLayout
from ui.factory import Factory
from ui.screen.screen import Screen
from util.keys import SCREEN_RECT, \
    KEY_HOME, KEY_SEEK, KEY_SHUTDOWN, KEY_PLAY_PAUSE, KEY_SET_VOLUME, \
    KEY_SET_CONFIG_VOLUME, KEY_SET_SAVER_VOLUME, KEY_MUTE, KEY_PLAY, \
    ARROW_BUTTON, RESUME, INIT
from util.config import CURRENT_FILE, CURRENT_FOLDER, AUDIO, MUSIC_FOLDER, CURRENT_TRACK_TIME, RADIO, AUDIO_FILES, STREAM, COLORS, \
    VOLUME, AUTO_PLAY_NEXT_TRACK, CYCLIC_PLAYBACK, CURRENT_FILE_PLAYBACK_MODE, CURRENT_FILE_PLAYLIST, BROWSER_BOOK_TIME, AUDIOBOOKS, \
    COLOR_CONTRAST, CURRENT, MODE, PLAYER_SETTINGS, MUTE, PAUSE, FILE_PLAYBACK, CD_PLAYER, CD_PLAYBACK, CD_TRACK, CD_TRACK_TIME, \
    CD_DRIVE_NAME, CD_DRIVE_ID
from util.fileutil import FILE_AUDIO, FILE_PLAYLIST
from util.cdutil import CdUtil

# percentage for 480x320
PIXELS_TOP_HEIGHT = 45
PIXELS_BOTTOM_HEIGHT = 46
PIXELS_SIDE_TOP_HEIGHT = 91
PIXELS_SIDE_BOTTOM_HEIGHT = 91
PIXELS_SIDE_WIDTH = 126

PERCENT_TOP_HEIGHT = 14.0625
PERCENT_BOTTOM_HEIGHT = 14.375
PERCENT_SIDE_TOP_HEIGHT = 39.738
PERCENT_SIDE_BOTTOM_HEIGHT = 39.738

PERCENT_TITLE_FONT = 66.66

class FilePlayerScreen(Screen):
    """ File Player Screen """
    
    def __init__(self, listeners, util, get_current_playlist, voice_assistant):
        """ Initializer
        
        :param listeners: screen listeners
        :param util: utility object         
        """
        self.util = util
        self.config = util.config
        self.cdutil = CdUtil(util)
        self.factory = Factory(util)
        self.get_current_playlist = get_current_playlist
        self.bounding_box = self.config[SCREEN_RECT]
        self.layout = BorderLayout(self.bounding_box)
        k = self.bounding_box.w/self.bounding_box.h
        percent_menu_width = (100.0 - PERCENT_TOP_HEIGHT - PERCENT_BOTTOM_HEIGHT)/k
        panel_width = (100.0 - percent_menu_width)/2.0
        self.layout.set_percent_constraints(PERCENT_TOP_HEIGHT, PERCENT_BOTTOM_HEIGHT, panel_width, panel_width)
        self.voice_assistant = voice_assistant
        Screen.__init__(self, util, "", PERCENT_TOP_HEIGHT, voice_assistant, "file_player_screen_title", True, self.layout.TOP)
        self.layout = BorderLayout(self.bounding_box)
        self.layout.set_percent_constraints(PERCENT_TOP_HEIGHT, PERCENT_BOTTOM_HEIGHT, panel_width, panel_width)
        
        self.create_left_panel(self.layout, listeners)
        self.create_right_panel(self.layout, listeners)
        
        self.file_button = self.factory.create_file_button(self.layout.CENTER, listeners[AUDIO_FILES])
        
        Container.add_component(self, self.file_button)        
        self.audio_files = self.get_audio_files()
        self.home_button.add_release_listener(listeners[KEY_HOME])
        self.shutdown_button.add_release_listener(listeners[KEY_SHUTDOWN])
        self.left_button.add_release_listener(self.go_left)
        self.right_button.add_release_listener(self.go_right)
        
        self.volume = self.factory.create_volume_control(self.layout.BOTTOM)
        self.volume.add_slide_listener(listeners[KEY_SET_VOLUME])
        self.volume.add_slide_listener(listeners[KEY_SET_CONFIG_VOLUME])
        self.volume.add_slide_listener(listeners[KEY_SET_SAVER_VOLUME])
        self.volume.add_knob_listener(listeners[KEY_MUTE])
        self.volume_visible = False
        self.volume.set_visible(self.volume_visible)
        Container.add_component(self, self.volume)
        
        self.time_control = self.factory.create_time_control(self.layout.BOTTOM)
        self.time_control.add_seek_listener(listeners[KEY_SEEK])
        
        self.play_button.add_listener(PAUSE, self.time_control.pause)
        self.play_button.add_listener(KEY_PLAY, self.time_control.resume)
        self.left_button.add_release_listener(self.play_button.draw_default_state)
        self.right_button.add_release_listener(self.play_button.draw_default_state)
        
        if self.config[PLAYER_SETTINGS][PAUSE]:
            self.time_control.pause()
        
        Container.add_component(self, self.time_control)

        self.play_listeners = []
        self.add_play_listener(listeners[KEY_PLAY])
        
        self.current_folder = self.config[FILE_PLAYBACK][CURRENT_FOLDER]
        self.file_button.state.cover_art_folder = self.util.file_util.get_cover_art_folder(self.current_folder)
        self.playlist_size = 0
        self.player_screen = True
        self.cd_album = None
        self.recursive_playback = False
        self.recursive_playback_start_folder = ""
        self.recursive_playback_current_folder = ""
    
    def get_audio_files(self):
        """ Return the list of audio files in current folder
        
        :return: list of audio files
        """
        files = []
        if self.config[CURRENT][MODE] == CD_PLAYER:
            af = getattr(self, "audio_files", None)
            if af == None:
                cd_drive_name = self.config[CD_PLAYBACK][CD_DRIVE_NAME]
                files = self.cdutil.get_cd_tracks_summary(cd_drive_name)
            else:
                return self.audio_files
        else:
            folder = self.config[FILE_PLAYBACK][CURRENT_FOLDER]
            files = self.util.get_audio_files_in_folder(folder)
            
        return files
    
    def get_current_track_index(self, state=None):
        """ Return current track index.
        In case of files goes through the file list.
        In case of playlist takes track index from the state object.
        
        :return: current track index
        """
        if self.config[CURRENT][MODE] == AUDIOBOOKS:
            t = None
            try:
                t = state["file_name"]
            except:
                pass
            
            if t == None:
                try:
                    t = state["current_title"]
                except:
                    pass
            
            if t == None:
                try:
                    t = state
                except:
                    pass
            
            for i, f in enumerate(self.audio_files):
                try:
                    s = f["file_name"]
                except:
                    pass
                
                if getattr(f, "file_name", None):
                    s = getattr(f, "file_name", None)
                
                if s.endswith(t):
                    return i
            return 0
        
        mode = self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE]       
        if state and mode == FILE_PLAYLIST:
            try:
                n = state["Track"]
                if n: return int(n) - 1
            except:
                pass

        if self.config[CURRENT][MODE] == CD_PLAYER:
            cmp = int(self.config[CD_PLAYBACK][CD_TRACK]) - 1
        else:
            cmp = self.config[FILE_PLAYBACK][CURRENT_FILE]
            if state and isinstance(state, State):
                cmp = state.file_name

        for f in self.audio_files:
            if self.config[CURRENT][MODE] == CD_PLAYER:
                if f.index == cmp:
                    return f.index
            else:
                if f.file_name == cmp:
                    return f.index
        return 0
        
    def go_left(self, state):
        """ Switch to the next track
        
        :param state: not used state object
        """        
        if getattr(self, "current_track_index", None) == None:
            return
        
        filelist_size = self.get_filelist_size()
         
        if self.current_track_index == 0:
            self.current_track_index = filelist_size - 1
        else:
            self.current_track_index -= 1
        self.change_track(self.current_track_index)
    
    def go_right(self, state):
        """ Switch to the previous track
        
        :param state: not used state object
        """
        if getattr(self, "current_track_index", None) == None:
            return
        
        filelist_size = self.get_filelist_size()
         
        if self.current_track_index == filelist_size - 1:
            self.current_track_index = 0
        else:
            self.current_track_index += 1
        
        self.change_track(self.current_track_index)
    
    def get_filelist_size(self):
        """ Return the file list size
        
        :return: file list size
        """
        if self.audio_files:
            return len(self.audio_files)
        else:
            return 0
    
    def change_track(self, track_index):
        """ Change track
        
        :param track_index: index track
        """
        a = [AUDIOBOOKS, CD_PLAYER]
        m = self.config[CURRENT][MODE]
        if not (m in a):
            self.config[FILE_PLAYBACK][CURRENT_FILE] = self.get_filename(track_index)
            
        self.stop_timer()
        time.sleep(0.3)
        s = State()
        if m == FILE_PLAYBACK:
            s.playback_mode = self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE]

        s.playlist_track_number = track_index
        s.index = track_index
        s.source = ARROW_BUTTON
        s.file_name = self.get_filename(track_index)
        
        if self.cd_album != None:
            s.album = self.cd_album
        
        self.set_current(True, s)
    
    def stop_timer(self):
        """ Stop time control timer """
        
        self.time_control.stop_timer()
    
    def get_filename(self, index):
        """ Get filename by index
        
        :param index: file index
        
        :return: filename
        """        
        for b in self.audio_files:
            if b.index == index:
                return b.file_name
        return ""
    
    def is_valid_mode(self):
        current_mode = self.config[CURRENT][MODE]
        modes = [AUDIO_FILES, AUDIOBOOKS, CD_PLAYER]
        if current_mode in modes:
            return True
        else:
            return False
    
    def update_arrow_button_labels(self, state=None):
        """ Update left/right arrow button labels
        
        :param state: state object representing current track
        """
        if (not self.is_valid_mode()) or (not self.screen_title.active): return
        
        self.set_current_track_index(state)
        left = self.current_track_index
        right = 0
        
        if self.audio_files and len(self.audio_files) > 1: 
            right = len(self.audio_files) - self.current_track_index - 1
            
        self.left_button.change_label(str(left))
        self.right_button.change_label(str(right))
        
    def set_current_track_index(self, state):
        """ Set current track index
        
        :param state: state object representing current track
        """
        if not self.is_valid_mode(): return
        
        if self.config[CURRENT][MODE] == CD_PLAYER and getattr(state, "cd_track_id", None):
            self.config[CD_PLAYBACK][CD_TRACK] = state["cd_track_id"]
        
        self.current_track_index = 0
        
        if self.playlist_size == 1:            
            return
        
        if not self.audio_files:
            self.audio_files = self.get_audio_files()            
            if not self.audio_files: return
        
        i = self.get_current_track_index(state)
        self.current_track_index = i
    
    def create_left_panel(self, layout, listeners):
        """ Create left side buttons panel
        
        :param layout: panel layout 
        :param listeners: button listeners 
        """
        panel_layout = BorderLayout(layout.LEFT)
        panel_layout.set_percent_constraints(PERCENT_SIDE_BOTTOM_HEIGHT, PERCENT_SIDE_BOTTOM_HEIGHT, 0, 0)
        self.left_button = self.factory.create_left_button(panel_layout.CENTER, '', 40, 100)
        self.shutdown_button = self.factory.create_shutdown_button(panel_layout.TOP)
        self.home_button = self.factory.create_button(KEY_HOME, KEY_HOME, panel_layout.BOTTOM, image_size_percent=36)
        panel = Container(self.util, layout.LEFT)
        panel.add_component(self.shutdown_button)
        panel.add_component(self.left_button)
        panel.add_component(self.home_button)
        Container.add_component(self, panel)
    
    def create_right_panel(self, layout, listeners):
        """ Create right side buttons panel
        
        :param layout: panel layout 
        :param listeners: button listeners 
        """
        panel_layout = BorderLayout(layout.RIGHT)
        panel_layout.set_percent_constraints(PERCENT_SIDE_BOTTOM_HEIGHT, PERCENT_SIDE_BOTTOM_HEIGHT, 0, 0)
        self.play_button = self.factory.create_play_pause_button(panel_layout.TOP, listeners[KEY_PLAY_PAUSE])
        self.right_button = self.factory.create_right_button(panel_layout.CENTER, '', 40, 100)
        self.time_volume_button = self.factory.create_time_volume_button(panel_layout.BOTTOM, self.toggle_time_volume)
        panel = Container(self.util, layout.RIGHT)
        panel.add_component(self.play_button)
        panel.add_component(self.right_button)
        panel.add_component(self.time_volume_button)
        Container.add_component(self, panel)
    
    def toggle_time_volume(self):
        """ Switch between time and volume controls """
        
        if self.volume_visible:
            self.volume.set_visible(False)
            self.time_control.set_visible(True)
            self.volume_visible = False
        else:
            volume_level = int(self.config[PLAYER_SETTINGS][VOLUME])
            self.volume.set_position(volume_level)
            self.volume.update_position()
            self.volume.set_visible(True)
            self.time_control.set_visible(False)
            self.volume_visible = True
        self.clean_draw_update()
    
    def eject_cd(self, state):
        """ Eject CD
        
        :param state: button state object
        """
        self.audio_files = []
        self.screen_title.set_text(" ")
        self.update_arrow_button_labels(state)
        self.time_control.reset()
        self.cd_album = None
        self.set_cd_album_art_image()   
    
    def set_current(self, new_track=False, state=None):
        """ Set current file or playlist
        
        :param new_track: True - new audio file
        """
        self.cd_album = getattr(state, "album", None)
        
        self.recursive_playback = getattr(state, "recursive_playback", False)
        if self.recursive_playback:
            self.recursive_playback_start_folder = self.recursive_playback_current_folder
            logging.debug(self.recursive_playback_start_folder)
        
        if self.config[CURRENT][MODE] == AUDIO_FILES:
            self.set_audio_file_image()
        elif self.config[CURRENT][MODE] == CD_PLAYER and getattr(state, "source", None) != INIT:
            self.set_cd_album_art_image()
            state.image_base = self.file_button.components[1].content
                        
        config_volume_level = int(self.config[PLAYER_SETTINGS][VOLUME])
        if state:
            state.volume = config_volume_level
            
        self.set_audio_file(new_track, state)
        
        if self.volume.get_position() != config_volume_level:
            self.volume.set_position(config_volume_level)
            self.volume.update_position()
    
    def set_audio_file_image(self):
        """ Set audio file image """
        
        f = self.config[FILE_PLAYBACK][CURRENT_FOLDER]
        if not f: return
        
        img_tuple = self.util.get_audio_file_icon(f, self.layout.CENTER)
        self.set_file_button(img_tuple)
    
    def set_cd_album_art_image(self):
        """ Set CD album art image """
        
        img_tuple = self.util.get_cd_album_art(self.cd_album, self.layout.CENTER)
        if img_tuple == None:
            return
        self.set_file_button(img_tuple)
        self.file_button.clean_draw_update()
    
    def set_file_button(self, img_tuple):
        """ Set image in file button
        
        :param img_tuple: tuple where first element is image location, second element image itself 
        """
        img = img_tuple[1]
        self.file_button.components[1].content = img
        self.file_button.state.icon_base = img
        self.file_button.components[1].image_filename = self.file_button.state.image_filename = img_tuple[0]
        
        self.file_button.components[1].content_x = self.layout.CENTER.x + (self.layout.CENTER.w - img.get_size()[0]) / 2
        
        if self.layout.CENTER.h > img.get_size()[1]:
            self.file_button.components[1].content_y = self.layout.CENTER.y + int((self.layout.CENTER.h - img.get_size()[1])/2) + 1
        else:
            self.file_button.components[1].content_y = self.layout.CENTER.y
        
    def set_audio_file(self, new_track, s=None):
        """ Set new audio file
        
        :param new_track: True - new audio file
        "param s" button state object
        """
        state = State()
        
        if s:
            state.playback_mode = getattr(s, "playback_mode", FILE_AUDIO)
            state.playlist_track_number = getattr(s, "playlist_track_number", None)
            if self.config[CURRENT][MODE] == CD_PLAYER and getattr(s, "source", None) != INIT:
                image_base = getattr(s, "image_base", None)
                if image_base != None:
                    state.image_base = image_base
        else:
            m = self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE]
            if m:
                state.playback_mode = m
            else:
                state.playback_mode = FILE_AUDIO
        
        if self.config[CURRENT][MODE] == AUDIO_FILES:            
            self.current_folder = self.config[FILE_PLAYBACK][CURRENT_FOLDER]        
            if not self.current_folder:
                return                
            state.folder = self.current_folder
            state.file_name = self.config[FILE_PLAYBACK][CURRENT_FILE]
            if state.folder[-1] == os.sep:
                state.folder = state.folder[:-1]
                
            if os.sep in state.file_name:
                state.url = "\"" + state.file_name + "\""
            else:
                state.url = "\"" + state.folder + os.sep + state.file_name + "\""
            
            state.music_folder = self.config[AUDIO][MUSIC_FOLDER]
        elif self.config[CURRENT][MODE] == CD_PLAYER:
            state.file_name = s.file_name
            state.url = getattr(s, "url", s.file_name)
            parts = s.file_name.split()
            self.config[CD_PLAYBACK][CD_DRIVE_NAME] = parts[0][len("cdda:///"):]
            id = self.cdutil.get_cd_drive_id_by_name(self.config[CD_PLAYBACK][CD_DRIVE_NAME]) 
            self.config[CD_PLAYBACK][CD_DRIVE_ID] = int(id)
            self.config[CD_PLAYBACK][CD_TRACK] = int(parts[1].split("=")[1])             

        state.mute = self.config[PLAYER_SETTINGS][MUTE]
        state.pause = self.config[PLAYER_SETTINGS][PAUSE]
        state.file_type = FILE_AUDIO
        state.dont_notify = True
        state.source = FILE_AUDIO        
        
        if self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] == FILE_AUDIO or self.config[CURRENT][MODE] == CD_PLAYER:
            self.audio_files = self.get_audio_files()            
        elif self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] == FILE_PLAYLIST:
            state.file_name = self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYLIST]
            self.load_playlist(state)
            state.file_name = self.config[FILE_PLAYBACK][CURRENT_FILE]
            self.audio_files = self.get_audio_files_from_playlist()
            state.playback_mode = FILE_PLAYLIST
            n = getattr(s, "file_name", None)
            if n:
                state.file_name = n
            
            try:
                state.playlist_track_number = int(state.file_name) - 1
            except:
                state.playlist_track_number = self.get_current_track_index(state)

        source = None
        if s:
            source = getattr(s, "source", None)

        if new_track:
            tt = 0.0
        else:        
            if self.config[CURRENT][MODE] == CD_PLAYER:
                tt = self.config[CD_PLAYBACK][CD_TRACK_TIME] 
            else:
                tt = self.config[FILE_PLAYBACK][CURRENT_TRACK_TIME]
                    
        if (isinstance(tt, str) and len(tt) != 0) or (isinstance(tt, float) or (source and source == RESUME)) or isinstance(tt, int):
            state.track_time = tt
        
        self.time_control.slider.set_position(0)
            
        if self.file_button and self.file_button.components[1] and self.file_button.components[1].content:
            state.icon_base = self.file_button.components[1].content
        
        if s and s.volume:
            state.volume = s.volume
            
        if self.config[CURRENT][MODE] == CD_PLAYER and s and getattr(s, "source", None) == INIT:
            try:
                self.cd_album = self.util.cd_titles[self.config[CD_PLAYBACK][CD_DRIVE_NAME]]
                self.set_cd_album_art_image()
                state.image_base = self.file_button.components[1].content
            except:
                self.cd_album = None 
            
        self.notify_play_listeners(state)
    
    def get_audio_files_from_playlist(self):
        """ Call player for files in the playlist 
        
        :return: list of files from playlist
        """
        playlist = self.get_current_playlist()
        files = []
        if playlist:
            for n in range(len(playlist)):
                st = State()
                st.index = st.comparator_item = n
                st.file_type = FILE_AUDIO
                st.file_name = playlist[n]
                files.append(st)
        return files
    
    def restore_current_folder(self, state=None):
        """ Set current folder in config object
        
        :param state: not used
        """
        self.config[FILE_PLAYBACK][CURRENT_FOLDER] = self.current_folder
    
    def set_audio_file_playlist(self, index):
        """ Set file in playlist
        
        :param index: file index in playlist
        """
        state = State()
        state.playback_mode = FILE_PLAYLIST
        state.playlist_track_number = index
        state.file_type = FILE_AUDIO
        self.current_folder = self.config[FILE_PLAYBACK][CURRENT_FOLDER]
        self.notify_play_listeners(state)
    
    def go_back(self):
        """ Go back """
        
        if self.config[CURRENT][MODE] == CD_PLAYER:
            return
        
        img_tuple = self.util.get_audio_file_icon(self.current_folder, self.layout.CENTER)
        img = img_tuple[1]
        self.file_button.components[1].content = img
        self.file_button.state.icon_base = img_tuple
        
        self.file_button.components[1].content_x = self.layout.CENTER.x
        if self.layout.CENTER.h > img.get_size()[1]:
            self.file_button.components[1].content_y = self.layout.CENTER.y + int((self.layout.CENTER.h - img.get_size()[1])/2)
        else:
            self.file_button.components[1].content_y = self.layout.CENTER.y
            
    def end_of_track(self):
        """ Handle end of track """

        if not self.screen_title.active:
            return

        i = getattr(self, "current_track_index", None)
        if i == None: return
        self.stop_timer()
        mode = self.config[CURRENT][MODE]
        if mode == RADIO or mode == STREAM or not self.audio_files:
            return
        
        self.time_control.stop_thread()

        if self.config[AUTO_PLAY_NEXT_TRACK]:
            if self.current_track_index == len(self.audio_files) - 1 and self.config[CYCLIC_PLAYBACK]:
                self.current_track_index = 0
            else:
                self.current_track_index += 1
                
            if mode == AUDIO_FILES:          
                self.config[FILE_PLAYBACK][CURRENT_TRACK_TIME] = None
            elif mode == AUDIOBOOKS:
                self.config[AUDIOBOOKS][BROWSER_BOOK_TIME] = None
                
            self.change_track(self.current_track_index)
    
    def set_playlist_size(self, size):
        """ Set playlist size
        
        :param size: playlist size
        """
        self.playlist_size = size
        self.stop_timer()
    
    def set_visible(self, flag):
        """ Set visibility flag
         
        :param flag: True - screen visible, False - screen invisible
        """
        Container.set_visible(self, flag)
        
        if flag:
            if self.volume_visible:
                self.volume.set_visible(True)
                self.time_control.set_visible(False)
            else:
                self.volume.set_visible(False)
                self.time_control.set_visible(True)            

    def add_play_listener(self, listener):
        """ Add play listener
        
        :param listener: event listener
        """
        if listener not in self.play_listeners:
            self.play_listeners.append(listener)
            
    def notify_play_listeners(self, state):
        """ Notify all play listeners
        
        :param state: button state
        """
        if not self.screen_title.active:
            return
        
        m = getattr(state, "playback_mode", None)
        if m != None and m != FILE_PLAYLIST:
            state.icon_base = self.file_button.state.icon_base
        folder = getattr(state, "folder", None)
        if folder:
            state.cover_art_folder = self.util.file_util.get_cover_art_folder(state.folder)

        for listener in self.play_listeners:
            listener(state)
            
    def enable_player_screen(self, flag):
        """ Enable player screen
        
        :param flag: enable/disable flag
        """
        self.screen_title.active = flag
        self.time_control.active = flag

    def add_screen_observers(self, update_observer, redraw_observer, start_time_control, stop_time_control, title_to_json):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        :param start_time_control:
        :param stop_time_control:
        :param title_to_json:
        """
        Screen.add_screen_observers(self, update_observer, redraw_observer, title_to_json)
        
        self.add_button_observers(self.shutdown_button, update_observer, redraw_observer=None)    
        self.shutdown_button.add_cancel_listener(redraw_observer)
        self.screen_title.add_listener(redraw_observer)
                 
        self.add_button_observers(self.play_button, update_observer, redraw_observer=None)
        self.add_button_observers(self.home_button, update_observer, redraw_observer)
         
        self.add_button_observers(self.left_button, update_observer, redraw_observer=None)
        self.left_button.add_label_listener(update_observer)
        self.add_button_observers(self.right_button, update_observer, redraw_observer=None)
        self.right_button.add_label_listener(update_observer)
                         
        self.volume.add_slide_listener(update_observer)
        self.volume.add_knob_listener(update_observer)
        self.volume.add_press_listener(update_observer)
        self.volume.add_motion_listener(update_observer)
         
        self.add_button_observers(self.time_volume_button, update_observer, redraw_observer, release=False)
        self.add_button_observers(self.file_button, update_observer, redraw_observer, press=False, release=False)
        
        self.time_control.web_seek_listener = update_observer        
        self.time_control.add_start_timer_listener(start_time_control)
        self.time_control.add_stop_timer_listener(stop_time_control)        
        self.time_control.slider.add_slide_listener(update_observer)
        self.time_control.slider.add_knob_listener(update_observer)
        self.time_control.slider.add_press_listener(update_observer)
        self.time_control.slider.add_motion_listener(update_observer)
