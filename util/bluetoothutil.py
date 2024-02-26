# Copyright 2020-2024 Peppy Player peppy.player@gmail.com
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
import time
import pexpect
import subprocess
import signal
import logging
import codecs
import shutil

from ui.state import State
from util.config import COLORS, COLOR_DARK, USAGE, USE_HEADLESS
from util.keys import LINUX_PLATFORM, UTF8
from string import Template
from os.path import expanduser
from configparser import ConfigParser
from subprocess import Popen

MENU_ROWS_BLUETOOTH = 5
MENU_COLUMNS_BLUETOOTH = 1
PAGE_SIZE_BLUETOOTH = MENU_ROWS_BLUETOOTH * MENU_COLUMNS_BLUETOOTH

DELAY_PAIR = 4
DELAY_TRUST = 4
DELAY_CONNECT = 2
DELAY_REMOVE = 3

BLUEALSA_CONFIG_FILE = "/lib/systemd/system/bluealsa.service"
SINK_CONFIGURATION_PARAMETERS = " -p a2dp-sink"
SERVICE = "Service"
EXEC_START = "ExecStart"
TMP_FILE = os.path.join(os.getcwd(), "bluealsa.service")
MOVE_COMMAND_LINUX = "sudo mv " + TMP_FILE + " " + BLUEALSA_CONFIG_FILE
COMMAND_RELOAD_DAEMON = "sudo systemctl daemon-reload"
COMMAND_RESTART_BLUEALSA = "sudo systemctl restart bluealsa"

USER_HOME = expanduser("~")
ASOUNDRC_FILENAME = os.path.join(USER_HOME, ".asoundrc")
ASOUNDRC_EQUALIZER_FILENAME = os.path.join(USER_HOME, ".asoundrc-equal")
ASOUNDRC_EQUALIZER_PEPPYALSA_FILENAME = os.path.join(USER_HOME, ".asoundrc-equal-peppyalsa")
BLUETOOTH_ASOUNDRC_TEMPLATE = """pcm.!default {
  type plug
  slave.pcm plugequal;
}
ctl.!default {
  type hw card 0
}
ctl.equal {
  type equal;
}
pcm.plugequal {
  type equal;
  slave.pcm bt
}
pcm.equal {
  type plug;
  slave.pcm plugequal;
}
pcm.bt {
    type plug
    slave.pcm {
        type bluealsa
        device "$mac_address"
        profile "a2dp"
    }
}
"""

