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
import os

from tornado.web import RequestHandler
from util.config import FILE_PLAYBACK, CURRENT_FOLDER, CURRENT_FILE, AUDIO_FILES
from util.keys import KEY_PLAY_FILE
from util.fileutil import FILE_AUDIO
from ui.state import State

class FilePlayerHandler(RequestHandler):
    def initialize(self, peppy):
        self.peppy = peppy
        self.file_util = peppy.util.file_util
        self.config = peppy.util.config

    def get(self):
        try:
            current_folder = self.file_util.current_folder
            current_file = self.config[FILE_PLAYBACK][CURRENT_FILE]

            if not current_folder or not current_file:
                return

            file = {"current.folder": current_folder, "current.file": current_file}
            self.write(json.dumps(file))
        except Exception as e:
            self.set_status(500)
            return self.finish()

    def put(self):
        player_screen = None
        
        try:
            player_screen = self.peppy.screens[KEY_PLAY_FILE]
        except:
            pass

        try:
            j = json.loads(self.request.body)

            if not j:
                return

            folder = j["folder"]
            file = j["file"]
            self.config[FILE_PLAYBACK][CURRENT_FOLDER] = folder
            self.config[FILE_PLAYBACK][CURRENT_FILE] = file

            state = State()
            state.file_name = file
            state.url = os.path.join(folder, file)
            state.playback_mode = FILE_AUDIO

            self.peppy.go_file_playback(state)
            player_screen.redraw_observer()

            self.peppy.screensaver_dispatcher.cancel_screensaver()
        except:
            self.set_status(500)
            return self.finish()
