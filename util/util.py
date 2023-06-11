# Copyright 2016-2023 Peppy Player peppy.player@gmail.com
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
import time
import threading
import requests

from subprocess import Popen, PIPE
from zipfile import ZipFile
from ui.state import State
from util.config import *
from util.keys import *
from util.fileutil import FileUtil, FOLDER_WITH_ICON, FILE_AUDIO, FILE_PLAYLIST, FILE_IMAGE
from urllib import request
from websiteparser.loyalbooks.constants import BASE_URL, LANGUAGE_PREFIX, ENGLISH_USA, RUSSIAN
from util.discogsutil import DiscogsUtil
from util.collector import DbUtil, INFO, METADATA, MP4_METADATA
from util.bluetoothutil import BluetoothUtil
from util.imageutil import ImageUtil, EXT_MP4, EXT_M4A
from util.cdutil import CdUtil
from util.switchutil import SwitchUtil
from util.sambautil import SambaUtil
from util.yastreamutil import YaStreamUtil
from util.jukeboxutil import JukeboxUtil
from util.archiveutil import ArchiveUtil
from mutagen import File

IMAGE_VOLUME = "volume"
IMAGE_MUTE = "volume-mute"
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

CLASSIC_PRESETS = [71, 71, 71, 71, 71, 71, 84, 83, 83, 87]
JAZZ_PRESETS = [71, 71, 72, 81, 71, 62, 62, 71, 71, 71]
POP_PRESETS = [74, 65, 61, 60, 64, 73, 75, 75, 74, 74]
ROCK_PRESETS = [58, 63, 80, 84, 77, 66, 58, 55, 55, 55]
CONTEMPORARY_PRESETS = [60, 63, 71, 80, 79, 71, 60, 57, 57, 58]
FLAT_PRESETS = [66, 66, 66, 66, 66, 66, 66, 66, 66, 66]

PLAYER_RUNNING = "running"
PLAYER_SLEEPING = "sleeping"

FILE_STATIONS = "stations.m3u"
FILE_STREAMS = "streams.m3u"
FILE_FOLDER = "folder.png"
FILE_FOLDER_ON = "folder-on.png"
FILE_FOLDER_SVG = "folder.svg"
FILE_DEFAULT_STATION = "default-station.png"
FILE_DEFAULT_STREAM = "default-stream.png"
FILE_FAVORITES = "favorites.m3u"

EXT_PROPERTIES = ".properties"
EXT_PNG = ".png"
EXT_JPG = ".jpg"
EXT_M3U = ".m3u"

FOLDER = "folder"
FOLDER_ICONS = "icons"
FOLDER_SLIDES = "slides"
FOLDER_STATIONS = "stations"
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

