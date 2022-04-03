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
from util.config import PLAYER_SETTINGS, VOLUME
from ui.state import State

class VolumeHandler(RequestHandler):
    def initialize(self, peppy):
        self.config = peppy.util.config
        self.peppy = peppy

    def get(self):
        try:
            v = {VOLUME: self.config[PLAYER_SETTINGS][VOLUME]}
            self.write(json.dumps(v))
        except:
            self.set_status(500)
            return self.finish()

    def put(self):
        try:
            d = json.loads(self.request.body)
            state = State()
            v = d[VOLUME]
            state.position = v
            self.peppy.set_volume(state)
            self.config[PLAYER_SETTINGS][VOLUME] = v
            screen = self.peppy.screens[self.peppy.current_player_screen]
            if screen:
                screen.refresh_volume()
                screen.redraw_observer()
        except:
            self.set_status(500)
            return self.finish()
