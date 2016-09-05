# Copyright 2016 Peppy Player peppy.player@gmail.com
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

from subprocess import Popen
from event.dispatcher import EventDispatcher
from player.proxy import Proxy 
from screensaver.screensaverdispatcher import ScreensaverDispatcher
from ui.screen.genre import GenreScreen
from ui.screen.home import HomeScreen
from ui.screen.language import LanguageScreen
from ui.screen.saver import SaverScreen
from ui.screen.about import AboutScreen
from ui.screen.station import StationScreen
from util.config import USAGE, USE_WEB, AUDIO, SERVER_FOLDER, SERVER_COMMAND, CLIENT_NAME, \
    LINUX_PLATFORM, CURRENT, LANGUAGE, STATION, VOLUME
from util.util import Util, LABELS

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
        self.screens = {"about" : about}        
        
        self.start_audio()
        
        self.screensaver_dispatcher = ScreensaverDispatcher(self.util)
        if self.use_web:
            self.web_server.add_screensaver_web_listener(self.screensaver_dispatcher)
               
        self.event_dispatcher = EventDispatcher(self.screensaver_dispatcher, self.util)        
        self.current_screen = None
        self.go_stations()
    
    def start_audio(self):
        """ Starts audio server and client """
        
        folder = self.config[AUDIO][SERVER_FOLDER]
        cmd = self.config[AUDIO][SERVER_COMMAND]
        client_name = self.config[AUDIO][CLIENT_NAME]
        linux = self.config[LINUX_PLATFORM]
        
        if folder != None and cmd != None:
            proxy = Proxy(linux, folder, cmd, self.config[CURRENT][VOLUME])
            self.audio_server = proxy.start()
        
        p = "player.client." + client_name
        m = importlib.import_module(p)
        n = client_name.title()
        self.player = getattr(m, n)()
        self.player.set_platform(linux)
        self.player.set_proxy(self.audio_server)
        self.player.start_client()
            
    def set_current_screen_visible(self, flag):
        """ Set current screen visibility flag
        
        :param flag: visibility flag
        """        
        with self.lock:
            cs = self.current_screen
            if cs and self.screens and self.screens[cs]:
                self.screens[cs].set_visible(flag)
        
    def set_mode(self, state):
        """ Set current mode (e.g. Radio, Language etc)
        
        :param state: button state
        """  
        if state.name == "radio": self.go_stations(state)
        elif state.name == "music": self.go_hard_drive(state)
        elif state.name == "language": self.go_language(state)
        elif state.name == "stream": self.go_stream(state)
        elif state.name == "screensaver": self.go_savers(state)
        elif state.name == "about": self.go_about(state)        

    def go_home(self, state):
        """ Go to the Home Screen
        
        :param state: button state
        """
        self.set_current_screen_visible(False)
        try:
            if self.screens and self.screens["home"]:
                self.set_current_screen("home")            
                return
        except KeyError:
            pass

        home_screen = HomeScreen(self.util, self.set_mode)
        self.screens["home"] = home_screen
        self.set_current_screen("home")
        
        if self.use_web:
            self.web_server.add_home_screen_web_listeners(home_screen)
    
    def go_language(self, state):
        """ Go to the Language Screen
        
        :param state: button state
        """
        self.set_current_screen_visible(False)
        try:
            if self.screens["language"]:
                self.set_current_screen("language")            
                return
        except KeyError:
            pass

        language_screen = LanguageScreen(self.util, self.change_language)
        self.screens["language"] = language_screen
        self.set_current_screen("language")
        
        if self.use_web:
            self.web_server.add_language_screen_web_listeners(language_screen)
    
    def change_language(self, state):
        """ Change current language and go to the Home Screen
        
        :param state: button state
        """
        if state.name != self.config[CURRENT][LANGUAGE]:
            self.config[LABELS].clear()
            try:
                stations = self.screens["stations"]
                if stations:
                    self.player.remove_player_listener(stations.screen_title.set_text)
            except KeyError:
                pass
            self.config[CURRENT][LANGUAGE] = state.name
            self.config[LABELS] = self.util.get_labels()        
            self.screens = {k : v for k, v in self.screens.items() if k == 'about'}
            self.current_screen = None            
        self.go_home(state)
        
    def go_hard_drive(self, state):
        """ Go to the Hard Drive Screen
        
        :param state: button state
        """
        pass
        
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
            if self.screens["saver"]:
                self.set_current_screen("saver")            
                return
        except KeyError:
            pass

        saver_screen = SaverScreen(self.util, self.go_home)
        saver_screen.saver_menu.add_listener(self.screensaver_dispatcher.change_saver_type)
        saver_screen.delay_menu.add_listener(self.screensaver_dispatcher.change_saver_delay)
        self.screens["saver"] = saver_screen
        self.set_current_screen("saver")
        
        if self.use_web:
            self.web_server.add_saver_screen_web_listeners(saver_screen)
        
    def go_about(self, state):
        """ Go to the About Screen
        
        :param state: button state
        """
        self.set_current_screen_visible(False)
        self.set_current_screen("about")
        if self.use_web:
            self.web_server.add_about_screen_web_listeners(self.screens["about"])
    
    def go_stations(self, state=None):
        """ Go to the Stations Screen
        
        :param state: button state
        """
        self.set_current_screen_visible(False)        
        try:
            if self.screens["stations"]:
                self.set_current_screen("stations")
                return
        except KeyError:
            pass
        
        listeners = {}
        listeners["go home"] = self.go_home
        listeners["go genres"] = self.go_genres
        listeners["shutdown"] = self.shutdown
        listeners["go config"] = self.go_savers
        listeners["play"] = self.play_pause
        listeners["play-pause"] = self.play_pause
        listeners["set volume"] = self.player.set_volume
        listeners["set config volume"] = self.set_config_volume
        listeners["set screensaver volume"] = self.screensaver_dispatcher.change_volume
        listeners["mute"] = self.player.mute
        listeners["play"] = self.player.play  
        station_screen = StationScreen(listeners, self.util)
        self.screens["stations"] = station_screen
        v = self.player.get_volume()
        if not v:
            v = "0"
        station_screen.volume.set_position(int(v))
        station_screen.volume.update_position()
        self.set_current_screen("stations")

        current_station = self.config[CURRENT][STATION]
        station_screen.station_menu.set_station(current_station)
        self.screensaver_dispatcher.change_image(station_screen.station_menu.station_button.state)
        station_screen.station_menu.add_listener(self.screensaver_dispatcher.change_image)
        self.player.add_player_listener(station_screen.screen_title.set_text)
        
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
            if self.screens["genres"]:
                self.set_current_screen("genres")            
                return
        except KeyError:
            pass

        genre_screen = GenreScreen(self.util, self.go_stations)
        self.screens["genres"] = genre_screen
        self.set_current_screen("genres")
        
        if self.use_web:
            self.web_server.add_genre_screen_web_listeners(genre_screen)
    
    def play_pause(self, state=None):
        """ Handle Play/Pause
        
        :param state: button state
        """
        self.player.play_pause()
    
    def set_current_screen(self, name):
        """ Set current screen defined by its name
        
        :param name: screen name
        """
        with self.lock:
            self.current_screen = name
            cs = self.screens[self.current_screen]
            cs.set_visible(True)
            cs.set_current()
            cs.clean_draw_update()
            self.event_dispatcher.set_current_screen(cs) 
        
    def shutdown(self, event):
        """ System shutdown handler
        
        :param event: the event
        """
        self.util.config_class.save_config()
        self.player.shutdown()
        
        if self.use_web:
            try:
                self.web_server.shutdown()
            except:
                pass
        
        stations = self.screens["stations"]
        stations.screen_title.shutdown()
        
        if self.config[LINUX_PLATFORM]:
            subprocess.call("sudo poweroff", shell=True)
        else:
            Popen("taskkill /F /T /PID {pid}".format(pid=self.audio_server.pid))
            pygame.quit()            
            os._exit(0)

def main():
    """ Main method """    
    peppy = Peppy()    
    peppy.event_dispatcher.dispatch(peppy.player, peppy.shutdown)    
        
if __name__ == "__main__":
    main()
