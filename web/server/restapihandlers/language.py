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
from util.keys import KEY_LANGUAGES
from util.config import CURRENT, LANGUAGE
from ui.state import State

LANGUAGE_NAME = "language.name"

class LanguageHandler(RequestHandler):
    def initialize(self, peppy):
        self.config = peppy.util.config
        self.peppy = peppy

    def get(self):
        try:
            if self.request.path.endswith("languages"):
                lang = [x["name"] for x in self.config[KEY_LANGUAGES]]
            else:
                lang = {LANGUAGE_NAME: self.config[CURRENT][LANGUAGE]}
            self.write(json.dumps(lang))
        except:
            self.set_status(404)
            return self.finish()

    def put(self):
        try:
            j = json.loads(self.request.body)
            state = State()
            state.name = j[LANGUAGE_NAME]
            self.peppy.change_language(state)
        except:
            self.set_status(500)
            return self.finish()
