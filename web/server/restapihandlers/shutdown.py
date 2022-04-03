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
from util.keys import KEY_SUB_TYPE, SUB_TYPE_KEYBOARD, KEY_ACTION, KEY_KEYBOARD_KEY, USER_EVENT_TYPE

class ShutdownHandler(RequestHandler):
    def initialize(self, peppy):
        self.peppy = peppy

    def get(self):
        try:
            if self.peppy.event_dispatcher.poweroff_flag == 1:
                s = True
            else:
                s = False

            v = {"shutdown": s}
            self.write(json.dumps(v))
        except:
            self.set_status(500)
            return self.finish()

    def put(self):
        try:
            d = {}
            d[KEY_SUB_TYPE] = SUB_TYPE_KEYBOARD
            d[KEY_ACTION] = pygame.KEYDOWN
            d[KEY_KEYBOARD_KEY] = pygame.K_END
            event = pygame.event.Event(USER_EVENT_TYPE, **d)
            pygame.event.post(event)
            d[KEY_ACTION] = pygame.KEYUP
            event = pygame.event.Event(USER_EVENT_TYPE, **d)
            pygame.event.post(event)
        except:
            self.set_status(500)
            return self.finish()

    def delete(self):
        try:
            self.peppy.event_dispatcher.poweroff_flag = 0
        except:
            self.set_status(500)
            return self.finish()
