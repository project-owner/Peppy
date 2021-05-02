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
from util.config import FILE_CURRENT, FILE_CONFIG, FILE_PLAYERS

class DefaultsHandler(RequestHandler):
    def initialize(self, config):
        self.config = config

    def put(self):
        value = json.loads(self.request.body)
        if not value:
            return

        if value[0]:
            self.config.set_default_file(FILE_CURRENT)

        if value[1]:
            self.config.set_default_file(FILE_CONFIG)
        
        if value[2]:
            self.config.set_default_file(FILE_PLAYERS)
