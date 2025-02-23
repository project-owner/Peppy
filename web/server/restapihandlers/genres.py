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
from util.keys import KEY_FAVORITES

NAME = "name"
FOLDER_IMAGE_PATH = "folder_image_path"
FOLDER_IMAGE_ON_PATH = "folder_image_on_path"
FOLDER_IMAGE_SVG = "folder_image_svg"

class GenresHandler(RequestHandler):
    def initialize(self, peppy):
        self.util = peppy.util

    def get(self):
        try:
            genres = self.util.get_genres()
            genres = [g for g in self.util.get_genres().keys() if g != KEY_FAVORITES]

            if not genres:
                return

            self.write(json.dumps(genres))
        except:
            self.set_status(500)
            return self.finish()
