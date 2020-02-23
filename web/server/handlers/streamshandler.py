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

from tornado.web import RequestHandler

class StreamsHandler(RequestHandler):
    def initialize(self, util):
        self.util = util

    def get(self):
        streams_str = self.util.get_streams_string()
        d = json.dumps(streams_str)
        self.write(d)
        return

    def put(self):
        value = json.loads(self.request.body)
        try:
            self.util.save_streams(value)
        except Exception as e:
            print(e)
