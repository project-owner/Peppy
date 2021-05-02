# Copyright 2019-2021 Peppy Player peppy.player@gmail.com
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

class PlaylistsHandler(RequestHandler):
    def initialize(self, util):
        self.util = util

    def get(self):
        language = self.get_argument("language", None)
        genre = self.get_argument("genre", None)
        folder = self.get_argument("folder", None)

        playlist = self.util.load_radio_playlist(language, genre, folder)
        d = json.dumps(playlist)
        self.write(d)
        return

    def put(self):
        value = json.loads(self.request.body)
        languages = list(value.keys())
        for language in languages:
            genres = list(value[language].keys())
            for genre in genres:
                self.util.save_radio_playlist(language, genre, value[language][genre])
