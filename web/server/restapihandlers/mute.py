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
import pygame

from tornado.web import RequestHandler
from util.config import PLAYER_SETTINGS, MUTE
from util.keys import KEY_SUB_TYPE, SUB_TYPE_KEYBOARD, KEY_ACTION, KEY_KEYBOARD_KEY, USER_EVENT_TYPE

class MuteHandler(RequestHandler):
    def initialize(self, peppy):
        self.config = peppy.util.config
        self.peppy = peppy

    def get(self):
        try:
            v = {MUTE: self.config[PLAYER_SETTINGS][MUTE]}
            self.write(json.dumps(v))
        except:
            self.set_status(500)
            return self.finish()

    def put(self):
        try:
            d = {}
            d[KEY_SUB_TYPE] = SUB_TYPE_KEYBOARD
            d[KEY_ACTION] = pygame.KEYDOWN
            d[KEY_KEYBOARD_KEY] = pygame.K_x
            event = pygame.event.Event(USER_EVENT_TYPE, **d)
            event.source = "volume"
            pygame.event.post(event)
            d[KEY_ACTION] = pygame.KEYUP
            event = pygame.event.Event(USER_EVENT_TYPE, **d)
            event.source = "volume"
            pygame.event.post(event)
        except:
            self.set_status(500)
            return self.finish()