class BluetoothUtil:
    """ Python wrapper for bluetoothctl utility.
        Based on code: https://gist.github.com/castis/0b7a162995d0b465ba9c84728e60ec01
    """
    def __init__(self, util):
        """ Initializer

        :param util: utility object
        """
        self.util = util
        self.config = util.config
        self.scanning = False

        if self.config[LINUX_PLATFORM]:
            logging.debug("Starting bluetoothctl utility...")
            try:
                subprocess.check_output("rfkill unblock bluetooth", shell=True)
                self.process = pexpect.spawnu("bluetoothctl", echo=False)
                logging.debug("bluetoothctl utility started")
            except Exception as e:
                logging.debug(f"Cannot start bluetoothctl utility: {e}")
                self.process = None
        else:
            self.process = None

    def send(self, command, pause=0):
        """ Send command to the process

        :param command: command to send
        :pause: timeout after send

        :return: True - success, False - failed
        """
        if not self.process:
            return

        self.process.send(f"{command}\n")
        time.sleep(pause)
        if self.process.expect(["(\x1b\\[0;94m)\\[.+\\](\x1b\\[0m)", pexpect.EOF]):
            logging.debug(f"Command '{command}' failed")
            return False
        else:
            return True

    def get_output(self, *args, **kwargs):
        """Run a command in bluetoothctl prompt

        :return: list of command output lines.
        """
        result = self.send(*args, **kwargs)
        if result:
            return self.process.before.split("\r\n")
        else:
            return []

    def start_scan(self):
        """Start bluetooth scanning process."""

        if self.scanning:
            return

        self.send("scan on", 2)
        self.scanning = True
        
    def stop_scan(self):
        """Stop bluetooth scanning process."""

        if not self.scanning:
            return

        self.send("scan off", 1)
        self.scanning = False

    def is_named_device(self, device):
        """ Check that device has name

        :param device: device object

        :return: True - device has name, False - no name
        """
        if not device:
            return False
        
        if device["mac_address"].replace(":", "-") == device["name"]:
            return False
        else:
            return True

    def parse_device_info(self, info_string):
        """ Parse device string
        
        :param info_string: device info string

        :return: device dictionary with keys: mac_address, name
        """
        device = {}
        block_list = ["[\x1b[0;", "removed"]
        if not any(keyword in info_string for keyword in block_list):
            try:
                device_position = info_string.index("Device")
            except ValueError:
                pass
            else:
                if device_position > -1:
                    attribute_list = info_string[device_position:].split(" ", 2)
                    device = {
                        "mac_address": attribute_list[1],
                        "name": attribute_list[2],
                    }
        return device

    def get_available_devices(self):
        """ Get available devices
        
        :return: list of device dictionaries
        """
        available_devices = []
        out = self.get_output("devices")

        if not out:
            return available_devices

        for line in out:
            device = self.parse_device_info(line)
            if device and self.is_named_device(device):
                available_devices.append(device)

        if available_devices:
            available_devices = sorted(available_devices, key=lambda i: i["name"], reverse=False)
            for i, d in enumerate(available_devices):
                d["index"] = i

        return available_devices

    def get_paired_devices(self):
        """ Get paired devices.
        
        :return: list of dictionaries with keys: mac_address, name
        """
        paired_devices = []
        out = self.get_output("devices Paired")
        if not out:
            return paired_devices

        for line in out:
            device = self.parse_device_info(line)
            if device:
                paired_devices.append(device)

        return paired_devices

    def get_device_info(self, mac_address):
        """ Get device info by mac address.
        
        :param mac_address: device MAC address

        :retun: device info as a list of strings or empty string if info was not found
        """
        out = self.get_output(f"info {mac_address}")
        if out:
            return out
        else:
            return ""

    def is_device_available(self, mac_address):
        """ Check that device is available

        :param mac_address: device MAC address

        :return: True - device available, False - unavailable
        """
        if self.get_device_info(mac_address):
            return True
        else:
            return False

    def is_device_paired(self, mac_address):
        """ Check that device is paired

        :param mac_address: device MAC address

        :return: True - device paired, False - unpaired
        """
        return self.get_device_parameter(mac_address, "Paired:")

    def is_device_trusted(self, mac_address):
        """ Check that device trusted

        :param mac_address: device MAC address

        :return: True - device trusted, False - untrusted
        """
        return self.get_device_parameter(mac_address, "Trusted:")

    def is_device_connected(self, mac_address):
        """ Check that device connected

        :param mac_address: device MAC address

        :return: True - device connected, False - disconnected
        """
        return self.get_device_parameter(mac_address, "Connected:")

    def get_device_parameter(self, mac_address, param):
        """ Get parameter from device info

        :param mac_address: device MAC address
        :param param: parameter name

        :return: True - parameter value is 'yes', False - value is 'no'
        """
        lines = self.get_device_info(mac_address)

        if not lines:
            return False

        for line in lines:
            if "Device" in line and "not available" in line:
                return False

            if param in line:
                tokens = line.split(":")
                return len(tokens) == 2 and "yes" in tokens[1]

        return False

    def expect(self, mac_address, command, expected_list, error_message, delay=0):
        """ Exoect output from command

        :param mac_address: MAC address
        :param command: bluetoothctl command
        :param expected_list: list of expected output strings from command
        :param error_message: error message for exception
        :param delay: delay after commad in seconds

        :return: True - command successful, False - command unsuccessful
        """
        sent = self.send(f"{command} {mac_address}", delay)
        if not sent:
            return False

        try:
            result = self.process.expect(expected_list)
            if result == 1:
                return True
            else:
                return False
        except Exception as e:
            logging.debug(f"{error_message}: {e}")
            return False

    def pair(self, mac_address):
        """ Pair device by mac address
        
        :param mac_address: device MAC address

        :return: True - paired successfully, False - pairing failed
        """
        return self.expect(mac_address, "pair", ["Failed to pair", "Pairing successful", pexpect.EOF], 
                           "Exception while pairing", DELAY_PAIR)

    def trust(self, mac_address):
        """ Trust device by mac address
        
        :param mac_address: device MAC address

        :return: True - trusted successfully, False - trust failed
        """
        return self.expect(mac_address, "trust", ["Failed to trust", "trust succeeded", pexpect.EOF], 
                           "Exception while trusting", DELAY_TRUST)

    def connect(self, mac_address):
        """ Connect device by mac address
        
        :param mac_address: device MAC address

        :return: True - connected successfully, False - connection failed
        """
        return self.expect(mac_address, "connect", ["Failed to connect", "Connection successful", pexpect.EOF], 
                           "Exception while connecting", DELAY_CONNECT)

    def restore_asoundrc(self):
        """ Restore .asoundrc file """

        if self.config[USAGE][USE_HEADLESS]:
            src = ASOUNDRC_EQUALIZER_FILENAME
        else:
            src = ASOUNDRC_EQUALIZER_PEPPYALSA_FILENAME

        try:
            shutil.copyfile(src, ASOUNDRC_FILENAME)
        except Exception as e:
            logging.error(e)

    def remove(self, mac_address):
        """ Remove device by mac address
        
        :param mac_address: device MAC address

        :return: True - removed successfully, False - removal failed
        """
        sent = self.send(f"remove {mac_address}", DELAY_REMOVE)
        if not sent:
            return False

        return self.process.expect(["not available", "Device has been removed", pexpect.EOF]) == 1

    def remove_devices(self):
        """ Remove all paired devices """

        paired_devices = self.get_paired_devices()
        for d in paired_devices:
            self.remove(d["mac_address"])
        
    def connect_device(self, name=None, mac_address=None, remove_previous=True):
        """ Connect Bluetooth device

        :param name: device name
        :param mac_address: device MAC address
        :param remove_previous: True - remove all previously paired devices, False - don't remove

        :return: device name if connected, None if not connected
        """
        paired_devices = self.get_paired_devices()
        if paired_devices:
            logging.debug(f"Found {len(paired_devices)} paired devices")
        else:
            logging.debug("Not found paired devices")

        if not mac_address and not name:
            if not paired_devices:
                logging.debug("No data for Bluetooth device")
                return None
            else:
                d = paired_devices[0]
                mac_address = d["mac_address"]
                name = d["name"]

        if not self.is_device_available(mac_address):
            logging.debug(f"Bluetooth device {mac_address} is not available")
            return None
        else:
            logging.debug(f"Bluetooth device {mac_address} is available")

        if remove_previous and paired_devices:
            for d in paired_devices:
                m = d["mac_address"]
                self.remove(m)

        paired = trusted = connected = False

        if not self.is_device_paired(mac_address):
            logging.debug(f"Pairing device {mac_address}")
            paired = self.pair(mac_address)
        else:
            logging.debug(f"Device {mac_address} paired")
            paired = True

        if not self.is_device_trusted(mac_address):
            logging.debug(f"Trusting device {mac_address}")
            trusted = self.trust(mac_address)
        else:
            logging.debug(f"Device {mac_address} trusted")
            trusted = True

        if not self.is_device_connected(mac_address):
            logging.debug(f"Connecting device {mac_address}")
            connected = self.connect(mac_address)
        else:
            logging.debug(f"Device {mac_address} connected")
            connected = True    

        if paired and trusted and connected:
            logging.debug(f"Connected Bluetooth device {name}")
            return name
        else:
            logging.debug(f"Cannot connect Bluetooth device {name}")
            return None

    def get_connected_device(self):
        """ Get connected device (if any)

        :return: connected device object or None if no connected objects
        """
        paired_devices = self.get_paired_devices()
        
        if not paired_devices:
            return None

        for d in paired_devices:
            if self.is_device_connected(d["mac_address"]):
                return d

        return None

    def get_page_num(self, device, devices):
        """ Get page number for the provided device

        :param device: device object
        :param networks: all devices

        :return: page number for specified device
        """
        if not devices or not device:
            return None

        n = 1
        i = 0

        for index, d in enumerate(devices):
            if d["name"] == device["name"]:
                i = index + 1
                break

        n = int(i / PAGE_SIZE_BLUETOOTH)
        r = int(i % PAGE_SIZE_BLUETOOTH)
        if r > 0:
            n += 1

        return n

    def get_page(self, page, devices):
        """ Get page of devices for provided page number

        :param page: page number
        :param devices: list of all devices

        :return: page of devices
        """
        p = {}
        if len(devices) == 0:
            return p

        start_index = (page - 1) * PAGE_SIZE_BLUETOOTH
        end_index = start_index + PAGE_SIZE_BLUETOOTH

        for i, d in enumerate(devices):
            s = State()
            s.index = i
            s.name = d["name"]
            s.l_name = s.name
            s.mac_address = d["mac_address"]
            s.comparator_item = i
            s.bgr = self.config[COLORS][COLOR_DARK]
            s.show_bgr = True
            if i >= start_index and i < end_index:
                p[d["name"]] = s

        return p

    def stop(self):
        """ Stop utility. Not used """
        
        try:
            self.process.kill(signal.SIGINT)
            self.process.close() # close pty
            logging.debug("Stopped bluetoothctl utility")
            return True
        except Exception as e:
            logging.debug(f"Cannot stop bluetoothctl utility: {e}")
            return False

    def update_asoundrc(self, mac=""):
        """ Update .asoundrc file or create if doesn't exist

        :oaram mac: Bluetooth device MAC address
        """
        t = Template(BLUETOOTH_ASOUNDRC_TEMPLATE)
        s = t.substitute(mac_address=mac)

        logging.debug(s)

        with open(ASOUNDRC_FILENAME, "w") as f:
            f.write(s)

    def configure_bluealsa(self, add_sink=True):
        """ Configure bluealsa.service

        :param add_sink: True - add sink parameters, False, - remove sink parameters
        :return: True - file changed, False - file didn't change
        """
        if not os.path.exists(BLUEALSA_CONFIG_FILE):
            return False

        exec_start = ""

        try:
            bluealsa_config = self.load_bluealsa_config()
            exec_start = bluealsa_config.get(SERVICE, EXEC_START)
            if not exec_start:
                return False
        except Exception as e:
            logging.debug(f"Problem parsing bluealsa configuration file: {e}")

        if SINK_CONFIGURATION_PARAMETERS in exec_start and add_sink:
            return False
        elif SINK_CONFIGURATION_PARAMETERS in exec_start and not add_sink:
            # remove
            new_value = bluealsa_config.get(SERVICE, EXEC_START).replace(SINK_CONFIGURATION_PARAMETERS, "")
            bluealsa_config.set(SERVICE, EXEC_START, new_value)
            self.save_bluealsa_config(bluealsa_config)
            return True
        elif not SINK_CONFIGURATION_PARAMETERS in exec_start and add_sink:
            # add
            new_value = bluealsa_config.get(SERVICE, EXEC_START) + SINK_CONFIGURATION_PARAMETERS
            bluealsa_config.set(SERVICE, EXEC_START, new_value)
            self.save_bluealsa_config(bluealsa_config)
            return True
        elif not SINK_CONFIGURATION_PARAMETERS in exec_start and not add_sink:
            return False

    def load_bluealsa_config(self):
        """ Get Bluealsa configuration file

        :return: the content of the configuration file
        """
        logging.debug("Get bluealsa.service file")
        config_file = ConfigParser()
        try:
            config_file.optionxform = str
            config_file.read(BLUEALSA_CONFIG_FILE, encoding=UTF8)
        except Exception as e:
            logging.debug(f"Problem loading configuration file {BLUEALSA_CONFIG_FILE} {e}")

        return config_file

    def save_bluealsa_config(self, bluealsa_config):
        """ Save Bluealsa configuration file

        :param bluealsa_config: the file content
        """
        with codecs.open(TMP_FILE, 'w', UTF8) as file:
            bluealsa_config.write(file)

        try:
            if self.config[LINUX_PLATFORM]:
                Popen(MOVE_COMMAND_LINUX.split(), shell=False)
            else:
                shutil.move(TMP_FILE, BLUEALSA_CONFIG_FILE)
        except Exception as e:
            logging.debug(e)

        logging.debug("Saved Bluealsa Service config")

    def restart_bluealsa_service(self):
        """ Restart Bluealsa service """

        try:
            Popen(COMMAND_RELOAD_DAEMON.split(), shell=False)
            logging.debug(f"Executed command '{COMMAND_RELOAD_DAEMON}'")
        except Exception as e:
            logging.debug(e)

        try:
            Popen(COMMAND_RESTART_BLUEALSA.split(), shell=False)
            logging.debug(f"Executed command '{COMMAND_RESTART_BLUEALSA}'")
        except Exception as e:
            logging.debug(e)

    def connect_bluetooth_sink(self):
        """ Connect Bluetooth Sink """

        config_file_changed = self.configure_bluealsa(True)
        if config_file_changed:
            logging.debug("Configuration changed")
            self.restart_bluealsa_service()
        else:
            logging.debug("Configuration didn't change")

        self.send("discoverable on", 1)
        self.send("pairable on", 1)

        self.remove_devices()

    def disconnect_bluetooth_sink(self):
        """ Disconnect Bluetooth Sink """

        config_file_changed = self.configure_bluealsa(False)
        if config_file_changed:
            logging.debug("Configuration changed")
            self.restart_bluealsa_service()
        else:
            logging.debug("Configuration didn't change")

        self.send("discoverable off", 1)
        self.send("pairable off", 1)
