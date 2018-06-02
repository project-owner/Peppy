# Copyright 2016-2017 Peppy Player peppy.player@gmail.com
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

from subprocess import Popen, PIPE

MPD = "mpd"
MPLAYER = "mplayer"
VLC = "vlc"

class Proxy(object):
    """ This class serves as a proxy object for audio players """
        
    def __init__(self, linux, folder, command, volume):
        """ Initializer
        
        :param linux: flag defining platform True - Linux, False - windows
        :param folder: folder where the music server program is located
        :param command: command which starts the process
        :param volume: volume level
        """
        self.linux = linux       
        self.folder = folder
        self.command = command
        self.volume = volume
        self.proxy = None
    
    def start(self):
        """ Start server process """
        
        if MPLAYER in self.command:
            self.command += " -volume " + str(self.volume)
        
        current_folder = os.getcwd()
        if self.folder:
            os.chdir(self.folder)
        
        if MPD in self.command or MPLAYER in self.command:    
            self.proxy = Popen(self.command, stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True, universal_newlines=True, bufsize=1)
        else: #VLC
            from  vlc import Instance
            self.proxy = Instance(self.command)
        if self.folder:
            os.chdir(current_folder)
            
        return self.proxy
