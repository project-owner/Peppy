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

import sys
import os
import logging
import codecs

from configparser import ConfigParser
from util.keys import *

FILE_CONFIG = "config.txt"
FILE_CURRENT = "current.txt"
FILE_PLAYERS = "players.txt"
AUDIO = "audio"

FILE_BROWSER = "file.browser"
AUDIO_FILE_EXTENSIONS = "audio.file.extensions"
PLAYLIST_FILE_EXTENSIONS = "playlist.file.extensions"
FOLDER_IMAGES = "folder.images"
COVER_ART_FOLDERS = "cover.art.folders"
AUTO_PLAY_NEXT_TRACK = "auto.play.next.track"
CYCLIC_PLAYBACK = "cyclic.playback"

CURRENT_FILE_PLAYBACK_MODE = "file.playback.mode"
CURRENT_FOLDER = "folder"
CURRENT_FILE_PLAYLIST = "file.playlist"
CURRENT_FILE = "file"
CURRENT_TRACK_TIME = "track.time"

BROWSER_SITE = "site"
BROWSER_BOOK_TITLE = "book.title"
BROWSER_BOOK_URL = "book.url"
BROWSER_TRACK_FILENAME = "book.track.filename"
BROWSER_BOOK_TIME = "book.time"

SERVER_FOLDER = "server.folder"
SERVER_COMMAND = "server.command"
CLIENT_NAME = "client.name"
MUSIC_FOLDER = "music.folder"
PLAYER_NAME = "player.name"
STREAM_CLIENT_PARAMETERS = "stream.client.parameters"
STREAM_SERVER_PARAMETERS = "stream.server.parameters"
HOST = "host"
PORT = "port"
USAGE = "usage"
USE_TOUCHSCREEN = "use.touchscreen"
USE_MOUSE = "use.mouse"
USE_LIRC = "use.lirc"
USE_ROTARY_ENCODERS = "use.rotary.encoders"
USE_WEB = "use.web"
USE_LOGGING = "use.logging"
USE_STDOUT = "use.stdout"
USE_STREAM_SERVER = "use.stream.server"
USE_BROWSER_STREAM_PLAYER = "use.browser.stream.player"
USE_VOICE_ASSISTANT = "use.voice.assistant"
USE_HEADLESS = "use.headless"
FONT_SECTION = "font"

VOICE_ASSISTANT = "voice.assistant"
VOICE_ASSISTANT_TYPE = "type"
VOICE_ASSISTANT_CREDENTIALS = "credentials"
VOICE_DEVICE_MODEL_ID = "device.model.id"
VOICE_DEVICE_ID = "device.id"

MPD = "mpdsocket"
MPLAYER = "mplayer"
VLC = "vlcclient"

