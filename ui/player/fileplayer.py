# Copyright 2016-2024 Peppy Player peppy.player@gmail.com
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
import random
import logging

from ui.state import State
from util.keys import *
from util.config import *
from util.fileutil import FILE_AUDIO, FILE_PLAYLIST, FOLDER, FILE_RECURSIVE
from ui.player.player import PlayerScreen
from ui.button.button import Button

class FilePlayerScreen(PlayerScreen):
    """ File Player Screen """
    
    def __init__(self, listeners, util, get_current_playlist, volume_control, \
        show_arrow_labels=True, show_order=True, show_info=True, show_time_control=True):
        """ Initializer
        
        :param listeners: screen listeners
        :param util: utility object
        :param get_current_playlist: current playlist getter
        :param volume_control: volume control
        """
        self.util = util
        self.config = util.config
        self.bounding_box = util.screen_rect
        self.image_util = util.image_util
        self.listeners = listeners
        try:
            self.center_button_listener = listeners[AUDIO_FILES]
        except:
            pass

        PlayerScreen.__init__(self, util, listeners, "file_screen_title", show_arrow_labels, show_order, \
            show_info, show_time_control, volume_control)

        self.set_custom_button()    
        self.center_button = self.get_center_button()
        self.add_component(self.center_button)
        self.add_component(self.order_popup)
        self.add_component(self.info_popup)
        self.set_listeners(listeners)

        self.current_button = self.center_button
        self.get_current_playlist = get_current_playlist
        self.audio_files = self.get_audio_files()
        self.play_listeners = []
        self.add_play_listener(self.get_listener(listeners, KEY_PLAY))
        
        self.current_folder = self.config[FILE_PLAYBACK][CURRENT_FOLDER]
        self.center_button.state.cover_art_folder = self.util.file_util.get_cover_art_folder(self.current_folder)
        self.playlist_size = 0

        self.link_borders()
        self.current_button = self.center_button
        self.current_button.set_selected(True)
        self.current_playlist_file = None

        if not self.config[PLAYER_SCREEN][SHOW_TIME_SLIDER]:
            self.toggle_time_volume()
            self.custom_button.draw_state(1)

    def set_custom_button(self):
        """ Set the custom buttom """

        self.custom_button = self.factory.create_time_volume_button(self.custom_button_layout, self.toggle_time_volume)
        self.right_panel.add_component(self.custom_button)

    def set_center_button(self, img_tuple=None):
        """ Set the center button """

        full_screen_image = img_tuple[1]
        self.center_button.state.full_screen_image = full_screen_image
        
        scale_ratio = self.image_util.get_scale_ratio((self.layout.CENTER.w - 2, self.layout.CENTER.h - 2), full_screen_image)
        img = self.image_util.scale_image(full_screen_image, scale_ratio)
        
        self.center_button.components[1].content = img
        self.center_button.state.icon_base = img
        self.center_button.components[1].image_filename = self.center_button.state.image_filename = img_tuple[0]
        
        self.center_button.components[1].content_x = self.layout.CENTER.x + (self.layout.CENTER.w - img.get_size()[0]) / 2
        
        if self.layout.CENTER.h > img.get_size()[1]:
            self.center_button.components[1].content_y = self.layout.CENTER.y + int((self.layout.CENTER.h - img.get_size()[1])/2)
        else:
            self.center_button.components[1].content_y = self.layout.CENTER.y

        self.set_background(full_screen_image)

        self.center_button.selected = True
        self.link_borders()

    def set_background(self, image):
        """ Set album art as a screen background

        :param image: image to set as a background
        """
        if image == None or self.config[BACKGROUND][BGR_TYPE] != USE_ALBUM_ART:
            return

        i = self.image_util.get_album_art_bgr(image)
        if i != self.content:
            self.content = i

    def get_center_button(self):
        """ Create default audio file button
        
        :return: default audio file button
        """
        state = State()
        bb = self.layout.CENTER

        state.icon_base = self.image_util.get_audio_file_icon("", bb)
        state.scaled = False
        state.name = "cd"
        state.keyboard_key = kbd_keys[KEY_SELECT]
        state.bounding_box = bb
        state.img_x = bb.x
        state.img_y = bb.y
        state.auto_update = False
        state.show_bgr = False
        state.show_img = True
        state.image_align_v = V_ALIGN_CENTER
        state.source = FILE_BUTTON
        button = Button(self.util, state)
        try:
            button.add_release_listener(self.center_button_listener)
        except:
            pass
        return button

    def get_audio_files(self):
        """ Return the list of audio files in current folder
        
        :return: list of audio files
        """
        folder = self.config[FILE_PLAYBACK][CURRENT_FOLDER]
        load_images = self.config[ENABLE_EMBEDDED_IMAGES]
        return self.util.get_audio_files_in_folder(folder, load_images=load_images)
    
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

        cmp = self.config[FILE_PLAYBACK][CURRENT_FILE]
        if state and isinstance(state, State):
            cmp = state.file_name

        for f in self.audio_files:
            if f.file_name == cmp:
                return f.index

        return 0
    
    def stop_recursive_playback(self):
        """ Stop recursive playback """
        
        self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] = FILE_AUDIO
        self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYLIST] = None
        self.config[FILE_PLAYBACK][CURRENT_TRACK_TIME] = None
        self.stop_timer()
        if self.show_time_control:
            self.time_control.stop_thread()
            self.time_control.reset()
        if self.stop_player != None:
            self.stop_player()

        self.update_component = True
        
    def go_left(self, state):
        """ Switch to the previous track
        
        :param state: NA
        """        
        if getattr(self, "current_track_index", None) == None:
            return
        
        filelist_size = self.get_filelist_size()
        
        if self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] == FILE_RECURSIVE:
            self.stop_recursive_playback()
            return
        
        if self.current_track_index == 0:
            self.current_track_index = filelist_size - 1
        else:
            self.current_track_index -= 1
        self.change_track(self.current_track_index)
    
    def go_right(self, state):
        """ Switch to the next track
        
        :param state: NA
        """
        if getattr(self, "current_track_index", None) == None:
            return
        
        filelist_size = self.get_filelist_size()
        
        if self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] == FILE_RECURSIVE and self.current_track_index == filelist_size - 1:
            self.stop_timer()
            if self.show_time_control:
                self.time_control.stop_thread()
            self.recursive_change_folder()
            self.current_track_index = 0
            self.change_track(self.current_track_index)
            self.update_component = True
            return
         
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
        self.stop_timer()
        time.sleep(0.3)
        s = State()
        if self.config[CURRENT][MODE] == FILE_PLAYBACK:
            s.playback_mode = self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE]

        s.playlist_track_number = track_index
        s.index = track_index
        s.source = ARROW_BUTTON
        s.file_name = self.get_filename(track_index)
        self.config[FILE_PLAYBACK][CURRENT_FILE] = s.file_name

        if self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] == FILE_PLAYLIST:
            if track_index == None:
                self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYLIST_INDEX] = ""
            else:
                self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYLIST_INDEX] = track_index
            s.url = s.file_name
        else:
            folder = self.current_folder
            if not folder.endswith(os.sep):
                folder += os.sep
            s.url = folder + s.file_name

        self.set_current(True, s)
        self.update_component = True

    def stop_timer(self):
        """ Stop time control timer """
        
        if self.show_time_control:
            self.time_control.stop_timer()

        self.update_component = True
    
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
        return True
    
    def update_arrow_button_labels(self, state=None):
        """ Update left/right arrow button labels
        
        :param state: state object representing current track
        """
        if (not self.is_valid_mode()) or (not self.enabled): return
        
        self.set_current_track_index(state)
        left = self.current_track_index
        right = 0
        
        if self.audio_files and len(self.audio_files) > 1: 
            right = len(self.audio_files) - self.current_track_index - 1
            
        self.left_button.change_label(str(left))
        self.right_button.change_label(str(right))

        self.update_component = True

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

        if self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] == FILE_PLAYLIST:
            index = self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYLIST_INDEX]
            if index:
                self.current_track_index = index
        else:
            self.current_track_index = self.get_current_track_index(state)

        self.update_component = True
    
    def toggle_time_volume(self):
        """ Switch between time and volume controls """
        
        if self.volume_visible:
            self.volume.set_visible(False)
            if self.show_time_control:
                self.time_control.set_visible(True)                
            self.volume_visible = False
        else:
            volume_level = int(self.config[PLAYER_SETTINGS][VOLUME])
            self.volume.set_position(volume_level)
            self.volume.update_position()
            self.volume.set_visible(True)
            if self.show_time_control:
                self.time_control.set_visible(False)
            self.volume_visible = True

        self.update_component = True
    
    def set_current(self, new_track=False, state=None):
        """ Set current file or playlist
        
        :param new_track: True - new audio file
        :param state: button state
        """
        if getattr(state, "url", None) is None:
            state.url = None

        if getattr(state, "source", None) == "home":
            state.file_name = state.url = self.config[FILE_PLAYBACK][CURRENT_FILE]
            state.index = self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYLIST_INDEX]
            state.playback_mode = self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE]
            state.track_time = self.config[FILE_PLAYBACK][CURRENT_TRACK_TIME]
                        
        config_volume_level = int(self.config[PLAYER_SETTINGS][VOLUME])
        if state:
            if self.config[VOLUME_CONTROL][VOLUME_CONTROL_TYPE] == VOLUME_CONTROL_TYPE_PLAYER:
                state.volume = config_volume_level
            else:
                state.volume = None
            
        self.set_audio_file(new_track, state)
        self.refresh_volume()
        self.update_component = True
    
    def set_audio_file_image(self, url=None, folder=None):
        """ Set audio file image

        :param url: audio file name
        :param folder: folder name

        :return: image
        """
        if folder:
            f = folder
        else:
            f = self.config[FILE_PLAYBACK][CURRENT_FOLDER]

        if not f: return None
        
        img_tuple = self.image_util.get_audio_file_icon(f, self.bounding_box, url)
        self.set_center_button(img_tuple)
        self.update_component = True
        
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
        else:
            m = self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE]
            if m:
                state.playback_mode = m
            else:
                state.playback_mode = FILE_AUDIO
        
        self.current_folder = self.config[FILE_PLAYBACK][CURRENT_FOLDER]
        if not self.current_folder:
            return
        state.folder = self.current_folder
        state.file_name = self.config[FILE_PLAYBACK][CURRENT_FILE]
        if state.folder[-1] == os.sep:
            state.folder = state.folder[:-1]

        if self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] == FILE_PLAYLIST:
            playlist_path = self.config[FILE_PLAYBACK][CURRENT_FOLDER] + os.sep + self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYLIST]
            if self.current_playlist_file != playlist_path:
                state.file_name = self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYLIST]
                self.load_playlist(state)
                self.audio_files = self.get_audio_files_from_playlist()
                self.util.prepend_playlist_items(state.folder, self.audio_files)
                self.current_playlist_file = playlist_path

            if hasattr(s, "playlist_track_number"):
                self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYLIST_INDEX] = int(getattr(s, "playlist_track_number"))
            elif hasattr(s, "index"):
                self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYLIST_INDEX] = int(s.index)

            index = int(self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYLIST_INDEX])
            state.file_name = state.url = self.get_filename(index)
        else:
            self.current_playlist_file = None
            if os.sep in state.file_name:
                state.url = "\"" + state.file_name + "\""
            else:
                state.url = "\"" + state.folder + os.sep + state.file_name + "\""
            
        state.full_screen_image = self.set_audio_file_image(state.url.replace('\"', ""))
        state.music_folder = self.config[MUSIC_FOLDER]

        self.config[PLAYER_SETTINGS][PAUSE] = False
        state.mute = self.config[PLAYER_SETTINGS][MUTE]
        state.pause = self.config[PLAYER_SETTINGS][PAUSE]
        self.play_button.draw_default_state(None)
        state.file_type = FILE_AUDIO
        state.dont_notify = True
        state.source = FILE_AUDIO
        
        if self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] == FILE_AUDIO:
            self.audio_files = self.get_audio_files()            
        elif self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] == FILE_PLAYLIST:
            state.playback_mode = FILE_PLAYLIST
            index = self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYLIST_INDEX]
            state.file_name = state.url = self.get_filename(index)
            state.index = getattr(s, "index", "") or getattr(s, "playlist_track_number", "")
            state.file_playlist = self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYLIST]

        source = None
        if s:
            source = getattr(s, "source", None)

        if new_track:
            tt = 0.0
        else:        
            tt = self.config[FILE_PLAYBACK][CURRENT_TRACK_TIME]
                    
        if (isinstance(tt, str) and len(tt) != 0) or (isinstance(tt, float) or (source and source == RESUME)) or isinstance(tt, int):
            state.track_time = tt

        if self.show_time_control:
            self.time_control.slider.set_position(0)
            
        if self.center_button and self.center_button.components[1] and self.center_button.components[1].content:
            state.icon_base = self.center_button.components[1].content
        
        if s and hasattr(s, "volume"):
            state.volume = s.volume
            
        if getattr(s, "full_screen_image", None) != None:
             state.full_screen_image = s.full_screen_image
        
        song_name = self.get_song_name(s)
        if song_name != None:
            state.album = song_name

        self.notify_play_listeners(state)
        self.update_component = True

    def add_url(self, folder, playlist):
        for n in playlist:
            if not n.file_name.startswith(os.sep):
                n.file_name = n.url = folder + os.sep + n.file_name

    def handle_order_popup_selection(self, state):
        """ Handle playback order menu selection

        :param state: button state
        """
        super().handle_order_popup_selection(state)

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
                m = self.util.get_file_metadata()
                a = m["artist"] + " - " + m["title"]
            except:
                pass
            if a != None:
                s = State()
                s.album = a
                self.start_screensaver(n, s)
            else:
                self.start_screensaver(n)
        else:
            self.go_info_screen(state)

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
        self.update_component = True
    
    def recursive_change_folder(self):
        start_folder = self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYLIST]
        current_folder = self.config[FILE_PLAYBACK][CURRENT_FOLDER]
        f = self.util.file_util.get_next_folder_with_audio_files(start_folder, current_folder)
        if f == None or (f != None and f[0] == None):
            self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] = FILE_AUDIO
            self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYLIST] = None
            return False
            
        self.config[FILE_PLAYBACK][CURRENT_FOLDER] = f[0]
        self.config[FILE_PLAYBACK][CURRENT_FILE] = f[1] 
        self.config[FILE_PLAYBACK][CURRENT_TRACK_TIME] = None
        state = State()
        state.file_type = FOLDER
        state.url = f[0]
        state.long_press = True
        state.playback_mode = FILE_RECURSIVE
        self.current_track_index = 0
        state.dont_notify = True
        self.audio_files = self.get_audio_files()
        self.recursive_notifier(f[0])
        return True
            
    def end_of_track(self):
        """ Handle end of track """

        if not self.enabled:
            return

        i = getattr(self, "current_track_index", None)
        if i == None: return
        self.stop_timer()
        mode = self.config[CURRENT][MODE]
        if mode == RADIO or mode == STREAM or not self.audio_files:
            return
        
        if self.show_time_control:
            self.time_control.stop_thread()

        playback_mode = self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE]
        if playback_mode == FILE_RECURSIVE:
            if self.current_track_index == (len(self.audio_files) - 1):
                if not self.recursive_change_folder():
                    self.stop_recursive_playback()
                    return
                else:
                    index = 0
            else:
                index = self.current_track_index + 1
        else:
            index = self.get_next_index()

        if index == None:
            self.time_control.stop_thread()
            self.time_control.reset()
            return
        else:
            self.current_track_index = index

        self.config[FILE_PLAYBACK][CURRENT_TRACK_TIME] = None
        self.change_track(index)
        self.update_component = True
    
    def get_next_index(self):
        """ Return next file index

        :return: file index or None
        """
        order = self.config[PLAYER_SETTINGS][PLAYBACK_ORDER]
        n = self.current_track_index
        last = len(self.audio_files) - 1

        if order == PLAYBACK_SINGLE_TRACK:
            return None

        if order == PLAYBACK_SINGLE_CYCLIC:
            return n

        if order == PLAYBACK_CYCLIC:
            if n == last:
                return 0
            else:
                return n + 1
        elif order == PLAYBACK_REGULAR:
            if n == last:
                return None
            else:
                return n + 1
        elif order == PLAYBACK_SHUFFLE:
            if len(self.audio_files) == 1:
                return n
            else:
                return random.randint(0, last)

    def set_playlist_size(self, size):
        """ Set playlist size
        
        :param size: playlist size
        """
        self.playlist_size = size
    
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
            state.icon_base = self.center_button.state.icon_base
        folder = getattr(state, "folder", None)
        if folder:
            state.cover_art_folder = self.util.file_util.get_cover_art_folder(state.folder)

        for listener in self.play_listeners:
            try:
                listener(state)
            except Exception as e:
                logging.debug(e)
    
    def enable_player_screen(self, flag):
        """ Enable player screen
        
        :param flag: enable/disable flag
        """
        self.screen_title.active = flag
        self.enabled = flag
        if self.show_time_control:
            self.time_control.active = flag

        self.update_component = True
