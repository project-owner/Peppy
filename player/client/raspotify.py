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

from player.client.baseplayer import BasePlayer

class Raspotify(BasePlayer):
    """ This class provides raspotify client functionality. """

    def __init__(self):
        """ Initializer """

        BasePlayer.__init__(self);
        self.proxy = None

    def set_proxy(self, proxy_process, proxy=None):
        """ Set proxy process.

        :param proxy: reference to the proxy process
        """
        self.proxy = proxy

    def start_client(self):
        """ There is no separate spotify connect client. """
        
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
