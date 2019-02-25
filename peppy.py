# Copyright 2016-2019 Peppy Player peppy.player@gmail.com
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
import pygame
import importlib
import time
import logging
import socket

from datetime import datetime
from threading import RLock, Thread
from subprocess import Popen
from event.dispatcher import EventDispatcher
from player.proxy import Proxy, MPLAYER, MPD 
from screensaver.screensaverdispatcher import ScreensaverDispatcher
from ui.state import State
from ui.screen.radiogroup import RadioGroupScreen
from ui.screen.home import HomeScreen
from ui.screen.language import LanguageScreen
from ui.screen.saver import SaverScreen
from ui.screen.about import AboutScreen
from ui.screen.black import BlackScreen
from ui.screen.station import StationScreen
from ui.screen.filebrowser import FileBrowserScreen
from ui.screen.fileplayer import FilePlayerScreen
from ui.screen.cddrives import CdDrivesScreen
from ui.screen.cdtracks import CdTracksScreen
from ui.screen.equalizer import EqualizerScreen
from ui.screen.timer import TimerScreen
from ui.layout.borderlayout import BorderLayout
from ui.screen.screen import Screen, PERCENT_TOP_HEIGHT, PERCENT_TITLE_FONT
from websiteparser.loyalbooks.loyalbooksparser import LoyalBooksParser
from websiteparser.audioknigi.audioknigiparser import AudioKnigiParser
from util.config import *
from util.util import Util, LABELS, KEY_GENRE, PLAYER_RUNNING, PLAYER_SLEEPING
from util.keys import *
from ui.screen.bookplayer import BookPlayer
from ui.screen.booktrack import BookTrack
from ui.screen.bookabc import BookAbc
from ui.screen.bookauthorbooks import BookAuthorBooks
from ui.screen.bookgenre import BookGenre
from ui.screen.bookgenrebooks import BookGenreBooks
from ui.screen.booknew import BookNew
from ui.screen.bookauthor import BookAuthor
from websiteparser.audioknigi.constants import AUDIOKNIGI_ROWS, AUDIOKNIGI_COLUMNS
from websiteparser.loyalbooks.constants import LANGUAGE_PREFIX, ENGLISH_USA, RUSSIAN
from websiteparser.siteparser import BOOK_URL, FILE_NAME
from util.cdutil import CdUtil
from ui.screen.podcasts import PodcastsScreen
from ui.screen.podcastepisodes import PodcastEpisodesScreen
from ui.screen.podcastplayer import PodcastPlayerScreen

