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

import os
import logging

from pyudev import Context, Monitor, MonitorObserver
from subprocess import check_output, Popen, PIPE, CalledProcessError
from util.config import DISK_MOUNT, MOUNT_POINT, MOUNT_READ_ONLY, MOUNT_OPTIONS

UTF8 = "utf-8"
EOL = "\n"
SPACE = " "
SPACE_CODE = "\\x20"
BASE_NAME = "Disk."
PROPERTY_NAME = "name"
PROPERTY_UUID = "uuid"
PROPERTY_DEVICE_NAME = "device"
PROPERTY_VENDOR = "vendor"
PROPERTY_MODEL = "model"
PROPERTY_FILESYSTEM_TYPE = "filesystem"
PROPERTY_MOUNT_POINT = "mount.point"
PROPERTY_MOUNTED = "mounted"

class DiskManager(object):
    """ Disk manager utility class """

    def __init__(self, peppy):
        """ Initializer. 
        
        :param peppy: main player class
        """
        self.peppy = peppy
        self.context = Context()
        config = peppy.util.config
        self.read_only = config[DISK_MOUNT][MOUNT_READ_ONLY]
        self.mount_point_base = config[DISK_MOUNT][MOUNT_POINT].strip()
        self.mount_options = config[DISK_MOUNT][MOUNT_OPTIONS].strip().replace(" ", "")
        if not self.mount_point_base.endswith(os.sep):
            self.mount_point_base += os.sep    
        self.disk_index = 0
        self.observer = None

    def get_mount_point(self, device_name):
        """ Get the device mount point (if any)

        :param device_name: the device name e.g. /dev/sda1

        :return: the mount point or None
        """
        try:
            command = f"findmnt -n -S {device_name} -o TARGET"
            return check_output(command.split()).decode(UTF8).rstrip("\n")
        except CalledProcessError as e:
            logging.debug(e)
            return None

    def get_usb_disks(self):
        """ Get the list of dictionaries representing each connected disk

        :return: list of connected disks with such properties as label, device name etc.
        """
        disks = []
        for device in self.context.list_devices(subsystem='block', DEVTYPE='partition'):
            if device.get('ID_BUS') and device.get('ID_BUS') == 'usb':
                props = self.get_device_properties(device)
                if props:
                    disks.append(props)

        return disks

    def get_device_properties(self, device):
        """ Get only required properties from the device object

        :param device: the device object

        :return: the dictionary with required properties
        """
        if not device:
            return None

        props = {}

        if device.get('ID_FS_LABEL_ENC'):
            props[PROPERTY_NAME] = self.clean_string(device.get('ID_FS_LABEL_ENC'))
        else:
            self.disk_index += 1
            props[PROPERTY_NAME] = BASE_NAME + str(self.disk_index)

        props[PROPERTY_UUID] = self.clean_string(device.get('ID_FS_UUID_ENC'))
        props[PROPERTY_DEVICE_NAME] = device.get('DEVNAME')
        props[PROPERTY_VENDOR] = device.get('ID_VENDOR')
        props[PROPERTY_MODEL] = self.clean_string(device.get('ID_MODEL_ENC'))
        props[PROPERTY_FILESYSTEM_TYPE] = device.get('ID_FS_TYPE')

        mount_point = self.get_mount_point(props[PROPERTY_DEVICE_NAME])

        if mount_point != None:
            props[PROPERTY_MOUNT_POINT] = self.get_mount_point(props[PROPERTY_DEVICE_NAME])
            props[PROPERTY_MOUNTED] = True
        else:
            props[PROPERTY_MOUNT_POINT] = ""
            props[PROPERTY_MOUNTED] = False

        return props

    def clean_string(self, s):
        """ Clean input string - replace space code by space and trim

        :param s: the input string

        :return: the processed string
        """
        return s.replace(SPACE_CODE, SPACE).strip()

    def mount(self, device_properties):
        """ Mount device

        :param device_properties: the dictionary of the properties of the device to mount

        :return: True - disk mount was successful, False - otherwise
        """
        device_name = device_properties[PROPERTY_DEVICE_NAME]
        existing_mount_point = device_properties[PROPERTY_MOUNT_POINT]
        label = device_properties[PROPERTY_NAME]
        mounted = device_properties[PROPERTY_MOUNTED]

        if mounted:
            logging.debug(f"Device {device_name} mounted already to {existing_mount_point}")
            return True

        mount_point = self.mount_point_base + label

        if os.path.ismount(mount_point):
            logging.debug(f"The mount point {mount_point} is in use already")
            return False

        if os.path.exists(mount_point):
            logging.debug(f"The mount point {mount_point} exists")
        else:
            try:
                os.makedirs(mount_point)
            except Exception as e:
                logging.debug(e)
                return False

        if self.read_only:
            command = "sudo mount -o ro".split()
        else:
            command = "sudo mount".split()

        if self.mount_options:
            command.append("-o")
            command.append(self.mount_options)

        command.append(device_name);
        command.append(mount_point);

        p = Popen(command, stdout=PIPE, stderr=PIPE)
        _, error = p.communicate()
        if p.returncode != 0:
            logging.debug(f"Mount failed with error: {error.decode(UTF8).rstrip(EOL)}")
            logging.debug(f"Failed mount command: {command}")
            return False
        else:
            logging.debug(f"Successfully mounted {device_name} to {mount_point}")
            return True

    def unmount(self, device_properties):
        """ Unmount device

        :param device_properties: the dictionary of the properties of the device to unmount

        :return: True - disk unmount was successful, False - otherwise
        """
        device_name = device_properties[PROPERTY_DEVICE_NAME]
        p = Popen(["sudo", "umount", device_name], stdout=PIPE, stderr=PIPE)
        _, error = p.communicate()
        if p.returncode != 0:
            logging.debug(f"Unmount failed with error: {error.decode(UTF8).rstrip(EOL)}")
            return False
        else:
            logging.debug(f"Successfully unmounted {device_name}")
            return True

    def poweroff(self, device_properties):
        """ Poweroff provided device. 
        If device is busy switch off player, go to Home, umnount and poweroff

        :param device_properties: the dictionary of the properties of the device to poweroff

        :return: True - disk poweroff was successful, False - otherwise
        """
        device_name = device_properties[PROPERTY_DEVICE_NAME]
        mounted = self.get_mount_point(device_name)
        if mounted:
            unmounted = self.unmount(device_properties)    
            if not unmounted:
                self.peppy.player.stop()
                self.peppy.go_home(None)
                self.unmount(device_properties)
        try:
            p = Popen(["sudo", "udisksctl", "power-off", "-b", device_name], stdout=PIPE, stderr=PIPE)
            _, error = p.communicate()
            if p.returncode != 0:
                logging.debug(f"Poweroff failed with error: {error.decode(UTF8).rstrip(EOL)}")
                return False
            else:
                logging.debug(f"Poweroff successful for device {device_name}")
                return True
        except Exception as e:
            logging.debug(e)  

    def mount_all_usb_disks(self):
        """ Mount all USB disks found in the system """

        disks = self.get_usb_disks()
        for d in disks:
            self.mount(d)

    def unmount_all_usb_disks(self):
        """ Unmount all USB disks found in the system """

        disks = self.get_usb_disks()
        for d in disks:
            self.unmount(d)

    def poweroff_all_usb_disks(self):
        """ Poweroff all USB disks found in the system """

        disks = self.get_usb_disks()
        for d in disks:
            self.poweroff(d)

    def usb_event_handler(self, device):
        """ Handle USB plug/unplug events

        :param device: the plugged/unplugged USB device 
        """
        if device and device.get('ID_BUS') and device.get('ID_BUS') == 'usb':
            device_properties = self.get_device_properties(device)
            if device.action == "add":
                self.mount(device_properties)
            elif device.action == "remove":
                unmounted = self.unmount(device_properties)    
                if not unmounted:
                    self.peppy.player.stop()
                    title_screen_name = self.peppy.get_title_screen_name()
                    self.peppy.stop_player_timer_thread(title_screen_name)
                    if self.peppy.is_player_screen():
                        self.peppy.go_home(None)
                        self.peppy.web_server.redraw_web_ui()
                    self.unmount(device_properties)

    def start_observer(self):
        """ Start plug/unplug event observer """

        monitor = Monitor.from_netlink(self.context)
        monitor.filter_by(subsystem="block", device_type="partition")
        self.observer = MonitorObserver(monitor, callback=self.usb_event_handler)
        self.observer.start()
        logging.debug("Started USB drive plug/unplug observer")
