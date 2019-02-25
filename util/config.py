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

FOLDER_LANGUAGES = "languages"
FOLDER_RADIO_STATIONS = "radio-stations"
FILE_LABELS = "labels.properties"
FILE_VOICE_COMMANDS = "voice-commands.properties"
FILE_WEATHER_CONFIG = "weather-config.txt"
FILE_FLAG = "flag.png"

FILE_CONFIG = "config.txt"
FILE_CURRENT = "current.txt"
FILE_PLAYERS = "players.txt"
FILE_LANGUAGES = "languages.txt"

SCREEN_INFO = "screen.info"
WIDTH = "width"
HEIGHT = "height"
DEPTH = "depth"
FRAME_RATE = "frame.rate"
HDMI = "hdmi"
NO_FRAME = "no.frame"
FLIP_TOUCH_XY = "flip.touch.xy"

USAGE = "usage"
USE_TOUCHSCREEN = "use.touchscreen"
USE_MOUSE = "use.mouse"
USE_LIRC = "use.lirc"
USE_ROTARY_ENCODERS = "use.rotary.encoders"
USE_WEB = "use.web"
USE_STREAM_SERVER = "use.stream.server"
USE_BROWSER_STREAM_PLAYER = "use.browser.stream.player"
USE_VOICE_ASSISTANT = "use.voice.assistant"
USE_HEADLESS = "use.headless"
USE_VU_METER = "use.vu.meter"
USE_ALBUM_ART = "use.album.art"
USE_AUTO_PLAY = "use.auto.play"
USE_LONG_PRESS_TIME = "use.long.press.time.ms"

LOGGING = "logging"
FILE_LOGGING = "file.logging"
LOG_FILENAME = "log.filename"
CONSOLE_LOGGING = "console.logging"
ENABLE_STDOUT = 'enable.stdout'
SHOW_MOUSE_EVENTS = 'show.mouse.events'

FILE_BROWSER = "file.browser"
AUDIO_FILE_EXTENSIONS = "audio.file.extensions"
PLAYLIST_FILE_EXTENSIONS = "playlist.file.extensions"
FOLDER_IMAGES = "folder.images"
COVER_ART_FOLDERS = "cover.art.folders"
AUTO_PLAY_NEXT_TRACK = "auto.play.next.track"
CYCLIC_PLAYBACK = "cyclic.playback"
HIDE_FOLDER_NAME = "hide.folder.name"
FOLDER_IMAGE_SCALE_RATIO = "folder.image.scale.ratio"

WEB_SERVER = "web.server"
HTTP_PORT = "http.port"

STREAM_SERVER = "stream.server"
STREAM_SERVER_PORT = "stream.server.port"

PODCASTS_FOLDER = "podcasts.folder"
PODCASTS = "podcasts"
PODCAST_URL = "podcast.url"
PODCAST_EPISODE_NAME = "podcast.episode.name"
PODCAST_EPISODE_URL = "podcast.episode.url"
PODCAST_EPISODE_TIME = "podcast.episode.time"

HOME_MENU = "home.menu"
RADIO = "radio"
AUDIO_FILES = "audio-files"
AUDIOBOOKS = "audiobooks"
STREAM = "stream"
CD_PLAYER = "cd-player"
EQUALIZER = "equalizer"
TIMER = "timer"
SLEEP = "sleep"
SLEEP_TIME = "sleep.time"
WAKE_UP = "wake.up"
WAKE_UP_TIME = "wake.up.time"
POWEROFF = "poweroff"
SLEEP_NOW = "sleep-now"
LOADING = "loading"

VOICE_ASSISTANT = "voice.assistant"
VOICE_ASSISTANT_TYPE = "type"
VOICE_ASSISTANT_CREDENTIALS = "credentials"
VOICE_DEVICE_MODEL_ID = "device.model.id"
VOICE_DEVICE_ID = "device.id"

