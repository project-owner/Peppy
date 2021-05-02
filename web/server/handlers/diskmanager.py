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

PROPETY_NAME = "name"
PROPERTY_DEVICE_NAME = "device"
PROPERTY_MOUNT_POINT = "mount.point"
PROPERTY_MOUNTED = "mounted"

class DiskManager(RequestHandler):
    def initialize(self, peppy):
        self.util = peppy.util
        self.config = peppy.util.config
        if self.config[LINUX_PLATFORM]:
            from util.diskmanager import DiskManager
            self.disk_manager = DiskManager(peppy)

    def get(self, command):
        if not self.config[LINUX_PLATFORM]:
            d = json.dumps(None)
            self.write(d)
            return

        if command == "disks":
            disks = self.disk_manager.get_usb_disks()
            d = json.dumps(disks)
            logging.debug(d)
            self.write(d)
            return

    def post(self, command):
        if command == "mount":
            disk = {
                PROPETY_NAME: self.get_argument("name"),
                PROPERTY_DEVICE_NAME: self.get_argument("device"),
                PROPERTY_MOUNT_POINT: self.get_argument("mount.point"),
                PROPERTY_MOUNTED: False
            }
            success = self.disk_manager.mount(disk)
            if success:
                logging.debug(f"Mounted disk: {disk}")
            else:
                self.set_status(500)
                return self.finish()     
        elif command == "unmount":
            disk = {
                PROPERTY_DEVICE_NAME: self.get_argument("device")
            }
            success = self.disk_manager.unmount(disk)
            if success:
                logging.debug(f"Unmounted disk: {disk}")
            else:
                self.set_status(500)
                return self.finish()
        elif command == "poweroff":
            disk = {
                PROPERTY_DEVICE_NAME: self.get_argument("device")
            }
            success = self.disk_manager.poweroff(disk)
            if success:
                logging.debug(f"Poweroff disk: {disk}")
            else:
                self.set_status(500)
                return self.finish()
