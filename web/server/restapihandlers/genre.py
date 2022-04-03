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
from util.keys import KEY_GENRES, GENRE, KEY_STATIONS
from ui.state import State

class GenreHandler(RequestHandler):
    def initialize(self, peppy):
        self.peppy = peppy
        self.util = peppy.util
        self.config = self.util.config

    def get(self):
        try:
            genre = self.util.get_current_genre().l_name
            self.write(genre)
        except:
            self.set_status(500)
            return self.finish()

    def put(self):
        group_screen = None
        station_screen = None
        
        try:
            group_screen = self.peppy.screens[KEY_GENRES]
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

            genre = j["genre"]
            key = STATIONS + "." + self.config[CURRENT][LANGUAGE]
            self.config[key][CURRENT_STATIONS] = genre

            state = State()
            state.name = state.l_name = state.comparator_item = genre
            state.genre = state.source = GENRE

            if group_screen != None and group_screen.visible:
                group_screen.change_group(state)
                group_screen.redraw_observer()
            else:
                self.peppy.go_stations(state)
                station_screen.redraw_observer()

            self.peppy.screensaver_dispatcher.cancel_screensaver()
        except:
            self.set_status(500)
            return self.finish()
