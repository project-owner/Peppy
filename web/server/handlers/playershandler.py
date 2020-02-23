# Copyright 2019 Peppy Player peppy.player@gmail.com
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

import os
import json

from util.config import SCREEN_INFO
from tornado.web import RequestHandler

class PlayersHandler(RequestHandler):
    def initialize(self, config_class):
        self.config_class = config_class

    def get(self):
        d = json.dumps(self.config_class.get_players())
        self.write(d)
        return

    def put(self):
        value = json.loads(self.request.body)
        try:
            self.config_class.save_players(value)
        except Exception as e:
            print(e)