class Config(object):
    """ Read the configuration file config.txt and prepare dictionary from it """
    
    def __init__(self):
        """ Initializer """
        
        self.config = {}
        self.load_config(self.config)
        self.load_players(self.config)
        self.load_current(self.config)
        self.init_lcd()
        self.config[PYGAME_SCREEN] = self.get_pygame_screen()
        
    def load_config(self, config):
        """ Loads and parses configuration file config.txt.
        Creates dictionary entry for each property in the file.
        
        :param config: configuration object
        :return: dictionary containing all properties from the config.txt file
        """
        linux_platform = True
        if "win" in sys.platform:
            linux_platform = False
        config[LINUX_PLATFORM] = linux_platform
        
        config_file = ConfigParser()
        config_file.read(FILE_CONFIG)
    
        c = {WIDTH : config_file.getint(SCREEN_INFO, WIDTH)}
        c[HEIGHT] = config_file.getint(SCREEN_INFO, HEIGHT)
        c[DEPTH] = config_file.getint(SCREEN_INFO, DEPTH)
        c[FRAME_RATE] = config_file.getint(SCREEN_INFO, FRAME_RATE)
        c[HDMI] = config_file.getboolean(SCREEN_INFO, HDMI)
        c[NO_FRAME] = config_file.getboolean(SCREEN_INFO, NO_FRAME)
        config[SCREEN_INFO] = c
        
        folder_name = "medium"
        if c[WIDTH] < 350:
            folder_name = "small"
        elif c[WIDTH] > 700:
            folder_name = "large"
        config[ICON_SIZE_FOLDER] = folder_name                        
        config[SCREEN_RECT] = pygame.Rect(0, 0, c[WIDTH], c[HEIGHT])

        config[AUDIO_FILE_EXTENSIONS] = self.get_list(config_file, FILE_BROWSER, AUDIO_FILE_EXTENSIONS)
        config[PLAYLIST_FILE_EXTENSIONS] = self.get_list(config_file, FILE_BROWSER, PLAYLIST_FILE_EXTENSIONS)
        config[FOLDER_IMAGES] = self.get_list(config_file, FILE_BROWSER, FOLDER_IMAGES)
        config[COVER_ART_FOLDERS] = self.get_list(config_file, FILE_BROWSER, COVER_ART_FOLDERS)
        config[AUTO_PLAY_NEXT_TRACK] = config_file.getboolean(FILE_BROWSER, AUTO_PLAY_NEXT_TRACK)
        config[CYCLIC_PLAYBACK] = config_file.getboolean(FILE_BROWSER, CYCLIC_PLAYBACK)
        
        c = {USE_LIRC : config_file.getboolean(USAGE, USE_LIRC)}
        c[USE_TOUCHSCREEN] = config_file.getboolean(USAGE, USE_TOUCHSCREEN)
        c[USE_MOUSE] = config_file.getboolean(USAGE, USE_MOUSE)
        c[USE_ROTARY_ENCODERS] = config_file.getboolean(USAGE, USE_ROTARY_ENCODERS)
        c[USE_WEB] = config_file.getboolean(USAGE, USE_WEB)
        c[USE_LOGGING] = config_file.getboolean(USAGE, USE_LOGGING)
        c[USE_STDOUT] = config_file.getboolean(USAGE, USE_STDOUT)
        c[USE_STREAM_SERVER] = config_file.getboolean(USAGE, USE_STREAM_SERVER)
        c[USE_BROWSER_STREAM_PLAYER] = config_file.getboolean(USAGE, USE_BROWSER_STREAM_PLAYER)
        c[USE_VOICE_ASSISTANT] = config_file.getboolean(USAGE, USE_VOICE_ASSISTANT)
        c[USE_HEADLESS] = config_file.getboolean(USAGE, USE_HEADLESS)
        
        if not c[USE_STDOUT]:
            sys.stdout = os.devnull
            sys.stderr = os.devnull
        
        if c[USE_LOGGING]:
            logging.basicConfig(level=logging.NOTSET)            
        else:
            logging.disable(logging.CRITICAL)
            
        config[USAGE] = c
        
        c = {HTTP_PORT : config_file.get(WEB_SERVER, HTTP_PORT)}
        config[WEB_SERVER] = c
        
        c = {STREAM_SERVER_PORT : config_file.get(STREAM, STREAM_SERVER_PORT)}
        config[STREAM] = c
        
        c = {VOICE_ASSISTANT_TYPE: config_file.get(VOICE_ASSISTANT, VOICE_ASSISTANT_TYPE)}
        c[VOICE_ASSISTANT_CREDENTIALS] = config_file.get(VOICE_ASSISTANT, VOICE_ASSISTANT_CREDENTIALS)
        c[VOICE_DEVICE_MODEL_ID] = config_file.get(VOICE_ASSISTANT, VOICE_DEVICE_MODEL_ID)
        c[VOICE_DEVICE_ID] = config_file.get(VOICE_ASSISTANT, VOICE_DEVICE_ID)
        config[VOICE_ASSISTANT] = c

        c = {COLOR_WEB_BGR : self.get_color_tuple(config_file.get(COLORS, COLOR_WEB_BGR))}
        c[COLOR_DARK] = self.get_color_tuple(config_file.get(COLORS, COLOR_DARK))
        c[COLOR_MEDIUM] = self.get_color_tuple(config_file.get(COLORS, COLOR_MEDIUM))
        c[COLOR_DARK_LIGHT] = self.get_color_tuple(config_file.get(COLORS, COLOR_DARK_LIGHT))
        c[COLOR_BRIGHT] = self.get_color_tuple(config_file.get(COLORS, COLOR_BRIGHT))
        c[COLOR_CONTRAST] = self.get_color_tuple(config_file.get(COLORS, COLOR_CONTRAST))
        c[COLOR_LOGO] = self.get_color_tuple(config_file.get(COLORS, COLOR_LOGO))
        config[COLORS] = c
            
        config[FONT_KEY] = config_file.get(FONT_SECTION, FONT_KEY)
            
        config[ORDER_HOME_MENU] = self.get_section(config_file, ORDER_HOME_MENU)
        config[ORDER_HOME_NAVIGATOR_MENU] = self.get_section(config_file, ORDER_HOME_NAVIGATOR_MENU)
        config[ORDER_LANGUAGE_MENU] = self.get_section(config_file, ORDER_LANGUAGE_MENU)
        config[ORDER_GENRE_MENU] = self.get_section(config_file, ORDER_GENRE_MENU)
        config[ORDER_SCREENSAVER_MENU] = self.get_section(config_file, ORDER_SCREENSAVER_MENU)
        config[ORDER_SCREENSAVER_DELAY_MENU] = self.get_section(config_file, ORDER_SCREENSAVER_DELAY_MENU)

    def load_players(self, config):
        """ Loads and parses configuration file players.txt.
        Creates dictionary entry for each property in the file.
        
        :param config: configuration object
        :return: dictionary containing all properties from the players.txt file
        """
        config_file = ConfigParser()
        config_file.read(FILE_PLAYERS)
        platform = LINUX_PLATFORM
    
        c = {PLAYER_NAME : config_file.get(AUDIO, PLAYER_NAME)}
        
        music_folder = None
        if config[LINUX_PLATFORM]:
            try:
                music_folder = config_file.get(AUDIO, MUSIC_FOLDER + "." + LINUX_PLATFORM)
            except:
                pass
        else:
            platform = WINDOWS_PLATFORM
            try:
                music_folder = config_file.get(AUDIO, MUSIC_FOLDER + "." + WINDOWS_PLATFORM)
            except:
                pass
            
        if music_folder and not music_folder.endswith(os.sep):
            music_folder += os.sep            
        c[MUSIC_FOLDER] = music_folder         
    
        player_name = c[PLAYER_NAME]
        section_name = player_name + "." + platform
        
        try:
            c[SERVER_FOLDER] = config_file.get(section_name, SERVER_FOLDER)
        except:
            pass
        
        c[SERVER_COMMAND] = config_file.get(section_name, SERVER_COMMAND)
        c[CLIENT_NAME] = config_file.get(section_name, CLIENT_NAME)
        try:
            c[STREAM_CLIENT_PARAMETERS] = config_file.get(section_name, STREAM_CLIENT_PARAMETERS)
        except:
            pass
        try:
            c[STREAM_SERVER_PARAMETERS] = config_file.get(section_name, STREAM_SERVER_PARAMETERS)
        except:
            pass
    
        config[AUDIO] = c

    def load_current(self, config):
        """ Loads and parses configuration file current.txt.
        Creates dictionary entry for each property in the file.
        
        :param config: configuration object
        :return: dictionary containing all properties from the current.txt file
        """
        config_file = ConfigParser()
        config_file.read_file(codecs.open(FILE_CURRENT, "r", "utf8"))
        
        m = config_file.get(CURRENT, MODE)
        c = {MODE : m}
        lang = config_file.get(CURRENT, KEY_LANGUAGE)
        if not lang: lang = "en_us"
        c[KEY_LANGUAGE] = lang
        pl = config_file.get(CURRENT, RADIO_PLAYLIST)
        if not pl: pl = "news"
        c[RADIO_PLAYLIST] = pl
        c[STATION] = 0
        try:
            c[STATION] = config_file.getint(CURRENT, STATION)
        except:
            pass
        c[STREAM] = 0
        try:
            c[STREAM] = config_file.getint(CURRENT, STREAM)
        except:
            pass
        config[CURRENT] = c
        
        s = config_file.get(KEY_SCREENSAVER, NAME)
        if not s: s = "slideshow"
        c = {NAME: s}
        d = config_file.get(KEY_SCREENSAVER, KEY_SCREENSAVER_DELAY)
        if not d: d = "delay.1"
        c[KEY_SCREENSAVER_DELAY] = d
        config[KEY_SCREENSAVER] = c
        
        c = {VOLUME: 20}
        try:
            c[VOLUME] = config_file.getint(PLAYER_SETTINGS, VOLUME)
        except:
            pass
        
        c[MUTE] = False
        try:
            c[MUTE] = config_file.getboolean(PLAYER_SETTINGS, MUTE)
        except:
            pass
        
        c[PAUSE] = False
        try:
            c[PAUSE] = config_file.getboolean(PLAYER_SETTINGS, PAUSE)
        except:
            pass
            
        config[PLAYER_SETTINGS] = c
        
        c = {CURRENT_FOLDER: config_file.get(FILE_PLAYBACK, CURRENT_FOLDER)}
        if not os.path.isdir(c[CURRENT_FOLDER]):
            c[CURRENT_FOLDER] = ""
            c[CURRENT_FILE] = "" 
        
        c[CURRENT_FILE_PLAYLIST] = config_file.get(FILE_PLAYBACK, CURRENT_FILE_PLAYLIST)
        c[CURRENT_FILE] = config_file.get(FILE_PLAYBACK, CURRENT_FILE)
        c[CURRENT_TRACK_TIME] = config_file.get(FILE_PLAYBACK, CURRENT_TRACK_TIME)
        c[CURRENT_FILE_PLAYBACK_MODE] = config_file.get(FILE_PLAYBACK, CURRENT_FILE_PLAYBACK_MODE)
        config[FILE_PLAYBACK] = c
        config[PREVIOUS_STATIONS] = self.get_section(config_file, PREVIOUS_STATIONS)
        
        c = {BROWSER_BOOK_TITLE: config_file.get(KEY_AUDIOBOOKS, BROWSER_BOOK_TITLE)}
        c[BROWSER_BOOK_URL] = config_file.get(KEY_AUDIOBOOKS, BROWSER_BOOK_URL)
        c[BROWSER_TRACK_FILENAME] = config_file.get(KEY_AUDIOBOOKS, BROWSER_TRACK_FILENAME)
        c[BROWSER_BOOK_TIME] = config_file.get(KEY_AUDIOBOOKS, BROWSER_BOOK_TIME)        
        c[BROWSER_SITE] = config_file.get(KEY_AUDIOBOOKS, BROWSER_SITE)
        config[KEY_AUDIOBOOKS] = c

    def get_list(self, c, section_name, property_name):
        """ Return property which contains comma separated values
        
        :param section_name: section name in the configuration file (string enclosed between [])
        :param property_name: property name        
        :return: list of values defined as comma separated properties 
        """
        a = c.get(section_name, property_name).split(",")
        return list(map(str.strip, a))

    def get_section(self, config_file, section_name):
        """ Return property file section specified by name
        
        :param config_file: parsed configuration file
        :section_name: section name in the configuration file (string enclosed between [])        
        :return: dictionary with properties from specified section 
        """
        c = config_file[section_name]
        d = r = {}
        for i in c.items():
            k = i[0]
            try:
                d[k] = int(i[1])
            except:
                d[k] = 0
        return r

    def get_color_tuple(self, s):
        """ Convert string with comma separated colors into tuple with integer number for each color
        
        :param s: input string (e.g. "10, 20, 30" for RGB)        
        :return: tuple with colors (e.g. (10, 20, 30))
        """
        a = s.split(",")
        return tuple(int(e) for e in a)
    
    def save_current_settings(self):
        """ Save current configuration object (self.config) into current.txt file """ 
              
        config_parser = ConfigParser()
        config_parser.read_file(codecs.open(FILE_CURRENT, "r", "utf8"))
        
        a = self.save_section(CURRENT, config_parser)
        b = self.save_section(PLAYER_SETTINGS, config_parser)
        c = self.save_section(FILE_PLAYBACK, config_parser)
        d = self.save_section(KEY_SCREENSAVER, config_parser)
        e = self.save_section(PREVIOUS_STATIONS, config_parser)
        f = self.save_section(KEY_AUDIOBOOKS, config_parser)
            
        if a or b or c or d or e or f:
            with codecs.open(FILE_CURRENT, 'w', "utf8") as file:
                config_parser.write(file)
    
    def save_section(self, name, config_parser):
        """ Save configuration file section
        
        :param name: section name
        :param config_parser: configuration parser
        """
        content = None
        try:
            content = self.config[name]
        except KeyError:
            pass
        
        if not content: return None
        
        for t in content.items():
            config_parser.set(name, t[0], str(t[1]))
            
        return 1            
    
    def get_pygame_screen(self):
        """ Initialize Pygame screen and place it in config object
        
        :return: pygame display object which is used as drawing context
        """
        w = self.config[SCREEN_INFO][WIDTH]
        h = self.config[SCREEN_INFO][HEIGHT]
        d = self.config[SCREEN_INFO][DEPTH]
        
        if self.config[USAGE][USE_HEADLESS]:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            os.environ["DISPLAY"] = ":0"
            pygame.display.init()
            pygame.font.init()
            return pygame.display.set_mode((1,1), pygame.DOUBLEBUF, d)
        
        pygame.display.init()
        pygame.font.init()
            
        if self.config[LINUX_PLATFORM]:
            pygame.mouse.set_visible(False)
        else:            
            pygame.display.set_caption("Peppy")
        
        if self.config[SCREEN_INFO][HDMI]:
            if self.config[SCREEN_INFO][NO_FRAME]:
                return pygame.display.set_mode((w, h), pygame.NOFRAME)
            else:
                return pygame.display.set_mode((w, h))
        else:
            if self.config[SCREEN_INFO][NO_FRAME]:
                return pygame.display.set_mode((w, h), pygame.DOUBLEBUF | pygame.NOFRAME, d)
            else:
                return pygame.display.set_mode((w, h), pygame.DOUBLEBUF, d)

    def init_lcd(self):
        """ Initialize touch-screen """
        
        if not self.config[USAGE][USE_TOUCHSCREEN] or self.config[USAGE][USE_HEADLESS]:
            return   
        
        os.environ["SDL_FBDEV"] = "/dev/fb1"
        if self.config[USAGE][USE_MOUSE]:
            os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"
            os.environ["SDL_MOUSEDRV"] = "TSLIB"
