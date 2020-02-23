# Copyright 2016-2018 Peppy Player peppy.player@gmail.com
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

import sys

from ui.factory import Factory
from ui.menu.menu import Menu
from player.proxy import VLC_NAME, MPV_NAME
from util.util import NUMBERS
from util.cdutil import CdUtil
from util.keys import LINUX_PLATFORM, V_ALIGN_TOP
from util.config import USAGE, USE_VOICE_ASSISTANT, HOME_MENU, RADIO, AUDIO_FILES, CURRENT, MODE, NAME, \
    AUDIOBOOKS, STREAM, CD_PLAYER, PODCASTS, AIRPLAY, AUDIO, PLAYER_NAME, SPOTIFY_CONNECT, COLLECTION

class HomeMenu(Menu):
    """ Home Menu class. Extends base Menu class """

    def __init__(self, util, bgr=None, bounding_box=None, font_size=None):
        """ Initializer

        :param util: utility object
        :param bgr: menu background
        :param bounding_box: bounding box
        """
        self.util = util
        self.factory = Factory(util)
        self.config = util.config
        m = self.factory.create_home_menu_button
        Menu.__init__(self, util, bgr, bounding_box, None, None,
                      create_item_method=m, font_size=font_size)
        self.cdutil = CdUtil(util)
        self.set_modes()

    def set_modes(self):
        items = []
        disabled_items = []
        player = self.config[AUDIO][PLAYER_NAME]

        if self.config[HOME_MENU][RADIO]:
            items.append(RADIO)
            if not self.util.is_radio_enabled() or not self.util.connected_to_internet:
                disabled_items.append(RADIO)

        if self.config[HOME_MENU][AUDIO_FILES]:
            items.append(AUDIO_FILES)

        if self.config[HOME_MENU][AUDIOBOOKS]:
            items.append(AUDIOBOOKS)
            if not self.util.is_audiobooks_enabled() or not self.util.connected_to_internet:
                disabled_items.append(AUDIOBOOKS)

        if self.config[HOME_MENU][STREAM]:
            items.append(STREAM)
            if not self.util.connected_to_internet:
                disabled_items.append(STREAM)

        if self.config[HOME_MENU][CD_PLAYER]:
            cd_drives_info = self.cdutil.get_cd_drives_info()
            if len(cd_drives_info) == 0 or player == MPV_NAME:
                disabled_items.append(CD_PLAYER)
            items.append(CD_PLAYER)

        if self.config[HOME_MENU][PODCASTS]:
            podcasts_util = self.util.get_podcasts_util()
            podcasts = podcasts_util.get_podcasts_links()
            downloads = podcasts_util.are_there_any_downloads()
            connected = self.util.connected_to_internet
            valid_players = [VLC_NAME, MPV_NAME]
            if (connected and len(podcasts) == 0 and not downloads) or (not connected and not downloads) or player not in valid_players:
                disabled_items.append(PODCASTS)
            items.append(PODCASTS)

        if self.config[HOME_MENU][AIRPLAY]:
            items.append(AIRPLAY)
            if not self.util.config[LINUX_PLATFORM]:
                disabled_items.append(AIRPLAY)

        if self.config[HOME_MENU][SPOTIFY_CONNECT]:
            items.append(SPOTIFY_CONNECT)
            if not self.util.config[LINUX_PLATFORM]:
                disabled_items.append(SPOTIFY_CONNECT)

        if self.config[HOME_MENU][COLLECTION]:
            items.append(COLLECTION)
            db_util = self.util.get_db_util()
            if db_util.conn == None:
                disabled_items.append(COLLECTION)

        l = self.get_layout(items)
        bounding_box = l.get_next_constraints()
        self.modes = self.util.load_menu(
            items, NAME, disabled_items, V_ALIGN_TOP, bb=bounding_box, scale=0.5)
        va_commands = self.util.get_voice_commands()

        if self.config[USAGE][USE_VOICE_ASSISTANT]:
            self.add_voice_command(RADIO, ["VA_RADIO", "VA_GO_RADIO"], va_commands)
            self.add_voice_command(AUDIO_FILES, ["VA_FILES", "VA_GO_FILES"], va_commands)
            self.add_voice_command(AUDIOBOOKS, ["VA_AUDIOBOOKS", "VA_BOOKS", "VA_GO_BOOKS"], va_commands)
            self.add_voice_command(STREAM, ["VA_STREAM", "VA_GO_STREAM"], va_commands)
            self.add_voice_command(CD_PLAYER, ["VA_CD_PLAYER"], va_commands)
            self.add_voice_command(PODCASTS, ["VA_PODCAST", "VA_PODCASTS"], va_commands)

        if not items:
            return

        if not self.config[CURRENT][MODE]:
            for i in items:
                if i not in disabled_items:
                    mode = i
                    break
        else:
            mode = self.config[CURRENT][MODE]

        self.set_items(self.modes, 0, self.change_mode, False)
        self.current_mode = self.modes[mode.lower()]
        self.item_selected(self.current_mode)

    def add_voice_command(self, name, commands, va_commands):
        """ Add voice command

        :param name: item name
        :param commands: item commands
        :param va_commands: voice commands
        """
        if not self.config[HOME_MENU][name]:
            return
        c = []
        for m in commands:
            c.append(va_commands[m].strip())
        self.modes[name].voice_commands = c

    def change_mode(self, state):
        """ Change mode event listener

        :param state: button state
        """
        if not self.visible:
            return
        state.previous_mode = self.current_mode.name
        self.current_mode = state
        self.config[CURRENT][MODE] = state.name
        self.notify_listeners(state)