COLORS = "colors"
COLOR_WEB_BGR = "color.web.bgr" 
COLOR_DARK = "color.dark"
COLOR_DARK_LIGHT = "color.dark.light"
COLOR_MEDIUM = "color.medium"
COLOR_BRIGHT = "color.bright"
COLOR_CONTRAST = "color.contrast"
COLOR_LOGO = "color.logo"
COLOR_MUTE = "color.mute"

FONT_SECTION = "font"
FONT_KEY = "font.name"

SCRIPTS = "scripts"
STARTUP = "startup.script.name"
SHUTDOWN = "shutdown.script.name"

SCREENSAVER_MENU = "screensaver.menu"
CLOCK = "clock"
LOGO = "logo"
SLIDESHOW = "slideshow"
VUMETER = "peppymeter"
WEATHER = "peppyweather"
SPECTRUM = "spectrum"
LYRICS = "lyrics"
RANDOM = "random"

CURRENT = "current"
MODE = "mode"
LANGUAGE = "language"

PLAYER_SETTINGS = "player.settings"
VOLUME = "volume"
MUTE = "mute"
PAUSE = "pause"

FILE_PLAYBACK = "file.playback"
CURRENT_FILE_PLAYBACK_MODE = "file.playback.mode"
CURRENT_FOLDER = "folder"
CURRENT_FILE_PLAYLIST = "file.playlist"
CURRENT_FILE = "file"
CURRENT_TRACK_TIME = "track.time"

CD_PLAYBACK = "cd.playback"
CD_DRIVE_ID = "cd.drive.id"
CD_DRIVE_NAME = "cd.drive.name"
CD_TRACK = "cd.track"
CD_TRACK_TIME = "cd.track.time"

BROWSER_SITE = "site"
BROWSER_BOOK_TITLE = "book.title"
BROWSER_BOOK_URL = "book.url"
BROWSER_TRACK_FILENAME = "book.track.filename"
BROWSER_BOOK_TIME = "book.time"

SCREENSAVER = "screensaver"
NAME = "name"
DELAY = "delay"
KEY_SCREENSAVER_DELAY_1 = "delay.1"
KEY_SCREENSAVER_DELAY_3 = "delay.3"
KEY_SCREENSAVER_DELAY_OFF = "delay.off"

STATIONS = "stations"
CURRENT_STATIONS = "current.stations" 

AUDIO = "audio"
PLAYER_NAME = "player.name"
MUSIC_FOLDER = "music.folder"

SERVER_FOLDER = "server.folder"
SERVER_COMMAND = "server.command"
CLIENT_NAME = "client.name"
STREAM_CLIENT_PARAMETERS = "stream.client.parameters"
STREAM_SERVER_PARAMETERS = "stream.server.parameters"

HOST = "host"
PORT = "port"

MPD = "mpdsocket"
MPLAYER = "mplayer"
VLC = "vlcclient"

CURRENT_PLAYER_MODE = "current.player.mode"

