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
from util.config import EQUALIZER

class EqualizerHandler(RequestHandler):
    def initialize(self, peppy):
        self.peppy = peppy
        self.util = peppy.util

    def get(self):
        try:
            d = self.util.get_equalizer()
            self.write(json.dumps(d))
        except:
            self.set_status(500)
            return self.finish()

    def put(self):
        screen = None
        try:
            screen = self.peppy.screens[EQUALIZER]
        except:
            pass

        try:
            d = json.loads(self.request.body)
            if isinstance(d, list):
                self.util.set_equalizer(d)
            elif isinstance(d, dict):
                self.util.preset_equalizer(d["presets"])
            
            if screen != None:
                screen.refresh_equalizer()
        except:
            self.set_status(500)
            return self.finish()
