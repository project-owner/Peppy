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
from util.config import PLAYER_SETTINGS, PLAYBACK_ORDER
from ui.state import State

class OrderHandler(RequestHandler):
    def initialize(self, peppy):
        self.config = peppy.util.config
        self.peppy = peppy

    def get(self):
        try:
            v = {PLAYBACK_ORDER: self.config[PLAYER_SETTINGS][PLAYBACK_ORDER]}
            self.write(json.dumps(v))
        except:
            self.set_status(500)
            return self.finish()

    def put(self):
        try:
            d = json.loads(self.request.body)
            self.config[PLAYER_SETTINGS][PLAYBACK_ORDER] = d[PLAYBACK_ORDER]
            screen = self.peppy.screens[self.peppy.current_player_screen]
            if screen and screen.show_order:
                state = State()
                state.name = d[PLAYBACK_ORDER]
                screen.handle_order_popup_selection(state)
                screen.redraw_observer()
        except:
            self.set_status(500)
            return self.finish()
