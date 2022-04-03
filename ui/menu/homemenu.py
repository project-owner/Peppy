# Copyright 2016-2022 Peppy Player peppy.player@gmail.com
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

from ui.factory import Factory
from ui.menu.menu import Menu
from util.cdutil import CdUtil
from util.keys import V_ALIGN_TOP
from util.config import USAGE, USE_VOICE_ASSISTANT, HOME_MENU, RADIO, AUDIO_FILES, CURRENT, MODE, NAME, \
    AUDIOBOOKS, STREAM, CD_PLAYER, PODCASTS, MODES
from ui.layout.buttonlayout import TOP

ICON_LOCATION = TOP
BUTTON_PADDING = 0
ICON_AREA = 70
ICON_SIZE = 70
FONT_HEIGHT = 48

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
        self.cdutil = CdUtil(util)

        self.bb = bounding_box
        self.horizontal_layout = True
        self.rows = None
        self.cols = None
        items = self.get_menu_items()
        cell_bb = items[2]

        m = self.create_home_menu_button
        label_area = (cell_bb.h / 100) * (100 - ICON_AREA)
        font_size = int((label_area / 100) * FONT_HEIGHT)
        Menu.__init__(self, util, bgr, bounding_box, None, None, create_item_method=m, font_size=font_size)
        self.set_modes(*items)

    def get_menu_items(self):
        """ Prepare menu items

        :return: array containing menu items, disabled items, cell bounding box and icon box
        """
        items = []
        disabled_items = []
        disabled_modes = self.util.get_disabled_modes()
        for mode in MODES:
            self.add_mode(mode, items, disabled_items, disabled_modes)

        l = self.get_layout(items)
        bounding_box = l.get_next_constraints()
        box = self.factory.get_icon_bounding_box(bounding_box, ICON_LOCATION, ICON_AREA, ICON_SIZE, BUTTON_PADDING)

        return (items, disabled_items, bounding_box, box)

    def add_mode(self, mode, enabled, disabled, disabled_modes):
        """ Add mode

        :param mode: the mode to add
        :param enabled: list of enabled items
        :param disabled: list of disabled items
        :param disabled_modes: list of disabled modes
        """
        if not self.config[HOME_MENU][mode]:
            return

        enabled.append(mode)
        if mode in disabled_modes:
            disabled.append(mode)

    def set_current_modes(self):
        """ Set current player modes """

        items = self.get_menu_items()
        self.set_modes(*items)

    def set_modes(self, items, disabled_items, bounding_box, box):
        """ Set menu items

        :param items: menu items
        :param disabled_items: disabled menu items
        :param bounding_box: cell bounding box
        :param box: image boundng box
        """
        self.modes = self.util.load_menu(items, NAME, disabled_items, V_ALIGN_TOP, bb=box)
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

        self.set_items(self.modes, 0, self.change_mode, False, fill=True)
        try:
            self.current_mode = self.modes[mode.lower()]
            self.item_selected(self.current_mode)
        except:
            pass

    def create_home_menu_button(self, s, constr, action, scale, font_size):
        """ Create Home Menu button

        :param s: button state
        :param constr: scaling constraints
        :param action: button event listener
        :param scale: True - scale images, False - don't scale images
        :param font_size: label font height in pixels

        :return: home menu button
        """
        s.padding = BUTTON_PADDING
        s.image_area_percent = ICON_AREA

        return self.factory.create_menu_button(s, constr, action, scale, font_size=font_size)

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
