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

import logging

from subprocess import Popen
from player.baseplayer import BasePlayer

class Bluetoothsink(BasePlayer):
    """ This class provides Bluetooth Sink client functionality """

    def __init__(self):
        """ Initializer """

        BasePlayer.__init__(self);
        self.proxy = None
        self.connector_dbus = None

    def set_proxy(self, proxy_process, proxy=None):
        """ Set proxy process.

        :param proxy: reference to the proxy process
        """
        self.proxy = proxy

    def start_client(self):
        """ This method starts client """

        try:
            Popen("sudo systemctl start bt-agent-a2dp.service".split(), shell=False)
            logging.debug("Started bt-agent-a2dp.service")
        except Exception as e:
            logging.debug(e)

    def stop_client(self):
        """ Stop threads """

        try:
            Popen("sudo systemctl stop bt-agent-a2dp.service".split(), shell=False)
            logging.debug("Started bt-agent-a2dp.service")
        except Exception as e:
            logging.debug(e)

    def next(self):
        """ Next track """

        pass

    def previous(self):
        """ Previous track """

        pass

    def get_volume(self):
        """  Get Volume """
        
        pass
        
    def set_volume(self, level):
        """ Set volume level
        
        :param level: new volume level in range 0-100
        """
        pass
    
    def mute(self):
        """ Mute """

        pass
        
    def play(self):
        """ Play """

        pass
    
    def pause(self):
        """ Pause """
        
        pass
    
    def play_pause(self, pause_flag=None):
        """ Play/pause """

        pass
    
    def stop(self, source=None):
        """ Stop playback """
        
        pass

    def shutdown(self):
        """ Shutdown the player """
        
        pass

    def get_current_track_time(self):
        """ Start getting current track time command
        
        :return: track time in seconds
        """
        pass
    
    def seek(self, time):
        """ Set current track time
        
        :param time: new track time in seconds
        """
        pass

    def get_current_playlist(self):
        """  Return current playlist
        
        :return: current playlist
        """
        pass
