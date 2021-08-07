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

INCREASE_DECREASE_STEP = 5

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
        self.volume_listeners = []

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

    def increase_volume(self):
        """ Increase volume level """

        volume = int(self.config[PLAYER_SETTINGS][VOLUME])
        volume += INCREASE_DECREASE_STEP
        if volume > 100:
            volume = 100
        self.config[PLAYER_SETTINGS][VOLUME] = volume
        self.set_volume(volume)
        self.notify_volume_listeners(volume)

    def decrease_volume(self):
        """ Decrease volume level """

        volume = int(self.config[PLAYER_SETTINGS][VOLUME])
        volume -= INCREASE_DECREASE_STEP
        if volume < 0:
            volume = 0
        self.config[PLAYER_SETTINGS][VOLUME] = volume
        self.set_volume(volume)
        self.notify_volume_listeners(volume)

    def add_volume_listener(self, listener):
        """ Add volume listener
        
        :param listener: event listener
        """
        if listener not in self.volume_listeners:
            self.volume_listeners.append(listener)
            
    def notify_volume_listeners(self, volume):
        """ Notify volume listeners """
        
        for listener in self.volume_listeners:
            listener(volume)
