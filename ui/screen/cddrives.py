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

import os

from ui.page import Page
from ui.container import Container
from ui.layout.borderlayout import BorderLayout
from ui.factory import Factory
from ui.screen.screen import Screen
from util.keys import SCREEN_RECT, GO_BACK, GO_LEFT_PAGE, GO_RIGHT_PAGE, GO_ROOT, GO_USER_HOME, GO_TO_PARENT, \
    KEY_PLAYER, KEY_CD_TRACKS, KEY_CD_PLAYERS, KEY_CD_DRIVES
from util.config import CURRENT_FOLDER, AUDIO, MUSIC_FOLDER, CURRENT_FILE_PLAYBACK_MODE, \
    CURRENT_FILE_PLAYLIST, COLORS, COLOR_DARK_LIGHT, COLOR_CONTRAST, FILE_PLAYBACK, CD_PLAYBACK, CD_DRIVE_ID, \
    CD_TRACK, CD_TRACK_TIME, LABELS, CD_DRIVE_NAME
from util.fileutil import FILE_AUDIO, FILE_PLAYLIST
from ui.menu.cddrivesmenu import CdDrivesMenu
from ui.state import State
from util.cdutil import CdUtil

# 480x320
PERCENT_TOP_HEIGHT = 14.0625
PERCENT_BOTTOM_HEIGHT = 14.0625
PERCENT_TITLE_FONT = 66.66

class CdDrivesScreen(Screen):
    """ File Browser Screen """
    
    def __init__(self, util, listeners, voice_assistant):
        """ Initializer
        
        :param util: utility object
        :param listeners: file browser listeners
        """
        self.util = util
        self.config = util.config
        self.cdutil = CdUtil(util)
        self.factory = Factory(util)
        self.bounding_box = self.config[SCREEN_RECT]
        layout = BorderLayout(self.bounding_box)
        layout.set_percent_constraints(PERCENT_TOP_HEIGHT, PERCENT_BOTTOM_HEIGHT, 0, 0)
        Screen.__init__(self, util, "", PERCENT_TOP_HEIGHT, voice_assistant, "file_browser_screen_title", True, layout.TOP)
        color_dark_light = self.config[COLORS][COLOR_DARK_LIGHT]
        
        self.cd_drive_id = self.config[CD_PLAYBACK][CD_DRIVE_ID]
        self.cd_track = self.config[CD_PLAYBACK][CD_TRACK]
        self.cd_track_time = self.config[CD_PLAYBACK][CD_TRACK_TIME]
        self.screen_title.set_text(self.config[LABELS][KEY_CD_DRIVES])
        
        drives = self.cdutil.get_cd_drives(self.font_size)
        self.cd_drives_menu = CdDrivesMenu(drives, util, (0, 0, 0), layout.CENTER, listeners[KEY_CD_TRACKS])        
        Container.add_component(self, self.cd_drives_menu)
        
        factory = Factory(util)
        self.menu_buttons = factory.create_home_player_buttons(self, self.layout.BOTTOM, listeners)
        self.home_button = self.menu_buttons[0]
        self.player_button = self.menu_buttons[1]    
    
    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        Screen.add_screen_observers(self, update_observer, redraw_observer)
        
        self.cd_drives_menu.add_menu_observers(update_observer, redraw_observer)
        for b in self.menu_buttons:
            self.add_button_observers(b, update_observer, redraw_observer)
        
        
