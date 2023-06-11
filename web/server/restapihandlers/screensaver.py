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
from util.config import SCREENSAVER, NAME

SCREENSAVER_NAME = "screensaver.name"

class ScreensaverHandler(RequestHandler):
    def initialize(self, peppy):
        self.config = peppy.util.config
        self.screensaver_dispatcher = peppy.screensaver_dispatcher

    def get(self):
        try:
            if self.request.path.endswith("screensavers"):
                s = self.screensaver_dispatcher.get_active_savers() 
            else:
                s = {SCREENSAVER_NAME: self.config[SCREENSAVER][NAME]}
            self.write(json.dumps(s))
        except:
            self.set_status(404)
            return self.finish()

    def put(self):
        try:
            self.screensaver_dispatcher.cancel_screensaver()
            j = json.loads(self.request.body)
            self.config[SCREENSAVER][NAME] = j[SCREENSAVER_NAME]
            self.screensaver_dispatcher.change_saver_type()
        except:
            self.set_status(500)
            return self.finish()

    def post(self, command):
        try:
            if command == "start":
                self.screensaver_dispatcher.start_screensaver()
            elif command == "stop":
                self.screensaver_dispatcher.cancel_screensaver()
        except:
            self.set_status(500)
            return self.finish()
