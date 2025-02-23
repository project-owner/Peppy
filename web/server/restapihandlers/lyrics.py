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

from util.lyricsutil import LyricsUtil
from util.config import CURRENT, MODE, AUDIO_FILES, COLLECTION, RADIO
from util.keys import KEY_STATIONS

from web.server.peppyrequesthandler import PeppyRequestHandler

class LyricsHandler(PeppyRequestHandler):
    def initialize(self, peppy):
        self.peppy = peppy
        self.util = peppy.util
        self.config = peppy.config
        self.lyrics_util = LyricsUtil(self.util.k2)

    def get(self):
        lyrics = None
        try:
            mode = self.config[CURRENT][MODE]
            if mode == AUDIO_FILES or mode == COLLECTION:
                m = self.util.get_file_metadata()
                song = m["artist"] + " - " + m["title"]
            elif mode == RADIO:
                screen = self.peppy.screens[KEY_STATIONS]
                song = screen.screen_title.text

            lyrics = self.lyrics_util.get_lyrics(song)

            if lyrics:
                lyrics = lyrics[0 : lyrics.find("*******")]
                self.write(lyrics)
        except:
            self.set_status(500)
            return self.finish()
