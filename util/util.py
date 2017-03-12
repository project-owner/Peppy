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
import codecs
import importlib
import logging
import base64

from ui.state import State
from util.config import Config
from util.keys import *
from util.fileutil import FileUtil, FOLDER, FOLDER_WITH_ICON, FILE_AUDIO, FILE_PLAYLIST, FILE_IMAGE

IMAGE_VOLUME = "volume"
IMAGE_MUTE = "volume-mute"
IMAGE_SHADOW = "shadow"
IMAGE_SELECTION = "selection"
IMAGE_SELECTED_SUFFIX = "-on"
IMAGE_DISABLED_SUFFIX = "-off"
IMAGE_ABOUT = "about"
IMAGE_LANGUAGE = "language"
IMAGE_RADIO = "radio"
IMAGE_STREAM = "stream"
IMAGE_SCREENSAVER = "screensaver"
IMAGE_TIME_KNOB = "time-knob"
EXT_PROPERTIES = ".properties"
EXT_PNG = ".png"
EXT_M3U = ".m3u"
FOLDER_ICONS = "icons"
FOLDER_SLIDES = "slides"
FOLDER_STATIONS = "stations"
FOLDER_HOME = "home"
FOLDER_GENRES = "genres"
FOLDER_FONT = "font"
FOLDER_PLAYLIST = "playlist"
PACKAGE_SCREENSAVER = "screensaver"    
FILE_LABELS = "labels.txt"
ICON_FOLDER = "folder.png"
ICON_FILE_AUDIO = "audio-file.png"
ICON_FILE_PLAYLIST = "playlist.png"
FOLDER_SAVER = "saver"
FOLDER_SAVER_TYPE = "type"
FOLDER_SAVER_DELAY = "delay"
PROPERTY_SEPARATOR = "="
PROPERTY_COMMENT_CHAR = "#"
CURRENT_PLAYLIST = "current playlist"
CURRENT_INDEX = "current index"
INDEX = "index"
KEY_GENRE = "genre"
KEY_BYE = "bye"
UTF_8 = "utf-8-sig"
HOME_ITEMS = [IMAGE_ABOUT, IMAGE_LANGUAGE, KEY_AUDIO_FILES, IMAGE_RADIO, IMAGE_STREAM, IMAGE_SCREENSAVER]
HOME_DISABLED_ITEMS = [IMAGE_STREAM]
GENRE_ITEMS = ["children", "classical", "contemporary", "culture", "jazz", "news", "pop", "retro", "rock"]
LANGUAGE_ITEMS = ["en_us", "de", "fr", "ru"]
SCREENSAVER_ITEMS = ["clock", "logo", "slideshow", "vumeter"]
FOLDER_BUNDLES = "bundles"

