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
import logging

from web.server.peppyrequesthandler import PeppyRequestHandler
from util.config import MODE, CURRENT, AUDIO_FILES, COLLECTION, RADIO, RADIO_BROWSER, PLAYER_SETTINGS, \
    VOLUME, MUTE, PAUSE, TITLE

class StateHandler(PeppyRequestHandler):
    def initialize(self, peppy):
        self.util = peppy.util
        self.config = peppy.util.config
        self.peppy = peppy
        self.supported_modes = [RADIO, RADIO_BROWSER, AUDIO_FILES, COLLECTION]

    def get(self):
        state = {}
        mode = state[MODE] = self.config[CURRENT][MODE]
        state[VOLUME] = self.config[PLAYER_SETTINGS][VOLUME]
        state[MUTE] = self.config[PLAYER_SETTINGS][MUTE]
        state[PAUSE] = self.config[PLAYER_SETTINGS][PAUSE]

        if self.config[CURRENT][MODE] not in self.supported_modes or not self.peppy.current_player_screen:
            state["time"] = None
            self.write(json.dumps(state))
            return self.finish()

        try:
            current_player_screen = self.peppy.screens[self.peppy.current_player_screen]
            state[TITLE] = current_player_screen.screen_title.text or ""

            if mode == AUDIO_FILES or mode == COLLECTION:
                state["metadata"] = self.util.get_file_metadata()
                if current_player_screen.show_time_control:
                    time_control = current_player_screen.time_control
                    total = time_control.total.text
                    current = time_control.current.text
                    state["time"] = {"current": current, "total": total}
                if self.config.get("file.playback", None):
                    state["currentFolder"] = self.config["file.playback"]["folder"]
                    state["currentFile"] = self.config["file.playback"]["file"]
            elif mode == RADIO or mode == RADIO_BROWSER:
                state["metadata"] = current_player_screen.station_metadata
                state["time"] = None

            self.write(json.dumps(state))
        except:
            self.set_status(500)
            return self.finish()
