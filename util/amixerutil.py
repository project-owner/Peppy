# Copyright 2020 Peppy Player peppy.player@gmail.com
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

from subprocess import Popen
from util.config import VOLUME_CONTROL, AMIXER_CONTROL, AMIXER_SCALE, LINUX_PLATFORM, \
    AMIXER_SCALE_LINEAR, AMIXER_SCALE_LOGARITHM

class AmixerUtil(object):
    """ ALSA amixer utility class """

    def __init__(self, util):
        """ Initializer

        :param util: utility object
        """
        self.config = util.config
        self.AMIXER_CONTROL = self.config[VOLUME_CONTROL][AMIXER_CONTROL]
        self.AMIXER_SCALE = self.config[VOLUME_CONTROL][AMIXER_SCALE]

    def set_volume(self, level):
        """ Set volume level 
        
        :param level: volume level 0-100
        """
        if self.AMIXER_SCALE == AMIXER_SCALE_LINEAR:
            command = "amixer sset {ctrl} {vol}% -M".format(ctrl=self.AMIXER_CONTROL, vol=level)
        elif self.AMIXER_SCALE == AMIXER_SCALE_LOGARITHM:
            command = "amixer sset {ctrl} {vol}%".format(ctrl=self.AMIXER_CONTROL, vol=level)
        
        try:
            Popen(command.split(), shell=False)
        except:
            pass
