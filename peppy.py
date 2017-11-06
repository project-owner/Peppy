# Copyright 2016-2017 Peppy Player peppy.player@gmail.com
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
import sys
import subprocess
import threading
import pygame
import importlib
import time

from subprocess import Popen
from event.dispatcher import EventDispatcher
from player.proxy import Proxy 
from screensaver.screensaverdispatcher import ScreensaverDispatcher
from ui.state import State
from ui.screen.radiogenre import RadioGenreScreen
from ui.screen.home import HomeScreen
from ui.screen.language import LanguageScreen
from ui.screen.saver import SaverScreen
from ui.screen.about import AboutScreen
from ui.screen.station import StationScreen
from ui.screen.filebrowser import FileBrowserScreen
from ui.screen.fileplayer import FilePlayerScreen
from websiteparser.loyalbooks.loyalbooksparser import LoyalBooksParser
from websiteparser.audioknigi.audioknigiparser import AudioKnigiParser
from util.config import USAGE, USE_WEB, AUDIO, SERVER_FOLDER, SERVER_COMMAND, CLIENT_NAME, LINUX_PLATFORM, \
    CURRENT, VOLUME, MODE, CURRENT_FILE, CURRENT_FOLDER, CURRENT_TRACK_TIME, USE_STREAM_SERVER, \
    STREAM_SERVER_PARAMETERS, STREAM_CLIENT_PARAMETERS, BROWSER_SITE, BROWSER_BOOK_TIME, BROWSER_BOOK_URL, \
    BROWSER_BOOK_TITLE, BROWSER_TRACK_FILENAME
from util.util import Util, LABELS, KEY_GENRE
from util.keys import KEY_RADIO, KEY_AUDIO_FILES, KEY_STREAM, KEY_LANGUAGE, KEY_SCREENSAVER, MUTE, PAUSE, \
    KEY_ABOUT, KEY_PLAY_FILE, KEY_STATIONS, KEY_GENRES, KEY_HOME, KEY_SEEK, KEY_BACK, KEY_SHUTDOWN, \
    KEY_PLAY_PAUSE, KEY_SET_VOLUME, KEY_SET_CONFIG_VOLUME, KEY_SET_SAVER_VOLUME, KEY_MUTE, KEY_PLAY, \
    PLAYER_SETTINGS, FILE_PLAYBACK, RADIO_PLAYLIST, KEY_AUDIOBOOKS, GO_USER_HOME, GO_ROOT, GO_TO_PARENT, KEY_BOOK_SCREEN,\
    KEY_PLAY_SITE, LOYALBOOKS, AUDIOKNIGI, INIT, KEY_PLAYER, GO_BACK, GO_PLAYER, KEY_MODE, RESUME
from ui.screen.bookplayer import BookPlayer
from ui.screen.booktrack import BookTrack
from ui.screen.bookabc import BookAbc
from ui.screen.bookauthorbooks import BookAuthorBooks
from ui.screen.bookgenre import BookGenre
from ui.screen.bookgenrebooks import BookGenreBooks
from ui.screen.booknew import BookNew
from ui.screen.bookauthor import BookAuthor
from websiteparser.audioknigi.constants import AUDIOKNIGI_ROWS, AUDIOKNIGI_COLUMNS
from websiteparser.loyalbooks.constants import EN_US, FR, DE
from websiteparser.siteparser import BOOK_URL, FILE_NAME

