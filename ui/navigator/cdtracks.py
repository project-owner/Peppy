# Copyright 2016-2021 Peppy Player peppy.player@gmail.com
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

from ui.navigator.navigator import Navigator
from util.keys import GO_BACK, GO_LEFT_PAGE, GO_RIGHT_PAGE, KEY_HOME, KEY_BACK, KEY_EJECT, KEY_CD_PLAYERS, \
    KEY_PLAYER, KEY_BACK, KEY_REFRESH
from util.config import AUDIO, PLAYER_NAME
from player.proxy import VLC_NAME, MPD_NAME

class CdTracksNavigator(Navigator):
    """ CD tracks navigator """

    def __init__(self, util, bounding_box, listeners, connected_cd_drives):
        """ Initializer
        
        :param util: utility object
        :param bounding_box: bounding box
        :param listeners: buttons listeners
        :param connected_cd_drives: number of connected drives
        """
        config = util.config
        p = config[AUDIO][PLAYER_NAME]
        show_drives = connected_cd_drives > 1 and (p == VLC_NAME or p == MPD_NAME)
        items = []
        self.add_button(items, KEY_HOME, None, [listeners[KEY_HOME]])
        if show_drives:
            self.add_button(items, KEY_CD_PLAYERS, None, [listeners[KEY_CD_PLAYERS]])
        self.add_button(items, KEY_REFRESH, None, [listeners[KEY_REFRESH]])
        self.add_button(items, KEY_EJECT, None, [listeners[KEY_EJECT]])
        lsnrs = []
        lsnrs.append(listeners[GO_BACK])
        lsnrs.append(listeners[KEY_PLAYER])
        self.add_button(items, KEY_BACK, None, lsnrs)

        arrow_items = []
        self.add_button(arrow_items, None, None, [listeners[GO_LEFT_PAGE]])
        self.add_button(arrow_items, None, None, [listeners[GO_RIGHT_PAGE]])
        
        Navigator.__init__(self, util, bounding_box, "cd.tracks.navigator", items, arrow_items)
