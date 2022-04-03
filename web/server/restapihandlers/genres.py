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

NAME = "name"
FOLDER_IMAGE_PATH = "folder_image_path"
FOLDER_IMAGE_ON_PATH = "folder_image_on_path"

class GenresHandler(RequestHandler):
    def initialize(self, peppy):
        self.util = peppy.util

    def get(self):
        try:
            genre = self.util.get_current_genre().l_name
            genres = self.util.get_genres()

            if not genres:
                return

            genres_dict = self.convert_to_dictionaries(genres)
            self.write(json.dumps(genres_dict))
        except:
            self.set_status(500)
            return self.finish()

    def convert_to_dictionaries(self, genres):
        result = []
        for genre in genres.values():
            new_dict = {}
            new_dict[NAME] = getattr(genre, NAME, None)
            new_dict[FOLDER_IMAGE_PATH] = getattr(genre, FOLDER_IMAGE_PATH, None)
            new_dict[FOLDER_IMAGE_ON_PATH] = getattr(genre, FOLDER_IMAGE_ON_PATH, None)
            result.append(new_dict)
        return result
