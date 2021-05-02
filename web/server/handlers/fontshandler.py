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

import os
import json

from tornado.web import RequestHandler

class FontsHandler(RequestHandler):
    def initialize(self, util):
        self.util = util

    def get(self):
        if self.get_argument("current", None) != None:
            d = self.util.get_current_font_name()
        else:
            fonts = self.util.get_fonts()
            d = json.dumps(fonts)

        self.write(d)
