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

from tornado.web import RequestHandler

class TimeHandler(RequestHandler):
    def initialize(self, peppy):
        self.peppy = peppy

    def get(self):
        try:
            current_player_screen = self.peppy.current_player_screen
            if not current_player_screen:
                return

            s = self.peppy.screens[current_player_screen]
            if s == None or not s.show_time_control:
                return

            time_control = s.time_control
            total = time_control.total.text
            current = time_control.current.text
            t = {"current": current, "total": total}

            self.write(json.dumps(t))
        except:
            self.set_status(500)
            return self.finish()
