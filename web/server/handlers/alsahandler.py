# Copyright 2023 Peppy Player peppy.player@gmail.com
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

from tornado.web import RequestHandler
from util.alsautil import AlsaUtil

class AlsaHandler(RequestHandler):
    def initialize(self):
        self.alsa_util = AlsaUtil()

    def get(self):
        devices = self.alsa_util.get_alsa_cards()
        d = json.dumps(devices)
        self.write(d)

    def put(self):
        devices = json.loads(self.request.body.decode("utf-8"))
        device_id = ""

        for device in devices:
            if device[2]:
                device_id = device[0]
                break    

        if device_id:
            logging.debug(f"Set new default ALSA device {device_id}")
            self.alsa_util.set_default_card(device_id)
