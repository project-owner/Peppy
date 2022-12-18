# Copyright 2021-2022 Peppy Player peppy.player@gmail.com
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

class InfoHandler(RequestHandler):
    """ curl http://localhost:8000/api/info
        curl http://localhost:8000/api/info?url="C:\music\test.flac"
    """
    def initialize(self, peppy):
        self.util = peppy.util

    def get(self):
        try:
            url = None
            if self.request.arguments:
                url = self.get_argument("url", default=None)

            if url == None:
                v = self.util.get_file_metadata()
            else:
                v = self.util.get_audio_file_metadata(url)

            self.write(json.dumps(v))
        except:
            self.set_status(500)
            return self.finish()
