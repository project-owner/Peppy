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

class TimezoneHandler(RequestHandler):
    def initialize(self, util):
        self.util = util

    def get(self):
        t = self.util.get_timezone()
        d = json.dumps(t)
        self.write(d)

    def put(self):
        new_timezone = json.loads(self.request.body)
        if not new_timezone:
            return

        current_timezone = self.util.set_timezone(new_timezone)
        d = json.dumps(current_timezone)
        self.write(d)
