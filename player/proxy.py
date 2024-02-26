# Copyright 2016-2024 Peppy Player peppy.player@gmail.com
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

from subprocess import Popen, PIPE

MPD_NAME = "mpd"
VLC_NAME = "vlc"
SHAIRPORT_SYNC_NAME = "shairport-sync"
SHAIRPORT_CLIENT_NAME = "shairport"
RASPOTIFY_NAME = "raspotify"
BLUETOOTH_SINK_NAME = "bluetooth-sink"
BLUETOOTH_CLIENT_NAME = "bluetoothsink"
MPV_NAME = "mpv"

class Proxy(object):
    """ This class serves as a proxy object for audio players """
        
    def __init__(self, client_name, linux, folder, start_command, stop_command, volume, stream_server_parameters):
        """ Initializer
        
        :param client_name: player class name
        :param linux: flag defining platform True - Linux, False - windows
        :param folder: folder where the music server program is located
        :param start_command: command which starts the process
        :param stop_command: command which stops the process
        :param volume: volume level
        :param stream_server_parameters: streaming server parameters
        """
        self.client_name = client_name
        self.linux = linux       
        self.folder = folder
        self.start_command = start_command
        self.stop_command = stop_command
        self.volume = volume
        self.stream_server_parameters = stream_server_parameters
        self.proxy = None
    
    def start(self):
        """ Start server process """
        
        current_folder = os.getcwd()
        if self.folder:
            os.chdir(self.folder)
        
        names = [SHAIRPORT_CLIENT_NAME, RASPOTIFY_NAME, BLUETOOTH_CLIENT_NAME]

        if MPD_NAME in self.client_name or self.client_name in names:
            self.proxy = Popen(self.start_command, stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True)
        elif VLC_NAME in self.client_name:
            try:
                from vlc import Instance
                self.proxy = Instance(self.start_command)
            except Exception as e:
                logging.debug(e)
                self.proxy = None

        if self.folder:
            os.chdir(current_folder)
            
        return self.proxy

    def stop(self):
        """ Stop server process """

        if not self.stop_command:
            return

        Popen(self.stop_command, stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True)
