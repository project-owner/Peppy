# Copyright 2019-2021 Peppy Player peppy.player@gmail.com
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

class CommandHandler(RequestHandler):
    def initialize(self, peppy):
        self.peppy = peppy

    def get(self, command):
        if command == "ping":
            d = json.dumps("success")
            self.write(d)
            return

    def post(self, command):
        try:
            if command == "reboot":
                if self.get_argument("save", "true") == "false":
                    save = False
                else:
                    save = True
                self.peppy.reboot(save)
            elif command == "shutdown":
                self.peppy.shutdown()
        except:
            pass