class Util(object):
    """ Utility class """
    
    def __init__(self):
        """ Initializer. Prepares Config object. """
                        
        self.font_cache = {}
        self.image_cache = {}
        self.image_cache_base64 = {}
        self.config_class = Config()
        self.config = self.config_class.config
        self.config[LABELS] = self.get_labels()
        self.file_util = FileUtil(self.config)
        self.CURRENT_WORKING_DIRECTORY = os.getcwd()
    
    def get_labels(self):
        """ Read labels for current language
        
        :return: labels dictionary
        """        
        path = os.path.join(FOLDER_BUNDLES, self.config[CURRENT][KEY_LANGUAGE] + EXT_PROPERTIES)
        labels = self.load_properties(path, UTF_8)
        return labels
    
    def load_image(self, path, base64=False, bounding_box=None):
        """ Load and return image
        
        :param path: image path 
        :param base64: True - encode image using base64 algorithm (for web), False - don't encode
        :param bounding_box: bounding box 
        """
        if base64:
            return self.load_base64_image(path)
        else:
            return self.load_pygame_image(path, bounding_box)
    
    def load_pygame_image(self, path, bounding_box=None):
        """ Load image. 
        First, check if image is in the cache.
        If yes, return the image from the cache.
        If not load image file and place it in the cache.
        
        :param path: image path
        :param bounding_box: bounding box 
        :return: tuple where the first element is the path to the image and the second element is the image itself
        """
        image = None
            
        try:
            p = path
            if bounding_box:
                p = path + "_s"
            i = self.image_cache[p]
            return (path, i)
        except KeyError:
            pass
            
        try:            
            image = pygame.image.load(path.encode("utf-8")).convert_alpha()            
        except Exception:
            pass
            
        if image:
            img = image
            p = path
            if bounding_box:
                scale_ratio = self.get_scale_ratio(bounding_box, img)
                img = self.scale_image(image, scale_ratio)
                p = path + "_s"
            self.image_cache[p] = img
            return (path, img)
        else:
            return None
    
    def get_scale_ratio(self, bounding_box, img):
        """ Return scale ratio calculated from provided constraints (bounding box) and image
        
        :param bounding_box: bounding box
        :param img: image
        :return: tuple representing scale ratio 
        """
        w = bounding_box[0]
        h = bounding_box[1]
        width = img.get_size()[0]
        height = img.get_size()[1]
        
        if width > w and height > h:
            k1 = w/width
            k2 = h/height                    
            width = int(width * (min(k1, k2)))
            height = int(height * (min(k1, k2)))
        elif width > w and height < h:
            k = w/width
            width = int(width * k)
            height = int(height * k)
        elif width < w and height >h:
            k = h/height
            width = int(width * k)
            height = int(height * k)
            
        return (width, height)        
        
    def load_base64_image(self, path):
        """ Load image and encode it using base64 encoding.

        :param path: image path
        :return: base64 encoded image
        """        
        with open(path, 'rb') as f:
            img = base64.b64encode(f.read()).decode()
            return img          
        
    def load_icon(self, filename, resizable=True):
        """ Load UI icon
        
        :param filename: icon name without extension
        :param resizable: True - load icon from small/medium/large folders, False - load from 'icons' folder        
        :return: pygame image
        """
        filename += EXT_PNG
        path = os.path.join(FOLDER_ICONS, self.config[ICON_SIZE_FOLDER], filename)
        if not resizable:
            path = os.path.join(FOLDER_ICONS, filename)
        return self.load_image(path)
        
    def load_screensaver_images(self, folder):
        """ Load screensaver images (e.g. for Slideshow plug-in)
        
        :param folder: new image folder
        :return: list of images
        """
        slides = []        
        for f in os.listdir(folder):
            path = os.path.join(folder, f)
            img = self.load_image(path)
            if img:
                slides.append(img)     
        return slides
        
    def load_station_icon(self, folder, index):
        """ Load station icon
        
        :param folder: image folder
        :param index: image filename without extension        
        :return: station icon
        """
        path = os.path.join(folder, str(index) + EXT_PNG)  
        return self.load_image(path)
        
    def get_font(self, size):
        """ Return font from cache if not in cache load, place in cache and return.
        
        :param size: font size 
        """
        font_name = self.config[FONT_KEY]
        key = font_name + str(size)
        if key in self.font_cache:
            return self.font_cache[key]
        filename = os.path.join(FOLDER_FONT, font_name)
        
        if os.getcwd() != self.CURRENT_WORKING_DIRECTORY:
            os.chdir(self.CURRENT_WORKING_DIRECTORY)
        
        font = pygame.font.Font(filename, size)
        self.font_cache[key] = font
        return font
        
    def scale_image(self, image, ratio):
        """ Scale image using specified ratio
        
        :param ratio: scaling ratio        
        :return: scaled image
        """
        if image == None:
            return None
        a = pygame.Surface(ratio, flags=pygame.SRCALPHA)
        if isinstance(image, tuple):
            image = image[1]
        if image:
            pygame.transform.smoothscale(image, ratio, a)
            return a
        else:
            return None
            
    def load_stations(self, language, genre, stations_per_page):
        """ Load stations for specified language and genre
        
        :param language: the language
        :param genre: the genre
        :param stations_per_page: stations per page used to assign indexes        
        :return: list of button state objects. State contains station icons, index, genre, name etc.
        """
        stations = []
        folder = os.path.join(FOLDER_STATIONS, language, genre)
        path = os.path.join(folder, genre + EXT_M3U)
        lines = []
        try:
            lines = codecs.open(path, "r", UTF_8).read().split("\n")
        except Exception as e:
            logging.error(str(e))
            pass
        for i in range(0, len(lines), 3):
            if len(lines[i].rstrip()) == 0: 
                continue
            index = int(lines[i].rstrip()[1:])
            localized_name = lines[i + 1][1:]
            url = lines[i + 2]
            icon = self.load_station_icon(folder, index)
            state = State()
            state.index = index
            state.genre = genre
            state.url = url.rstrip()
            state.name = str(index)
            state.l_name = localized_name.rstrip()
            state.icon_base = icon
            state.comparator_item = INDEX
            state.index_in_page = index % stations_per_page
            stations.append(state)    
        return stations
        
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
                properties[pair[0].rstrip()] = pair[1].rstrip()
        return properties
        
    def load_menu(self, names, comparator, disabled_items=None):
        """ Load menu items
        
        :param names: list of menu item names (should have corresponding filename)
        :param comparator: string used to sort items
        :param disabled_items: list of items which should be disabled        
        :return: dictionary with menu items
        """
        items = {}
        f = self.config[ICON_SIZE_FOLDER]
            
        for name in names:
            filename = name + EXT_PNG
            path = os.path.join(FOLDER_ICONS, f, filename)
            icon = self.load_image(path)
                
            filename = name + IMAGE_SELECTED_SUFFIX + EXT_PNG
            path_on = os.path.join(FOLDER_ICONS, f, filename)
            icon_on = self.load_image(path_on)
            
            filename = name + IMAGE_DISABLED_SUFFIX + EXT_PNG
            path_off = os.path.join(FOLDER_ICONS, f, filename)
            icon_off = self.load_image(path_off)
                
            state = State()
            state.name = name
            state.genre = name 
            state.l_genre = self.config[LABELS][name]
            state.l_name = self.config[LABELS][name]
            state.icon_base = icon
            if icon_on:
                state.icon_selected = icon_on
            else:
                state.icon_selected = icon
            if not icon_off:
                state.icon_disabled = icon_on
            state.bgr = self.config[COLORS][COLOR_DARK]
            state.img_x = None
            state.img_y = None
            state.auto_update = True
            state.show_bgr = True
            state.show_img = True
            state.show_label = True
            if comparator == NAME:
                state.comparator_item = state.name
            elif comparator == GENRE:
                state.comparator_item = state.genre
            if disabled_items and name in disabled_items:
                state.enabled = False
            items[state.name] = state            
        return items
        
    def get_screensaver_labels(self):
        """ Return localized screensaver labels 
        
        :return: labels dictionary
        """        
        screensaver_labels = {}
        for name in SCREENSAVER_ITEMS:
            screensaver_labels[name.lower()] = self.config[LABELS][name.lower()]
        return screensaver_labels
        
    def get_screensaver_delays(self):
        """ Get screensaver delay button states
        
        :return: dictionary with button states
        """
        names = [KEY_SCREENSAVER_DELAY_1, KEY_SCREENSAVER_DELAY_3, KEY_SCREENSAVER_DELAY_OFF]
        delays = {}
        for n in names:            
            state = State()
            state.name = n
            state.l_name = self.config[LABELS][n]
            state.comparator_item = n
            state.bgr = self.config[COLORS][COLOR_DARK]
            delays[state.name] = state                
        return delays
        
    def load_screensaver(self, name):
        """ Load screensaver plug-in module and create object
        
        :param name: plug-in name        
        :return: screensaver object
        """
        p = PACKAGE_SCREENSAVER + ('.' + name.lower())*2
        m = importlib.import_module(p)
        return getattr(m, name.title())(self)

    def get_file_icon(self, file_type, file_image_path=None, icon_bb=None):
        """ Load image representing file. Four types of icons supported:
        1. Folder icon
        2. Audio file icon
        3. Folder with folder icon (folder icon will be displayed in this case)
        4. Playlist icon
        
        :param file_type: defines file type 
        :param file_image_path: path to image file       
        :param icon_bb: image bounding box
        :return: image representing file
        """
        icon_folder = self.load_image(os.path.join(FOLDER_ICONS, self.config[ICON_SIZE_FOLDER], ICON_FOLDER))
        icon_file_audio = self.load_image(os.path.join(FOLDER_ICONS, self.config[ICON_SIZE_FOLDER], ICON_FILE_AUDIO))
        icon_file_playlist = self.load_image(os.path.join(FOLDER_ICONS, self.config[ICON_SIZE_FOLDER], ICON_FILE_PLAYLIST))

        if file_type == FOLDER:
            return icon_folder
        elif file_type == FILE_AUDIO: return icon_file_audio
        elif file_type == FILE_PLAYLIST: return icon_file_playlist
        elif file_type == FOLDER_WITH_ICON or file_type == FILE_IMAGE:
            bounding_box = (icon_bb[0] * 0.8, icon_bb[1] * 0.8) 
            img = self.load_image(file_image_path, bounding_box=bounding_box)
            if img:
                return img
            else:
                return icon_folder        
   
    def load_folder_content(self, folder_name, rows, cols, bounding_box):
        """ Prepare list of state objects representing folder content
        
        :param folder_name: folder name 
        :param rows: number of rows in file browser  
        :param cols: number of columns in file browser       
        :param bounding_box: file menu bounding box
        :return: list of state objects representing folder content
        """
        content = self.file_util.get_folder_content(folder_name)
        
        if not content:
            return None
        
        items = []
        items_per_page = cols * rows
        item_width = bounding_box.w / cols
        item_height = (bounding_box.h / rows) * 0.7 # as label takes 30 % by default

        for index, s in enumerate(content):
            s.index = index
            s.name = s.file_name
            s.l_name = s.name            
            s.icon_base = self.get_file_icon(s.file_type, getattr(s, "file_image_path", ""), (item_width, item_height))
            s.comparator_item = index
            s.bgr = self.config[COLORS][COLOR_DARK]
            s.show_bgr = True
            s.index_in_page = index % items_per_page
            items.append(s)    
        return items

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
            s.name = s.l_name = s.file_name
            s.icon_base = self.get_file_icon(FILE_AUDIO)
            s.comparator_item = index
            s.bgr = self.config[COLORS][COLOR_DARK]
            s.show_bgr = True
            s.index_in_page = index % items_per_page
            items.append(s)    
        return items

    def get_audio_files_in_folder(self, folder_name):
        """ Return the list of audio files in specified folder
        
        :param folder_name: folder name      
        :return: list of audio files
        """
        files = self.file_util.get_folder_content(folder_name)        
        if not files:
            return None
                
        files[:] = (f for f in files if f.file_type == FILE_AUDIO)
        
        for n, f in enumerate(files):
            f.index = n
    
        return files

    def get_audio_file_icon(self, folder, bb):
        """ Return audio file icon which is album art image. 
        If it's not available then CD image will be returned.
        
        :param folder: folder name 
        :param bb: bounding box  
        :return: audio file icon
        """
        d = os.path.join(FOLDER_ICONS, self.config[ICON_SIZE_FOLDER], "cd.png")
        p = self.file_util.get_folder_image_path(folder)
        if not p: p = d
        
        img = self.load_image(p)
        k = img[1].get_size()[0] / img[1].get_size()[1]        
        new_w = int(bb.w / k) if k < 1.0 else bb.w
        new_h = int(bb.h / k) if k > 1.0 else bb.h
        img = self.scale_image(img, (new_w, new_h))
        
        return (p, img)
        
