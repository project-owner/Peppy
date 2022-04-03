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
from util.networkutil import NetworkUtil

COMMAND_CONNECT = "connect"
COMMAND_DISCONNECT = "disconnect"
NETWORK = "network"
PASSWORD = "password"

class WiFiHandler(RequestHandler):
    def initialize(self, peppy):
        self.config = peppy.util.config
        self.peppy = peppy
        self.network_util = NetworkUtil(peppy.util, peppy.check_internet_connectivity)

    def get(self):
        try:
            i = self.network_util.get_wifi_networks()
            self.write(json.dumps(i))
        except:
            self.set_status(500)
            return self.finish()

    def post(self, command):
        try:
            if command == COMMAND_CONNECT:
                d = json.loads(self.request.body)
                self.network_util.connect_wifi(d[NETWORK], d[PASSWORD])
            elif command == COMMAND_DISCONNECT:
                self.network_util.disconnect_wifi()
        except:
            self.set_status(500)
            return self.finish()
