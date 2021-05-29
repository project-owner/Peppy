# Copyright 2020-2021 Peppy Player peppy.player@gmail.com
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

from util.config import VOLUME_CONTROL, VOLUME_CONTROL_TYPE, PLAYER_SETTINGS, VOLUME, \
    VOLUME_CONTROL_TYPE_PLAYER, VOLUME_CONTROL_TYPE_AMIXER, VOLUME_CONTROL_TYPE_HARDWARE, \
    CURRENT, MODE, AIRPLAY
from util.amixerutil import AmixerUtil

class VolumeControl(object):
    """ Volume Control class """

    def __init__(self, util):
        """ Initializer

        :param util: utility object
        """
        self.config = util.config
        self.VOLUME_CONTROL_TYPE = self.config[VOLUME_CONTROL][VOLUME_CONTROL_TYPE]
        self.current_volume_level = self.config[PLAYER_SETTINGS][VOLUME]
        self.amixer_util = AmixerUtil(util)
        self.volume_controller = None

    def set_player(self, player):
        """ Set player object

        :param player: player object
        """
        self.player = player
        if self.VOLUME_CONTROL_TYPE == VOLUME_CONTROL_TYPE_PLAYER:
            self.volume_controller = player
        elif self.VOLUME_CONTROL_TYPE == VOLUME_CONTROL_TYPE_AMIXER:
            self.volume_controller = self.amixer_util
            if player:
                player.set_volume(100)
        elif self.VOLUME_CONTROL_TYPE == VOLUME_CONTROL_TYPE_HARDWARE:
            self.amixer_util.set_volume(100)
            if player:
                player.set_volume(100)

    def set_volume(self, level):
        """ Set volume level 
        
        :param level: volume level 0-100
        """
        if self.config[CURRENT][MODE] == AIRPLAY:
            self.player.set_volume(level)
        else:
            if self.VOLUME_CONTROL_TYPE != VOLUME_CONTROL_TYPE_HARDWARE:
                self.volume_controller.set_volume(level)
