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

from subprocess import Popen, PIPE
import os

class Proxy(object):
    """ This class serves as a proxy object for music servers.
    The examples of configuration settings (folder names are specific for each user):
    
    mpd:
    linux:
    server.folder = /usr/bin
    server.command = mpd
    client.name = mpdsocket
    windows:
    server.folder = C:\mpd-0.17.4-win32\bin
    server.command = mpd mpd.conf
    client.name = mpdsocket
    
    mplayer:
    linux:
    server.folder = /usr/bin
    server.command = mplayer -af volnorm=2:0.75 -idle -slave -quiet -msglevel statusline=6 -msglevel global=6
    client.name = mplayer
    windows:
    server.folder = C:\\mplayer-svn-37551-2
    server.command = mplayer -af volnorm=2:0.75 -idle -slave -nofontconfig -quiet -msglevel statusline=6 -msglevel global=6
    client.name = mplayer
    """
        
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
                  
        if self.linux and "mpd" in self.command:
            return None    
        current_folder = os.getcwd()
        os.chdir(self.folder)
        if "mplayer" in self.command:
            self.command += " -volume " + str(self.volume)
        self.proxy = Popen(self.command, stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True, universal_newlines=True, bufsize=1)
        os.chdir(current_folder)
        return self.proxy
