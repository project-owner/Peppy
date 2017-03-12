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
from ui.screen.genre import GenreScreen
from ui.screen.home import HomeScreen
from ui.screen.language import LanguageScreen
from ui.screen.saver import SaverScreen
from ui.screen.about import AboutScreen
from ui.screen.station import StationScreen
from ui.screen.filebrowser import FileBrowserScreen
from ui.screen.fileplayer import FilePlayerScreen
from util.config import USAGE, USE_WEB, AUDIO, SERVER_FOLDER, SERVER_COMMAND, CLIENT_NAME, \
    LINUX_PLATFORM, CURRENT, VOLUME, MODE, CURRENT_FILE, CURRENT_FOLDER, CURRENT_TRACK_TIME
from util.util import Util, LABELS
from util.keys import KEY_RADIO, KEY_AUDIO_FILES, KEY_STREAM, KEY_LANGUAGE, KEY_SCREENSAVER, \
    KEY_ABOUT, KEY_PLAY_FILE, KEY_STATIONS, KEY_GENRES, KEY_HOME, KEY_SEEK, KEY_BACK, KEY_SHUTDOWN, \
    KEY_PLAY_PAUSE, KEY_SET_VOLUME, KEY_SET_CONFIG_VOLUME, KEY_SET_SAVER_VOLUME, KEY_MUTE, KEY_PLAY, GO_BACK

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
        
        self.start_audio()
        
        self.screensaver_dispatcher = ScreensaverDispatcher(self.util)
        if self.use_web:
            self.web_server.add_screensaver_web_listener(self.screensaver_dispatcher)
               
        self.event_dispatcher = EventDispatcher(self.screensaver_dispatcher, self.util)        
        self.current_screen = None
        
        if self.config[CURRENT][MODE] == KEY_RADIO:            
            self.go_stations()
        elif self.config[CURRENT][MODE] == KEY_AUDIO_FILES:
            state = State()
            state.folder = self.config[CURRENT][CURRENT_FOLDER].replace('\\\\', '\\')
            state.file_name = self.config[CURRENT][CURRENT_FILE]            
            state.url = state.folder + os.sep + state.file_name
            self.go_file_playback(state)
    
    def start_audio(self):
        """ Starts audio server and client """
        
        folder = self.config[AUDIO][SERVER_FOLDER]
        cmd = self.config[AUDIO][SERVER_COMMAND]
        client_name = self.config[AUDIO][CLIENT_NAME]
        linux = self.config[LINUX_PLATFORM]
        
        if folder != None and cmd != None:
            proxy = Proxy(linux, folder, cmd, self.config[CURRENT][VOLUME])
            self.audio_server = proxy.start()
        
        time.sleep(2)
            
        p = "player.client." + client_name
        m = importlib.import_module(p)
        n = client_name.title()
        self.player = getattr(m, n)()
        self.player.set_platform(linux)
        self.player.set_proxy(self.audio_server)
        self.player.set_file_util(self.util.file_util)
        self.player.start_client()
        
    def set_current_screen_visible(self, flag):
        """ Set current screen visibility flag
        
        :param flag: visibility flag
        """        
        with self.lock:
            cs = self.current_screen
            if cs and self.screens and self.screens[cs]:
                self.screens[cs].set_visible(flag)
                
    def stop_file_playback(self):
        """ Stop file playback if any """
                
        with self.lock:
            try:
                s = self.screens[KEY_PLAY_FILE]
                s.time_control.timer_started = False
            except:
                pass
        
    def set_mode(self, state):
        """ Set current mode (e.g. Radio, Language etc)
        
        :param state: button state
        """ 
        self.store_current_track_time(state.previous_mode)         
        if state.name == KEY_RADIO: self.go_stations(state)
        elif state.name == KEY_AUDIO_FILES: self.go_file_playback(state)
        elif state.name == KEY_LANGUAGE: self.go_language(state)
        elif state.name == KEY_STREAM: self.go_stream(state)
        elif state.name == KEY_SCREENSAVER: self.go_savers(state)
        elif state.name == KEY_ABOUT: self.go_about(state)        

    def go_home(self, state):
        """ Go to the Home Screen
        
        :param state: button state
        """
        self.set_current_screen_visible(False)
        try:
            if self.screens and self.screens[KEY_HOME]:
                self.set_current_screen(KEY_HOME)            
                return
        except KeyError:
            pass

        home_screen = HomeScreen(self.util, self.set_mode)
        self.screens[KEY_HOME] = home_screen
        self.set_current_screen(KEY_HOME)
        
        if self.use_web:
            self.web_server.add_home_screen_web_listeners(home_screen)
    
    def go_language(self, state):
        """ Go to the Language Screen
        
        :param state: button state
        """
        self.set_current_screen_visible(False)
        try:
            if self.screens[KEY_LANGUAGE]:
                self.set_current_screen(KEY_LANGUAGE)            
                return
        except KeyError:
            pass

        language_screen = LanguageScreen(self.util, self.change_language)
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
        
    def go_files(self, state=None):
        """ Go to the File Browser Screen
        
        :param state: button state
        """
        self.set_current_screen_visible(False)
        try:
            if self.screens[KEY_AUDIO_FILES]:
                self.set_current_screen(KEY_AUDIO_FILES)            
                return
        except KeyError:
            pass

        file_player = self.screens[KEY_PLAY_FILE]

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_PLAY_FILE] = self.go_file_playback
        listeners[GO_BACK] = file_player.restore_current_folder
        file_browser_screen = FileBrowserScreen(self.util, self.player.load_playlist, listeners)
        
        file_player.add_play_listener(file_browser_screen.file_menu.select_item)
        file_browser_screen.file_menu.add_playlist_size_listener(file_player.set_playlist_size)
        file_browser_screen.file_menu.add_play_file_listener(file_player.play_button.draw_default_state)
        
        self.screens[KEY_AUDIO_FILES] = file_browser_screen
        self.set_current_screen(KEY_AUDIO_FILES)
        
        if self.use_web:
            self.web_server.add_file_browser_screen_web_listeners(file_browser_screen)
    
    def go_file_playback(self, state=None):
        """ Go to the File Player Screen
        
        :param state: button state
        """
        self.set_current_screen_visible(False)
        try:
            if self.screens[KEY_PLAY_FILE]:
                if getattr(state, "name", None) and (state.name == KEY_HOME or state.name == KEY_BACK):
                    self.set_current_screen(KEY_PLAY_FILE, True)
                else:
                    self.set_current_screen(name=KEY_PLAY_FILE, state=state)
                return
        except KeyError:
            pass        
        
        if getattr(state, "url", None):        
            tokens = state.url.split(os.sep)       
            self.config[CURRENT][CURRENT_FILE] = tokens[len(tokens) - 1]
        
        listeners = self.get_play_screen_listeners()
        listeners[KEY_AUDIO_FILES] = self.go_files
        listeners[KEY_SEEK] = self.player.seek
        screen = FilePlayerScreen(listeners, self.util)
        self.screens[KEY_PLAY_FILE] = screen
        screen.playlist_provider = self.player.load_playlist
        
        self.player.add_player_listener(screen.screen_title.set_text)
        self.player.add_player_listener(screen.time_control.set_track_info)
        self.player.add_player_listener(screen.update_arrow_button_labels)
        self.player.add_end_of_track_listener(screen.end_of_track)
        screen.add_play_listener(self.screensaver_dispatcher.change_image)
        screen.add_play_listener(self.screensaver_dispatcher.change_image_folder)
        
        self.set_current_screen(KEY_PLAY_FILE)
        self.screensaver_dispatcher.change_image(screen.file_button.state)
        state = State()
        state.cover_art_folder = screen.file_button.state.cover_art_folder
        self.screensaver_dispatcher.change_image_folder(state)
        
        if self.use_web:
            self.web_server.add_file_player_web_listeners(screen)
            self.player.add_player_listener(self.web_server.file_player_time_control_change)
                        
    def get_play_screen_listeners(self):
        """ File player screen listeners getter """
        
        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_SHUTDOWN] = self.shutdown        
        listeners[KEY_PLAY_PAUSE] = self.play_pause
        listeners[KEY_SET_VOLUME] = self.player.set_volume
        listeners[KEY_SET_CONFIG_VOLUME] = self.set_config_volume
        listeners[KEY_SET_SAVER_VOLUME] = self.screensaver_dispatcher.change_volume
        listeners[KEY_MUTE] = self.player.mute
        listeners[KEY_PLAY] = self.player.play
        return listeners
        
    def go_stream(self, state):
        """ Go to the Stream Screen
        
        :param state: button state
        """
        pass
        
    def go_savers(self, state):
        """ Go to the Screensavers Screen
        
        :param state: button state
        """
        self.set_current_screen_visible(False)
        try:
            if self.screens[KEY_SCREENSAVER]:
                self.set_current_screen(KEY_SCREENSAVER)            
                return
        except KeyError:
            pass

        saver_screen = SaverScreen(self.util, self.go_home)
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
        self.set_current_screen_visible(False)
        self.set_current_screen(KEY_ABOUT)
        if self.use_web:
            self.web_server.add_about_screen_web_listeners(self.screens[KEY_ABOUT])
    
    def go_stations(self, state=None):
        """ Go to the Stations Screen
        
        :param state: button state
        """
        self.set_current_screen_visible(False)
        self.stop_file_playback()
                
        try:
            if self.screens[KEY_STATIONS]:
                self.set_current_screen(KEY_STATIONS)
                return
        except KeyError:
            pass
        
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
        self.config[CURRENT][VOLUME] = str(int(volume))
            
    def go_genres(self, state):
        """ Go to the Genre Screen
        
        :param state: button state
        """
        self.set_current_screen_visible(False)
        try:
            if self.screens[KEY_GENRES]:
                self.set_current_screen(KEY_GENRES)            
                return
        except KeyError:
            pass

        genre_screen = GenreScreen(self.util, self.go_stations)
        self.screens[KEY_GENRES] = genre_screen
        self.set_current_screen(KEY_GENRES)
        
        if self.use_web:
            self.web_server.add_genre_screen_web_listeners(genre_screen)
    
    def play_pause(self, state=None):
        """ Handle Play/Pause
        
        :param state: button state
        """
        self.player.play_pause()
    
    def set_current_screen(self, name, go_back=False, state=None):
        """ Set current screen defined by its name
        
        :param name: screen name
        """
        with self.lock:
            self.current_screen = name
            cs = self.screens[self.current_screen]
            cs.set_visible(True)
            if go_back:
                cs.go_back()
            else:
                cs.set_current(state=state)
            cs.clean_draw_update()
            self.event_dispatcher.set_current_screen(cs)
            
            config_volume = int(self.config[CURRENT][VOLUME])
            if self.player.get_volume() != config_volume:
                self.player.set_volume(config_volume) 
    
    def store_current_track_time(self, mode):
        """ Save current track time in configuration object
        
        :param mode: 
        """
        if mode == KEY_AUDIO_FILES: 
            self.config[CURRENT][CURRENT_TRACK_TIME] = self.player.get_current_track_time()
        
    def shutdown(self, event):
        """ System shutdown handler
        
        :param event: the event
        """
        self.store_current_track_time(self.config[CURRENT][MODE])
            
        self.util.config_class.save_config()
        self.player.shutdown()
        
        if self.use_web:
            try:
                self.web_server.shutdown()
            except:
                pass
        
        if self.config[CURRENT][MODE] == KEY_RADIO:
            self.screens[KEY_STATIONS].screen_title.shutdown()
        elif self.config[CURRENT][MODE] == KEY_AUDIO_FILES:
            self.screens[KEY_PLAY_FILE].screen_title.shutdown()
            
        pygame.quit()
        
        if self.config[LINUX_PLATFORM]:
            subprocess.call("sudo poweroff", shell=True)
        else:
            Popen("taskkill /F /T /PID {pid}".format(pid=self.audio_server.pid))                        
            os._exit(0)

def main():
    """ Main method """
        
    peppy = Peppy()    
    peppy.event_dispatcher.dispatch(peppy.player, peppy.shutdown)    
        
if __name__ == "__main__":
    main()
