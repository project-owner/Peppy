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
from util.config import TIMER, SLEEP_TIME, WAKE_UP_TIME, SLEEP, POWEROFF, WAKE_UP
from ui.state import State

class TimerHandler(RequestHandler):
    def initialize(self, peppy):
        self.config = peppy.util.config
        self.peppy = peppy

    def get(self):
        try:
            v = self.config[TIMER]
            self.write(json.dumps(v))
        except:
            self.set_status(500)
            return self.finish()

    def post(self, command):
        commands = [SLEEP, POWEROFF, WAKE_UP]
        time_commands = [SLEEP_TIME, WAKE_UP_TIME]

        try:
            screen = self.peppy.screens[TIMER]
            state = State()

            if command in commands:
                state = State()

                if command == SLEEP:
                    state.event_origin = screen.sleep_menu.sleep_button
                elif command == POWEROFF:
                    state.event_origin = screen.sleep_menu.poweroff_button
                elif command == WAKE_UP:
                    state.event_origin = screen.wake_up_menu.button

                screen.handle_button(state)
                screen.update_web_observer()
            elif command in time_commands:
                t = json.loads(self.request.body)
                if screen != None:
                    if command == SLEEP_TIME:
                        screen.sleep_menu.clock.change_hours(int(t[SLEEP_TIME][:2]), int(t[SLEEP_TIME][2:]))
                        screen.sleep_menu.clock.change_minutes(int(t[SLEEP_TIME][2:]))
                    elif command == WAKE_UP_TIME:
                        screen.wake_up_menu.clock.change_hours(int(t[WAKE_UP_TIME][:2]), int(t[WAKE_UP_TIME][2:]))
                        screen.wake_up_menu.clock.change_minutes(int(t[WAKE_UP_TIME][2:]))
                    screen.update_web_observer()
                else:
                    if command == SLEEP_TIME:
                        self.config[TIMER][SLEEP_TIME] = t[SLEEP_TIME]
                    elif command == WAKE_UP_TIME:
                        self.config[TIMER][WAKE_UP_TIME] = t[WAKE_UP_TIME]
        except:
            self.set_status(500)
            return self.finish()
