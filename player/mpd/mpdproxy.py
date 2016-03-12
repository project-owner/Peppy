# Copyright 2016 Peppy Player peppy.player@gmail.com
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

import subprocess
import os

MPC = "mpc "
GET_VOLUME = "volume"
SET_VOLUME_1 = "volume "
SET_VOLUME_2 = "setvol "
RESUME = "play"
PLAY = "play "
PAUSE = "pause"
STOP = "stop"
MUTE_1 = "volume 0"
MUTE_2 = "setvol 0"
CLEAR = "clear"
ADD = "add "
STATUS = "status"
IDLE = "idle"
IDLELOOP = "idleloop"
PLAYER = "player"
CURRENT = "current"
CURRENT_SONG = "currentsong"

class MpdProxy(object):
    """ This class serves as a proxy object for MPD process. 
    Linux version of the MPC starts MPD if it's not running. It knows how to do that.
    Windows version doesn't do that. So this class is for Windows platform.
    """    
    def __init__(self, linux, folder, command):
        """ Initializer
        :param linux: flag defining platform True - Linux, False - windows
        :param folder: folder where MPD process is located
        :param command: command which starts MPD process
        """
        self.linux = linux       
        self.folder = folder
        self.command = command
    
    def start(self):
        """ Start MPD process """
        
        current_folder = os.getcwd()
        os.chdir(self.folder)
        self.music_server = subprocess.Popen(self.command, shell=True)
        os.chdir(current_folder)

    def stop(self):
        """ Stop MPD process """
        
        if not self.linux:
            subprocess.Popen("taskkill /F /T /PID {pid}".format(pid=self.music_server.pid))
