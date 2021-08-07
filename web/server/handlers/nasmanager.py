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

import logging
import json

from tornado.web import RequestHandler
from util.config import LINUX_PLATFORM
from util.keys import KEY_NAS

PROPETY_NAME = "name"
PROPERTY_DEVICE_NAME = "device"
PROPERTY_MOUNT_POINT = "mount.point"
PROPERTY_MOUNTED = "mounted"

class NasManager(RequestHandler):
    def initialize(self, peppy, config_class):
        self.util = peppy.util
        self.config = peppy.util.config
        self.config_class = config_class

        if self.config[LINUX_PLATFORM]:
            from util.nasmanager import NasManager
            self.nas_manager = NasManager(peppy)

    def get(self, command):
        if not self.config[LINUX_PLATFORM]:
            d = json.dumps(None)
            self.write(d)
            return

        if command == "nases":
            nases = self.nas_manager.get_nases()
            d = json.dumps(nases)
            self.write(d)
            return

    def put(self, command):
        if command != "save":
            d = json.dumps(None)
            self.write(d)
            return

        try:
            self.config[KEY_NAS] = json.loads(self.request.body)
            self.config_class.save_nas_config()
        except Exception as e:
            logging.debug(e)
            self.set_status(500)
            self.finish(json.dumps({ "message": "Cannot save NAS file"}))

    def post(self, command):
        nas = json.loads(self.request.body)
        nas_name = nas["name"]
        if command == "mount":
            success = self.nas_manager.mount(nas)
            if success:
                logging.debug(f"Mounted NAS: {nas_name}")
            else:
                self.set_status(500)
                return self.finish()     
        elif command == "unmount":
            success = self.nas_manager.unmount(nas)
            if success:
                logging.debug(f"Unmounted NAS: {nas_name}")
            else:
                self.set_status(500)
                return self.finish()
