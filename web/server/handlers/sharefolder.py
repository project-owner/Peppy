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

import logging
import json

from tornado.web import RequestHandler
from util.config import LINUX_PLATFORM

class ShareFolder(RequestHandler):
    def initialize(self, peppy):
        self.config = peppy.util.config
        self.samba_util = peppy.util.samba_util

    def get(self, command):
        if not self.config[LINUX_PLATFORM]:
            d = json.dumps(None)
            self.write(d)
            return

        if command == "shares":
            shares = self.samba_util.get_shares()
            d = json.dumps(shares)
            self.write(d)
            return

    def put(self, command):
        if command != "save":
            d = json.dumps(None)
            self.write(d)
            return

        try:
            shares = json.loads(self.request.body)
            self.samba_util.save_shares(shares)
        except Exception as e:
            logging.debug(e)
            self.set_status(500)
            self.finish(json.dumps({ "message": "Cannot save Share"}))
