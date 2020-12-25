# Copyright 2016-2020 Peppy Player peppy.player@gmail.com
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
import ssl
import codecs
import importlib
import logging
import base64
import hashlib
import pygame
import collections
import urllib

from subprocess import Popen, PIPE
from zipfile import ZipFile
from ui.state import State
from util.config import Config, USAGE, USE_VOICE_ASSISTANT, COLORS, COLOR_DARK, FONT_KEY, CURRENT, FILE_LABELS, \
    LANGUAGE, FILE_PLAYBACK, NAME, KEY_SCREENSAVER_DELAY_1, KEY_SCREENSAVER_DELAY_3, KEY_SCREENSAVER_DELAY_OFF, \
    FOLDER_LANGUAGES, FILE_FLAG, FOLDER_RADIO_STATIONS, FILE_VOICE_COMMANDS, SCREENSAVER_MENU, USE_WEB, \
    FILE_WEATHER_CONFIG, EQUALIZER, SCRIPTS, FILE_BROWSER, HIDE_FOLDER_NAME, COLLECTION, DATABASE_FILE, \
    CURRENT_FOLDER, CURRENT_FILE, COLLECTION_PLAYBACK, MODE, AUDIO_FILES, COLLECTION_FOLDER, \
    COLLECTION_FILE, FOLDER_IMAGES, BACKGROUND, BGR_TYPE, BGR_TYPE_IMAGE, SCREEN_BGR_COLOR, GENERATED_IMAGE
from util.keys import *
from util.fileutil import FileUtil, FOLDER, FOLDER_WITH_ICON, FILE_AUDIO, FILE_PLAYLIST, FILE_IMAGE
from urllib import request
from websiteparser.loyalbooks.constants import BASE_URL, LANGUAGE_PREFIX, ENGLISH_USA, RUSSIAN
from screensaver.peppyweather.weatherconfigparser import WeatherConfigParser
from util.discogsutil import DiscogsUtil
from util.collector import DbUtil, INFO, METADATA, MP4_METADATA
from util.bluetoothutil import BluetoothUtil
from util.imageutil import ImageUtil, EXT_MP4, EXT_M4A
from mutagen import File

IMAGE_VOLUME = "volume"
IMAGE_MUTE = "volume-mute"
IMAGE_SHADOW = "shadow"
IMAGE_SELECTION = "selection"
IMAGE_SELECTED_SUFFIX = "-on"
IMAGE_DISABLED_SUFFIX = "-off"
IMAGE_MUTE_SUFFIX = "-mute"
IMAGE_ABOUT = "about"
IMAGE_LANGUAGE = "language"
IMAGE_RADIO = "radio"
IMAGE_STREAM = "stream"
IMAGE_AUDIOBOOKS = "audiobooks"
IMAGE_SCREENSAVER = "screensaver"
IMAGE_PLAYER = "player"
IMAGE_TIME_KNOB = "time-knob"
IMAGE_BACK = "back"
IMAGE_ABC = "abc"
IMAGE_NEW_BOOKS = "new-books"
IMAGE_BOOK_GENRE = "book-genre"
IMAGE_STAR = "star"

PLAYER_RUNNING = "running"
PLAYER_SLEEPING = "sleeping"

FILE_STATIONS = "stations.m3u"
FILE_STREAMS = "streams.m3u"
FILE_FOLDER = "folder.png"
FILE_FOLDER_ON = "folder-on.png"
FILE_DEFAULT_STATION = "default-station.png"
FILE_DEFAULT_STREAM = "default-stream.png"

EXT_PROPERTIES = ".properties"
EXT_PNG = ".png"
EXT_JPG = ".jpg"
EXT_M3U = ".m3u"

FOLDER_ICONS = "icons"
FOLDER_SLIDES = "slides"
FOLDER_STATIONS = "stations"
FOLDER_STREAMS = "streams"
FOLDER_HOME = "home"
FOLDER_GENRES = "genres"
FOLDER_FONT = "font"
FOLDER_PLAYLIST = "playlist"