class Peppy(object):
    """ Main class """
    
    lock = threading.RLock()        
    def __init__(self):
        """ Initializer """
    
        self.util = Util()
        self.config = self.util.config
        self.use_web = self.config[USAGE][USE_WEB]
        
        if self.use_web:
            f = open(os.devnull, 'w')
            sys.stdout = sys.stderr = f
            from web.server.webserver import WebServer
            self.web_server = WebServer(self.util, self)
        
        about = AboutScreen(self.util)
        about.add_listener(self.go_home)
        self.screens = {KEY_ABOUT : about}
        self.current_player_screen = None
        self.current_radio_genre = self.config[CURRENT][RADIO_PLAYLIST]
        self.current_audio_file = None
        self.current_language = self.config[CURRENT][KEY_LANGUAGE]
        
        self.start_audio()
        
        self.screensaver_dispatcher = ScreensaverDispatcher(self.util)
        if self.use_web:
            self.web_server.add_screensaver_web_listener(self.screensaver_dispatcher)
               
        self.event_dispatcher = EventDispatcher(self.screensaver_dispatcher, self.util)        
        self.current_screen = None
        self.PLAYER_SCREENS = [KEY_STATIONS, KEY_STREAM, KEY_PLAY_FILE]
        
        if not self.config[CURRENT][MODE]:
            self.go_home(None)        
        elif self.config[CURRENT][MODE] == KEY_RADIO:            
            self.go_stations()
        elif self.config[CURRENT][MODE] == KEY_AUDIO_FILES:
            state = State()
            state.folder = self.config[FILE_PLAYBACK][CURRENT_FOLDER].replace('\\\\', '\\')
            state.file_name = self.config[FILE_PLAYBACK][CURRENT_FILE]            
            state.url = state.folder + os.sep + state.file_name
            self.go_file_playback(state)
        elif self.config[CURRENT][MODE] == KEY_STREAM:
            self.go_stream()
        elif self.config[CURRENT][MODE] == KEY_AUDIOBOOKS:
            state = State()
            state.name = self.config[KEY_AUDIOBOOKS][BROWSER_BOOK_TITLE]
            state.book_url = self.config[KEY_AUDIOBOOKS][BROWSER_BOOK_URL]
            state.track_filename = self.config[KEY_AUDIOBOOKS][BROWSER_TRACK_FILENAME]
            state.source = INIT
            self.go_site_playback(state)
            
    def start_audio(self):
        """ Starts audio server and client """
        
        folder = None
        try:
            folder = self.config[AUDIO][SERVER_FOLDER]
        except:
            pass
        
        cmd = None
        try:
            cmd = self.config[AUDIO][SERVER_COMMAND]
        except:
            pass
        
        stream_server_parameters = None
        try:
            stream_server_parameters = self.config[AUDIO][STREAM_SERVER_PARAMETERS]
        except:
            pass
        
        if self.config[USAGE][USE_STREAM_SERVER] and stream_server_parameters:
            if cmd:
                cmd = cmd + " " + stream_server_parameters
            else:
                cmd = stream_server_parameters
                
        stream_client_parameters = None
        try:
            stream_client_parameters = self.config[AUDIO][STREAM_CLIENT_PARAMETERS]
        except:
            pass
        
        if stream_client_parameters:
            if cmd:
                cmd = cmd + " " + stream_client_parameters
            else:
                cmd = stream_client_parameters
        
        client_name = self.config[AUDIO][CLIENT_NAME]
        linux = self.config[LINUX_PLATFORM]
        
        proxy = Proxy(linux, folder, cmd, self.config[PLAYER_SETTINGS][VOLUME])
        self.audio_server = proxy.start()
        
        p = "player.client." + client_name
        m = importlib.import_module(p)
        n = client_name.title()
        self.player = getattr(m, n)()
        self.player.set_platform(linux)
        self.player.set_proxy(self.audio_server)
        self.player.set_file_util(self.util.file_util)
        self.player.start_client()
        
        if self.config[PLAYER_SETTINGS][PAUSE]:
            self.player.pause()
        
    def exit_current_screen(self):
        """ Complete action required to exit screen """
                
        with self.lock:
            cs = self.current_screen
            if cs and self.screens and self.screens[cs]:
                self.screens[cs].exit_screen()
                
    def set_mode(self, state):
        """ Set current mode (e.g. Radio, Language etc)
        
        :param state: button state
        """ 
        self.store_current_track_time(self.current_screen)         
        if state.name == KEY_RADIO: self.go_stations(state)
        elif state.name == KEY_AUDIO_FILES: self.go_file_playback(state)
        elif state.name == KEY_STREAM: self.go_stream(state)
        elif state.name == KEY_AUDIOBOOKS: self.go_audiobooks(state)

    def go_player(self, state):
        """ Go to the current player screen
        
        :param state: button state
        """ 
        state.source = GO_PLAYER
        
        if self.current_player_screen == KEY_PLAY_SITE:
            self.go_site_playback(state)
        elif self.current_player_screen == KEY_STATIONS:
            self.go_stations(state)
        elif self.current_player_screen == KEY_PLAY_FILE:
            self.go_file_playback(state)
        elif self.current_player_screen == KEY_STREAM:
            self.go_stream(state)  

    def get_current_screen(self, key):
        """ Return current screen by name
        
        :param key: screen name
        """ 
        s = None
        self.exit_current_screen()
        try:
            if self.screens and self.screens[key]:
                s = self.screens[key]
                self.set_current_screen(key)
        except KeyError:
            pass
        return s

    def go_home(self, state):
        """ Go to the Home Screen
        
        :param state: button state
        """        
        if self.get_current_screen(KEY_HOME): return
        
        listeners = self.get_home_screen_listeners()
        home_screen = HomeScreen(self.util, listeners)
        self.screens[KEY_HOME] = home_screen
        self.set_current_screen(KEY_HOME)
        
        if self.use_web:
            self.web_server.add_home_screen_web_listeners(home_screen)
    
    def go_language(self, state):
        """ Go to the Language Screen
        
        :param state: button state
        """
        if self.get_current_screen(KEY_LANGUAGE): return

        listeners = {KEY_HOME: self.go_home, KEY_PLAYER: self.go_player}
        language_screen = LanguageScreen(self.util, self.change_language, listeners)
        self.screens[KEY_LANGUAGE] = language_screen
        self.set_current_screen(KEY_LANGUAGE)
        
        if self.use_web:
            self.web_server.add_language_screen_web_listeners(language_screen)
    
    def change_language(self, state):
        """ Change current language and go to the Home Screen
        
        :param state: button state
        """
        if state.name != self.config[CURRENT][KEY_LANGUAGE]:
            self.config[LABELS].clear()
            try:
                stations = self.screens[KEY_STATIONS]
                if stations:
                    self.player.remove_player_listener(stations.screen_title.set_text)
            except KeyError:
                pass
            self.config[CURRENT][KEY_LANGUAGE] = state.name
            self.config[LABELS] = self.util.get_labels()        
            self.screens = {k : v for k, v in self.screens.items() if k == KEY_ABOUT}
            self.current_screen = None            
        self.go_home(state)
        self.player.stop()
        
    def go_file_browser(self, state=None):
        """ Go to the File Browser Screen
        
        :param state: button state
        """
        if self.get_current_screen(KEY_AUDIO_FILES): return
        
        file_player = self.screens[KEY_PLAY_FILE]

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_PLAY_FILE] = self.go_file_playback
        listeners[GO_BACK] = file_player.restore_current_folder
        
        file_browser_screen = FileBrowserScreen(self.util, self.player.get_current_playlist, self.player.load_playlist, listeners)
        
        file_player.add_play_listener(file_browser_screen.file_menu.select_item)
        file_browser_screen.file_menu.add_playlist_size_listener(file_player.set_playlist_size)
        file_browser_screen.file_menu.add_play_file_listener(file_player.play_button.draw_default_state)
        
        self.player.add_player_listener(file_browser_screen.file_menu.update_playlist_menu)        
        
        self.screens[KEY_AUDIO_FILES] = file_browser_screen
        self.set_current_screen(KEY_AUDIO_FILES)
        
        if self.use_web:
            self.web_server.add_file_browser_screen_web_listeners(file_browser_screen)
    
    def go_file_playback(self, state=None):
        """ Go to the File Player Screen
        
        :param state: button state
        """
        self.deactivate_current_player(KEY_PLAY_FILE)
        try:
            if self.screens[KEY_PLAY_FILE]:
                if getattr(state, "name", None) and (state.name == KEY_HOME or state.name == KEY_BACK):
                    self.set_current_screen(KEY_PLAY_FILE, True)
                else:
                    if state:
                        state.source = RESUME
                    self.set_current_screen(name=KEY_PLAY_FILE, state=state)
                self.current_player_screen = KEY_PLAY_FILE
                return
        except:
            pass
        if getattr(state, "url", None):        
            tokens = state.url.split(os.sep)       
            self.config[FILE_PLAYBACK][CURRENT_FILE] = tokens[len(tokens) - 1]
        
        listeners = self.get_play_screen_listeners()
        listeners[KEY_AUDIO_FILES] = self.go_file_browser
        listeners[KEY_SEEK] = self.player.seek
        screen = FilePlayerScreen(listeners, self.util, self.player.get_current_playlist)
        self.screens[KEY_PLAY_FILE] = screen
        self.current_player_screen = KEY_PLAY_FILE
        screen.load_playlist = self.player.load_playlist
        
        self.player.add_player_listener(screen.screen_title.set_text)
        self.player.add_player_listener(screen.time_control.set_track_info)
        self.player.add_player_listener(screen.update_arrow_button_labels)
        self.player.add_end_of_track_listener(screen.end_of_track)
        
        screen.add_play_listener(self.screensaver_dispatcher.change_image)
        screen.add_play_listener(self.screensaver_dispatcher.change_image_folder)
        
        f = getattr(state, "file_name", None)
        if f == None and state != None:
            state.file_name = self.config[FILE_PLAYBACK][CURRENT_FILE]
            
        self.set_current_screen(KEY_PLAY_FILE, state=state)
        self.screensaver_dispatcher.change_image(screen.file_button.state)
        state = State()
        state.cover_art_folder = screen.file_button.state.cover_art_folder
        self.screensaver_dispatcher.change_image_folder(state)
        
        if self.use_web:
            self.web_server.add_file_player_web_listeners(screen)
            self.player.add_player_listener(self.web_server.file_player_time_control_change)

    def go_site_playback(self, state=None):
        """ Go to the Site Player Screen
        
        :param state: button state
        """
        self.deactivate_current_player(KEY_PLAY_SITE)
        name = KEY_PLAY_SITE
        s = State()
        s.name = state.name
        s.file_name = getattr(state, FILE_NAME, None)
        a = getattr(state, "source", None)
        if a:
            s.source = a
        else: 
            s.source = INIT
        
        if getattr(state, BOOK_URL, None):
            self.config[KEY_AUDIOBOOKS][BROWSER_BOOK_URL] = s.book_url = state.book_url 
        
        try:
            if self.screens[name]:
                if state.name == LOYALBOOKS or state.name == AUDIOKNIGI:
                    s.name = self.config[KEY_AUDIOBOOKS][BROWSER_BOOK_TITLE]
                else:
                    s.name = state.name
                self.set_current_screen(name, state=s)
                self.current_player_screen = name
                return
        except:
            pass

        listeners = self.get_play_screen_listeners()
        listeners[KEY_SEEK] = self.player.seek
        listeners[KEY_AUDIO_FILES] = self.go_book_track_screen       
        
        if not getattr(state, BOOK_URL, None):
            self.go_site_news_screen(state)
            return
        
        self.config[KEY_AUDIOBOOKS][BROWSER_BOOK_URL] = state.book_url
        self.config[KEY_AUDIOBOOKS][BROWSER_BOOK_TITLE] = state.name
        s = BookPlayer(listeners, self.util, self.get_parser())
        
        self.player.add_player_listener(s.time_control.set_track_info)            
        self.player.add_player_listener(s.update_arrow_button_labels)
        self.player.add_end_of_track_listener(s.end_of_track)         
        s.add_play_listener(self.screensaver_dispatcher.change_image)
        
        if self.use_web:
            self.web_server.add_site_player_web_listeners(s)
            self.player.add_player_listener(self.web_server.site_player_time_control_change)
            
        s.name = name
        self.screens[name] = s
        self.current_player_screen = KEY_PLAY_SITE
        self.set_current_screen(name, state=state) 

    def go_book_track_screen(self, state):
        """ Go to the Book Tracks Screen
        
        :param state: button state
        """
        listeners = self.get_site_navigator_listeners()
        self.exit_current_screen()        
        name = "book.track.screen"
        try:
            if self.screens[name]:
                self.set_current_screen(name)
                return
        except:
            pass
        
        d = self.get_book_menu_settings()
        s = BookTrack(self.util, listeners, self.go_site_playback, d)
        self.screens[name] = s
        self.set_current_screen(name)
        
        if self.use_web:
            self.web_server.add_book_track_screen_web_listeners(s)  
    
    def go_site_abc_screen(self, state):
        """ Go to the Site ABC Screen
        
        :param state: button state
        """
        if "abc.screen" == self.current_screen:
            return
        
        site = self.config[KEY_AUDIOBOOKS][BROWSER_SITE]      
        name = site + ".author.books"
        try:
            if self.screens[name] and self.current_screen != name and self.current_screen != site + ".authors.screen":
                self.set_current_screen(name, state=state)
                cs = self.screens[name]
                cs.set_current(state)
                return
        except:
            pass
        
        name = site + ".authors.screen"
        try:
            if self.screens[name] and self.current_screen != name:
                self.set_current_screen(name, state=state)
                cs = self.screens[name]
                cs.set_current() 
                return
        except:
            pass
        
        listeners = self.get_site_navigator_listeners()
        self.exit_current_screen()        
        name = "abc.screen"
        try:
            if self.screens[name]:
                self.set_current_screen(name)
                return
        except:
            pass
        
        d = self.get_book_menu_settings()
        s = BookAbc(self.util, listeners, self.go_site_authors_screen, d)
        self.screens[name] = s
        self.set_current_screen(name)
        
        if self.use_web:
            self.web_server.add_site_abc_screen_web_listeners(s) 
    
    def go_site_authors_screen(self, ch, f=None):
        """ Go to the Site Authors Screen
        
        :param ch: selected character
        :param f: selected filter
        """
        listeners = self.get_site_navigator_listeners()
        self.exit_current_screen()
        site = self.config[KEY_AUDIOBOOKS][BROWSER_SITE]        
        name = site + ".authors.screen"
        try:
            if self.screens[name]:
                self.set_current_screen(name)
                cs = self.screens[name]
                cs.set_current(ch, f)
                return
        except:
            pass
        
        base_url = None
        
        if site == AUDIOKNIGI:
            from websiteparser.audioknigi.constants import AUTHOR_URL
            base_url = AUTHOR_URL
        
        d = self.get_book_menu_settings()          
        s = BookAuthor(self.util, listeners, ch, f, self.go_site_books_by_author, self.get_parser(), base_url, d)
        self.screens[name] = s
        self.set_current_screen(name)
        
        if self.use_web:
            s.add_loading_listener(self.web_server.create_screen)
        
        s.set_current(ch, f)
         
        if self.use_web:
            self.web_server.add_site_authors_screen_web_listeners(s)

    def go_site_books_by_author(self, state):
        """ Go to the Author Books Screen
        
        :param state: button state
        """
        listeners = self.get_site_navigator_listeners()
        self.exit_current_screen()  
        site = self.config[KEY_AUDIOBOOKS][BROWSER_SITE]      
        name = site + ".author.books"
        try:
            if self.screens[name]:
                self.set_current_screen(name, state=state)
                cs = self.screens[name]
                cs.set_current(state) 
                return
        except:
            pass
        
        d = self.get_book_menu_settings(show_author=False)
        parser = self.get_parser()
        from websiteparser.audioknigi.constants import PAGE_URL_PREFIX
        parser.news_parser.page_url_prefix = PAGE_URL_PREFIX
        s = BookAuthorBooks(self.util, listeners, state.name, self.go_site_playback, state.url, parser, d)        
        self.screens[name] = s
        self.set_current_screen(name)
        
        if self.use_web:
            self.web_server.add_site_author_books_screen_web_listeners(s)
            
        s.turn_page()
        
    def go_site_news_screen(self, state):
        """ Go to the Site New Books Screen
        
        :param state: button state
        """
        listeners = self.get_site_navigator_listeners()
        self.exit_current_screen()        
        name = self.config[KEY_AUDIOBOOKS][BROWSER_SITE] + ".new.books.screen"
        try:
            if self.screens[name]:
                self.set_current_screen(name)
                return
        except:
            pass
        
        d = self.get_book_menu_settings()
        parser = self.get_parser()
        site = self.config[KEY_AUDIOBOOKS][BROWSER_SITE]
        
        if site == AUDIOKNIGI:
            from websiteparser.audioknigi.constants import PAGE_URL_PREFIX
            parser.news_parser.page_url_prefix = PAGE_URL_PREFIX
        elif site == LOYALBOOKS:
            from websiteparser.loyalbooks.constants import TOP_100
            parser.news_parser.page_url_prefix = TOP_100
            parser.language_url = d[4]
            
        s = BookNew(self.util, listeners, self.go_site_playback, parser, d)
        self.screens[name] = s
        self.set_current_screen(name)
        
        if self.use_web:
            self.web_server.add_site_news_screen_web_listeners(s)
            
        s.turn_page()
    
    def get_book_menu_settings(self, show_author=True, show_genre=True):
        """ Return book menu settings for defined parameters
        
        :param show_author: flag indicating if authors button should be included
        :param show_genre: flag indicating if genre button should be included
        """
        rows = AUDIOKNIGI_ROWS
        columns = AUDIOKNIGI_COLUMNS        
        if self.config[KEY_AUDIOBOOKS][BROWSER_SITE] == LOYALBOOKS:
            from websiteparser.loyalbooks.constants import BOOKS_ROWS, BOOKS_COLUMNS
            rows = BOOKS_ROWS
            columns = BOOKS_COLUMNS
            show_genre = False
        return [rows, columns, show_author, show_genre, self.get_language_url()]
    
    def go_site_genre_screen(self, state):
        """ Go to the Site Genres Screen
        
        :param state: button state
        """
        site = self.config[KEY_AUDIOBOOKS][BROWSER_SITE]
        
        if site + ".genre.screen" == self.current_screen:
            return
              
        name = site + ".genre.books"
        try:
            if self.screens[name] and self.current_screen != name:
                cs = self.screens[name]
                cs.set_current(state) 
                self.set_current_screen(name, state=state)
                return
        except:
            pass
        
        listeners = self.get_site_navigator_listeners()
        self.exit_current_screen()
        name = site + ".genre.screen"
        try:
            if self.screens[name]:
                self.set_current_screen(name)
                return
        except:
            pass
        
        constants = None
        base_url = None
        
        if site == AUDIOKNIGI:
            from websiteparser.audioknigi.constants import AUDIOKNIGI_GENRE, SECTION_URL
            constants = AUDIOKNIGI_GENRE
            base_url = SECTION_URL
        elif site == LOYALBOOKS:
            from websiteparser.loyalbooks.constants import LOYALBOOKS_GENRE, GENRE_URL
            constants = LOYALBOOKS_GENRE
            base_url = GENRE_URL
        
        d = self.get_book_menu_settings()    
        s = BookGenre(self.util, listeners, self.go_site_books_by_genre, constants, base_url, d)
        self.screens[name] = s
        self.set_current_screen(name)
        
        if self.use_web:
            self.web_server.add_site_genre_screen_web_listeners(s) 

    def go_site_books_by_genre(self, state):
        """ Go to the Genre Books Screen
        
        :param state: button state
        """
        listeners = self.get_site_navigator_listeners()
        self.exit_current_screen()  
        site = self.config[KEY_AUDIOBOOKS][BROWSER_SITE]      
        name = site + ".genre.books"
        try:
            if self.screens[name]:                
                self.set_current_screen(name, state=state)                
                cs = self.screens[name]
                cs.set_current(state)                 
                return
        except:
            pass
        
        parser = self.get_parser()
        
        if site == AUDIOKNIGI:
            from websiteparser.audioknigi.constants import SECTION_URL, PAGE_URL_PREFIX
            parser.genre_books_parser.base_url = SECTION_URL
            parser.genre_books_parser.page_url_prefix = PAGE_URL_PREFIX
        elif site == LOYALBOOKS:
            from websiteparser.loyalbooks.constants import BASE_URL, PAGE_PREFIX
            parser.genre_books_parser.base_url = BASE_URL
            parser.genre_books_parser.page_url_prefix = PAGE_PREFIX
        
        d = self.get_book_menu_settings(show_genre=False)
        s = BookGenreBooks(self.util, listeners, state.name, self.go_site_playback, state.genre, parser, d)
        self.screens[name] = s
        self.set_current_screen(name)
        
        if self.use_web:
            self.web_server.add_genre_books_screen_web_listeners(s)
            
        s.turn_page() 
    
    def get_site_navigator_listeners(self):
        """ Return site navigator listeners """
        
        listeners = {}
        listeners[GO_USER_HOME] = self.go_site_abc_screen
        listeners[GO_ROOT] = self.go_site_news_screen
        listeners[GO_TO_PARENT] = self.go_site_genre_screen
        listeners[GO_PLAYER] = self.go_player
        listeners[GO_BACK] = self.go_back
        listeners[KEY_HOME] = self.go_home
        return listeners 
    
    def get_home_screen_listeners(self):
        """ Return home screen listeners """
        
        listeners = {}
        listeners[KEY_MODE] = self.set_mode
        listeners[KEY_BACK] = self.go_back
        listeners[KEY_SCREENSAVER] = self.go_savers
        listeners[KEY_LANGUAGE] = self.go_language
        listeners[KEY_PLAYER] = self.go_player
        listeners[KEY_ABOUT] = self.go_about
        return listeners    

    def get_play_screen_listeners(self):
        """ File player screen listeners getter """
        
        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_SHUTDOWN] = self.shutdown        
        listeners[KEY_PLAY_PAUSE] = self.play_pause
        listeners[KEY_SET_VOLUME] = self.set_volume
        listeners[KEY_SET_CONFIG_VOLUME] = self.set_config_volume
        listeners[KEY_SET_SAVER_VOLUME] = self.screensaver_dispatcher.change_volume
        listeners[KEY_MUTE] = self.mute
        listeners[KEY_PLAY] = self.player.play
        return listeners
        
    def go_stream(self, state=None):
        """ Go to the Stream Screen
        
        :param state: button state
        """
        self.deactivate_current_player(KEY_STREAM)
        
        if self.get_current_screen(KEY_STREAM): return
             
        listeners = self.get_play_screen_listeners()
        stream_screen = StationScreen(listeners, self.util, KEY_STREAM)
        self.screens[KEY_STREAM] = stream_screen
        self.set_current_screen(KEY_STREAM)
        self.screensaver_dispatcher.change_image(stream_screen.station_menu.station_button.state)
        stream_screen.station_menu.add_listener(self.screensaver_dispatcher.change_image)
        stream_screen.station_menu.add_listener(self.screensaver_dispatcher.change_image_folder)
        self.player.add_player_listener(stream_screen.screen_title.set_text)
        stream_screen.station_menu.add_listener(stream_screen.play_button.draw_default_state)

        if self.use_web:
            self.web_server.add_station_screen_web_listeners(stream_screen)
    
    def go_audiobooks(self, state=None):
        """ Go to the Audiobooks Screen
        
        :param state: button state
        """
        listeners = self.get_play_screen_listeners()
        listeners[KEY_SEEK] = self.player.seek        
        self.exit_current_screen()
        s = State()
        s.source = INIT
        s.book_url = self.config[KEY_AUDIOBOOKS][BROWSER_BOOK_URL]
        
        if self.config[CURRENT][KEY_LANGUAGE] == "ru":
            s.name = AUDIOKNIGI
        else:
            s.name = LOYALBOOKS
        
        s.language_url = self.get_language_url()
        self.config[KEY_AUDIOBOOKS][BROWSER_SITE] = s.name
        site_player = None
        
        state = State()
        self.screensaver_dispatcher.change_image_folder(state)
        
        try:
            site_player = self.screens[KEY_PLAY_SITE]
            s.source = RESUME
            if getattr(state, "file_name", None) == None:
                s.file_name = self.config[KEY_AUDIOBOOKS][BROWSER_TRACK_FILENAME]
        except:
            pass
            
        if not self.config[KEY_AUDIOBOOKS][BROWSER_BOOK_URL] or site_player == None:
            self.go_site_news_screen(s)
        else:
            self.go_site_playback(s)
    
    def get_language_url(self):
        """ Return language URL constant for current language """
        
        language = self.config[CURRENT][KEY_LANGUAGE]
        
        if language == "en_us":
            return EN_US
        elif language == "fr":
            return FR 
        elif language == "de":
            return DE
        elif language == "ru":
            return None
    
    def get_parser(self):
        """ Return site parser for the current site """
        
        name = self.config[KEY_AUDIOBOOKS][BROWSER_SITE]
        if name == LOYALBOOKS:            
            return LoyalBooksParser()            
        elif name == AUDIOKNIGI:
            return AudioKnigiParser()
        return None
                    
    def go_savers(self, state):
        """ Go to the Screensavers Screen
        
        :param state: button state
        """
        if self.get_current_screen(KEY_SCREENSAVER): return
        
        listeners = {KEY_HOME: self.go_home, KEY_PLAYER: self.go_player}
        saver_screen = SaverScreen(self.util, listeners)
        saver_screen.saver_menu.add_listener(self.screensaver_dispatcher.change_saver_type)
        saver_screen.delay_menu.add_listener(self.screensaver_dispatcher.change_saver_delay)
        self.screens[KEY_SCREENSAVER] = saver_screen
        self.set_current_screen(KEY_SCREENSAVER)
        
        if self.use_web:
            self.web_server.add_saver_screen_web_listeners(saver_screen)
        
    def go_about(self, state):
        """ Go to the About Screen
        
        :param state: button state
        """
        self.exit_current_screen()
        self.set_current_screen(KEY_ABOUT)
        if self.use_web:
            self.web_server.add_about_screen_web_listeners(self.screens[KEY_ABOUT])
    
    def go_stations(self, state=None):
        """ Go to the Stations Screen
        
        :param state: button state
        """
        self.deactivate_current_player(KEY_STATIONS)
        
        if self.get_current_screen(KEY_STATIONS): return
        
        listeners = self.get_play_screen_listeners()
        listeners[KEY_GENRES] = self.go_genres
        station_screen = StationScreen(listeners, self.util)
        self.screens[KEY_STATIONS] = station_screen
        self.set_current_screen(KEY_STATIONS)
        self.screensaver_dispatcher.change_image(station_screen.station_menu.station_button.state)
        station_screen.station_menu.add_listener(self.screensaver_dispatcher.change_image)
        station_screen.station_menu.add_listener(self.screensaver_dispatcher.change_image_folder)
        self.player.add_player_listener(station_screen.screen_title.set_text)
        station_screen.station_menu.add_listener(station_screen.play_button.draw_default_state)        
        
        if self.use_web:
            self.web_server.add_station_screen_web_listeners(station_screen)
    
    def set_config_volume(self, volume):
        """ Listener for volume change events
        
        :param volume: new volume value
        """
        self.config[PLAYER_SETTINGS][VOLUME] = str(int(volume))
            
    def go_genres(self, state):
        """ Go to the Genre Screen
        
        :param state: button state
        """
        if self.get_current_screen(KEY_GENRES): return
        
        listeners = {KEY_GENRE: self.go_stations, KEY_HOME: self.go_home, KEY_PLAYER: self.go_player}
        genre_screen = RadioGenreScreen(self.util, listeners)
        self.screens[KEY_GENRES] = genre_screen
        self.set_current_screen(KEY_GENRES)
        
        if self.use_web:
            self.web_server.add_genre_screen_web_listeners(genre_screen)
    
    def play_pause(self, state=None):
        """ Handle Play/Pause
        
        :param state: button state
        """
        self.config[PLAYER_SETTINGS][PAUSE] = not self.config[PLAYER_SETTINGS][PAUSE]
        self.player.play_pause(self.config[PLAYER_SETTINGS][PAUSE])
        
    def set_current_screen(self, name, go_back=False, state=None):
        """ Set current screen defined by its name
        
        :param name: screen name
        """
        with self.lock:
            self.previous_screen_name = self.current_screen
            self.current_screen = name
            cs = self.screens[self.current_screen]            
            p = getattr(cs, "player_screen", None)
            if p: 
                cs.enable_player_screen(True)
            
            cs.set_visible(True)
            if go_back:
                cs.go_back()
            else:
                if name == KEY_STATIONS:
                    new_genre = self.current_radio_genre != self.config[CURRENT][RADIO_PLAYLIST]
                    new_language = self.current_language != self.config[CURRENT][KEY_LANGUAGE]
                    if new_genre or new_language or self.current_player_screen != name:
                        self.current_radio_genre = self.config[CURRENT][RADIO_PLAYLIST]
                        self.current_language = self.config[CURRENT][KEY_LANGUAGE]
                        cs.set_current(state=state)
                elif name == KEY_PLAY_FILE:
                    f = getattr(state, "file_name", None)
                    if f and self.current_audio_file != state.file_name or self.current_player_screen != name:
                        a = getattr(state, "file_name", None)
                        if a != None: 
                            self.current_audio_file = a 
                        cs.set_current(state=state)
                elif name.endswith(KEY_BOOK_SCREEN):
                    if state:
                        cs.set_current(state)
                elif name == KEY_PLAY_SITE or name == KEY_STREAM:
                    cs.set_current(state=state)
                elif name == "book.track.screen":
                    state = State()
                    ps = self.screens[KEY_PLAY_SITE]
                    state.playlist = ps.get_playlist()
                    cs.set_current(state)
                
            cs.clean_draw_update()
            self.event_dispatcher.set_current_screen(cs)
            if name != self.current_player_screen:
                self.set_volume()
                
            if p: 
                self.current_player_screen = name
    
    def go_back(self, state):
        """ Go to the previous screen
        
        :param state: button state
        """
        if not self.previous_screen_name:
            return
        
        cs = self.screens[self.current_screen]
        cs.exit_screen()
        self.set_current_screen(self.previous_screen_name, state=state)
    
    def set_volume(self, volume=None):
        """ Set volume """
        
        cs = self.screens[self.current_screen]
        player_screen = getattr(cs, "player_screen", None) 
        if player_screen and not cs.volume.selected:
            config_volume = volume
            if volume == None: 
                config_volume = int(self.config[PLAYER_SETTINGS][VOLUME])
            
            if self.player.get_volume() != config_volume:
                self.player.set_volume(config_volume)
    
    def mute(self):
        """ Mute """

        self.config[PLAYER_SETTINGS][MUTE] = not self.config[PLAYER_SETTINGS][MUTE]
        self.player.mute()
    
    def deactivate_current_player(self, new_player_screen_name):
        """ Disable current player
        
        :param new_player_screen_name: new player screen name
        """
        for scr in self.screens.items():
            p = getattr(scr[1], "player_screen", None)
            if not p: 
                continue
            scr[1].enable_player_screen(False)
            
        self.exit_current_screen()
        
        if new_player_screen_name == self.current_player_screen:
            return
        
        with self.lock:
            try:
                s = self.screens[self.current_player_screen]
                s.stop_timer()
            except:
                pass
    
    def store_current_track_time(self, mode):
        """ Save current track time in configuration object
        
        :param mode: 
        """
        k = None
        if self.current_player_screen == KEY_PLAY_FILE:
            k = KEY_PLAY_FILE
        elif self.current_player_screen == KEY_PLAY_SITE:
            k = KEY_PLAY_SITE
        
        if k and k in self.screens:    
            s = self.screens[k]
            tc = s.time_control
            t = tc.seek_time
            if self.current_player_screen == KEY_PLAY_SITE:
                self.config[KEY_AUDIOBOOKS][BROWSER_BOOK_TIME] = t
            else:
                self.config[FILE_PLAYBACK][CURRENT_TRACK_TIME] = t
        
    def shutdown(self, event):
        """ System shutdown handler
        
        :param event: the event
        """
        self.store_current_track_time(self.config[CURRENT][MODE])
            
        self.util.config_class.save_current_settings()
        self.player.shutdown()
        
        if self.use_web:
            try:
                self.web_server.shutdown()
            except:
                pass
        
        self.event_dispatcher.run_dispatcher = False
        time.sleep(0.4)
        
        title_screen_name = None
        
        if self.config[CURRENT][MODE] == KEY_RADIO:
            title_screen_name = KEY_STATIONS
        elif self.config[CURRENT][MODE] == KEY_AUDIO_FILES:
            title_screen_name = KEY_PLAY_FILE
        elif self.config[CURRENT][MODE] == KEY_AUDIOBOOKS:
            title_screen_name = KEY_PLAY_SITE
        
        if title_screen_name:
            self.screens[title_screen_name].screen_title.shutdown()
        
        if title_screen_name and (title_screen_name == KEY_PLAY_FILE or title_screen_name == KEY_PLAY_SITE):
            self.screens[title_screen_name].time_control.stop_thread()
        
        pygame.quit()
        
        if self.config[LINUX_PLATFORM]:
            subprocess.call("sudo poweroff", shell=True)
        else:
            try:
                Popen("taskkill /F /T /PID {pid}".format(pid=self.audio_server.pid))
            except:
                pass
            os._exit(0)

def main():
    """ Main method """
    
    peppy = Peppy()
    peppy.event_dispatcher.dispatch(peppy.player, peppy.shutdown)    
        
if __name__ == "__main__":
    main()
