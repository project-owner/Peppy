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

import logging
import time

from ui.player.fileplayer import FilePlayerScreen
from util.keys import BOOK_MENU, HOME_NAVIGATOR, \
    TRACK_MENU, BOOK_NAVIGATOR_BACK, ARROW_BUTTON, INIT, BOOK_NAVIGATOR, LABELS, KEY_LOADING, GO_PLAYER, RESUME
from ui.state import State
from util.fileutil import FILE_AUDIO
from util.config import AUDIO, MUSIC_FOLDER, AUDIOBOOKS, VOLUME, \
    BROWSER_TRACK_FILENAME, BROWSER_BOOK_TIME, BROWSER_BOOK_TITLE, BROWSER_BOOK_URL, \
    COLOR_DARK, COLORS, COLOR_BRIGHT, COLOR_MEDIUM, PLAYER_SETTINGS, MUTE, PAUSE, \
    VOLUME_CONTROL, VOLUME_CONTROL_TYPE, VOLUME_CONTROL_TYPE_PLAYER, BROWSER_IMAGE_URL
from util.cache import Cache
import pygame

class BookPlayer(FilePlayerScreen):
    """ Book Player Screen """
    
    def __init__(self, listeners, util, site_parser, voice_assistant, volume_control):
        """ Initializer
        
        :param listeners: screen listeners
        :param util: utility object 
        :param site_parser: site parser 
        :param voice_assistant: voice assistant
        :param volume_control: volume control       
        """
        FilePlayerScreen.__init__(self, listeners, util, self.get_playlist, voice_assistant, volume_control)
        self.config = util.config
        self.image_util = util.image_util

        self.current_playlist = None        
        self.parser = site_parser
        self.cache = Cache(self.util)
        self.current_book_state = None
        self.current_track_index = 0        
        self.playlist = self.get_playlist()
        self.audio_files = self.get_audio_files_from_playlist()
        self.loading_listeners = []
        self.reset_loading_listeners = []
        self.LOADING = util.config[LABELS][KEY_LOADING]
    
    def get_playlist(self):
        """ Return current playlist
        
        :return: playlist
        """
        return self.current_playlist
    
    def set_book(self, new_track, state=None):
        """ Set book
        
        :param new_track: flag defining if track is new
        :param state: button state object 
        """
        self.set_loading()
        
        self.current_book_state = state
        img_url = None
        if hasattr(state, "event_origin"):
            img_url = state.event_origin.state.icon_base[0]
        elif hasattr(state, "img_url"):
            img_url = state.img_url
        self.current_playlist = self.parser.get_book_audio_files_by_url(state.book_url, img_url)
        state.url = self.parser.book_parser.img_url
        
        img = self.cache.get_image(state.url)
        if img == None:
            i = self.image_util.load_image_from_url(state.url)
            if i:
                self.cache.cache_image(i[1], state.url)
                img = i[1]
        
        bb = self.center_button.bounding_box
        w = bb.w
        h = bb.h
        self.cover_image = self.image_util.scale_image_with_padding(w, h, img, padding=1)        
        
        self.screen_title.set_text(state.name)
        
        if self.current_playlist == None:
            return
        
        self.playlist = self.current_playlist
        
        if new_track and self.playlist:
            self.config[AUDIOBOOKS][BROWSER_BOOK_TITLE] = state.name
            self.config[AUDIOBOOKS][BROWSER_BOOK_URL] = state.book_url
            self.config[AUDIOBOOKS][BROWSER_IMAGE_URL] = img_url
            self.config[AUDIOBOOKS][BROWSER_TRACK_FILENAME] = self.playlist[0]["title"]
            state.track_time = self.config[AUDIOBOOKS][BROWSER_BOOK_TIME] = "0"
        elif not new_track:
            state.track_time = self.config[AUDIOBOOKS][BROWSER_BOOK_TIME] 
        
        self.audio_files = self.playlist        
        
    def set_current(self, new_track=False, state=None):
        """ Set current file 
        
        :param new_track: True - new audio file
        :param state: button state object 
        """
        if state.source == BOOK_MENU or state.source == INIT:
            if self.current_book_state and self.current_book_state.book_url == state.book_url and self.time_control.timer_started:
                return
            
            self.current_track_index = 0
            if state.source == INIT:
                new_track = False
            else:
                new_track = True
            self.set_book(new_track, state)
        elif state.source == TRACK_MENU:
            if getattr(state, "index", None) and state.index == self.current_track_index:
                return
            new_track = True
            st = {"file_name": state.file_name}
            self.set_current_track_index(st)
        elif state.source == ARROW_BUTTON:
            new_track = True
            st = {"file_name": state.file_name}
            self.set_current_track_index(st)
        elif state.source == RESUME:
            new_track = False
            st = {"file_name": state.file_name}
            self.set_current_track_index(st)
        elif state.source == HOME_NAVIGATOR or state.source == BOOK_NAVIGATOR_BACK or state.source == BOOK_NAVIGATOR or state.source == GO_PLAYER:
            return        
        
        if getattr(state, "url", None):
            self.center_button.components[1].image_filename = self.img_filename = state.url
        else:
            if hasattr(self, "img_filename"):
                self.center_button.components[1].image_filename = self.img_filename
            else:
                self.center_button.components[1].image_filename = self.img_filename = None
        img = self.cover_image
        if img:
            self.center_button.components[1].content = img
            self.center_button.state.icon_base = img
            self.center_button.state.show_bgr = True
            self.center_button.state.bgr = self.config[COLORS][COLOR_MEDIUM]
            self.center_button.add_background(self.center_button.state)
            self.center_button.components[1].content_x = self.layout.CENTER.x + int((self.layout.CENTER.w - img.get_size()[0])/2)
            if self.layout.CENTER.h > img.get_size()[1]:
                self.center_button.components[1].content_y = self.layout.CENTER.y + int((self.layout.CENTER.h - img.get_size()[1])/2)
            else:
                self.center_button.components[1].content_y = self.layout.CENTER.y
        
        if self.current_playlist == None:
            return
        
        self.set_audio_file(new_track, state)        

    def set_audio_file(self, new_track, s=None):
        """ Set new audio file
        
        :param new_track: True - new audio file
        :param s: button state object 
        """
        state = State()
        state.playback_mode = FILE_AUDIO
        state.playlist_track_number = 0
        name = url = None

        if s == None:
            if self.config[AUDIOBOOKS][BROWSER_TRACK_FILENAME]:
                name = self.config[AUDIOBOOKS][BROWSER_TRACK_FILENAME]
                for t in self.playlist:
                    if t["title"].endswith(name):
                        url = t["mp3"]                    
            else:
                i = 0
                if s != None:
                    i = s.index
                t = self.playlist[i]
                url = t["mp3"]
                name = t["title"]
        else:
            if getattr(s, "file_name", None):
                i = self.get_current_track_index({"file_name": s.file_name})
            elif getattr(s, "playlist_track_number", None):
                i = s.playlist_track_number
            else:
                i = self.current_track_index 
            
            t = self.playlist[i]
            url = t["mp3"]
            name = t["title"]

        self.config[PLAYER_SETTINGS][PAUSE] = False
        state.file_name = name
        self.config[AUDIOBOOKS][BROWSER_TRACK_FILENAME] = t["file_name"]        
        state.mute = self.config[PLAYER_SETTINGS][MUTE]
        state.pause = self.config[PLAYER_SETTINGS][PAUSE]
        self.play_button.draw_default_state(None)

        if self.config[VOLUME_CONTROL][VOLUME_CONTROL_TYPE] == VOLUME_CONTROL_TYPE_PLAYER:
            state.volume = self.config[PLAYER_SETTINGS][VOLUME]
        else:
            state.volume = None

        state.file_type = FILE_AUDIO
        state.dont_notify = True
        state.source = FILE_AUDIO
        state.url = url
        state.mode = AUDIOBOOKS
        
        state.playback_mode = FILE_AUDIO
        state.music_folder = self.config[AUDIO][MUSIC_FOLDER] 
        self.audio_files = self.get_audio_files_from_playlist()
        
        if self.config[AUDIOBOOKS][BROWSER_BOOK_TIME]:
            if new_track:
                state.track_time = "0"
            else:
                state.track_time = self.config[AUDIOBOOKS][BROWSER_BOOK_TIME]
        
        self.reset_loading()
        
        logging.debug(state.url)
        
        self.notify_play_listeners(state)
    
    def get_audio_files(self):
        """ Return audio files from playlist
        
        :return: files
        """
        return self.get_audio_files_from_playlist()
        
    def get_audio_files_from_playlist(self):
        """ Call player for files in the playlist 
        
        :return: list of files from playlist
        """
        files = []
        if getattr(self, "playlist", None):
            for n in range(len(self.playlist)):
                st = State()
                st.index = st.comparator_item = n
                t = self.playlist[n]
                st.file_type = FILE_AUDIO
                st.file_name = t["file_name"]
                files.append(st)
        return files

    def get_current_track_index(self, state=None):
        """ Return current track index.
        In case of files goes through the file list.
        In case of playlist takes track index from the state object.
        
        :param state: button state

        :return: current track index
        """
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
        self.set_current(True, s)

    def is_valid_mode(self):
        return True

    def end_of_track(self):
        """ Handle end of track """

        FilePlayerScreen.end_of_track(self)
        self.config[AUDIOBOOKS][BROWSER_BOOK_TIME] = None

    def set_loading(self):
        """ Show Loading... sign """
        
        b = self.config[COLORS][COLOR_DARK]
        f = self.config[COLORS][COLOR_BRIGHT]
        fs = 20
        bx = self.center_button.bounding_box
        x = bx.x - 1
        y = bx.y
        w = bx.w + 2
        h = bx.h
        bb = pygame.Rect(x, y, w, h)
        t = self.factory.create_output_text(self.LOADING, bb, b, f, fs)
        t.set_text(self.LOADING)
        t.layer_name = self.LOADING
        self.left_button.change_label("")
        self.right_button.change_label("")
        self.add_component(t)
        self.clean_draw_update()
        self.notify_loading_listeners()
        
    def reset_loading(self):
        """ Remove Loading... sign """
        
        n = getattr(self.components[-1], "layer_name", None)
        if n and n == self.LOADING:
            del self.components[-1]
            pygame.event.clear()
        self.notify_reset_loading_listeners()
    
    def add_loading_listener(self, listener):
        """ Add loading listener
        
        :param listener: event listener
        """
        if listener not in self.loading_listeners:
            self.loading_listeners.append(listener)
            
    def notify_loading_listeners(self):
        """ Notify all loading listeners """
        
        for listener in self.loading_listeners:
            listener(None)
            
    def add_reset_loading_listener(self, listener):
        """ Add reset loading listener
        
        :param listener: event listener
        """
        if listener not in self.reset_loading_listeners:
            self.reset_loading_listeners.append(listener)
            
    def notify_reset_loading_listeners(self):
        """ Notify all reset loading listeners """
        
        for listener in self.reset_loading_listeners:
            listener(None)

    def add_screen_observers(self, update_observer, redraw_observer, start_time_control, stop_time_control, title_to_json):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        :param start_time_control:
        :param stop_time_control:
        :param title_to_json:
        """
        FilePlayerScreen.add_screen_observers(self, update_observer, redraw_observer, start_time_control, stop_time_control, title_to_json)
        self.add_loading_listener(redraw_observer)
        self.add_reset_loading_listener(redraw_observer)

