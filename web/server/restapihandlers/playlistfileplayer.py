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
from util.config import FILE_PLAYBACK, CURRENT_FOLDER, CURRENT_FILE
from util.keys import KEY_PLAY_FILE
from util.fileutil import FILE_AUDIO, FILE_PLAYLIST
from ui.state import State

class PlaylistFilePlayerHandler(RequestHandler):
    def initialize(self, peppy):
        self.peppy = peppy
        self.file_util = peppy.util.file_util
        self.config = peppy.util.config

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

            file = j.get("file", None)

            if not os.path.exists(file):
                self.set_status(500)
                self.set_status(500, reason="File not found")
                return self.finish()

            state = State()

            i = file.rfind(os.sep)
            if i != -1:
                folder = file[0 : i]
                f = file[i + 1:]
                self.config[FILE_PLAYBACK][CURRENT_FOLDER] = folder
                self.config[FILE_PLAYBACK][CURRENT_FILE] = f
                state.file_name = f
            else:
                folder = ""
                self.config[FILE_PLAYBACK][CURRENT_FOLDER] = folder
                self.config[FILE_PLAYBACK][CURRENT_FILE] = file
                state.file_name = file

            state.url = os.path.join(folder, state.file_name)
            state.playback_mode = FILE_PLAYLIST
            self.peppy.go_file_playback(state)
            player_screen.redraw_observer()

            self.peppy.screensaver_dispatcher.cancel_screensaver()
        except:
            self.set_status(500)
            return self.finish()