class Util(object):
    """ Utility class """
    
    def __init__(self):
        """ Initializer. Prepares Config object. """

        self.connected_to_internet = False
        self.font_cache = {}
        self.voice_commands_cache = {}
        self.cd_titles = {}
        self.cd_track_names_cache = {}
        self.screensaver_cache = {}
        self.radio_player_playlist_cache = {}
        self.stream_player_playlist_cache = []
        self.radio_browser_playlist_cache = {}
        self.genres_cache = {}
        self.config_class = Config()
        self.config = self.config_class.config
        self.screen_rect = self.config_class.screen_rect
        self.config[LABELS] = self.get_labels()
        self.pygame_screen = self.config_class.pygame_screen
        self.CURRENT_WORKING_DIRECTORY = os.getcwd()
        self.read_storage()
                
        if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)): 
            ssl._create_default_https_context = ssl._create_unverified_context
        self.podcasts_util = None
        self.db_util = None
        self.bluetooth_util = None
    
    def init_utilities(self):
        """ Initialize utilities """

        self.discogs_util = DiscogsUtil(self.k1)
        self.image_util = ImageUtil(self)
        self.file_util = FileUtil(self)
        if self.config[USE_SWITCH]:
            self.switch_util = SwitchUtil(self)
        self.samba_util = SambaUtil(self)
        self.ya_stream_util = YaStreamUtil(self)
        self.jukebox_util = JukeboxUtil(self)
        self.archive_util = ArchiveUtil(self)

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
        self.voice_commands_cache[lang[NAME]] = voice_commands
        
        return voice_commands
    
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
        try:
            return self.config[VOICE_ASSISTANT_LANGUAGE_CODES][language]
        except:
            return None

    def get_weather_language_code(self, language):
        """ Return the language code required by the weather screensaver

        :param language: current language
        :return: language code
        """
        try:
            return self.config[WEATHER_SCREENSAVER_LANGUAGE_CODES][language]
        except:
            return None
    
    def get_file_metadata(self):
        """ Return current file metadata. 
            Valid only for modes: audio files and collection

        :return: dictionary with metadata
        """
        mode = self.config[CURRENT][MODE]

        if mode == AUDIO_FILES:
            folder = self.config[FILE_PLAYBACK][CURRENT_FOLDER]
            filename = self.config[FILE_PLAYBACK][CURRENT_FILE]            
        elif mode == COLLECTION:
            folder = self.config[COLLECTION_PLAYBACK][COLLECTION_FOLDER]
            filename = self.config[COLLECTION_PLAYBACK][COLLECTION_FILE]
        else:
            return {}

        path = os.path.join(folder, filename)
        if not path:
            return {}

        return self.get_audio_file_metadata(path)

    def get_audio_file_metadata(self, path):
        """ Get audio file metadata

        :param path: file path

        :return: the dictionary with file metadata
        """
        meta = {}
        if os.sep in path:
            meta["filename"] = path[path.rfind(os.sep) + 1 : ]
        else:
            meta["filename"] = path

        try:
            filesize = os.stat(path).st_size
            meta["filesize"] = filesize
            m = File(path)
            for i in INFO:
                meta[i] = getattr(m.info, i, None)

            if path.lower().endswith(EXT_MP4) or path.lower().endswith(EXT_M4A):
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

    def get_fonts(self):
        """ Return the list of all fonts available in the 'font' folder

        :return: list of font names
        """
        fonts = []
        folder = os.path.join(FOLDER_FONT)

        for file in os.listdir(folder):
            if file.lower().endswith(".ttf"):
                fonts.append(file)

        return fonts        

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

    def get_current_font_name(self):
        """ Return the current font name

        :return: current font name
        """
        return self.config[FONT_KEY]
        
    def load_radio_playlist(self, language, genre, top_folder):
        """ Load radio playlist

        :param language: laguage for playlist
        :param genre: genre playlist
        :param top_folder: top folder under language
        :return: playlist as a string
        """
        if genre == KEY_FAVORITES:
            folder = os.path.join(os.getcwd(), FOLDER_LANGUAGES, language, FOLDER_RADIO_STATIONS, top_folder)
            path = os.path.join(folder, FILE_FAVORITES)
        else:
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
        previous_index = new_index = None
        previous_station = None

        for lang in languages:
            if language == lang[NAME]:
                stations = lang[KEY_STATIONS]
                top_folder = list(stations.keys())[0]

        previous_playlist = self.get_radio_playlist(self.radio_player_playlist_cache, genre, language)
        k = STATIONS + "." + language

        try:
            previous_index = self.config[k][genre]
            previous_station = previous_playlist[previous_index]
        except:
            pass

        path = os.path.join(os.getcwd(), FOLDER_LANGUAGES, language, FOLDER_RADIO_STATIONS, top_folder, genre, FILE_STATIONS)
        with codecs.open(path, 'w', UTF8) as file:
            file.write(playlist)

        new_playlist = self.get_radio_playlist({}, genre, language)
        for i, s in enumerate(new_playlist):
            if previous_station and s.l_name == previous_station.l_name:
                new_index = i

        if new_index != None:
            self.config[k][genre] = new_index
        else:
            self.config[k][genre] = 0

    def get_genres(self):
        """ Get all genres available for the current language

        :return: genres
        """
        folders = self.get_stations_folders()
        if not folders:
            return {}

        items = {}
        current_language = self.config[CURRENT][LANGUAGE]

        try:
            items = self.genres_cache[current_language]
            return items
        except:
            pass

        folders = self.get_stations_folders()
        top_folder = self.get_stations_top_folder()
            
        for index, folder in enumerate(folders):
            name = folder
            state = State()
            state.name = state.l_name = state.genre = name
            state.folder_image_path = os.path.join(os.getcwd(), FOLDER_LANGUAGES, current_language, FOLDER_RADIO_STATIONS, top_folder, folder, FILE_FOLDER)
            state.folder_image_on_path = os.path.join(os.getcwd(), FOLDER_LANGUAGES, current_language, FOLDER_RADIO_STATIONS, top_folder, folder, FILE_FOLDER_ON)
            state.folder_image_svg = os.path.join(os.getcwd(), FOLDER_LANGUAGES, current_language, FOLDER_RADIO_STATIONS, top_folder, folder, FILE_FOLDER_SVG)
            state.comparator_item = state.name
            state.index = index
            state.voice_commands = name
            items[name] = state

        self.genres_cache[current_language] = items
        return items

    def add_icons(self, genre_button_state):
        """ Add icons to the genre button

        :param genre_button_state: button state object
        """
        if genre_button_state.name == KEY_FAVORITES:
            return

        bb = genre_button_state.bounding_box

        folder_image_svg = getattr(genre_button_state, "folder_image_svg", None)
        if folder_image_svg and os.path.isfile(folder_image_svg):
            folder_image = self.image_util.load_icon_main(FOLDER, bb, filepath=folder_image_svg)
            folder_image_on = self.image_util.load_icon_on(FOLDER, bb, filepath=folder_image_svg)
            path = folder_image[0]
            path_on = folder_image_on[0]
        else:
            path = genre_button_state.folder_image_path
            folder_image = self.image_util.load_image(path)
            path_on = genre_button_state.folder_image_on_path
            folder_image_on = self.image_util.load_image(path_on)
            
        if folder_image:
            scale_ratio = self.image_util.get_scale_ratio((bb.w, bb.h), folder_image[1])
            scaled_image = self.image_util.scale_image(folder_image, scale_ratio)
            genre_button_state.icon_base = (path, scaled_image)
            if folder_image_on:
                scaled_image_on = self.image_util.scale_image(folder_image_on, scale_ratio)
                genre_button_state.icon_selected = (path_on, scaled_image_on)

        genre_button_state.bgr = self.config[COLORS][COLOR_DARK]
        genre_button_state.img_x = None
        genre_button_state.img_y = None
        genre_button_state.auto_update = True
        genre_button_state.show_bgr = True
        genre_button_state.show_img = True
        genre_button_state.show_label = True
        genre_button_state.v_align = V_ALIGN_TOP
        genre_button_state.v_offset = 35

    def add_icon(self, button_state, scale_factor=None):
        """ Add icons to the button

        :param button_state: button state object
        :param scale_factor: image scale factor
        """
        path = button_state.image_path
        icon = self.image_util.load_image(path)
        if not icon:
            if hasattr(button_state, "default_icon_path"):
                icon = self.image_util.load_image(button_state.default_icon_path)
            elif hasattr(button_state, "logo_image_path"):
                icon = self.image_util.load_image(button_state.logo_image_path)
            else:
                icon = button_state.icon_base
        
        button_state.icon_base = icon
        bb = button_state.bounding_box
        if scale_factor:
            sf = scale_factor
        else:
            sf = (bb.w, bb.h)

        if icon:
            scale_ratio = self.image_util.get_scale_ratio(sf, icon[1])
            scaled_image = self.image_util.scale_image(icon, scale_ratio)
            button_state.icon_base_scaled = scaled_image

    def get_radio_player_playlist(self, genre=None):
        """ Get radio playlist for the player screen

        :param genre: the genre

        :return: the radio playlist for specified genre
        """
        return self.get_radio_playlist(self.radio_player_playlist_cache, genre)

    def get_radio_browser_playlist(self, genre=None):
        """ Get radio playlist for the browser screen

        :param genre: the genre

        :return: the radio playlist for specified genre
        """
        return self.get_radio_playlist(self.radio_browser_playlist_cache, genre)

    def get_radio_playlist(self, cache, genre=None, lang=None):
        """ Get radio playlist for the specified genre

        :param cache: the cache
        :param genre: the genre
        :param lang: the language

        :return: the radio playlist
        """
        if lang:
            language = lang
        else:
            language = self.config[CURRENT][LANGUAGE]

        if genre == None:
            k = STATIONS + "." + language
            try:
                self.config[k]
                genre = self.config[k][CURRENT_STATIONS]
            except:
                pass

        items = []
        try:
            return cache[language + "_" + genre]
        except:
            pass

        lines = []
        item_name = None
        index = 0
        top_folder = self.get_stations_top_folder()

        if genre == None:
            try:
                genres = self.get_genres()
                keys = list(genres.keys())
                first_key = keys[0]
                genre = genres[first_key].l_name
            except:
                return []

        folder = os.path.join(os.getcwd(), FOLDER_LANGUAGES, language, FOLDER_RADIO_STATIONS, top_folder, genre)
        path = os.path.join(folder, FILE_STATIONS)

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
            state = State()
            state.index = index
            state.url = line.rstrip()
            state.name = str(index)
            state.l_name = name
            state.comparator_item = name
            state.genre = genre
            state.image_path = os.path.join(folder, state.l_name + EXT_PNG)

            if not os.path.isfile(state.image_path):
                state.image_path = os.path.join(folder, state.l_name + EXT_JPG)

            state.default_icon_path = os.path.join(os.getcwd(), FOLDER_ICONS, FILE_DEFAULT_STATION)
            state.bgr = self.config[COLORS][COLOR_DARK]
            state.img_x = None
            state.img_y = None
            state.auto_update = True
            state.show_bgr = True
            state.show_img = True
            state.show_label = True
            state.v_align = V_ALIGN_TOP
            state.v_offset = 35
            items.append(state)
            item_name = None
            index += 1

        if items:
            cache[language + "_" + genre] = items

        return items

    def get_stream_playlist(self):
        """ Get stream playlist

        :return: the playlist
        """
        if len(self.stream_player_playlist_cache) != 0:
            return self.stream_player_playlist_cache

        items = []
        lines = []
        item_name = None
        index = 0

        folder = os.path.join(os.getcwd(), FOLDER_PLAYLISTS)
        path = os.path.join(folder, FILE_STREAMS)
        default_icon_path = os.path.join(os.getcwd(), FOLDER_ICONS, FILE_DEFAULT_STREAM)
        
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
            state = State()
            state.index = index
            state.url = line.rstrip()
            state.name = str(index)
            state.l_name = name
            state.comparator_item = name
            state.image_path = os.path.join(folder, state.l_name + EXT_PNG)
            state.default_icon_path = default_icon_path
            state.bgr = self.config[COLORS][COLOR_DARK]
            state.img_x = None
            state.img_y = None
            state.auto_update = True
            state.show_bgr = True
            state.show_img = True
            state.show_label = True
            state.v_align = V_ALIGN_TOP
            state.v_offset = 35
            items.append(state)
            item_name = None
            index += 1

        self.stream_player_playlist_cache = items
        return items

    def get_station(self, language, genre, station_index):
        """ Get radio station by index

        :param language: the language
        :param genre: the genre
        :param station_index: the index

        :return: the station state object
        """
        top_folder = self.get_stations_top_folder()
        folder = os.path.join(os.getcwd(), FOLDER_LANGUAGES, language, FOLDER_RADIO_STATIONS, top_folder, genre)
        default_icon_path = os.path.join(os.getcwd(), FOLDER_ICONS, FILE_DEFAULT_STATION)
        playlist = self.get_radio_playlist(language, genre)
        state = playlist[station_index]

        path = os.path.join(folder, state.l_name + EXT_PNG)
        icon = self.image_util.load_image(path)
        if not icon:
            icon = self.image_util.load_image(default_icon_path)
        
        state.icon_base = icon
        return state

    def get_streams_string(self):
        """ Read file

        :return: string
        """
        path = os.path.join(os.getcwd(), FOLDER_PLAYLISTS, FILE_STREAMS)

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
        path = os.path.join(os.getcwd(), FOLDER_PLAYLISTS, FILE_STREAMS)
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

    def get_current_language_translation(self):
        """ Get current language parameters
        
        :return: current language translation
        """
        if self.get_current_language() == None:
            return None

        current_language = self.get_current_language()[NAME]
        languages = self.config[KEY_LANGUAGES]
        for language in languages:
            if current_language == language[NAME]:
                return language[TRANSLATIONS][current_language]
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
    
    def load_languages_menu(self, button_bounding_box):
        """ Load languages menu items
        
        :param button_bounding_box: menu button bounding box
        
        :return: dictionary with menu items
        """
        items = {}
        i = 0
        current_language = self.get_current_language()
        labels = current_language[TRANSLATIONS]
            
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
            state.v_align = V_ALIGN_TOP
            
            items[state.name] = state
            i += 1            
        return items

    def load_disk_switch_menu(self, disk_config):
        """ Load disk switch menu items
        
        :param disk_config: file configuration
        
        :return: dictionary with menu button states
        """
        items = {}
            
        for i, disk in enumerate(disk_config):
            if not disk[NAME]:
                continue
            state = State()
            state.l_name = state.name = state.filename = disk[NAME]
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
            state.button_on = disk[KEY_POWER_ON]
            state.bit_address = disk[BIT_ADDRESS]
            items[state.name] = state

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
            path = os.path.join(os.getcwd(), FOLDER_LANGUAGES, current_language, FOLDER_RADIO_STATIONS, top_folder, folder, FILE_FOLDER_SVG)

            if os.path.isfile(path):
                folder_image = self.image_util.load_icon_main(FOLDER, button_bounding_box, filepath=path)
                folder_image_on = self.image_util.load_icon_on(FOLDER, button_bounding_box, filepath=path)
                path = folder_image[0]
                path_on = folder_image_on[0]
            else:
                path = os.path.join(os.getcwd(), FOLDER_LANGUAGES, current_language, FOLDER_RADIO_STATIONS, top_folder, folder, FILE_FOLDER)
                folder_image = self.image_util.load_image(path)
                path_on = os.path.join(os.getcwd(), FOLDER_LANGUAGES, current_language, FOLDER_RADIO_STATIONS, top_folder, folder, FILE_FOLDER_ON)
                folder_image_on = self.image_util.load_image(path_on)
            
            state = State()
            name = folder
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
        
    def load_menu(self, names, comparator, disabled_items=None, h_align=None, v_align=None, bb=None, scale=1, suffix=None, show_image=True, wrap_lines=False):
        """ Load menu items
        
        :param names: list of menu item names (should have corresponding filename)
        :param comparator: string used to sort items
        :param disabled_items: list of items which should be disabled
        :param v_align: vertical alignment
        :param bb: bounding box
        :param scale: image scale factor
        :param suffix: label suffix
        :param show_image: True - show button image, False don't show
        :param wrap_lines: True - wrap lines, False - show ellipsis
                
        :return: dictionary with menu items
        """
        items = {}
            
        for i, name in enumerate(names):
            if show_image:
                icon = self.image_util.load_icon_main(name, bb, scale)
                icon_on = self.image_util.load_icon_on(name, bb, scale)
            else:
                icon = icon_on = None
            
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
            state.show_img = show_image
            state.show_label = True
            state.h_align = h_align
            if wrap_lines:
                state.wrap_labels = wrap_lines
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
        if script_name == None or len(script_name.strip()) == 0:
            logging.debug("No script name")
            return

        n = script_name[0:script_name.find(".py")]
        name = SCRIPTS + "." + n

        try:
            m = importlib.import_module(name)
        except Exception as e:
            logging.debug(e)
            os._exit(0)

        s = getattr(m, n.title())()

        if s.type == "sync":
            s.start()
        else:
            s.start_thread()

    def load_folder_content(self, folder_name, rows, cols):
        """ Prepare list of state objects representing folder content
        
        :param folder_name: folder name 
        :param rows: number of rows in file browser  
        :param cols: number of columns in file browser       
        
        :return: list of state objects representing folder content
        """
        content = self.file_util.get_folder_content(folder_name, load_images=False)
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
            else:
                s.show_label = True
            
            s.comparator_item = index
            s.bgr = self.config[COLORS][COLOR_DARK]
            s.show_bgr = True
            s.index_in_page = index % items_per_page
            items.append(s)
        return items

    def load_playlist(self, state, playlist_provider, rows, columns, icon_box=None):
        """ Handle playlist
        
        :param state: state object defining playlist
        :param playlist_provider: provider
        :param rows: menu rows 
        :param columns: menu columns
        :param icon_box: icon bounding box
        
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
         
        return self.load_playlist_content(play_list, rows, columns, icon_box)               

    def load_playlist_content(self, playlist, rows, cols, icon_box=None):
        """ Prepare list of state objects representing playlist content
        
        :param playlist: list of items in playlist 
        :param rows: number of rows in file browser  
        :param cols: number of columns in file browser
        :param icon_box: icon bounding box
              
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
            s.icon_base = self.image_util.get_file_icon(FILE_AUDIO, icon_bb=icon_box)
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
    
    def get_equalizer(self):
        """ Get equalizer values for all frequency bands

        :return: list of frequency bands
        """
        values = FLAT_PRESETS.copy()
        try:
            config_values = self.config[CURRENT][EQUALIZER]
            values = config_values.copy()
        except:
            pass

        return values

    def preset_equalizer(self, name):
        """ Set equalizer values using presets

        :param name: preset name
        """
        values = self.get_equalizer()

        if name == CLASSICAL: values = CLASSIC_PRESETS.copy()
        elif name == JAZZ: values = JAZZ_PRESETS.copy()
        elif name == POP: values = POP_PRESETS.copy()
        elif name == ROCK: values = ROCK_PRESETS.copy()
        elif name == CONTEMPORARY: values = CONTEMPORARY_PRESETS.copy()
        elif name == FLAT: values = FLAT_PRESETS.copy()

        self.config[CURRENT][EQUALIZER] = values.copy()
        self.set_equalizer(values)

        return values

    def set_equalizer(self, values):
        """ Set equalizer values for all frequency bands
        
        :param values: values in range 0-100
        """
        if not self.config[LINUX_PLATFORM]:
            self.config[CURRENT][EQUALIZER] = values.copy()
            return

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
        n3 = 32
        n4 = 56
        self.k1 = storage[:n1]
        self.k2 = storage[n1 : n1 + n2]
        self.k3 = storage[n1 + n2 : n1 + n2 + n3]
        self.k4 = storage[n1 + n2 + n3 : n1 + n2 + n3 + n4]
        
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

        if bgr_type == BGR_TYPE_IMAGE or bgr_type == USE_ALBUM_ART or blur_radius != None:
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

    def get_current_timezone(self):
        """ Get the current timezone info

        :return: dictionary represnting the current timezone info
        """
        subp = Popen("timedatectl", shell=False, stdout=PIPE)
        result = subp.stdout.read()
        decoded = result.decode(UTF_8)
        lines = decoded.split("\n")
        d = {}

        for line in lines:
            if line.strip().startswith("Local time:"):
                d["currentTime"] = line.strip()[12:]
            if line.strip().startswith("Time zone:"):
                tz = line.strip()[11:]
                sp = tz.split()
                area_city = sp[0].strip()
                pos = area_city.find("/")
                area = area_city[0:pos]
                city = area_city[pos + 1:]
                city = city.replace("_", " ")

                tz = tz.replace("_", " ")
                d["currentTimezone"] = tz
                d["currentArea"] = area
                d["currentCity"] = city

        return d

    def get_all_timezones(self):
        """ Get the info about all timezones

        :return: dictionary where key - area, value - list of cities
        """
        cmd = "timedatectl list-timezones"
        subp = Popen(cmd.split(), shell=False, stdout=PIPE)
        result = subp.stdout.read()
        decoded = result.decode(UTF_8)
        lines = decoded.split("\n")
        area_cities = {}

        for line in lines:
            line = line.strip()
            if len(line) == 0:
                continue
            pos = line.find("/")
            if pos == -1:
                area_cities[line] = [] # UTC
            else:
                area = line[0:pos]
                city = line[pos + 1:]
                city = city.replace("_", " ")
                if area in area_cities.keys():
                    cities = area_cities[area]
                    cities.append(city)
                else:
                    cities = [city]
                    area_cities[area] = cities

        return area_cities   

    def get_timezone(self):
        """ Get timezone info

        :return: dictionary representing the timezone info
        """
        if not self.config[LINUX_PLATFORM]:
            return None

        d = self.get_current_timezone()
        d["areaCities"] = self.get_all_timezones()

        return d

    def  set_timezone(self, timezone):
        """ Set new timezone

        :param timezone: new timezone

        :return: new timezone info
        """
        timezone = timezone.replace(" ", "_")
        
        cmd = "sudo timedatectl set-timezone " + timezone
        Popen(cmd.split(), shell=False, stdout=PIPE)
        time.sleep(1)
        t = self.get_current_timezone()

        return t

    def post_exit_event(self, x, y, source):
        """ Post exit event

        :param x: x coordinate
        :param y: y coordinate
        :param source: the source
        """
        d = {}
        d["x"] = x
        d["y"] = y
        d["source"] = source
        t = threading.Thread(target=self.start_exit_container_thread, args=[d])
        t.start()

    def start_exit_container_thread(self, args):
        """ Start exit event

        :param args: the arguments
        """
        event = pygame.event.Event(SELECT_EVENT_TYPE, args)
        event.source = args["source"]
        pygame.event.post(event)

    def get_current_genre(self):
        """ Get the current genre

        :return: the genre
        """
        genres = self.get_genres()
        current_genre_name = list(genres.keys())[0]
        current_genre = genres[current_genre_name]        
        
        k = STATIONS + "." + self.config[CURRENT][LANGUAGE]
        try:
            self.config[k]
            current_genre = genres[self.config[k][CURRENT_STATIONS]]
        except:
            pass
        
        return current_genre

    def get_current_radio_station_index(self):
        """ Get the current radio station index

        :return: the index
        """
        index = 0
        genre = self.get_current_genre()
        current_language = self.config[CURRENT][LANGUAGE]
        try:
            index = self.config[STATIONS + "." + current_language][genre.name]
        except KeyError:
            pass

        if index == None:
            index = 0

        return index

    def set_radio_station_index(self, index):
        """ Set the radio station index

        :param index: the index to set
        """
        language = self.config[CURRENT][LANGUAGE]
        genre = self.get_current_genre()
        k = STATIONS + "." + language

        try:
            self.config[k]
        except:
            self.config[k] = {}
            self.config[k][CURRENT_STATIONS] = genre.name
                
        self.config[k][genre.name] = index

    def get_current_radio_station(self):
        """ Get the current radio station

        :return: the station state object
        """
        playlist = self.get_radio_browser_playlist()
        index = self.get_current_radio_station_index()
        if playlist:
            return playlist[index]
        return None

    def get_disabled_modes(self):
        """ Get the disabled modes

        :return: the list of disabled modes
        """
        disabled_modes = []

        if not self.config[HOME_MENU][RADIO] or not self.is_radio_enabled() or not self.connected_to_internet:
            disabled_modes.append(RADIO)

        if not self.is_audiobooks_enabled() or not self.connected_to_internet:
            disabled_modes.append(AUDIOBOOKS)

        if not self.connected_to_internet:
            disabled_modes.append(STREAM)
            disabled_modes.append(ARCHIVE)
            disabled_modes.append(YA_STREAM)
            if self.jukebox_util.is_online_playlist():
                disabled_modes.append(JUKEBOX)

        cdutil = CdUtil(self)
        cd_drives_info = cdutil.get_cd_drives_info()
        player = self.config[AUDIO][PLAYER_NAME]
        if len(cd_drives_info) == 0 or player == MPV_NAME:
            disabled_modes.append(CD_PLAYER)

        podcasts_util = self.get_podcasts_util()
        podcasts = podcasts_util.get_podcasts_links()
        downloads = podcasts_util.are_there_any_downloads()
        connected = self.connected_to_internet
        valid_players = [VLC_NAME, MPV_NAME]
        if (connected and len(podcasts) == 0 and not downloads) or (not connected and not downloads) or player not in valid_players:
            disabled_modes.append(PODCASTS)

        if not self.config[LINUX_PLATFORM]:
            disabled_modes.append(AIRPLAY)
            disabled_modes.append(SPOTIFY_CONNECT)
            disabled_modes.append(BLUETOOTH_SINK)

        if not self.config[HOME_MENU][COLLECTION] or self.get_db_util() == None:
            disabled_modes.append(COLLECTION)

        return disabled_modes

    def get_modes(self):
        """ Get all user defined and enabled modes

        :return: list of modes
        """
        disabled = self.get_disabled_modes()
        return [m for m in MODES if m not in disabled and self.config[HOME_MENU][m]]

    def translate(self, text, from_language, to_language):
        """ Translate text from one language to another using Google translate API

        :param text: text to translate
        :param from_language: source language code
        :param to_language: target language code

        :return: translated text
        """
        if text == None:
            return None

        if from_language.startswith("en"):
            from_language = "en"

        if to_language.startswith("en"):
            to_language = "en"

        url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=" + from_language + "&tl=" + to_language + "&dt=t&q='" + text + "'"
        content = None
        try:
            content = requests.get(url, timeout=(5, 5))
        except Exception as e:
            logging.debug(e)

        if content == None:
            return None

        j = content.json()
        top = j[0]
        translated = ""
        for n in range(len(top)):
            translated += top[n][0]

        if not translated[0].isalpha():
            translated = translated[1:]
        if not translated[len(translated) - 1].isalpha():
            translated = translated[0 : len(translated) - 1]
        if not translated[len(translated) - 1].isalpha():
            translated = translated[0 : len(translated) - 1]

        return translated