class Config(object):
    """ Read configuration files and prepare dictionary """
    
    def __init__(self):
        """ Initializer """
        
        self.config = {}
        self.load_languages(self.config)
        self.load_config(self.config)
        self.load_players(self.config)
        self.load_current(self.config)
        self.init_lcd()
        self.config[PYGAME_SCREEN] = self.get_pygame_screen()
        
    def load_languages(self, config):
        """ Load all languages configurations
        
        :param config: configuration object
        """
        config_file = ConfigParser()
        config_file.optionxform = str
        try:
            path = os.path.join(os.getcwd(), FOLDER_LANGUAGES, FILE_LANGUAGES)
            config_file.read_file(codecs.open(path, "r", UTF8))
        except Exception as e:
            logging.error(e)
            os._exit(0)
            
        sections = config_file.sections()
        languages = []
        
        if sections:
            if len(sections) > 12:
                self.exit("Only 12 languages are supported.")
        else:
            self.exit("No sections found in file: " + FILE_LANGUAGES)
        
        for section in sections:
            language = {NAME: section}            
            translations = {}
            for (k, v) in config_file.items(section):
                translations[k] = v
            language[TRANSLATIONS] = translations
            languages.append(language)
        
            path = os.path.join(os.getcwd(), FOLDER_LANGUAGES, section)
            if os.path.isdir(path):
                files = [FILE_LABELS, FILE_VOICE_COMMANDS, FILE_WEATHER_CONFIG, FILE_FLAG]
                self.check_files(path, files)
                p = os.path.join(path, FOLDER_RADIO_STATIONS) 
                if not os.path.isdir(p):
                    language[RADIO_MODE_ENABLED] = False                    
                else:
                    station_folders = self.get_radio_stations_folders(p)
                    if station_folders:
                        language[KEY_STATIONS] = station_folders
                        language[RADIO_MODE_ENABLED] = True             
            else:
                self.exit("Folder was not found: " + path)
                
        config[KEY_LANGUAGES] = languages

    def get_radio_stations_folders(self, path):
        """ Get all radio station folders in specified folder
        
        :param path: path to search for station folders
        
        :return: list of folders
        """
        parent_folder = next(os.walk(path))[1]
        if parent_folder:
            p = os.path.join(path, parent_folder[0])
            child_folders = next(os.walk(p))[1]
            return {parent_folder[0]: sorted(child_folders)}
        return None

    def check_files(self, path, files):
        """ Check that specified files exist. Exit if doesn't exist
        
        :param files: list of files
        """
        msg = "File doesn't exist: " 
        for f in files:              
            p = os.path.join(path, f)
            if not os.path.exists(p):
                self.exit(msg + p)
        
    def exit(self, msg):
        """ Exit with provided message
        
        :param msg: message to output before exit
        """
        logging.error(msg)
        os._exit(0)
        
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
        c[FLIP_TOUCH_XY] = config_file.getboolean(SCREEN_INFO, FLIP_TOUCH_XY)
        config[SCREEN_INFO] = c        
        config[SCREEN_RECT] = pygame.Rect(0, 0, c[WIDTH], c[HEIGHT])

        config[AUDIO_FILE_EXTENSIONS] = self.get_list(config_file, FILE_BROWSER, AUDIO_FILE_EXTENSIONS)
        config[PLAYLIST_FILE_EXTENSIONS] = self.get_list(config_file, FILE_BROWSER, PLAYLIST_FILE_EXTENSIONS)
        config[FOLDER_IMAGES] = self.get_list(config_file, FILE_BROWSER, FOLDER_IMAGES)
        config[COVER_ART_FOLDERS] = self.get_list(config_file, FILE_BROWSER, COVER_ART_FOLDERS)
        config[AUTO_PLAY_NEXT_TRACK] = config_file.getboolean(FILE_BROWSER, AUTO_PLAY_NEXT_TRACK)
        config[CYCLIC_PLAYBACK] = config_file.getboolean(FILE_BROWSER, CYCLIC_PLAYBACK)
        config[HIDE_FOLDER_NAME] = config_file.getboolean(FILE_BROWSER, HIDE_FOLDER_NAME)
        config[FOLDER_IMAGE_SCALE_RATIO] = float(config_file.get(FILE_BROWSER, FOLDER_IMAGE_SCALE_RATIO))
        
        c = {USE_LIRC : config_file.getboolean(USAGE, USE_LIRC)}
        c[USE_TOUCHSCREEN] = config_file.getboolean(USAGE, USE_TOUCHSCREEN)
        c[USE_MOUSE] = config_file.getboolean(USAGE, USE_MOUSE)
        c[USE_ROTARY_ENCODERS] = config_file.getboolean(USAGE, USE_ROTARY_ENCODERS)
        c[USE_WEB] = config_file.getboolean(USAGE, USE_WEB)
        c[USE_STREAM_SERVER] = config_file.getboolean(USAGE, USE_STREAM_SERVER)
        c[USE_BROWSER_STREAM_PLAYER] = config_file.getboolean(USAGE, USE_BROWSER_STREAM_PLAYER)
        c[USE_VOICE_ASSISTANT] = config_file.getboolean(USAGE, USE_VOICE_ASSISTANT)
        c[USE_HEADLESS] = config_file.getboolean(USAGE, USE_HEADLESS)
        c[USE_VU_METER] = config_file.getboolean(USAGE, USE_VU_METER)
        c[USE_ALBUM_ART] = config_file.getboolean(USAGE, USE_ALBUM_ART)
        c[USE_AUTO_PLAY] = config_file.getboolean(USAGE, USE_AUTO_PLAY)
        c[USE_LONG_PRESS_TIME] = config_file.getint(USAGE, USE_LONG_PRESS_TIME)
        config[USAGE] = c
        
        if not config_file.getboolean(LOGGING, ENABLE_STDOUT):
            sys.stdout = os.devnull
            sys.stderr = os.devnull
        
        c[FILE_LOGGING] = config_file.getboolean(LOGGING, FILE_LOGGING)
        c[CONSOLE_LOGGING] = config_file.getboolean(LOGGING, CONSOLE_LOGGING)
        c[LOG_FILENAME] = config_file.get(LOGGING, LOG_FILENAME)
        config[FILE_LOGGING] = c[FILE_LOGGING]
        config[SHOW_MOUSE_EVENTS] = config_file.getboolean(LOGGING, SHOW_MOUSE_EVENTS)
        config[CONSOLE_LOGGING] = c[CONSOLE_LOGGING]
        
        log_handlers = []         
        if c[FILE_LOGGING]:
            log_handlers.append(logging.FileHandler(filename=c[LOG_FILENAME], mode='w'))
        if c[CONSOLE_LOGGING]:   
            log_handlers.append(logging.StreamHandler(sys.stdout))            
        if len(log_handlers) > 0:
            logging.basicConfig(
                level=logging.NOTSET, 
                format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
                handlers=log_handlers
            )
        else:
            logging.disable(logging.CRITICAL)
        
        c = {HTTP_PORT : config_file.get(WEB_SERVER, HTTP_PORT)}
        config[WEB_SERVER] = c
        
        c = {STREAM_SERVER_PORT : config_file.get(STREAM_SERVER, STREAM_SERVER_PORT)}
        config[STREAM_SERVER] = c
        
        config[PODCASTS_FOLDER] = config_file.get(PODCASTS, PODCASTS_FOLDER)

        c = {RADIO: config_file.getboolean(HOME_MENU, RADIO)}
        c[AUDIO_FILES] = config_file.getboolean(HOME_MENU, AUDIO_FILES)
        c[AUDIOBOOKS] = config_file.getboolean(HOME_MENU, AUDIOBOOKS)
        c[STREAM] = config_file.getboolean(HOME_MENU, STREAM)
        c[CD_PLAYER] = config_file.getboolean(HOME_MENU, CD_PLAYER)
        c[PODCASTS] = config_file.getboolean(HOME_MENU, PODCASTS)
        c[EQUALIZER] = config_file.getboolean(HOME_MENU, EQUALIZER)
        c[TIMER] = config_file.getboolean(HOME_MENU, TIMER)
        config[HOME_MENU] = c
        
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
        c[COLOR_MUTE] = self.get_color_tuple(config_file.get(COLORS, COLOR_MUTE))
        config[COLORS] = c
            
        config[FONT_KEY] = config_file.get(FONT_SECTION, FONT_KEY)

        c = {}
        c[STARTUP] = config_file.get(SCRIPTS, STARTUP)
        c[SHUTDOWN] = config_file.get(SCRIPTS, SHUTDOWN)
        config[SCRIPTS] = c
            
        c = {CLOCK: config_file.getboolean(SCREENSAVER_MENU, CLOCK)}
        c[LOGO] = config_file.getboolean(SCREENSAVER_MENU, LOGO)
        c[SLIDESHOW] = config_file.getboolean(SCREENSAVER_MENU, SLIDESHOW)
        c[VUMETER] = config_file.getboolean(SCREENSAVER_MENU, VUMETER)
        c[WEATHER] = config_file.getboolean(SCREENSAVER_MENU, WEATHER)
        c[SPECTRUM] = config_file.getboolean(SCREENSAVER_MENU, SPECTRUM)
        c[LYRICS] = config_file.getboolean(SCREENSAVER_MENU, LYRICS)
        c[RANDOM] = config_file.getboolean(SCREENSAVER_MENU, RANDOM)          
        config[SCREENSAVER_MENU] = c
        
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
        config_file.optionxform = str
        config_file.read_file(codecs.open(FILE_CURRENT, "r", UTF8))
        
        m = config_file.get(CURRENT, MODE)
        c = {MODE : m}
        
        initial_language = None
        lang = config_file.get(CURRENT, LANGUAGE)
        
        if not lang:
            initial_language = config[KEY_LANGUAGES][0]
            lang = initial_language[NAME]
        else:
            languages = config[KEY_LANGUAGES]
            language_name_found = False
            for language in languages:
                if language[NAME] == lang:
                    initial_language = language
                    language_name_found = True
                    break
            if not language_name_found:
                self.exit("Language is not supported: " + lang)
                            
        c[LANGUAGE] = lang        
        c[STREAM] = 0
        
        try:
            c[STREAM] = config_file.getint(CURRENT, STREAM)
        except:
            pass
        
        try:
            c[EQUALIZER] = self.get_equalizer(config_file.get(CURRENT, EQUALIZER))
        except:
            pass
        
        config[CURRENT] = c
        
        s = config_file.get(SCREENSAVER, NAME)
        if not s: s = "slideshow"
        c = {NAME: s}
        d = config_file.get(SCREENSAVER, DELAY)
        if not d: d = "delay.1"
        c[DELAY] = d
        config[SCREENSAVER] = c
        
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
        
        c = {CD_DRIVE_ID: config_file.get(CD_PLAYBACK, CD_DRIVE_ID)}
        c[CD_DRIVE_NAME] = config_file.get(CD_PLAYBACK, CD_DRIVE_NAME)
        c[CD_TRACK] = config_file.get(CD_PLAYBACK, CD_TRACK)
        c[CD_TRACK_TIME] = config_file.get(CD_PLAYBACK, CD_TRACK_TIME)
        config[CD_PLAYBACK] = c
        
        c = {PODCAST_URL: config_file.get(PODCASTS, PODCAST_URL)}
        c[PODCAST_EPISODE_NAME] = config_file.get(PODCASTS, PODCAST_EPISODE_NAME)
        c[PODCAST_EPISODE_URL] = config_file.get(PODCASTS, PODCAST_EPISODE_URL)
        c[PODCAST_EPISODE_TIME] = config_file.get(PODCASTS, PODCAST_EPISODE_TIME)
        config[PODCASTS] = c

        for language in config[KEY_LANGUAGES]:
            n = language[NAME]
            k = STATIONS + "." + n
            try:
                config[k] = self.get_section(config_file, k)
            except:
                config[k] = {}
        
        c = {BROWSER_BOOK_TITLE: config_file.get(AUDIOBOOKS, BROWSER_BOOK_TITLE)}
        c[BROWSER_BOOK_URL] = config_file.get(AUDIOBOOKS, BROWSER_BOOK_URL)
        c[BROWSER_TRACK_FILENAME] = config_file.get(AUDIOBOOKS, BROWSER_TRACK_FILENAME)
        c[BROWSER_BOOK_TIME] = config_file.get(AUDIOBOOKS, BROWSER_BOOK_TIME)        
        c[BROWSER_SITE] = config_file.get(AUDIOBOOKS, BROWSER_SITE)
        config[AUDIOBOOKS] = c
        
        c = {SLEEP_TIME: config_file.get(TIMER, SLEEP_TIME)}
        c[WAKE_UP_TIME] = config_file.get(TIMER, WAKE_UP_TIME)
        try:
            c[SLEEP] = config_file.getboolean(TIMER, SLEEP)
        except:
            c[SLEEP] = False
        try:
            c[WAKE_UP] = config_file.getboolean(TIMER, WAKE_UP)
        except:
            c[WAKE_UP] = False
        try:
            c[POWEROFF] = config_file.getboolean(TIMER, POWEROFF)
        except:
            c[POWEROFF] = False                   
        config[TIMER] = c

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
            if k == CURRENT_STATIONS:
                try:                
                    d[k] = i[1]
                except:
                    d[k] = ""
            else:
                try:
                    d[k] = int(i[1])
                except:
                    d[k] = 0
        return r

    def get_color_tuple(self, s):
        """ Convert string with comma separated colors into tuple with integer number for each color
        
        :param s: input string (e.g. "10,20,30" for RGB)        
        :return: tuple with colors (e.g. (10,20,30))
        """
        a = s.split(",")
        return tuple(int(e) for e in a)
    
    def get_equalizer(self, s):
        """ Convert string with comma separated colors into tuple with integer number for each color
        
        :param s: input string        
        :return: frequency list
        """
        a = s[1 : -1].split(",")
        return list(int(e) for e in a)
    
    def save_current_settings(self):
        """ Save current configuration object (self.config) into current.txt file """ 
              
        config_parser = ConfigParser()
        config_parser.optionxform = str
        config_parser.read_file(codecs.open(FILE_CURRENT, "r", UTF8))
        
        a = b = c = d = e = f = g = h = stations_changed = None
        
        if self.config[USAGE][USE_AUTO_PLAY]:        
            a = self.save_section(CURRENT, config_parser)
            c = self.save_section(FILE_PLAYBACK, config_parser)
            d = self.save_section(CD_PLAYBACK, config_parser)
            keys = self.config.keys()
            s = STATIONS + "."
            stations_changed = False
            for key in keys:
                if key.startswith(s):
                    z = self.save_section(key, config_parser)
                    if z: stations_changed = True
            
            f = self.save_section(AUDIOBOOKS, config_parser)
            h = self.save_section(PODCASTS, config_parser)

        b = self.save_section(PLAYER_SETTINGS, config_parser)
        e = self.save_section(SCREENSAVER, config_parser)
        g = self.save_section(TIMER, config_parser)
        
        if a or b or c or d or e or f or g or h or stations_changed:
            with codecs.open(FILE_CURRENT, 'w', UTF8) as file:
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
        
        sections = config_parser.sections()
        if name not in sections:
            config_parser.add_section(name)
        
        for t in content.items():
            config_parser.set(name, t[0], str(t[1]))
            
        return 1            
    
    def get_pygame_screen(self):
        """ Initialize Pygame screen
        
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
        
        if not self.config[USAGE][USE_TOUCHSCREEN] or self.config[USAGE][USE_HEADLESS] or not self.config[LINUX_PLATFORM]:
            return   
        
        if os.path.exists("/dev/fb1"):
            os.environ["SDL_FBDEV"] = "/dev/fb1"
        elif os.path.exists("/dev/fb0"):
            os.environ["SDL_FBDEV"] = "/dev/fb0"
            
        if self.config[USAGE][USE_MOUSE]:
            if os.path.exists("/dev/input/touchscreen"):
                os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"
            else:
                os.environ["SDL_MOUSEDEV"] = "/dev/input/event0"
            os.environ["SDL_MOUSEDRV"] = "TSLIB"
