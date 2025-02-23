# Copyright 2024 Peppy Player peppy.player@gmail.com
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
import socket
import logging
import math
import requests

from operator import itemgetter
from urllib.parse import quote
from util.config import *
from util.keys import *
from ui.state import State
from copy import copy

BASE_URL = "all.api.radio-browser.info"
PAGE_SIZE = 10
NAME = "name"
STATIONCOUNT = "stationcount"
URL_RESOLVED = "url_resolved"
STATION_UUID = "stationuuid"
FAV_ICON = "favicon"
COUNTRY_CODE = "iso_3166_1"
LANGUAGE_CODE = "iso_639"
BUFFER_PAGE_SIZE = 100
MAX_BUFFER_PAGES = 100
FILE_RADIO_BROWSER_FAVORITES = "radiobrowser.m3u"

class RadioBrowser(object):
    """ Radio Browser Utility class """

    def __init__(self, util):
        """ Initializer 
        
        :param util: base utility object
        """
        self.util = util
        self.config = util.config
        self.default_radio_icon_path = util.default_radio_icon_path
        self.languages = None
        self.countries = None
        self.config = util.config
        self.radio_browser_playlist_cache = {}
        self.urls = None
        self.initial_favorites_size = 0

        self.buffers = {
            KEY_SEARCH_BY_COUNTRY: [],
            KEY_SEARCH_BY_LANGUAGE: [],
            KEY_SEARCH_BY_GENRE: [],
            KEY_SEARCH_BY_NAME: []
        }
        self.current_items = {
            KEY_SEARCH_BY_COUNTRY: None,
            KEY_SEARCH_BY_LANGUAGE: None,
            KEY_SEARCH_BY_GENRE: None,
            KEY_SEARCH_BY_NAME: None
        }
        self.cache_num = {
            KEY_SEARCH_BY_COUNTRY: {},
            KEY_SEARCH_BY_LANGUAGE: {},
            KEY_SEARCH_BY_GENRE: {},
            KEY_SEARCH_BY_NAME: {}
        }
        self.resources = {
            KEY_SEARCH_BY_COUNTRY: "bycountrycodeexact",
            KEY_SEARCH_BY_LANGUAGE: "bylanguageexact",
            KEY_SEARCH_BY_GENRE: "bytagexact",
            KEY_SEARCH_BY_NAME: "byname"
        }

    def get_urls(self):
        """ Get all available service URLs
        
        :return: the list of available URLs
        """
        urls = []

        try:
            info = socket.getaddrinfo(BASE_URL, 80, family=socket.AF_INET, proto=socket.IPPROTO_TCP)
            for i in info:
                ip = i[4][0]
                urls.append("https://" + socket.gethostbyaddr(ip)[0])
        except Exception as e:
            logging.debug(e)

        return urls

    def get_data(self, resource):
        """ Get data from the Radio Browser server
        
        :param resource: resource to get

        :return: data dictionary
        """
        if not self.urls:
            self.urls = self.get_urls()
            if not self.urls:
                return None
        
        d = None
        
        for url in self.urls:
            try:
                headers = {"User-Agent": "Peppy Player", "Content-Type": "application/json"}
                link = url + resource
                logging.debug(link)
                data = requests.get(link, headers=headers, timeout=(10, 10))
                if data.status_code != 200:
                    logging.debug(f"Error code: {data.status_code} reason: {data.reason} for url: {link}")
                    continue
                d = data.json()
                break
            except Exception as e:
                logging.debug(e)

        return d
    
    def get_server_stats(self):
        """ Get radio browser statistics

        :return: dictionary with statistics
        """
        uri = "/json/stats"
        return self.get_data(uri)
    
    def get_countries(self):
        """ Get list of countries
        
        :return: list of country dictionaries
        """
        if self.countries != None:
            return self.countries

        uri = f"/json/countries?hidebroken=true"
        self.countries = self.get_data(uri)
        self.countries = [c for c in self.countries if c["name"]]

        if self.countries == None:
            logging.debug("No countries found")
            return None

        cache = self.cache_num[KEY_SEARCH_BY_COUNTRY]
        for c in self.countries:
            cache[c[COUNTRY_CODE]] = c[STATIONCOUNT]

        return self.countries
    
    def get_languages(self):
        """ Get list of languages
        
        :return: list of lanaguage dictionaries
        """
        if self.languages != None:
            return self.languages

        uri = f"/json/languages?hidebroken=true"
        data = self.get_data(uri)

        if data == None:
            logging.debug("No languages found")
            return None

        self.languages = []
        cache = self.cache_num[KEY_SEARCH_BY_LANGUAGE]
        for d in data:
            if d[LANGUAGE_CODE] != None and d[LANGUAGE_CODE] != "null":
                self.languages.append(d)
                cache[d[NAME]] = d[STATIONCOUNT]

        return self.languages
    
    def get_page(self, resource, item, offset=0):
        """ Get stations page
        
        :param resource: search resource
        :param item: search item
        :param offset: page offset

        :return: page dictionary
        """
        uri = f"/json/stations/{resource}/{quote(item)}?offset={offset}&limit={BUFFER_PAGE_SIZE}&hidebroken=true"
        return self.get_data(uri)
    
    def get_items_num(self, search_by, item):
        """ Get the number of items
        
        :param search_by: search by resource
        :param item: item name

        :return: the number of items
        """
        resource = self.resources[search_by]
        buffer = self.buffers[search_by]

        if self.cache_num[search_by].get(item, None):
            return self.cache_num[search_by][item]
        
        data_length = len(buffer)

        if data_length == 0:
            start_index = 0
        else:
            if data_length < BUFFER_PAGE_SIZE:
                self.cache_num[search_by][item] = data_length
                return self.cache_num[search_by][item]
            start_index = 1

        length = BUFFER_PAGE_SIZE
        for n in range(start_index, MAX_BUFFER_PAGES):
            data = self.get_page(resource, item, n * BUFFER_PAGE_SIZE)

            if data == None:
                tmp = 0
            else:
                tmp = len(data)

            if tmp == 0:
                break
            elif tmp < BUFFER_PAGE_SIZE:
                length += tmp
                data = None
                break
            else:
                length += BUFFER_PAGE_SIZE

        self.cache_num[search_by][item] = length

        return self.cache_num[search_by][item]
    
    def get_pages_num(self, search_by, item, page_size):
        """ Get number of pages 
        
        :param search_by: search by resource
        :param item: item name
        :param page_size: page size

        :return: the number of pages
        """
        n = self.get_items_num(search_by, item)
        return math.ceil(n / page_size)
    
    def get_stations_page(self, search_by, item, offset=0, limit=PAGE_SIZE):
        """ Get stations by tag
        
        :param search_by: search by resource
        :param item: item name
        :param offset: page offset
        :param limit: page size

        :return: list of stations dictionaries
        """
        if item != self.current_items[search_by]:
            self.buffers[search_by] = []

        data_length = len(self.buffers[search_by])
        resource = self.resources[search_by]

        if data_length == 0 or item != self.current_items[search_by] or offset >= data_length:
            self.current_items[search_by] = item
            data = self.get_page(resource, item, offset=offset)
            if data:
                data_length = len(data)
                for i, d in enumerate(data):
                    d["index"] = offset + i

                if data_length == 0:
                    self.buffers[search_by] = []
                else:
                    self.buffers[search_by].extend(data)
            else:
                data_length = 0
                self.buffers[search_by] = []
        
        return self.buffers[search_by][offset : offset + limit]
    
    def sort_list(self, list_to_sort, key, reversed=False):
        """ Sort list of dictionaries in-place
        
        :param list_to_sort: list of dictionaries to sort
        :param key: dictionary key to sort by
        :param reversed: True - ascending sort order, False - descending sort order
        """
        if not list_to_sort:
            return

        list_to_sort.sort(key = itemgetter(key), reverse=reversed)

    def get_states_from_items(self, items, bgr, search_by=None, search_item=None):
        """ Get states from browser items

        :param items: browser items
        :param bgr: menu background
        :param search_by: search by resource
        :param search_item: item name

        :return: the list of states
        """
        if not items or not items[0]:
            return []

        menu_items = []
        
        for i, item in enumerate(items):
            state = self.get_state_from_item(item, bgr, search_by, search_item, i)
            menu_items.append(state)

        return menu_items

    def get_state_from_item(self, item, bgr, search_by=None, search_item=None, index=0):
        """ Get state

        :param item: browser item
        :bgr: menu background
        :param search_by: search by resource
        :param search_item: item name
        :param index: item index

        :return: the state
        """
        name = item[NAME]
        state = State()
        state.url = item.get(URL_RESOLVED, None)
        state.id = item[STATION_UUID]
        if not name:
            name = state.url
        if item.get("index", None) == None:
            state.index = index
        else:
            state.index = item["index"]
        state.l_name = f"{name}".strip()
        state.name = state.l_name
        state.comparator_item = state.id
        image_path = item.get(FAV_ICON, None)
        state.image_path = image_path
        state.original_image_path = image_path
        state.default_icon_path = self.default_radio_icon_path
        state.bgr = bgr
        state.img_x = None
        state.img_y = None
        state.auto_update = True
        state.show_bgr = True
        state.show_img = False
        state.show_label = True
        state.h_align = H_ALIGN_LEFT
        state.v_align = V_ALIGN_TOP
        state.v_offset = 35
        state.search_by = search_by
        state.search_item = search_item

        return state

    def is_favorite(self, state):
        """ Check if provided button state belongs to favorites
        
        :param state: button state
        
        :retun: True - favorite, False - not favorite
        """
        favorites = self.config.get(KEY_RADIO_BROWSER_FAVORITES, [])
        for favorite in favorites:
            if favorite.id == state.id:
                return True
        return False

    def remove_favorite(self, state):
        """ Remove provided state from the list of favorite states
        
        :param state: state to remove
        """
        favorites = self.config.get(KEY_RADIO_BROWSER_FAVORITES, None)
        if not favorites:
            return

        for i, favorite in enumerate(favorites):
            if favorite.id == state.id:
                del favorites[i]
                break

        for i, favorite in enumerate(favorites):
            favorite.index = i

    def add_favorite(self, state):
        """ Add provided state to favorites 
        
        :param state: item state
        """
        favorites = self.config.get(KEY_RADIO_BROWSER_FAVORITES, None)
        if not favorites:
            favorites = []
            self.config[KEY_RADIO_BROWSER_FAVORITES] = favorites

        s = copy(state)
        s.index = len(favorites)
        s.show_bgr = True
        s.show_img = False
        s.show_label = True

        for f in favorites:
            if f.id == state.id:
                return

        try:
            del s.icon_base
            del s.icon_base_scaled
        except:
            pass
        favorites.append(s)

        self.set_favorite_config(state)

    def get_image_path(self, state):
        """ Get image path
        
        :param state: item state

        :return: image path
        """
        image_path = ""

        if hasattr(state, "image_path"):
            if state.image_path.startswith(GENERATED_IMAGE):
                image_path = getattr(state, "original_image_path", "")
            else:
                image_path = state.image_path
        else:
            image_path = getattr(state, "default_icon_path", "")

        return image_path  

    def set_favorite_config(self, state):
        """ Set favorite config
        
        :param state: item state
        """
        if state:
            self.config[RADIO_BROWSER][FAVORITE_STATION_ID] = getattr(state, "id", "")
            self.config[RADIO_BROWSER][FAVORITE_STATION_NAME] = getattr(state, "l_name", "")
            self.config[RADIO_BROWSER][FAVORITE_STATION_LOGO] = self.get_image_path(state)
            self.config[RADIO_BROWSER][FAVORITE_STATION_URL] = getattr(state, "url", "")
        else:
            self.config[RADIO_BROWSER][FAVORITE_STATION_ID] = ""
            self.config[RADIO_BROWSER][FAVORITE_STATION_NAME] = ""
            self.config[RADIO_BROWSER][FAVORITE_STATION_LOGO] = ""
            self.config[RADIO_BROWSER][FAVORITE_STATION_URL] = ""

    def save_favorites(self, state):
        """ Write radio browser favorites to file 
        
        :param state: button state
        """
        favorites = self.config.get(KEY_RADIO_BROWSER_FAVORITES, None)
        favorites_str = ""
        path = os.path.join(os.getcwd(), FOLDER_PLAYLISTS, FILE_RADIO_BROWSER_FAVORITES)

        if favorites:
            for state in favorites:
                favorites_str += "#" + state.l_name + "\n"
                favorites_str += "#" + state.id + "\n"
                favorites_str += "#" + self.get_image_path(state) + "\n"
                favorites_str += state.url + "\n"
        else:
            if len(favorites) == 0 and os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass
            return

        with codecs.open(path, 'w', UTF8) as file:
            file.write(favorites_str)

    def load_favorites(self, bgr):
        """ Load radio browser playlist
        
        :param bgr:menu background
        
        :return: favorites
        """
        favorites = []
        lines = []
        station = []
        items = []
        path = os.path.join(os.getcwd(), FOLDER_PLAYLISTS, FILE_RADIO_BROWSER_FAVORITES)
        
        try:
            lines = codecs.open(path, "r", UTF8).read().split("\n")
        except:
            pass

        for line in lines:
            if len(line.strip()) == 0: 
                continue
            
            if line.startswith("#"):
                station.append(line[1:].strip())
            else:
                item = {NAME: station[0]}
                item[STATION_UUID] = station[1]
                item[FAV_ICON] = station[2]
                item[URL_RESOLVED] = line
                station = []
                items.append(item)

        if items:
            favorites = self.get_states_from_items(items, bgr)

        self.initial_favorites_size = len(favorites)
        return favorites

    def mark_favorites(self, buttons):
        """ Mark provided buttons with favorite icon
        
        :param buttons: buttons to mark
        """
        if not buttons:
            return

        favorites = self.config.get(KEY_RADIO_BROWSER_FAVORITES, None)

        if favorites == None or len(favorites) == 0:
            return

        favorite_ids = []

        for favorite in favorites:
            favorite_ids.append(favorite.id)
        
        for button in buttons.values():
            if button.state.id in favorite_ids:
                c = self.util.get_star_component(button)
                button.add_component(c)
            else:
                if len(button.components) == 4:
                    del button.components[3]

    def get_favorite(self, bgr=None):
        """ Get favorite from configuration
        
        :param bgr: menu background

        :return: favorite state
        """
        playlist = self.config[KEY_RADIO_BROWSER_FAVORITES]
        id = self.config[RADIO_BROWSER][FAVORITE_STATION_ID]
        s = None

        if not playlist or not id:
            return None
        
        for state in playlist:
            if state.id == id:
                s = state
                break
            
        if id and not s:
            s = self.get_favorite_state(bgr)

        return s
    
    def get_favorite_state(self, bgr=None):
        """ Get favorite state
        
        :param bgr: menu background

        :return: favorite state
        """
        s = None
        item = {NAME: self.config[RADIO_BROWSER][FAVORITE_STATION_NAME]}
        item[STATION_UUID] = self.config[RADIO_BROWSER][FAVORITE_STATION_ID]
        item[FAV_ICON] = self.config[RADIO_BROWSER][FAVORITE_STATION_LOGO]
        item[URL_RESOLVED] = self.config[RADIO_BROWSER][FAVORITE_STATION_URL]
        p = [item]
        favorites = self.get_states_from_items(p, bgr)
        if favorites:
            s = favorites[0]

        return s   
