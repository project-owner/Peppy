# Copyright 2021 Peppy Player peppy.player@gmail.com
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

import json

from tornado.web import RequestHandler
from util.config import STATIONS, CURRENT, LANGUAGE, CURRENT_STATIONS
from util.keys import KEY_RADIO_BROWSER, GENRE, KEY_STATIONS
from ui.state import State

DEFAULT_ICON_PATH = "default_icon_path"
GENRE = "genre"
IMAGE_PATH = "image_path"
INDEX = "index"
L_NAME = "l_name"
NAME = "name"
URL = "url"

class RadioPlayerHandler(RequestHandler):
    def initialize(self, peppy):
        self.peppy = peppy
        self.util = peppy.util
        self.config = self.util.config

    def get(self):
        try:
            state = self.util.get_current_radio_station()
            station = self.convert_to_dictionary(state)
            self.write(json.dumps(station))
        except:
            self.set_status(500)
            return self.finish()

    def convert_to_dictionary(self, state):
        if state == None:
            return None
        
        new_dict = {}
        new_dict[NAME] = getattr(state, L_NAME, None)
        new_dict[DEFAULT_ICON_PATH] = getattr(state, DEFAULT_ICON_PATH, None)
        new_dict[GENRE] = getattr(state, GENRE, None)
        new_dict[IMAGE_PATH] = getattr(state, IMAGE_PATH, None)
        new_dict[INDEX] = getattr(state, INDEX, None)
        new_dict[URL] = getattr(state, URL, None)
        
        return new_dict

    def put(self):
        browser_screen = None
        station_screen = None
        
        try:
            browser_screen = self.peppy.screens[KEY_RADIO_BROWSER]
        except:
            pass

        try:
            station_screen = self.peppy.screens[KEY_STATIONS]
        except:
            pass

        try:
            j = json.loads(self.request.body)

            if not j:
                return

            genre = j[GENRE]
            index = j[INDEX]
            key = STATIONS + "." + self.config[CURRENT][LANGUAGE]
            self.config[key][CURRENT_STATIONS] = genre
            self.util.set_radio_station_index(index)

            state = State()
            state.name = state.l_name = state.comparator_item = genre
            state.genre = GENRE
            state.source = KEY_RADIO_BROWSER
            state.url = j[URL]
            state.index = index

            if browser_screen != None and browser_screen.visible:
                browser_screen.change_station(state)
                browser_screen.redraw_observer()
            else:
                self.peppy.go_stations(state)
                station_screen = self.peppy.screens[KEY_STATIONS]
                station_screen.redraw_observer()
                
            self.peppy.screensaver_dispatcher.cancel_screensaver()
        except Exception as e:
            self.set_status(500)
            return self.finish()
