# Copyright 2024 Peppy Player peppy.player@gmail.com
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

class RadioBrowserHandler(RequestHandler):
    """ curl http://localhost:8000/api/radiobrowser """

    def initialize(self, peppy):
        self.util = peppy.util
        self.radio_browser = peppy.util.radio_browser

    def get(self):
        try:
            r = None

            a = self.get_argument("category", None)
            if a:
                if a == "countries":
                    r = self.radio_browser.get_countries()
                    if r:
                        self.radio_browser.sort_list(r, "name")

            a = self.get_argument("country", None)
            if a:
                r = self.radio_browser.get_countries()   

            if r:
                self.write(json.dumps(r))
        except Exception as e:
            self.set_status(500, reason=str(e))
            return self.finish()
