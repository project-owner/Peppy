# Copyright 2019 Peppy Player peppy.player@gmail.com
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

from player.client.baseplayer import BasePlayer
from player.client.shairportpipe import ShairportPipeConnector
from player.client.shairportdbus import ShairportDbusConnector

class Shairport(BasePlayer):
    """ This class provides shairport-sync client functionality. 
        It reads metadata from the named pipe and issues commands using D-bus
    """

    def __init__(self):
        """ Initializer """

        BasePlayer.__init__(self);
        self.proxy = None
        self.muted = False
        self.file_playback = False
        self.current_title = None
        self.UTF8 = "UTF-8"
        self.current_track_time = None
        self.current_track_length = None
        self.connector_pipe = None
        self.connector_dbus = None

    def set_proxy(self, proxy_process, proxy=None):
        """ Set proxy process.

        :param proxy: reference to the proxy process
        """
        self.proxy = proxy

    def start_client(self):
        """ This method starts metadata reader thread """

        self.connector_pipe = ShairportPipeConnector(self.util, self.notify_player_listeners)
        self.connector_pipe.start_metadata_reader()
        self.connector_dbus = ShairportDbusConnector(self.util, self.notify_player_listeners)

    def next(self):
        """ Next track """

        self.connector_dbus.next()

    def previous(self):
        """ Previous track """

        self.connector_dbus.previous()

    def get_volume(self):
        """  Get Volume """
        
        pass
        
    def set_volume(self, level):
        """ Set volume level
        
        :param level: new volume level in range 0-100
        """
        self.connector_pipe.enable_volume_callback = False
        self.connector_dbus.set_volume(int(level))
    
    def mute(self):
        """ Mute """

        self.connector_dbus.mute()
        
    def play(self):
        """ Play """

        self.connector_dbus.play()
    
    def pause(self):
        """ Pause """
        
        self.connector_dbus.pause()
    
    def play_pause(self, pause_flag=None):
        """ Play/pause """

        self.connector_dbus.play_pause(pause_flag)
    
    def stop(self, source=None):
        """ Stop playback """
        
        self.connector_dbus.pause()

    def shutdown(self):
        """ Shutdown the player """
        
        self.playing = False
        self.connector_pipe.stop_metadata_reader()

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
