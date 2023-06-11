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

import json

from tornado.web import RequestHandler
from ui.state import State
from util.config import COLLECTION_PLAYBACK, COLLECTION_TOPIC, COLLECTION_FOLDER, COLLECTION_FILE, \
    COLLECTION_URL, COLLECTION_TRACK_TIME

class CollectionHandler(RequestHandler):
    def initialize(self, peppy):
        self.config = peppy.util.config
        self.peppy = peppy

    def post(self, command):
        try:
            d = json.loads(self.request.body)
            if command == "play/disc":
                s = State()
                s.source = "init"
                self.config[COLLECTION_PLAYBACK][COLLECTION_TOPIC] = s.topic = "album"
                self.config[COLLECTION_PLAYBACK][COLLECTION_FOLDER] = s.folder = d["path"]
                self.config[COLLECTION_PLAYBACK][COLLECTION_FILE] = s.file_name = None
                self.config[COLLECTION_PLAYBACK][COLLECTION_URL] = s.url = None
                self.config[COLLECTION_PLAYBACK][COLLECTION_TRACK_TIME] = 0
                self.peppy.go_collection_playback(s)
            elif command == "play/song":
                s = State()
                s.source = "init"
                self.config[COLLECTION_PLAYBACK][COLLECTION_TOPIC] = s.topic = "title"
                self.config[COLLECTION_PLAYBACK][COLLECTION_FOLDER] = s.folder = d["folder"]
                self.config[COLLECTION_PLAYBACK][COLLECTION_FILE] = s.file_name = d["file_name"]
                self.config[COLLECTION_PLAYBACK][COLLECTION_URL] = s.url = d["url"]
                self.config[COLLECTION_PLAYBACK][COLLECTION_TRACK_TIME] = 0
                self.peppy.go_collection_playback(s)
        except:
            self.set_status(500)
            return self.finish()