PACKAGE_SCREENSAVER = "screensaver"    
FOLDER_SAVER = "saver"
FOLDER_SAVER_TYPE = "type"
FOLDER_SAVER_DELAY = "delay"
PROPERTY_SEPARATOR = "="
PROPERTY_COMMENT_CHAR = "#"
CURRENT_PLAYLIST = "current playlist"
CURRENT_INDEX = "current index"
INDEX = "index"
KEY_GENRE = "genre"
UTF_8 = "utf-8-sig"
FOLDER_BUNDLES = "bundles"
FOLDER_VOICE_ASSISTANT = "voiceassistant"
NUMBERS = {
           "VA_ONE" : 1,
           "VA_TWO" : 2,
           "VA_THREE" : 3,
           "VA_FOUR" : 4,
           "VA_FIVE" : 5,
           "VA_SIX" : 6,
           "VA_SEVEN" : 7,
           "VA_EIGHT" : 8,
           "VA_NINE" : 9,
           "VA_ZERO" : 0}

class Util(object):
    """ Utility class """
    
    def __init__(self, connected_to_internet):
        """ Initializer. Prepares Config object.
        
        :param connected_to_internet: True - connected to the Interner, False - disconnected
        """
        self.connected_to_internet = connected_to_internet
        self.font_cache = {}
        self.voice_commands_cache = {}
        self.cd_titles = {}
        self.cd_track_names_cache = {}
        self.screensaver_cache = {}
        self.config_class = Config()
        self.config = self.config_class.config
        self.screen_rect = self.config_class.screen_rect
        self.config[LABELS] = self.get_labels()
        self.weather_config = self.get_weather_config()
        self.pygame_screen = self.config_class.pygame_screen
        self.CURRENT_WORKING_DIRECTORY = os.getcwd()
        self.read_storage()
        self.discogs_util = DiscogsUtil(self.k1)
        self.image_util = ImageUtil(self)
        self.file_util = FileUtil(self)
                
        if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)): 
            ssl._create_default_https_context = ssl._create_unverified_context
        self.podcasts_util = None
        self.db_util = None
        self.bluetooth_util = None
    
    def get_labels(self):
        """ Read labels for current language
        
        :return: labels dictionary
        """
        return self.get_labels_by_language(self.config[CURRENT][LANGUAGE])

    def get_labels_by_language(self, language):
        """ Read labels for the provided language

        :param language: provided language

        :return: labels
        """
        path = os.path.join(os.getcwd(), FOLDER_LANGUAGES, language, FILE_LABELS)
        return self.get_properties(path)
    
    def get_voice_commands(self):
        """ Return voice commands for current language """
        
        lang = self.get_current_language()
        
        try:
            return self.voice_commands_cache[lang[NAME]]
        except:
            pass
        
        path = os.path.join(os.getcwd(), FOLDER_LANGUAGES, lang[NAME], FILE_VOICE_COMMANDS)
        voice_commands = self.load_properties(path, UTF_8)
        voice_commands.update(NUMBERS)
        
        self.voice_commands_cache[lang[NAME]] = voice_commands
        
        return voice_commands
    
    def get_weather_config(self):
        """ Read weather config for the current language
        
        :return: weather config
        """
        current_language = self.config[CURRENT][LANGUAGE] 
        path = os.path.join(os.getcwd(), FOLDER_LANGUAGES, current_language)
        parser = WeatherConfigParser(path)
        return parser.weather_config
    
    def get_properties(self, folder):
        """ Read properties file from specified folder
        
        :param folder: folder name
        :return: labels dictionary
        """        
        labels = self.load_properties(folder, UTF_8)
        return labels
    
    def get_voice_assistant_language_code(self, language):
        """ Return the language code required by voice assistant
        
        :param language: current language
        :return: language code
        """
        code = None
        if language == "English-USA":
            code = "en-US"
        elif language == "German":
            code = "de-DE"
        elif language == "French":
            code = "fr-FR"
        elif language == "Italian":
            code = "it-IT"
        elif language == "Japanese":
            code = "ja-JP"
        elif language == "Korean":
            code = "ko-KR"
        elif language == "Spanish":
            code = "es-ES"
        elif language == "Portuguese":
            code = "pt-BR"
        return code
    
    def get_file_metadata(self):
        """ Return current file metadata. 
            Valid only for modes: audio files and collection

        :return: dictionary with metadata
        """
        meta = {}
        mode = self.config[CURRENT][MODE]

        if mode == AUDIO_FILES:
            folder = self.config[FILE_PLAYBACK][CURRENT_FOLDER]
            filename = self.config[FILE_PLAYBACK][CURRENT_FILE]            
        elif mode == COLLECTION:
            folder = self.config[COLLECTION_PLAYBACK][COLLECTION_FOLDER]
            filename = self.config[COLLECTION_PLAYBACK][COLLECTION_FILE]
        else:
            return meta

        path = os.path.join(folder, filename)
        if not path:
            return meta

        meta["filename"] = filename
        try:
            filesize = os.stat(path).st_size
            meta["filesize"] = filesize
            m = File(path)
            for i in INFO:
                meta[i] = getattr(m.info, i, None)

            if filename.lower().endswith(EXT_MP4) or filename.lower().endswith(EXT_M4A):
                metadata = MP4_METADATA
            else:
                metadata = METADATA

            for i, key in enumerate(metadata):
                if key not in m.keys() or len(m[key][0].replace(" ", "").strip()) == 0:
                    v = None
                else:
                    v = m[key][0].strip()
                meta[METADATA[i]] = v
        except Exception as e:
            logging.debug(e)

        return meta

    def get_font(self, size):
        """ Return font from cache if not in cache load, place in cache and return.
        
        :param size: font size 
        """
        if os.getcwd() != self.CURRENT_WORKING_DIRECTORY:
            os.chdir(self.CURRENT_WORKING_DIRECTORY)
        
        current_language = self.config[CURRENT][LANGUAGE]
        path = os.path.join(os.getcwd(), FOLDER_LANGUAGES, current_language)
        language_specific_font = None
        for file in os.listdir(path):
            if file.lower().endswith(".ttf"):
                language_specific_font = file
                break
        
        if language_specific_font:
            key = language_specific_font + str(size)
            filename = os.path.join(path, language_specific_font)
        else:
            font_name = self.config[FONT_KEY]
            key = font_name + str(size)
            filename = os.path.join(FOLDER_FONT, font_name)
            
        if key in self.font_cache:
            return self.font_cache[key]
        
        font = pygame.font.Font(filename, size)
        self.font_cache[key] = font
        return font
        
    def load_radio_playlist(self, language, genre, top_folder):
        """ Load radio playlist

        :param language: laguage for playlist
        :param genre: genre playlist
        :param top_folder: top folder under language
        :return: playlist as a string
        """
        folder = os.path.join(os.getcwd(), FOLDER_LANGUAGES, language, FOLDER_RADIO_STATIONS, top_folder, genre)
        path = os.path.join(folder, FILE_STATIONS)
        playlist =""

        for encoding in ["utf8", "utf-8-sig", "utf-16"]:
            try:
                playlist = codecs.open(path, "r", encoding).read()
                break
            except Exception as e:
                logging.error(e)

        return playlist

    def save_radio_playlist(self, language, genre, playlist):
        """ Save radio playlist

        :param language: laguage for playlist
        :param genre: genre playlist
        :param playlist: playlist as a string to save
        """
        languages = self.config[KEY_LANGUAGES]
        top_folder = ""
        for lang in languages:
            if language == lang[NAME]:
                stations = lang[KEY_STATIONS]
                top_folder = list(stations.keys())[0]

        path = os.path.join(os.getcwd(), FOLDER_LANGUAGES, language, FOLDER_RADIO_STATIONS, top_folder, genre,
            FILE_STATIONS)
        with codecs.open(path, 'w', UTF8) as file:
            file.write(playlist)

    def get_stations_playlist(self, language, genre, stations_per_page):
        """ Load stations for specified language and genre
        
        :param language: the language
        :param genre: the genre
        :param stations_per_page: stations per page used to assign indexes 
               
        :return: list of button state objects. State contains station icons, index, genre, name etc.
        """
        top_folder = self.get_stations_top_folder()
        folder = os.path.join(os.getcwd(), FOLDER_LANGUAGES, language, FOLDER_RADIO_STATIONS, top_folder, genre)
        path = os.path.join(folder, FILE_STATIONS)
        default_icon_path = os.path.join(os.getcwd(), FOLDER_ICONS, FILE_DEFAULT_STATION)
        return self.load_m3u(path, folder, genre, stations_per_page, default_icon_path)
            
    def load_streams(self, streams_per_page):
        """ Load streams
        
        :param streams_per_page: streams per page used to assign indexes 
               
        :return: list of button state objects. State contains icons, index, name etc.
        """
        streams = []
        path = os.path.join(os.getcwd(), FOLDER_STREAMS, FILE_STREAMS)
        default_icon_path = os.path.join(os.getcwd(), FOLDER_ICONS, FILE_DEFAULT_STREAM)
        
        return self.load_m3u(path, FOLDER_STREAMS, "", streams_per_page, default_icon_path)

    def get_streams_string(self):
        """ Read file

        :return: string
        """
        path = os.path.join(os.getcwd(), FOLDER_STREAMS, FILE_STREAMS)

        for encoding in ["utf8", "utf-8-sig", "utf-16"]:
            try:
                with codecs.open(path, 'r', encoding) as file:
                    return file.read()
            except Exception as e:
                logging.error(e)

    def save_streams(self, streams):
        """ Save podcasts file

        :param streams: file with podcasts links
        """
        path = os.path.join(os.getcwd(), FOLDER_STREAMS, FILE_STREAMS)
        with codecs.open(path, 'w', UTF8) as file:
            file.write(streams)

    def load_m3u(self, path, folder, top_folder, items_per_page, default_icon_path):
        """ Load m3u playlist
        
        :param path: base path
        :param folder: main folder
        :param top_folder: top folder
        :param items_per_page: items per page
        :param default_icon_path: path to the default icon
        
        :return: list of State objects representing playlist
        """
        items = []
        lines = []
        item_name = None
        index = 0
        
        for encoding in ["utf8", "utf-8-sig", "utf-16"]:
            try:
                lines = codecs.open(path, "r", encoding).read().split("\n")
                break
            except Exception as e:
                logging.error(e)           
        
        for line in lines:
            if len(line.rstrip()) == 0: 
                continue
            
            if line.startswith("#") and not item_name:
                item_name = line[1:].rstrip()
                continue
            
            name = item_name.rstrip()
            path = os.path.join(folder, name + EXT_PNG)
            icon = self.image_util.load_image(path)

            if not icon:
                path = os.path.join(folder, name + EXT_JPG)
                icon = self.image_util.load_image(path)
            
            if not icon:
                icon = self.image_util.load_image(default_icon_path)
            
            state = State()
            state.index = index
            state.genre = top_folder
            state.url = line.rstrip()
            state.name = str(index)
            state.l_name = name
            state.icon_base = icon
            state.comparator_item = NAME
            state.index_in_page = index % items_per_page
            items.append(state)
            index += 1
            item_name = None  
             
        return items
        
    def load_properties(self, path, encoding=None):
        """ Load properties file
        
        :param path: file path
        :param encoding: file encoding  
              
        :return: dictionary with properties
        """
        properties = {}
        file = codecs.open(path, "r", encoding)
        for line in file:
            l = line.rstrip()
            if l and not l.startswith(PROPERTY_COMMENT_CHAR):
                pair = l.split(PROPERTY_SEPARATOR)
                properties[pair[0].strip()] = pair[1].strip()
        return properties
    
    def get_current_language(self):
        """ Get current language parameters
        
        :return: dictionary with current language parameters
        """
        current_language = self.config[CURRENT][LANGUAGE]
        languages = self.config[KEY_LANGUAGES]
        for language in languages:
            if current_language == language[NAME]:
                return language
        return None
    
    def is_radio_enabled(self):
        """ Check that radio mode enabled for current language
        
        :return: True - enabled, False - disabled
        """
        lang = self.get_current_language()
        if lang:
            return lang[RADIO_MODE_ENABLED]
        else:
            return False
    
    def is_audiobooks_enabled(self):
        """ Check that audiobooks mode enabled for current language
        
        :return: True - enabled, False - disabled
        """
        lang = self.get_current_language()
        name = lang[NAME]
        if name == ENGLISH_USA or name == RUSSIAN:
            return True
        
        url = BASE_URL + LANGUAGE_PREFIX + name
        req = request.Request(url)
        try:
            request.urlopen(req)
        except:
            return False

        return True
    
    def get_va_language_commands(self):
        """ Get voice assistant commands for current language
        
        :return: va commands
        """
        current_language = self.get_current_language()
        translations = current_language[TRANSLATIONS]
        va_commands = {}
        for (k, v) in translations.items():
            if "-" in v:
                v = v[:v.find("-")]
            va_commands[k] = v
        return va_commands
    
    def load_languages_menu(self, button_bounding_box):
        """ Load languages menu items
        
        :param button_bounding_box: menu button bounding box
        
        :return: dictionary with menu items
        """
        items = {}
        i = 0
        current_language = self.get_current_language()
        labels = current_language[TRANSLATIONS]
        va_commands = self.get_va_language_commands()
            
        for language in self.config[KEY_LANGUAGES]:
            name = language[NAME]            
            state = State()
            state.name = name
            state.l_name = labels[name]

            path = os.path.join(os.getcwd(), FOLDER_LANGUAGES, name, FILE_FLAG)
            img = self.image_util.prepare_flag_image(path, button_bounding_box)
            state.icon_base = (path, img)
            
            state.bgr = self.config[COLORS][COLOR_DARK]
            state.img_x = None
            state.img_y = None
            state.auto_update = True
            state.show_bgr = True
            state.show_img = True
            state.show_label = True
            state.comparator_item = state.name
            state.index = i
            state.voice_commands = va_commands[name]
            state.v_align = V_ALIGN_TOP
            
            items[state.name] = state
            i += 1            
        return items
    
    def get_stations_top_folder(self):
        """ Get radio stations top folder
        
        :return: top folder name
        """
        language = self.get_current_language()
        stations = language[KEY_STATIONS]
        return list(stations.keys())[0]

    def get_stations_folders(self):
        """ Get radio stations folders
        
        :return: list of folders
        """
        top_folders = None
        language = self.get_current_language()
        try:
            stations = language[KEY_STATIONS]
            top_folder = list(stations.keys())[0]
            top_folders = stations[top_folder]
        except:
            pass
        return top_folders
    
    def get_radio_group_slice(self, group, start, end):
        """ Create radio group slice
        
        :param group: the whole group
        :param start: start index
        :param end: end index
        
        :return: slice list
        """
        keys = list(group.keys())
        key_slice = keys[start : end]
        group_slice = collections.OrderedDict()
        for k in key_slice:
            group_slice[k] = group[k]
            
        return group_slice
    
    def load_stations_folders(self, button_bounding_box):
        """ Load languages menu items
        
        :param button_bounding_box: bounding box
        
        :return: dictionary with menu items
        """
        items = collections.OrderedDict()
        i = 0
        current_language = self.config[CURRENT][LANGUAGE]
        folders = self.get_stations_folders()
        top_folder = self.get_stations_top_folder()
            
        for folder in folders:
            name = folder
            path = os.path.join(os.getcwd(), FOLDER_LANGUAGES, current_language, FOLDER_RADIO_STATIONS, top_folder, folder, FILE_FOLDER)
            folder_image = self.image_util.load_image(path)
            path_on = os.path.join(os.getcwd(), FOLDER_LANGUAGES, current_language, FOLDER_RADIO_STATIONS, top_folder, folder, FILE_FOLDER_ON)
            folder_image_on = self.image_util.load_image(path_on)
            
            state = State()
            state.name = state.l_name = state.genre = name

            if folder_image:
                scale_ratio = self.image_util.get_scale_ratio((button_bounding_box.w, button_bounding_box.h), folder_image[1])
                scaled_image = self.image_util.scale_image(folder_image, scale_ratio)
                state.icon_base = (path, scaled_image)
                if folder_image_on:
                    scaled_image_on = self.image_util.scale_image(folder_image_on, scale_ratio)
                    state.icon_selected = (path_on, scaled_image_on)
            
            state.bgr = self.config[COLORS][COLOR_DARK]
            state.img_x = None
            state.img_y = None
            state.auto_update = True
            state.show_bgr = True
            state.show_img = True
            state.show_label = True
            state.comparator_item = state.name
            state.index = i
            state.v_align = V_ALIGN_TOP
            state.v_offset = 35
            state.voice_commands = name
            items[state.name] = state
            i += 1            
        return items
        
    def load_menu(self, names, comparator, disabled_items=None, v_align=None, bb=None, scale=1, suffix=None):
        """ Load menu items
        
        :param names: list of menu item names (should have corresponding filename)
        :param comparator: string used to sort items
        :param disabled_items: list of items which should be disabled
        :param v_align: vertical alignment
        :param bb: bounding box
        :param scale: image scale factor
        :param suffix: label suffix
                
        :return: dictionary with menu items
        """
        items = {}
            
        for i, name in enumerate(names):
            icon = self.image_util.load_icon_main(name, bb, scale)
            icon_on = self.image_util.load_icon_on(name, bb, scale)
            
            if disabled_items and name in disabled_items:
                icon_off = self.image_util.load_icon_off(name, bb, scale)
            else:
                icon_off = None
            
            state = State()
            state.name = name
            state.genre = name
            try: 
                state.l_genre = self.config[LABELS][name]
                state.l_name = self.config[LABELS][name]
                if suffix:
                    state.l_name += " (" + str(suffix[i]) + ")"    
            except:
                state.l_genre = name
                state.l_name = name
            state.icon_base = icon
            if icon_on:
                state.icon_selected = icon_on
            else:
                state.icon_selected = icon
                
            if not icon_off:
                state.icon_disabled = icon_on
            else:
                state.icon_disabled = icon_off
                
            state.bgr = self.config[COLORS][COLOR_DARK]
            state.img_x = None
            state.img_y = None
            state.auto_update = True
            state.show_bgr = True
            state.show_img = True
            state.show_label = True
            state.v_align = v_align
            if comparator == NAME:
                state.comparator_item = state.name
            elif comparator == GENRE:
                state.comparator_item = state.genre
            if disabled_items and name in disabled_items:
                state.enabled = False
            state.index = i
            items[state.name] = state
        return items
        
    def get_screensaver_delays(self):
        """ Get screensaver delay button states
        
        :return: dictionary with button states
        """
        names = [KEY_SCREENSAVER_DELAY_1, KEY_SCREENSAVER_DELAY_3, KEY_SCREENSAVER_DELAY_OFF]
        delays = {}
        index = 0
        for n in names:            
            state = State()
            state.name = n
            state.index = index
            state.l_name = self.config[LABELS][n]
            state.comparator_item = index
            state.bgr = self.config[COLORS][COLOR_DARK]
            delays[state.name] = state
            index += 1             
        return delays
        
    def load_screensaver(self, name):
        """ Load screensaver plug-in module and create object
        
        :param name: plug-in name        
        :return: screensaver object
        """
        try:
            s = self.screensaver_cache[name]
            return s
        except KeyError:
            pass
        
        p = PACKAGE_SCREENSAVER + ('.' + name.lower())*2
        try:
            m = importlib.import_module(p)
        except Exception as e:
            logging.debug(e)
        s = getattr(m, name.title())(self)
        self.screensaver_cache[name] = s
        return s

    def run_script(self, script_name):
        """ Load and run script

        :param script_name: script name
        """
        n = script_name[0:script_name.find(".py")]
        m = importlib.import_module(SCRIPTS + "." + n)
        s = getattr(m, n.title())()

        if s.type == "sync":
            s.start()
        else:
            s.start_thread()

    def load_folder_content(self, folder_name, rows, cols, icon_box, icon_box_without_label):
        """ Prepare list of state objects representing folder content
        
        :param folder_name: folder name 
        :param rows: number of rows in file browser  
        :param cols: number of columns in file browser       
        :param icon_box: icon bounding box
        :param icon_box_without_label: icon bounding box without label
        
        :return: list of state objects representing folder content
        """
        content = self.file_util.get_folder_content(folder_name)
        if not content:
            return None
        
        items = []
        items_per_page = cols * rows

        for index, s in enumerate(content):
            s.index = index
            s.name = s.file_name
            s.l_name = s.name
            has_embedded_image = getattr(s, "has_embedded_image", False)
            if (s.file_type == FOLDER_WITH_ICON or s.file_type == FILE_IMAGE or has_embedded_image) and self.config[HIDE_FOLDER_NAME]:
                s.show_label = False
                w = icon_box_without_label.w
                h = icon_box_without_label.h
            else:
                s.show_label = True
                w = icon_box.w
                h = icon_box.h
            s.icon_base = self.image_util.get_file_icon(s.file_type, getattr(s, "file_image_path", ""), (w, h), url=s.url, show_label=s.show_label)
            s.comparator_item = index
            s.bgr = self.config[COLORS][COLOR_DARK]
            s.show_bgr = True
            s.index_in_page = index % items_per_page
            items.append(s)
        return items

    def load_playlist(self, state, playlist_provider, rows, columns):
        """ Handle playlist
        
        :param state: state object defining playlist
        :param playlist_provider: provider
        :param rows: menu rows 
        :param columns: menu columns
        
        :return: playlist 
        """               
        n = getattr(state, "file_name", None)
        if n == None:
            state.file_name = self.config[FILE_PLAYBACK][FILE_AUDIO]
            
        p = playlist_provider(state)
        
        if not p:
            return

        play_list = []
        
        for i, n in enumerate(p):
            s = State()
            s.index = i
            s.playlist_track_number = i
            s.file_name = n
            s.file_type = FILE_AUDIO
            s.url = state.folder + os.sep + n
            s.playback_mode = FILE_PLAYLIST
            play_list.append(s)
         
        return self.load_playlist_content(play_list, rows, columns)               

    def load_playlist_content(self, playlist, rows, cols):
        """ Prepare list of state objects representing playlist content
        
        :param playlist: list of items in playlist 
        :param rows: number of rows in file browser  
        :param cols: number of columns in file browser 
              
        :return: list of state objects representing playlist
        """
        items = []
        items_per_page = cols * rows

        for index, s in enumerate(playlist):
            s.index = index
            if os.sep in s.file_name:
                s.name = s.l_name = s.file_name[s.file_name.rfind(os.sep) + 1 : ]
            else:
                s.name = s.l_name = s.file_name
            s.icon_base = self.image_util.get_file_icon(FILE_AUDIO)
            s.comparator_item = index
            s.bgr = self.config[COLORS][COLOR_DARK]
            s.show_bgr = True
            s.index_in_page = index % items_per_page
            items.append(s)    
        return items

    def get_audio_files_in_folder(self, folder_name, store_folder_name=True, load_images=True):
        """ Return the list of audio files in specified folder
        
        :param folder_name: folder name
        :param store_folder_name: remember folder name 
            
        :return: list of audio files
        """
        files = self.file_util.get_folder_content(folder_name, store_folder_name, load_images)
        if not files:
            return None
                
        files[:] = (f for f in files if f.file_type == FILE_AUDIO)
        
        for n, f in enumerate(files):
            f.index = n
    
        return files

    def get_folder_image_path(self, folder):
        """ Return the path to image representing folder 
        
        :param folder_name: folder name
        :return: path to image file
        """
        if not folder: return None
        
        if not os.path.isdir(folder):
            self.config[FILE_PLAYBACK][CURRENT_FOLDER] = ""
            self.config[FILE_PLAYBACK][CURRENT_FILE] = "" 
            return None
        
        for f in os.listdir(folder):
            if f.lower() in self.config[FOLDER_IMAGES]:
                file_path = os.path.join(folder, f)
                real_path = os.path.realpath(file_path)
                return real_path
        return None

    def get_dictionary_value(self, d, key, df=None):
        """ Return value retrieved from provided dictionary by provided key
        
        :param d: dictionary
        :param key: key
        :param df: default value
        """
        if not d or not key: return None
        
        try:
            return d[key]
        except:
            return df 

    def get_hash(self, s):
        """ Return string's hash
        
        :param s: input string
        
        :return: hash of the input string
        """
        m = hashlib.sha1()
        m.update(s)
        return m.hexdigest() 
         
    def is_screensaver_available(self):
        """ Check that at least one screensaver available
        
        :return: True - available, False - unavailable
        """
        s = self.config[SCREENSAVER_MENU]
        n = 0
        
        for v in s.values():
            if v == True:
                n = 1
                break
            
        if n > 0:
            return True
        else:
            return False
        
    def encode_url(self, url):
        """ Encode URL using ascii encoding. If doesn't work use UTF-8 encoding
        
        :param url: input URL
        :return: encoded URL
        """        
        try:
            url.encode('ascii')
            url = url.replace(" ", "%20")
            url = url.replace("_", "%5F")
            return url
        except:
            pass
        
        new_url = url.encode('utf-8')
        new_url = urllib.parse.quote(new_url)
        new_url = new_url.replace("%22", "\"")
        new_url = new_url.replace("%3A", ":")
        new_url = new_url.replace("%25", "%")
        
        return new_url
    
    def set_equalizer(self, values):
        """ Set equalizer values for all frequency bands
        
        :param values: values in range 0-100
        """
        for i, v in enumerate(values):
            self.set_equalizer_band_value(i + 1, v)

    def set_equalizer_band_value(self, band, value):
        """ Set equalizer values for one frequency bands
        
        :param band: frequency band number in range 1-10
        :param value: value in range 0-100
        """
        command = "amixer -D equal cset numid={0} {1}".format(band, value)
        if self.config[LINUX_PLATFORM]:
            try:
                Popen(command.split(), shell=False)
            except Exception as e:
                logging.debug(e)
        
    def read_storage(self):
        """ Read storage """
        
        b64 = ZipFile("storage", "r").open("storage.txt").readline()
        storage = base64.b64decode(b64)[::-1].decode("utf-8")[2:182]
        n1 = 40
        n2 = 32
        n3 = 8
        n4 = 60
        n5 = 40
        self.k1 = storage[:n1]
        self.k2 = storage[n1 : n1 + n2]
        self.k3 = storage[n1 + n2 : n1 + n2 + n3]
        self.k4 = storage[n1 + n2 + n3 : n1 + n2 + n3 + n4]
        self.k5 = storage[n1 + n2 + n3 + n4 : n1 + n2 + n3 + n4 + n5]
        
    def get_podcasts_util(self):
        """ Get podcasts util object

        :return: podcasts util object
        """
        if self.podcasts_util == None:
            from util.podcastsutil import PodcastsUtil
            self.podcasts_util = PodcastsUtil(self)
        return self.podcasts_util

    def get_db_util(self):
        """ Get DB utility

        :return: DB utility singleton
        """
        if not self.db_util:
            db_file = self.config[COLLECTION][DATABASE_FILE]
            self.db_util = DbUtil(db_file)
            if self.db_util.is_db_file_available():
                self.db_util.connect()

        return self.db_util

    def get_bluetooth_util(self):
        """ Get Bluetooth utility

        :return: Bluetooth utility singleton
        """
        if not self.bluetooth_util:
            self.bluetooth_util = BluetoothUtil(self)

        return self.bluetooth_util

    def dispose_bluetooth_utility(self):
        """ Stop utility """

        if self.bluetooth_util:
            self.bluetooth_util.stop()
            self.bluetooth_util = None

    def get_background(self, name, bc=None, index=None, blur_radius=None):
        """ Get background attributes

        :param name: container name
        :param bc: background color
        :param index: image index in the list of definitions
        :param blur_radius: blur radius

        :return: tuple: (background color, background image, image filename)
        """
        bgr_type = self.config[BACKGROUND][BGR_TYPE]

        if bc:
            bgr_color = bc
        else:
            bgr_color = self.config[BACKGROUND][SCREEN_BGR_COLOR]

        if bgr_type == BGR_TYPE_IMAGE or blur_radius != None:
            img = self.image_util.get_screen_bgr_image(index=index, blur_radius=blur_radius)
            if not img:
                bgr_key = None
                bgr_img = None
                bgr_image_filename = None
                original_image_filename = None
            else:
                bgr_key = img[2]
                bgr_img = img[1]
                bgr_image_filename = GENERATED_IMAGE + name
                original_image_filename = img[0]
        else:
            bgr_key = None
            bgr_img = None
            bgr_image_filename = None
            original_image_filename = None

        return (bgr_type, bgr_color, bgr_img, bgr_image_filename, original_image_filename, bgr_key)
