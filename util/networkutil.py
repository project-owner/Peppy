# Copyright 2019-2023 Peppy Player peppy.player@gmail.com
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

import time

from util.config import BLUETOOTH
from util.wifiutil import WiFiUtil, CONNECTED, ETHERNET_IP, WIFI_NETWORK, WIFI_IP
from util.config import LINUX_PLATFORM

class NetworkUtil(object):
    """ Network Utility """

    def __init__(self, util, check_internet_connectivity):
        """ Initializer

        :param util: utility object
        :param listeners: listeners
        """
        self.util = util
        self.check_internet_connectivity = check_internet_connectivity

        self.config = util.config
        self.linux = self.config[LINUX_PLATFORM]

        self.wifi_util = WiFiUtil(util)
        self.bluetooth_util = self.util.get_bluetooth_util()

    def get_network_info(self):
        """ Get network information

        :return: dictionary with network info
        """
        info = self.wifi_util.get_network()
        info[CONNECTED] = self.check_internet_connectivity()

        info[BLUETOOTH] = ""
        d = self.bluetooth_util.get_connected_device()
        if d:
            info[BLUETOOTH] = d["name"]

        keys = [CONNECTED, ETHERNET_IP, WIFI_NETWORK, WIFI_IP, BLUETOOTH]
        for key in keys:
            try:
                info[key] = info[key]
            except:
                info[key] = ""

        return info

    def get_wifi_networks(self):
        """ Get Wi-Fi networks

        :return: wi-fi networks
        """
        return self.wifi_util.get_wifi_networks()

    def connect_wifi(self, network, password):
        """ Connect to Wi-Fi network

        :param state: button state
        """
        if self.linux:
            self.connect_wifi_linux(network, password)
        else:
            self.connect_wifi_windows(network)

    def connect_wifi_windows(self, network):
        """ Connect to Wi-Fi on Windows """

        self.wifi_util.connect_wifi_windows(network, network)
        self.wait_for_connection(4)

    def connect_wifi_linux(self, network, password):
        """" Connect to Wi-Fi on Linux

        :param state: button state
        """
        if not network or not password:
            return

        encrypted_pswd = self.wifi_util.encrypt_psk(network, password)

        if not encrypted_pswd:
            return

        self.wifi_util.create_wpa_file(network, encrypted_pswd)
        self.wait_for_connection(10)

    def wait_for_connection(self, attempts):
        """ Wait for the Internet connection
        
        :param attempts: the number of attempts with 1 sec interval
        """
        attempt = 0
        while not self.check_internet_connectivity() and attempt < attempts:
            time.sleep(1)
            attempt += 1

    def disconnect_wifi(self):
        """ Disconnect from Wi-Fi network """

        self.wifi_util.disconnect_wifi()

    def remove_bluetooth_devices(self, state):
        """ Remove bluetooth devices

        :param state: button state
        """
        self.bluetooth_util.remove_devices()
