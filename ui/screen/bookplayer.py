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

from ui.screen.fileplayer import FilePlayerScreen
from util.keys import BOOK_MENU, HOME_NAVIGATOR, \
    TRACK_MENU, BOOK_NAVIGATOR_BACK, ARROW_BUTTON, INIT, BOOK_NAVIGATOR, LABELS, KEY_LOADING, GO_PLAYER, RESUME
from ui.state import State
from util.fileutil import FILE_AUDIO
from util.config import AUDIO, MUSIC_FOLDER, AUDIOBOOKS, VOLUME, \
    BROWSER_TRACK_FILENAME, BROWSER_BOOK_TIME, BROWSER_BOOK_TITLE, BROWSER_BOOK_URL, \
    COLOR_DARK, COLORS, COLOR_BRIGHT, COLOR_MEDIUM, PLAYER_SETTINGS, MUTE, PAUSE
from util.cache import Cache
import pygame

class BookPlayer(FilePlayerScreen):
    """ Book Player Screen """
    
    def __init__(self, listeners, util, site_parser, voice_assistant):
        """ Initializer
        
        :param listeners: screen listeners
        :param util: utility object 
        :param site_parser: site parser        
        """
        FilePlayerScreen.__init__(self, listeners, util, self.get_playlist, voice_assistant)
        self.config = util.config
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
        self.current_playlist = self.parser.get_book_audio_files_by_url(state.book_url)
        state.url = self.parser.book_parser.img_url
        
        img = self.cache.get_image(state.url)
        if img == None:
            i = self.util.load_image_from_url(state.url)
            self.cache.cache_image(i[1], state.url)
            img = i[1]
        
        bb = self.file_button.bounding_box
        w = bb.w
        h = bb.h
        self.cover_image = self.util.scale_image_with_padding(w, h, img, padding=1)        
        
        self.screen_title.set_text(state.name)
        
        if self.current_playlist == None:
            return
        
        self.playlist = self.current_playlist
        
        if new_track and self.playlist:
            self.config[AUDIOBOOKS][BROWSER_BOOK_TITLE] = state.name
            self.config[AUDIOBOOKS][BROWSER_BOOK_URL] = state.book_url
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
            self.file_button.components[1].image_filename = self.img_filename = state.url
        else:
            self.file_button.components[1].image_filename = self.img_filename 
        img = self.cover_image
        self.file_button.components[1].content = img
        self.file_button.state.icon_base = img
        self.file_button.state.show_bgr = True
        self.file_button.state.bgr = self.config[COLORS][COLOR_MEDIUM]
        self.file_button.add_background(self.file_button.state)
        self.file_button.components[1].content_x = self.layout.CENTER.x + int((self.layout.CENTER.w - img.get_size()[0])/2)
        if self.layout.CENTER.h > img.get_size()[1]:
            self.file_button.components[1].content_y = self.layout.CENTER.y + int((self.layout.CENTER.h - img.get_size()[1])/2)
        else:
            self.file_button.components[1].content_y = self.layout.CENTER.y
        
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
            if getattr(s, "track_filename", None):
                i = self.get_current_track_index({"file_name": s.track_filename})
            elif getattr(s, "playlist_track_number", None):
                i = s.playlist_track_number
            else:
                i = self.current_track_index 
            
            t = self.playlist[i]
            url = t["mp3"]
            name = t["title"]
            
        state.file_name = name
        self.config[AUDIOBOOKS][BROWSER_TRACK_FILENAME] = t["file_name"]        
        state.mute = self.config[PLAYER_SETTINGS][MUTE]
        state.pause = self.config[PLAYER_SETTINGS][PAUSE]
        state.volume = int(self.config[PLAYER_SETTINGS][VOLUME])
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
    
    def set_loading(self):
        """ Show Loading... sign """
        
        b = self.config[COLORS][COLOR_DARK]
        f = self.config[COLORS][COLOR_BRIGHT]
        fs = 20
        bx = self.file_button.bounding_box
        x = bx.x - 1
        y = bx.y - 1
        w = bx.w + 2
        h = bx.h + 2
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

