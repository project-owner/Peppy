# Copyright 2018 Peppy Player peppy.player@gmail.com
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
from pygame import Rect

from copy import copy
from util.keys import *
from ui.state import State
from ui.component import Component
from util.util import FOLDER_ICONS, FILE_DEFAULT_STATION, IMAGE_STAR, EXT_PNG
from util.config import COLORS, COLOR_DARK, CURRENT, LANGUAGE, FOLDER_LANGUAGES, STATIONS, \
    FOLDER_RADIO_STATIONS, STATIONS, CURRENT_STATIONS, SCREEN_INFO, HEIGHT, WIDTH

FILE_FAVORITES = "favorites.m3u"

class FavoritesUtil(object):
    """ Radio favorites utility class """
    
    def __init__(self, util):
        """ Initializer
        
        :param util: utility object
        """
        self.util = util
        self.config = util.config

    def is_favorite_mode(self):
        """ Check if current mode is favorites mode
        
        :return: True - favorites mode, False - not favorites mode
        """
        lang = self.config[CURRENT][LANGUAGE]
        k = STATIONS + "." + lang

        if len(self.config[k]) == 0:
            return False

        group = self.config[k][CURRENT_STATIONS]                
        if group == KEY_FAVORITES:
            return True
        return False

    def get_favorites_button_state(self, button_bounding_box):
        """ Get Favorites button state
        
        :param button_bounding_box: bounding box
        
        :return: favorites button state
        """
        state = State()
        state.bounding_box = button_bounding_box
        scale_factor = 0.45
        state.icon_base = self.util.load_mono_svg_icon(KEY_FAVORITES, self.util.COLOR_MAIN, button_bounding_box, scale_factor)
        state.icon_selected = self.util.load_mono_svg_icon(KEY_FAVORITES, self.util.COLOR_ON, button_bounding_box, scale_factor)
        state.name = state.l_name = state.genre = KEY_FAVORITES            
        state.bgr = self.config[COLORS][COLOR_DARK]
        state.img_x = None
        state.img_y = None
        state.auto_update = True
        state.show_bgr = False
        state.show_img = True
        state.show_label = False
        state.comparator_item = state.name
        state.index = 0
        state.v_align = V_ALIGN_TOP
        state.v_offset = 0
        state.voice_commands = state.name
        return state
    
    def set_favorites_in_config(self, items_per_line):
        """ Set list of favorites in configuration object 
        
        :param items_per_line: items in menu line
        """
        favorites, lang_dict = self.get_favorites_from_config()
        size = items_per_line * items_per_line
        lang = self.config[CURRENT][LANGUAGE]
        items = self.get_favorites_playlist(lang, size) 
        
        if items != None and favorites == None:
            lang_dict[KEY_FAVORITES] = items

    def get_favorites_from_config(self):
        """ Get list of favorites from configuration object
        
        :return: list of favorites
        """
        current_language = self.config[CURRENT][LANGUAGE]
        languages = self.config[KEY_LANGUAGES]
        lang_dict = favorites = None
        
        for language in languages:
            if language[NAME] == current_language:
                lang_dict = language
                break
            
        if lang_dict == None: 
            return None
        
        try:
            favorites = lang_dict[KEY_FAVORITES]
        except:
            pass
        
        return (favorites, lang_dict)
    
    def mark_favorites(self, buttons):
        """ Mark provided buttons with favorite icon
        
        :param buttons: buttons to mark
        """
        if len(self.config[STATIONS + "." + self.config[CURRENT][LANGUAGE]]) == 0:
            return

        group = self.config[STATIONS + "." + self.config[CURRENT][LANGUAGE]][CURRENT_STATIONS]
        if group == KEY_FAVORITES: 
            return
        
        favorites, lang_dict = self.get_favorites_from_config()
        favorite_names = []
        favorite_genres = []
        for favorite in favorites:
            favorite_names.append(favorite.l_name)
            favorite_genres.append(favorite.genre)
        
        for button in buttons.values():
            if button.state.l_name in favorite_names and button.state.genre in favorite_genres:
                c = self.get_star_component(button)
                button.add_component(c)
            else:
                if len(button.components) == 4:
                    del button.components[3]
    
    def get_star_component(self, button):
        """ Prepare star icon component for marking
        
        :param button: button to mark
        
        :return: star component
        """
        button_image_comp = button.components[1]
        button_image_x = button_image_comp.content_x
        button_image_y = button_image_comp.content_y
        button_image_size = button_image_comp.content.get_size()
        button_image_w = button_image_size[0]
        button_image_h = button_image_size[1]
        
        c = Component(self.util)
        bb = Rect(0, 0, self.config[SCREEN_INFO][WIDTH], self.config[SCREEN_INFO][HEIGHT])
        r = 1/25
        c.content = self.util.load_svg_icon(IMAGE_STAR, bb, r)  
        c.bgr = c.fgr = (0, 0, 255)
        c.name = button.state.l_name + ".fav"
        img_w = c.content[1].get_size()[0]
        c.content_x = button_image_x + button_image_w - img_w - 2
        c.content_y = button_image_y + 2
        
        return c
        
    def is_favorite(self, favorites, state):
        """ Check if provided button state belongs to favorites
        
        :param state: button state
        
        :retun: True - favorite, False - not favorite
        """
        for favorite in favorites:
            if favorite.l_name == state.l_name and favorite.genre == state.genre:
                return True
        return False 

    def add_favorite(self, favorites, state, items_per_page):
        """ Add provided state to the list of favorite states
        
        :param favorites: list of favorites
        :param state: state to add
        :param items_per_page: menu items per page
        """
        s = copy(state)
        s.index = len(favorites)
        s.index_in_page = s.index % items_per_page
        s.name = str(state.index)
        s.comparator_item = NAME
        s.favorite = True
        favorites.append(s)
        self.update_favorites_indexes(favorites, items_per_page)        

    def remove_favorite(self, favorites, state, rows, columns):
        """ Remove provided state from the list of favorite states
        
        :param favorites: list of favorites
        :param state: state to remove
        :param rows: menu rows
        :param columns: menu columns
        """
        for favorite in favorites:
            if favorite.l_name == state.l_name and favorite.genre == state.genre:
                del favorites[favorite.index]
                break
        if len(favorites) != 0:
            self.update_favorites_indexes(favorites, rows * columns)
    
    def update_favorites_indexes(self, favorites, items_per_page):
        """ Update the indexes of favorites
        
        :param favorites: list of favorites
        :param items_per_page: items per menu page
        """
        for index, value in enumerate(favorites):
            value.index = index
            value.index_in_page = index % items_per_page
            value.name = str(index)

    def get_favorites_playlist(self, language, stations_per_page):
        """ Load favorites for specified language
        
        :param language: the language
        :param stations_per_page: stations per page used to assign indexes 
               
        :return: list of button state objects. State contains station icons, index, genre, name etc.
        """
        favorites, lang_dict = self.get_favorites_from_config()
        if favorites != None:
            return favorites
        
        top_folder = self.util.get_stations_top_folder()
        folder = os.path.join(os.getcwd(), FOLDER_LANGUAGES, language, FOLDER_RADIO_STATIONS, top_folder)
        default_icon_path = os.path.join(os.getcwd(), FOLDER_ICONS, FILE_DEFAULT_STATION)
        return self.load_favorites(folder, stations_per_page, default_icon_path)

    def load_favorites(self, p, items_per_page, default_icon_path):
        """ Load m3u playlist
        
        :param p: base path
        :param items_per_page: items per page
        :param items_per_page: items per page
        :param default_icon_path: path to the default icon
        
        :return: list of State objects representing playlist
        """
        favorites = []
        lines = []
        state = None
        index = 0
        
        if p == None:
            return favorites
        
        try:
            path = os.path.join(p, FILE_FAVORITES)
            lines = codecs.open(path, "r", UTF8).read().split("\n")
        except Exception as e:
            pass
            
        for line in lines:
            if len(line.rstrip()) == 0: 
                continue
                
            if line.startswith("#") and state == None:
                state = State()
                state.favorite = True
                state.index = index
                state.name = str(index)
                state.index_in_page = index % items_per_page
                state.genre = line[1:].rstrip()
            elif line.startswith("#") and state != None:
                state.l_name = line[1:].rstrip()
                path = os.path.join(p, state.genre, state.l_name + EXT_PNG)
                icon = self.util.load_image(path)
                if not icon:
                    icon = self.util.load_image(default_icon_path)
                state.icon_base = icon
                state.comparator_item = NAME
            elif line.startswith("http"):
                state.url = line.rstrip()
                favorites.append(state)
                state = None
                index += 1                 
        return favorites

    def save_favorites(self, state):
        """ Save favorites 
        
        :param state: button state
        """        
        languages = self.config[FOLDER_LANGUAGES]
        
        for lang in languages:
            favorites = None
            s = ""
            try:
                favorites = lang[KEY_FAVORITES]
            except:
                pass
            if favorites != None:
                for favorite in favorites:
                    s += self.get_favorite_string(favorite)
                stations = lang[KEY_STATIONS]
                group_folder = list(stations.keys())[0]
                self.save_favorites_file(lang[NAME], group_folder, s)
                
    def get_favorite_string(self, state):
        """ Create entry for the favorites file from state object
        
        :param state: object representing favorite entry
        
        :return: string representation of the favorite entry in the favorites.txt file
        """
        s = ""
        s += "#" + state.genre + "\n"
        s += "#" + state.l_name + "\n"
        s += state.url + "\n"
        return s
    
    def save_favorites_file(self, language, group_folder, favorites):
        """ Write favorites to file
        
        :param language: favorites' language
        :param favorites: favorites string to write
        """
        path = os.path.join(os.getcwd(), FOLDER_LANGUAGES, language, FOLDER_RADIO_STATIONS, group_folder, FILE_FAVORITES)
        with codecs.open(path, 'w', UTF8) as file:
            file.write(favorites)        
    