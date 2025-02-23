# Copyright 2022 Peppy Player peppy.player@gmail.com
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
import os

from tornado.web import RequestHandler
from util.config import CURRENT, LANGUAGE
from util.keys import KEY_FAVORITES

DEFAULT_ICON_PATH = "default_icon_path"
IMAGE_PATH = "image_path"
L_NAME = "l_name"
URL = "url"
GENRE = "genre"
INDEX = "index"

class PlaylistHandler(RequestHandler):
    def initialize(self, peppy):
        self.util = peppy.util
        self.config = self.util.config
        self.default_radio_icon_path = self.util.default_radio_icon_path

    def get(self):
        try:
            language = self.config[CURRENT][LANGUAGE]
            genre = self.util.get_current_genre().l_name

            if genre == KEY_FAVORITES:
                stations = self.favorites_util.get_favorites_playlist()
            else:
                stations = self.util.get_radio_browser_playlist(genre)

            if not stations:
                return

            playlist = self.convert_to_dictionaries(stations, genre)
            playlist_object = {"language": language, "genre": genre, "defaultIcon": self.default_radio_icon_path, "playlist": playlist}

            self.write(json.dumps(playlist_object))
        except:
            self.set_status(500)
            return self.finish()

    def convert_to_dictionaries(self, stations, genre):
        result = []
        for index, station in enumerate(stations):
            new_dict = {}
            new_dict[IMAGE_PATH] = getattr(station, IMAGE_PATH, None)
            new_dict[L_NAME] = getattr(station, L_NAME, None)
            new_dict[URL] = getattr(station, URL, None)
            new_dict[GENRE] = genre
            new_dict[INDEX] = index
            
            result.append(new_dict)
        return result