class Peppy(object):
    """ Main class """
    
    lock = RLock()        
    def __init__(self):
        """ Initializer """

        connected_to_internet = self.check_internet_connectivity()
    
        self.util = Util(connected_to_internet)
        self.config = self.util.config
        self.cdutil = CdUtil(self.util)
        self.use_web = self.config[USAGE][USE_WEB]
        
        s = self.config[SCRIPTS][STARTUP]
        if s != None and len(s.strip()) != 0:
            self.util.run_script(s)
        
        layout = BorderLayout(self.config[SCREEN_RECT])
        layout.set_percent_constraints(PERCENT_TOP_HEIGHT, PERCENT_TOP_HEIGHT, 0, 0)
        self.config[MAXIMUM_FONT_SIZE] = int((layout.TOP.h * PERCENT_TITLE_FONT)/100.0)
        
        self.screensaver_dispatcher = ScreensaverDispatcher(self.util)

        try:
            values = self.config[CURRENT][EQUALIZER]
            if values:
                self.util.set_equalizer(values)
        except:
            pass            

        if self.use_web:
            try:
                import tornado
                f = open(os.devnull, 'w')
                sys.stdout = sys.stderr = f
                from web.server.webserver import WebServer
                self.web_server = WebServer(self.util, self)
            except Exception as e:
                self.use_web = False
        
        self.voice_assistant = None        
        if self.config[USAGE][USE_VOICE_ASSISTANT]:
            language = self.util.get_voice_assistant_language_code(self.config[CURRENT][LANGUAGE])
            if language:
                try:
                    from voiceassistant.voiceassistant import VoiceAssistant
                    self.voice_assistant = VoiceAssistant(self.util)
                except:
                    pass
        
        about = AboutScreen(self.util)
        about.add_listener(self.go_home)
        self.screens = {KEY_ABOUT : about}
        self.current_player_screen = None
        
        self.current_audio_file = None
        self.current_language = self.config[CURRENT][LANGUAGE]
        
        if self.config[AUDIO][PLAYER_NAME] == MPD:
            self.start_audio()
            if self.config[USAGE][USE_VU_METER]:
                self.util.load_screensaver(VUMETER)
        else:
            if self.config[USAGE][USE_VU_METER]:
                self.util.load_screensaver(VUMETER)
            self.start_audio()        
                
        if self.voice_assistant:
            self.voice_assistant.assistant.add_start_conversation_listener(self.screensaver_dispatcher.handle_event)            
        
        if self.use_web:
            self.screensaver_dispatcher.add_start_listener(self.web_server.start_screensaver_to_json)
            self.screensaver_dispatcher.add_stop_listener(self.web_server.stop_screensaver_to_json)
               
        self.event_dispatcher = EventDispatcher(self.screensaver_dispatcher, self.util)        
        self.current_screen = None
        self.current_mode = self.config[CURRENT][MODE]
        self.PLAYER_SCREENS = [KEY_STATIONS, STREAM, KEY_PLAY_FILE, KEY_PLAY_CD, KEY_PODCAST_PLAYER]
        
        if not self.config[CURRENT][MODE] or not self.config[USAGE][USE_AUTO_PLAY]:
            self.go_home(None)        
        elif self.config[CURRENT][MODE] == RADIO:            
            self.go_stations()
        elif self.config[CURRENT][MODE] == AUDIO_FILES:
            state = State()
            state.folder = self.config[FILE_PLAYBACK][CURRENT_FOLDER].replace('\\\\', '\\')
            state.file_name = self.config[FILE_PLAYBACK][CURRENT_FILE]            
            state.url = state.folder + os.sep + state.file_name
            self.go_file_playback(state)
        elif self.config[CURRENT][MODE] == STREAM:
            self.go_stream()
        elif self.config[CURRENT][MODE] == AUDIOBOOKS:
            state = State()
            state.name = self.config[AUDIOBOOKS][BROWSER_BOOK_TITLE]
            state.book_url = self.config[AUDIOBOOKS][BROWSER_BOOK_URL]
            state.track_filename = self.config[AUDIOBOOKS][BROWSER_TRACK_FILENAME]
            state.source = INIT
            self.go_site_playback(state)
        elif self.config[CURRENT][MODE] == CD_PLAYER:
            self.go_cd_playback()
        elif self.config[CURRENT][MODE] == PODCASTS:
            state = State()
            state.podcast_url = self.config[PODCASTS][PODCAST_URL]
            state.name = self.config[PODCASTS][PODCAST_EPISODE_NAME]
            state.url = self.config[PODCASTS][PODCAST_EPISODE_URL]
            state.episode_time = self.config[PODCASTS][PODCAST_EPISODE_TIME]
            state.source = INIT
            self.go_podcast_player(state)
        
        self.player_state = PLAYER_RUNNING
        self.run_timer_thread = False   
        self.start_timer_thread()
        
    def check_internet_connectivity(self):
        """ Exit if Internet is not available after 3 attempts 3 seconds each """

        attempts = 3
        timeout = 3
        for n in range(attempts):
            internet_available = self.is_internet_available(timeout)
            if internet_available:
                break
            else:
                if n == (attempts - 1):
                    logging.error("Internet is not available")
                    return False
                else:
                    time.sleep(timeout)
                    continue
        return True
    
    def is_internet_available(self, timeout):
        """ Check that Internet is available. The solution was taken from here:
        https://stackoverflow.com/questions/3764291/checking-network-connection

        :param timeout: request timeout
        :return: True - Internet available, False - not available
        """
        google_dns_server = "8.8.8.8"
        google_dns_server_port = 53
        
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((google_dns_server, google_dns_server_port))
            return True
        except Exception as e:
            logging.error("Connection error: {0}".format(e))
            return False
            
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
        
        default_cd_drive = self.cdutil.get_default_cd_drive()
        if self.config[AUDIO][PLAYER_NAME] == MPLAYER and default_cd_drive:
            cd_drive_name = default_cd_drive[1]
            if ":" in cd_drive_name: # Windows
                cd_drive_name = cd_drive_name.split(":")[0] + ":"
            cmd = cmd + " -cdrom-device " + cd_drive_name
        
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
        logging.debug("started audio server")
        
        p = "player.client." + client_name
        m = importlib.import_module(p)
        n = client_name.title()
        self.player = getattr(m, n)()
        self.player.set_platform(linux)
        self.player.set_player_mode(self.config[CURRENT][MODE])
        self.player.set_proxy(self.audio_server)
        self.player.set_util(self.util)
        self.player.start_client()
        self.player.cd_track_title = self.config[LABELS][CD_TRACK]        
        
        if self.config[PLAYER_SETTINGS][PAUSE]:
            self.player.pause()
    
    def start_timer_thread(self):
        """ Start timer thread """
        
        if not self.config[HOME_MENU][TIMER] or self.run_timer_thread:
            return
        
        sleep_selected = self.config[TIMER][SLEEP] and len(self.config[TIMER][SLEEP_TIME]) > 0
        poweroff_selected = self.config[TIMER][POWEROFF] and len(self.config[TIMER][SLEEP_TIME]) > 0
        wake_up_selected = self.config[TIMER][WAKE_UP] and len(self.config[TIMER][WAKE_UP_TIME]) > 0
        
        if not sleep_selected and not poweroff_selected:
            return
        
        self.run_timer_thread = True
        self.timer_thread = Thread(target=self.timer_thread)
        self.timer_thread.start()
    
    def timer_thread(self):
        """ Timer thread function """
        
        while self.run_timer_thread:
            time.sleep(2)
            
            with self.lock:
                sleep_selected = self.config[TIMER][SLEEP]
                poweroff_selected = self.config[TIMER][POWEROFF]
                wake_up_selected = self.config[TIMER][WAKE_UP]            
                sleep_time = self.config[TIMER][SLEEP_TIME] + "00"
                wake_up_time = self.config[TIMER][WAKE_UP_TIME] + "00"
                
            current_time = datetime.now().strftime("%H%M%S")
            
            if sleep_selected:
                if wake_up_selected and self.player_state == PLAYER_SLEEPING and self.is_time_in_range(current_time, wake_up_time):
                    with self.lock:
                        self.player_state = PLAYER_RUNNING
                    self.wake_up()                 
                if not self.is_time_in_range(current_time, sleep_time):
                    continue                
                if self.player_state == PLAYER_RUNNING:
                    self.sleep()                
            elif poweroff_selected:
                if not self.is_time_in_range(current_time, sleep_time):
                    continue          
                logging.debug("poweroff")
                self.run_timer_thread = False
                self.shutdown()
    
    def is_time_in_range(self, t1, t2):
        """ Check if provided time (t1) is in range of 4 seconds (t1)
        
        :param t1: current time
        :param t2: time to compare to
        
        :return: True - time in range, False - time out of range
        """
        current_h_m = t1[0:4]
        current_sec = t1[4:]
        
        if current_h_m != t2[0:4]:
            return False

        if int(current_sec) < 3:
            return True
        else:
            return False
    
    def sleep(self, state=None):
        """ Go to sleep mode
        
        :param state: button state object
        """
        logging.debug("sleep")
        with self.lock:
            self.player_state = PLAYER_SLEEPING
        self.player.stop()
        if self.screensaver_dispatcher.saver_running:
            self.screensaver_dispatcher.cancel_screensaver()
        self.screensaver_dispatcher.current_delay = 0      
        self.go_black()
        
    def wake_up(self, state=None):
        """ Wake up from sleep mode
        
        :param state: button state object
        """
        logging.debug("wake up")
        self.player_state = PLAYER_RUNNING
        self.player.resume_playback()
        self.set_current_screen(self.previous_screen_name)
        self.screensaver_dispatcher.delay_counter = 0
        self.screensaver_dispatcher.current_delay = self.screensaver_dispatcher.get_delay()
        if self.use_web:
            self.web_server.redraw_web_ui()
        
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
        
        mode = state.genre
        
        if self.current_mode != mode:
            self.player.stop()
            self.current_mode = mode
                 
        if mode == RADIO: 
            self.go_stations(state)
        elif mode == AUDIO_FILES: self.go_file_playback(state)
        elif mode == STREAM: self.go_stream(state)
        elif mode == AUDIOBOOKS: self.go_audiobooks(state)
        elif mode == CD_PLAYER: self.go_cd_playback(state)
        elif mode == PODCASTS: self.go_podcast_player(state)
        
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
        elif self.current_player_screen == KEY_PLAY_CD:
            self.go_cd_playback(state)
        elif self.current_player_screen == STREAM:
            self.go_stream(state)
        elif self.current_player_screen == KEY_PODCAST_PLAYER:
            self.go_podcast_player(state)  

    def go_favorites(self, state):
        """ Go to the favorites screen
        
        :param state: button state
        """ 
        state.source = KEY_FAVORITES
        self.go_stations(state)

    def get_current_screen(self, key, state=None):
        """ Return current screen by name
        
        :param key: screen name
        """ 
        s = None
        self.exit_current_screen()
        try:
            if self.screens and self.screens[key]:
                s = self.screens[key]
                self.set_current_screen(key, state=state)
        except KeyError:
            pass
        return s

    def add_screen_observers(self, screen):
        """ Add web obervers to the provided screen
        
        :param screen: screen for observers
        """
        screen.add_screen_observers(self.web_server.update_web_ui, self.web_server.redraw_web_ui)

    def go_home(self, state):
        """ Go to the Home Screen
        
        :param state: button state
        """        
        if self.get_current_screen(KEY_HOME): return
        
        listeners = self.get_home_screen_listeners()
        home_screen = HomeScreen(self.util, listeners, self.voice_assistant)
        self.screens[KEY_HOME] = home_screen
        self.set_current_screen(KEY_HOME)
        
        if self.use_web:
            self.add_screen_observers(home_screen)
    
    def go_language(self, state):
        """ Go to the Language Screen
        
        :param state: button state
        """
        if self.get_current_screen(LANGUAGE): return

        listeners = {KEY_HOME: self.go_home, KEY_PLAYER: self.go_player}
        language_screen = LanguageScreen(self.util, self.change_language, listeners, self.voice_assistant)
        self.screens[LANGUAGE] = language_screen
        self.set_current_screen(LANGUAGE)
        
        if self.use_web:
            self.add_screen_observers(language_screen)
    
    def change_language(self, state):
        """ Change current language and go to the Home Screen
        
        :param state: button state
        """
        if state.name != self.config[CURRENT][LANGUAGE]:
            self.config[LABELS].clear()
            try:
                stations = self.screens[KEY_STATIONS]
                if stations:
                    self.player.remove_player_listener(stations.screen_title.set_text)
            except KeyError:
                pass
            self.config[CURRENT][LANGUAGE] = state.name            
            self.config[LABELS] = self.util.get_labels()
            self.util.weather_config = self.util.get_weather_config()
            try:
                self.screensaver_dispatcher.current_screensaver.set_util(self.util)
            except:
                pass 
            
            self.config[AUDIOBOOKS][BROWSER_BOOK_URL] = ""       
            self.screens = {k : v for k, v in self.screens.items() if k == KEY_ABOUT}
            self.current_screen = None
            
            if self.config[USAGE][USE_VOICE_ASSISTANT]:
                language = self.util.get_voice_assistant_language_code(state.name)
                if language:
                    if self.voice_assistant == None:
                        try:
                            from voiceassistant.voiceassistant import VoiceAssistant
                            self.voice_assistant = VoiceAssistant(self.util)
                        except:
                            pass
                else:
                    self.voice_assistant.change_language()
                           
        self.go_home(state)
        self.player.stop()
        
    def go_file_browser(self, state=None):
        """ Go to the File Browser Screen
        
        :param state: button state
        """
        if self.get_current_screen(AUDIO_FILES): return
        
        file_player = self.screens[KEY_PLAY_FILE]

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_PLAY_FILE] = self.go_file_playback
        listeners[GO_BACK] = file_player.restore_current_folder
        
        file_browser_screen = FileBrowserScreen(self.util, self.player.get_current_playlist, self.player.load_playlist, listeners, self.voice_assistant)
        
        file_player.add_play_listener(file_browser_screen.file_menu.select_item)
        file_player.recursive_notifier = file_browser_screen.file_menu.change_folder
        
        file_browser_screen.file_menu.add_playlist_size_listener(file_player.set_playlist_size)
        file_browser_screen.file_menu.add_play_file_listener(file_player.play_button.draw_default_state)
        
        self.player.add_player_listener(file_browser_screen.file_menu.update_playlist_menu)        
        
        self.screens[AUDIO_FILES] = file_browser_screen
        self.set_current_screen(AUDIO_FILES)
        
        if self.use_web:
            self.add_screen_observers(file_browser_screen)

    def go_cd_drives(self, state=None):
        """ Go to the CD drives Screen
        
        :param state: button state
        """
        if self.get_current_screen(KEY_CD_PLAYERS): return
        
        if self.cdutil.get_cd_drives_number() == 1:
            self.go_cd_tracks()

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_PLAYER] = self.go_cd_playback
        listeners[KEY_CD_TRACKS] = self.go_cd_tracks
        cd_drives_screen = CdDrivesScreen(self.util, listeners, self.voice_assistant)
        self.screens[KEY_CD_PLAYERS] = cd_drives_screen
        self.set_current_screen(KEY_CD_PLAYERS)
        
        if self.use_web:
            self.add_screen_observers(cd_drives_screen)
    
    def go_cd_tracks(self, state=None):
        """ Go to the CD tracks Screen
        
        :param state: button state
        """
        
        if self.cdutil.get_cd_drives_number() == 0:
            return
        
        try:
            if self.screens[KEY_CD_TRACKS]:
                self.set_current_screen(KEY_CD_TRACKS, state=state)
                return
        except:
            pass
        
        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_PLAYER] = self.go_cd_playback
        listeners[KEY_CD_PLAYERS] = self.go_cd_drives
        listeners[GO_BACK] = self.go_cd_playback
        screen = CdTracksScreen(self.util, listeners, self.voice_assistant, state)
        screen.navigator.eject_button.add_release_listener(self.player.stop)
        self.screens[KEY_CD_TRACKS] = screen
        
        file_player = self.screens[KEY_PLAY_CD]
        screen.navigator.eject_button.add_release_listener(file_player.eject_cd)
        self.player.cd_tracks = file_player.audio_files       
        file_player.add_play_listener(screen.file_menu.select_item)
        screen.file_menu.add_playlist_size_listener(file_player.set_playlist_size)
        screen.file_menu.add_play_file_listener(file_player.play_button.draw_default_state)        
        self.player.add_player_listener(screen.file_menu.update_playlist_menu)   
        
        self.set_current_screen(KEY_CD_TRACKS, state=state)
        
        if self.use_web:
            self.add_screen_observers(screen)
    
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
        listeners[AUDIO_FILES] = self.go_file_browser
        listeners[KEY_SEEK] = self.player.seek
        screen = FilePlayerScreen(listeners, self.util, self.player.get_current_playlist, self.voice_assistant, self.player.stop)
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
        state = State()
        state.cover_art_folder = screen.file_button.state.cover_art_folder
        self.screensaver_dispatcher.change_image_folder(state)
        
        if self.use_web:
            update = self.web_server.update_web_ui
            redraw = self.web_server.redraw_web_ui
            start = self.web_server.start_time_control_to_json
            stop = self.web_server.stop_time_control_to_json
            title_to_json = self.web_server.title_to_json
            screen.add_screen_observers(update, redraw, start, stop, title_to_json)
            self.web_server.add_player_listener(screen.time_control)
            self.player.add_player_listener(self.web_server.update_player_listeners)

    def go_cd_playback(self, state=None):
        """ Go to the CD Player Screen
        
        :param state: button state
        """        
        self.deactivate_current_player(KEY_PLAY_CD)
        if getattr(state, "file_name", None):
            state.url = state.file_name            
        
        try:
            cd_player = self.screens[KEY_PLAY_CD]
            cd_drive_name = self.config[CD_PLAYBACK][CD_DRIVE_NAME]
            cd_player.audio_files = self.cdutil.get_cd_tracks_summary(cd_drive_name)
            self.player.cd_tracks = cd_player.audio_files
                
            if getattr(state, "name", None) and (state.name == KEY_HOME or state.name == KEY_BACK):
                self.set_current_screen(KEY_PLAY_CD, True)
            else:
                if state:
                    state.source = RESUME
                self.set_current_screen(name=KEY_PLAY_CD, state=state)
            self.current_player_screen = KEY_PLAY_CD
            return
        except:
            pass
        
        listeners = self.get_play_screen_listeners()
        listeners[GO_BACK] = self.go_cd_playback
        listeners[AUDIO_FILES] = self.go_cd_tracks
        listeners[KEY_SEEK] = self.player.seek
        screen = FilePlayerScreen(listeners, self.util, self.player.get_current_playlist, self.voice_assistant)
        self.screens[KEY_PLAY_CD] = screen
        self.current_player_screen = KEY_PLAY_CD
        screen.load_playlist = self.player.load_playlist
        
        self.player.cd_tracks = screen.audio_files
        self.player.add_player_listener(screen.screen_title.set_text)
        self.player.add_player_listener(screen.time_control.set_track_info)
        self.player.add_player_listener(screen.update_arrow_button_labels)
        self.player.add_end_of_track_listener(screen.end_of_track)
        
        screen.add_play_listener(self.screensaver_dispatcher.change_image)
        screen.add_play_listener(self.screensaver_dispatcher.change_image_folder)
        
        if state == None:
            state = State()
        state.source = INIT
        self.set_current_screen(KEY_PLAY_CD, state=state)
        self.screensaver_dispatcher.change_image(screen.file_button.state)
        state = State()
        state.cover_art_folder = screen.file_button.state.cover_art_folder
        self.screensaver_dispatcher.change_image_folder(state)
        
        if self.use_web:
            update = self.web_server.update_web_ui
            redraw = self.web_server.redraw_web_ui
            start = self.web_server.start_time_control_to_json
            stop = self.web_server.stop_time_control_to_json
            title_to_json = self.web_server.title_to_json
            screen.add_screen_observers(update, redraw, start, stop, title_to_json)
            self.web_server.add_player_listener(screen.time_control)
            self.player.add_player_listener(self.web_server.update_player_listeners)

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
            self.config[AUDIOBOOKS][BROWSER_BOOK_URL] = s.book_url = state.book_url 
        
        try:
            if self.screens[name]:
                if state.name == LOYALBOOKS or state.name == AUDIOKNIGI:
                    s.name = self.config[AUDIOBOOKS][BROWSER_BOOK_TITLE]
                else:
                    s.name = state.name
                self.set_current_screen(name, state=s)
                self.current_player_screen = name
                return
        except:
            pass

        listeners = self.get_play_screen_listeners()
        listeners[KEY_SEEK] = self.player.seek
        listeners[AUDIO_FILES] = self.go_book_track_screen       
        
        if not getattr(state, BOOK_URL, None):
            self.go_site_news_screen(state)
            return
        
        self.config[AUDIOBOOKS][BROWSER_BOOK_URL] = state.book_url
        self.config[AUDIOBOOKS][BROWSER_BOOK_TITLE] = state.name
        s = BookPlayer(listeners, self.util, self.get_parser(), self.voice_assistant)
        
        self.player.add_player_listener(s.time_control.set_track_info)            
        self.player.add_player_listener(s.update_arrow_button_labels)
        self.player.add_end_of_track_listener(s.end_of_track)         
        s.add_play_listener(self.screensaver_dispatcher.change_image)
        
        if self.use_web:
            update = self.web_server.update_web_ui
            redraw = self.web_server.redraw_web_ui
            start = self.web_server.start_time_control_to_json
            stop = self.web_server.stop_time_control_to_json
            title_to_json = self.web_server.title_to_json
            s.add_screen_observers(update, redraw, start, stop, title_to_json)
            self.web_server.add_player_listener(s.time_control)
            self.player.add_player_listener(self.web_server.update_player_listeners)
        
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
        name = KEY_BOOK_TRACK_SCREEB
        try:
            if self.screens[name]:
                self.set_current_screen(name)
                return
        except:
            pass
        
        d = self.get_book_menu_settings()
        s = BookTrack(self.util, listeners, self.go_site_playback, self.voice_assistant, d)
        ps = self.screens[KEY_PLAY_SITE]
        ps.add_play_listener(s.track_menu.select_track)
        
        self.screens[name] = s
        self.set_current_screen(name)
        
        if self.use_web:
            self.add_screen_observers(s)
    
    def go_site_abc_screen(self, state):
        """ Go to the Site ABC Screen
        
        :param state: button state
        """
        if "abc.screen" == self.current_screen:
            return
        
        site = self.config[AUDIOBOOKS][BROWSER_SITE]      
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
        s = BookAbc(self.util, listeners, self.go_site_authors_screen, self.voice_assistant, d)
        self.screens[name] = s
        self.set_current_screen(name)
        
        if self.use_web:
            self.add_screen_observers(s)
    
    def go_site_authors_screen(self, ch, f=None):
        """ Go to the Site Authors Screen
        
        :param ch: selected character
        :param f: selected filter
        """
        listeners = self.get_site_navigator_listeners()
        self.exit_current_screen()
        site = self.config[AUDIOBOOKS][BROWSER_SITE]        
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
        s = BookAuthor(self.util, listeners, ch, f, self.go_site_books_by_author, self.get_parser(), base_url, self.voice_assistant, d)
        self.screens[name] = s
        self.set_current_screen(name)
        
        if self.use_web:
            s.add_loading_listener(self.web_server.redraw_web_ui)
        
        s.set_current(ch, f)
         
        if self.use_web:
            self.add_screen_observers(s)

    def go_site_books_by_author(self, state):
        """ Go to the Author Books Screen
        
        :param state: button state
        """
        listeners = self.get_site_navigator_listeners()
        self.exit_current_screen()  
        site = self.config[AUDIOBOOKS][BROWSER_SITE]      
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
        s = BookAuthorBooks(self.util, listeners, state.name, self.go_site_playback, state.url, parser, self.voice_assistant, d)        
        self.screens[name] = s
        self.set_current_screen(name)
        
        if self.use_web:
            self.add_screen_observers(s)
            
        s.turn_page()
        
    def go_site_news_screen(self, state):
        """ Go to the Site New Books Screen
        
        :param state: button state
        """
        listeners = self.get_site_navigator_listeners()
        self.exit_current_screen()        
        name = self.config[AUDIOBOOKS][BROWSER_SITE] + ".new.books.screen"
        try:
            if self.screens[name]:
                self.set_current_screen(name)
                return
        except:
            pass
        
        d = self.get_book_menu_settings()
        parser = self.get_parser()
        site = self.config[AUDIOBOOKS][BROWSER_SITE]
        
        if site == AUDIOKNIGI:
            from websiteparser.audioknigi.constants import PAGE_URL_PREFIX
            parser.news_parser.page_url_prefix = PAGE_URL_PREFIX
        elif site == LOYALBOOKS:
            from websiteparser.loyalbooks.constants import TOP_100
            parser.news_parser.page_url_prefix = TOP_100
            parser.language_url = d[4]
            
        s = BookNew(self.util, listeners, self.go_site_playback, parser, self.voice_assistant, d)
        self.screens[name] = s
        self.set_current_screen(name)
        
        if self.use_web:
            self.add_screen_observers(s)
            
        s.turn_page()
    
    def get_book_menu_settings(self, show_author=True, show_genre=True):
        """ Return book menu settings for defined parameters
        
        :param show_author: flag indicating if authors button should be included
        :param show_genre: flag indicating if genre button should be included
        """
        rows = AUDIOKNIGI_ROWS
        columns = AUDIOKNIGI_COLUMNS        
        if self.config[AUDIOBOOKS][BROWSER_SITE] == LOYALBOOKS:
            from websiteparser.loyalbooks.constants import BOOKS_ROWS, BOOKS_COLUMNS
            rows = BOOKS_ROWS
            columns = BOOKS_COLUMNS
            show_genre = False
        return [rows, columns, show_author, show_genre, self.get_language_url()]
    
    def go_site_genre_screen(self, state):
        """ Go to the Site Genres Screen
        
        :param state: button state
        """
        site = self.config[AUDIOBOOKS][BROWSER_SITE]
        
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
        s = BookGenre(self.util, listeners, self.go_site_books_by_genre, constants, base_url, self.voice_assistant, d)
        self.screens[name] = s
        self.set_current_screen(name)
        
        if self.use_web:
            self.add_screen_observers(s)

    def go_site_books_by_genre(self, state):
        """ Go to the Genre Books Screen
        
        :param state: button state
        """
        listeners = self.get_site_navigator_listeners()
        self.exit_current_screen()  
        site = self.config[AUDIOBOOKS][BROWSER_SITE]      
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
        s = BookGenreBooks(self.util, listeners, state.name, self.go_site_playback, state.genre, parser, self.voice_assistant, d)
        self.screens[name] = s
        self.set_current_screen(name)
        
        if self.use_web:
            self.add_screen_observers(s)
            
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
        listeners[SCREENSAVER] = self.go_savers
        listeners[LANGUAGE] = self.go_language
        listeners[KEY_PLAYER] = self.go_player
        listeners[KEY_ABOUT] = self.go_about
        listeners[EQUALIZER] = self.go_equalizer
        listeners[TIMER] = self.go_timer
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
        listeners[KEY_STOP] = self.player.stop        
        return listeners
    
    def go_stream(self, state=None):
        """ Go to the Stream Screen
        
        :param state: button state
        """
        self.deactivate_current_player(STREAM)
        
        if self.get_current_screen(STREAM): return
             
        listeners = self.get_play_screen_listeners()
        stream_screen = StationScreen(listeners, self.util, self.voice_assistant, STREAM)
        self.screens[STREAM] = stream_screen
        self.set_current_screen(STREAM)
        self.screensaver_dispatcher.change_image(stream_screen.station_menu.station_button.state)
        stream_screen.station_menu.add_listener(self.screensaver_dispatcher.change_image)
        stream_screen.station_menu.add_listener(self.screensaver_dispatcher.change_image_folder)
        self.player.add_player_listener(stream_screen.screen_title.set_text)
        stream_screen.station_menu.add_listener(stream_screen.play_button.draw_default_state)

        if self.use_web:
            update = self.web_server.update_web_ui
            redraw = self.web_server.redraw_web_ui
            title_to_json = self.web_server.title_to_json
            stream_screen.add_screen_observers(update, redraw, title_to_json)
            self.web_server.station_menu = stream_screen.station_menu
            stream_screen.station_menu.add_menu_click_listener(self.web_server.station_menu_to_json)
            stream_screen.station_menu.add_mode_listener(self.web_server.station_menu_to_json) 

    def go_podcasts(self, state=None):
        """ Go to the Podcasts Screen
        
        :param state: button state
        """
        if self.get_current_screen(PODCASTS): return
        
        try:
            if self.screens[PODCASTS]:
                self.set_current_screen(PODCASTS, state=state)
                return
        except:
            pass
        
        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_PLAYER] = self.go_podcast_player
        listeners[GO_BACK] = self.go_back
        listeners[KEY_PODCAST_EPISODES] = self.go_podcast_episodes
        podcasts_screen = PodcastsScreen(self.util, listeners, self.voice_assistant)
        self.screens[PODCASTS] = podcasts_screen
        if self.use_web:
            self.add_screen_observers(podcasts_screen)
        self.set_current_screen(PODCASTS)
    
    def go_podcast_episodes(self, state):
        """ Go to the podcast episodes screen
        
        :param state: button state
        """
        url = getattr(state, "podcast_url", None)
               
        if url != None:
            self.config[PODCASTS][PODCAST_URL] = url
            
        try:
            if self.screens[KEY_PODCAST_EPISODES]:
                self.set_current_screen(KEY_PODCAST_EPISODES, state=state)
                return
        except:
            if state and hasattr(state, "name") and len(state.name) == 0:
                self.go_podcasts(state)
                return
        
        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[PODCASTS] = self.go_podcasts
        listeners[GO_BACK] = self.go_back
        listeners[KEY_PLAYER] = self.go_podcast_player
        screen = PodcastEpisodesScreen(self.util, listeners, self.voice_assistant, state)
        self.screens[KEY_PODCAST_EPISODES] = screen
        
        podcast_player = self.screens[KEY_PODCAST_PLAYER]
        podcast_player.add_play_listener(screen.turn_page)
        if self.use_web:
            self.add_screen_observers(screen)
        self.set_current_screen(KEY_PODCAST_EPISODES, state=state)

    def go_podcast_player(self, state):
        """ Go to the podcast player screen
        
        :param state: button state
        """
        self.deactivate_current_player(KEY_PODCAST_PLAYER)
        try:
            if self.screens[KEY_PODCAST_PLAYER]:
                if getattr(state, "name", None) and (state.name == KEY_HOME or state.name == KEY_BACK):
                    self.set_current_screen(KEY_PODCAST_PLAYER)
                else:
                    if getattr(state, "source", None) == None:                    
                        state.source = RESUME
                    self.set_current_screen(name=KEY_PODCAST_PLAYER, state=state)
                self.current_player_screen = KEY_PODCAST_PLAYER
                return
        except:
            pass
        
        if state.name != PODCASTS:
            self.config[PODCASTS][PODCAST_EPISODE_NAME] = state.name
            
        if hasattr(state, "file_name"):
            self.config[PODCASTS][PODCAST_EPISODE_URL] = state.file_name
        elif hasattr(state, "url"):
            self.config[PODCASTS][PODCAST_EPISODE_URL] = state.url
        
        listeners = self.get_play_screen_listeners()
        listeners[AUDIO_FILES] = self.go_podcast_episodes
        listeners[KEY_SEEK] = self.player.seek
        screen = PodcastPlayerScreen(listeners, self.util, self.player.get_current_playlist, self.voice_assistant, self.player.stop)
        self.screens[KEY_PODCAST_PLAYER] = screen
        self.current_player_screen = KEY_PODCAST_PLAYER
        screen.load_playlist = self.player.load_playlist
        
        self.player.add_player_listener(screen.time_control.set_track_info)
        self.player.add_player_listener(screen.update_arrow_button_labels)
        self.player.add_end_of_track_listener(screen.end_of_track)
        
        screen.add_play_listener(self.screensaver_dispatcher.change_image)
        screen.add_play_listener(self.screensaver_dispatcher.change_image_folder)
        
        self.set_current_screen(KEY_PODCAST_PLAYER, state=state)
        state = State()
        state.cover_art_folder = screen.file_button.state.cover_art_folder
        self.screensaver_dispatcher.change_image_folder(state)
        
        if self.use_web:
            update = self.web_server.update_web_ui
            redraw = self.web_server.redraw_web_ui
            start = self.web_server.start_time_control_to_json
            stop = self.web_server.stop_time_control_to_json
            title_to_json = self.web_server.title_to_json
            screen.add_screen_observers(update, redraw, start, stop, title_to_json)
            screen.add_loading_listener(redraw)
            self.web_server.add_player_listener(screen.time_control)
            self.player.add_player_listener(self.web_server.update_player_listeners)
        
    def go_audiobooks(self, state=None):
        """ Go to the Audiobooks Screen
        
        :param state: button state
        """
        listeners = self.get_play_screen_listeners()
        listeners[KEY_SEEK] = self.player.seek        
        self.exit_current_screen()
        s = State()
        s.source = INIT
        s.book_url = self.config[AUDIOBOOKS][BROWSER_BOOK_URL]
        
        if self.config[CURRENT][LANGUAGE] == RUSSIAN:
            s.name = AUDIOKNIGI
        else:
            s.name = LOYALBOOKS
        
        s.language_url = self.get_language_url()
        self.config[AUDIOBOOKS][BROWSER_SITE] = s.name
        site_player = None
        
        state = State()
        self.screensaver_dispatcher.change_image_folder(state)
        
        try:
            site_player = self.screens[KEY_PLAY_SITE]
            s.source = RESUME
            if getattr(state, "file_name", None) == None:
                s.file_name = self.config[AUDIOBOOKS][BROWSER_TRACK_FILENAME]
        except:
            pass
            
        if not self.config[AUDIOBOOKS][BROWSER_BOOK_URL]:
            self.go_site_news_screen(s)
        else:
            self.go_site_playback(s)
    
    def go_equalizer(self, state=None):
        """ Go to the Equalizer Screen
        
        :param state: button state
        """        
        if self.get_current_screen(EQUALIZER): return
        
        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_PLAYER] = self.go_player
        equalizer_screen = EqualizerScreen(self.util, listeners, self.voice_assistant)
        self.screens[EQUALIZER] = equalizer_screen
        self.set_current_screen(EQUALIZER)
        
        if self.use_web:
            self.add_screen_observers(equalizer_screen)
            
    def go_timer(self, state=None):
        """ Go to the Timer Screen
        
        :param state: button state
        """        
        if self.get_current_screen(TIMER): return
        
        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_PLAYER] = self.go_player
        listeners[SLEEP_NOW] = self.sleep
        timer_screen = TimerScreen(self.util, listeners, self.voice_assistant, self.lock, self.start_timer_thread)
        self.screens[TIMER] = timer_screen
        self.set_current_screen(TIMER)
        
        if self.use_web:
            self.add_screen_observers(timer_screen)
    
    def get_language_url(self):
        """ Return language URL constant for current language """
        
        language = self.config[CURRENT][LANGUAGE]
        
        if language == ENGLISH_USA:
            return ""
        elif language == RUSSIAN:
            return None
        else:
            return LANGUAGE_PREFIX + language + os.sep
    
    def get_parser(self):
        """ Return site parser for the current site """
        
        name = self.config[AUDIOBOOKS][BROWSER_SITE]
        if name == LOYALBOOKS:            
            return LoyalBooksParser()            
        elif name == AUDIOKNIGI:
            return AudioKnigiParser()
        return None
                    
    def go_savers(self, state):
        """ Go to the Screensavers Screen
        
        :param state: button state
        """
        if self.get_current_screen(SCREENSAVER): return
        
        listeners = {KEY_HOME: self.go_home, KEY_PLAYER: self.go_player}
        saver_screen = SaverScreen(self.util, listeners, self.voice_assistant)
        saver_screen.saver_menu.add_listener(self.screensaver_dispatcher.change_saver_type)
        saver_screen.delay_menu.add_listener(self.screensaver_dispatcher.change_saver_delay)
        self.screens[SCREENSAVER] = saver_screen
        self.set_current_screen(SCREENSAVER)
        
        if self.use_web:
            self.add_screen_observers(saver_screen)
        
    def go_about(self, state):
        """ Go to the About Screen
        
        :param state: button state
        """
        self.exit_current_screen()
        self.set_current_screen(KEY_ABOUT)
        if self.use_web:
            self.add_screen_observers(self.screens[KEY_ABOUT])
    
    def go_black(self):
        """ Go to the Black Screen for sleeping mode
        
        :param state: button state
        """
        self.exit_current_screen()
        
        try:
            self.screens[KEY_BLACK]    
        except:
            black = BlackScreen(self.util)
            black.add_listener(self.wake_up)
            self.screens[KEY_BLACK] = black
        
        self.set_current_screen(KEY_BLACK)
        if self.use_web:
            self.web_server.redraw_web_ui()
    
    def go_stations(self, state=None):
        """ Go to the Stations Screen
        
        :param state: button state
        """
        self.deactivate_current_player(KEY_STATIONS)
        
        if self.get_current_screen(KEY_STATIONS, state): return
        
        listeners = self.get_play_screen_listeners()
        listeners[KEY_GENRES] = self.go_genres
        station_screen = StationScreen(listeners, self.util, self.voice_assistant)
        self.screens[KEY_STATIONS] = station_screen
        self.set_current_screen(KEY_STATIONS)
        self.screensaver_dispatcher.change_image(station_screen.station_menu.station_button.state)
        station_screen.station_menu.add_listener(self.screensaver_dispatcher.change_image)        
        station_screen.station_menu.add_change_logo_listener(self.screensaver_dispatcher.change_image)        
        station_screen.station_menu.add_listener(self.screensaver_dispatcher.change_image_folder)
        self.player.add_player_listener(station_screen.screen_title.set_text)
        station_screen.station_menu.add_listener(station_screen.play_button.draw_default_state)
        
        if self.config[USAGE][USE_ALBUM_ART]:
            self.player.add_player_listener(station_screen.station_menu.show_album_art)        
        
        if self.use_web:
            update = self.web_server.update_web_ui
            redraw = self.web_server.redraw_web_ui
            title_to_json = self.web_server.title_to_json
            station_screen.add_screen_observers(update, redraw, title_to_json)
            self.web_server.station_menu = station_screen.station_menu
            station_screen.station_menu.add_menu_click_listener(self.web_server.station_menu_to_json)
            station_screen.station_menu.add_mode_listener(self.web_server.station_menu_to_json)
    
    def set_config_volume(self, volume):
        """ Listener for volume change events
        
        :param volume: new volume value
        """
        self.config[PLAYER_SETTINGS][VOLUME] = str(int(volume.position))
            
    def go_genres(self, state):
        """ Go to the Genre Screen
        
        :param state: button state
        """
        if self.get_current_screen(KEY_GENRES): return
        
        listeners = {KEY_GENRE: self.go_stations, KEY_HOME: self.go_home, KEY_PLAYER: self.go_player, KEY_FAVORITES: self.go_favorites}
        genre_screen = RadioGroupScreen(self.util, listeners, self.voice_assistant)
        self.screens[KEY_GENRES] = genre_screen
        self.set_current_screen(KEY_GENRES)
        
        if self.use_web:
            self.add_screen_observers(genre_screen)
    
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
            if self.current_screen:
                ps = self.screens[self.current_screen]
                ps.set_visible(False)
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
                    new_genre = False
                    if state != None and getattr(state, "source", None) != None:
                        src = getattr(state, "source", None)
                        if src == GENRE or src == KEY_FAVORITES:
                            new_genre = True
                    new_language = self.current_language != self.config[CURRENT][LANGUAGE]
                    if new_genre or new_language or self.current_player_screen != name or self.current_mode != name:
                        self.current_language = self.config[CURRENT][LANGUAGE]
                        cs.set_current(state=state)
                elif name == KEY_PLAY_FILE:
                    f = getattr(state, "file_name", None)
                    if f and self.current_audio_file != state.file_name or self.current_player_screen != name:
                        a = getattr(state, "file_name", None)
                        if a != None: 
                            self.current_audio_file = a 
                        cs.set_current(state=state)
                elif name == KEY_PLAY_CD:
                    cd_drive_name = self.config[CD_PLAYBACK][CD_DRIVE_NAME]
                    if self.cdutil.get_cd_drive_id_by_name(cd_drive_name) != None:
                        file_name = getattr(state, "file_name", None) 
                        if file_name and file_name.startswith("cdda:"):
                            state.url = state.file_name
                            parts = state.url.split()
                            cd_track_id = parts[1].split("=")[1]       
                            self.config[CD_PLAYBACK][CD_TRACK] = int(cd_track_id)
                            if cs.cd_album != None:
                                state.album = cs.cd_album
                            cs.set_current(new_track=True, state=state)
                        else:
                            s = self.cdutil.get_cd_track()
                            if s and s.file_name:
                                if state != None and getattr(state, "source", None) != None:
                                    s.source = state.source
                                
                                if cs.cd_album != None:
                                    s.album = cs.cd_album
                                cd_track_id = int(s.file_name.split("=")[1])
                                if cd_track_id != self.config[CD_PLAYBACK][CD_TRACK] or self.current_player_screen != name:
                                    cs.set_current(state=s)
                elif name.endswith(KEY_BOOK_SCREEN):
                    if state:
                        cs.set_current(state)
                elif name == KEY_PLAY_SITE or name == STREAM:
                    cs.set_current(state=state)
                elif name == KEY_BOOK_TRACK_SCREEB:
                    state = State()
                    ps = self.screens[KEY_PLAY_SITE]
                    state.playlist = ps.get_playlist()
                    state.current_track_index = ps.current_track_index
                    cs.set_current(state)
                elif name == KEY_CD_TRACKS:
                    cs.set_current(state)
                elif name == PODCASTS or name == KEY_PODCAST_EPISODES:
                    cs.set_current(state)
                elif name == KEY_PODCAST_PLAYER:
                    f = getattr(state, "file_name", None)
                    if f and self.current_audio_file != f or self.current_player_screen != name or state.source == INIT:
                        self.current_audio_file = f
                        source = getattr(state, "source", None)
                        if source == "episode_menu":
                            cs.set_current(state=state, new_track=True)
                        elif source == RESUME:
                            s = State()
                            s.name = self.config[PODCASTS][PODCAST_EPISODE_NAME] 
                            s.url = self.config[PODCASTS][PODCAST_EPISODE_URL]
                            s.podcast_url = self.config[PODCASTS][PODCAST_URL]
                            podcasts_util = self.util.get_podcasts_util()
                            s.podcast_image_url = podcasts_util.summary_cache[s.podcast_url].episodes[0].podcast_image_url
                            s.status = podcasts_util.get_episode_status(s.podcast_url, s.url)
                            if self.util.connected_to_internet:
                                s.online = True
                            else:
                                s.online = False
                            cs.set_current(state=s)
                        else:
                            cs.set_current(state=state)
                    else:
                        source = getattr(state, "source", None)
                        if source == RESUME:
                            cs.start_timer()                             
            cs.clean_draw_update()
            self.event_dispatcher.set_current_screen(cs)
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
            if volume == None: 
                config_volume = int(self.config[PLAYER_SETTINGS][VOLUME])
            else:
                config_volume = volume.position
            
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
        
        self.player.cd_tracks = None
    
    def store_current_track_time(self, mode):
        """ Save current track time in configuration object
        
        :param mode: 
        """
        k = None
        if self.current_player_screen == KEY_PLAY_FILE:
            k = KEY_PLAY_FILE
        elif self.current_player_screen == KEY_PLAY_SITE:
            k = KEY_PLAY_SITE
        elif self.current_player_screen == KEY_PLAY_CD:
            k = KEY_PLAY_CD
        elif self.current_player_screen == KEY_PODCAST_PLAYER:
            k = KEY_PODCAST_PLAYER
        
        if k and k in self.screens:    
            s = self.screens[k]
            tc = s.time_control
            t = tc.seek_time
            ps = self.current_player_screen
            if ps == KEY_PLAY_SITE:
                self.config[AUDIOBOOKS][BROWSER_BOOK_TIME] = t
            elif ps == KEY_PLAY_FILE:
                self.config[FILE_PLAYBACK][CURRENT_TRACK_TIME] = t
            elif ps == KEY_PLAY_CD:
                self.config[CD_PLAYBACK][CD_TRACK_TIME] = t
            elif ps == KEY_PODCAST_PLAYER:
                self.config[PODCASTS][PODCAST_EPISODE_TIME] = t
        
    def shutdown(self, event=None):
        """ System shutdown handler
        
        :param event: the event
        """
        s = self.config[SCRIPTS][SHUTDOWN]
        if s != None and len(s.strip()) != 0:
            self.util.run_script(s)
        
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
        
        if self.config[CURRENT][MODE] == RADIO:
            title_screen_name = KEY_STATIONS
        elif self.config[CURRENT][MODE] == AUDIO_FILES:
            title_screen_name = KEY_PLAY_FILE
        elif self.config[CURRENT][MODE] == AUDIOBOOKS:
            title_screen_name = KEY_PLAY_SITE
        elif self.config[CURRENT][MODE] == CD_PLAYER:
            title_screen_name = KEY_PLAY_CD
        
        if title_screen_name:
            self.screens[title_screen_name].screen_title.shutdown()
        
        players = [KEY_PLAY_FILE, KEY_PLAY_SITE, KEY_PLAY_CD]
        
        if title_screen_name and (title_screen_name in players):
            self.screens[title_screen_name].time_control.stop_thread()
        
        pygame.quit()
        
        if self.config[LINUX_PLATFORM]:
            subprocess.call("sudo poweroff", shell=True)
        else:
            if self.config[AUDIO][PLAYER_NAME] == MPD:
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
