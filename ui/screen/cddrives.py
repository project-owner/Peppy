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

from ui.layout.borderlayout import BorderLayout
from ui.factory import Factory
from ui.screen.screen import Screen
from util.keys import KEY_CD_TRACKS, KEY_CD_DRIVES, KEY_HOME
from util.config import CD_PLAYBACK, CD_DRIVE_ID, CD_TRACK, CD_TRACK_TIME, LABELS
from ui.menu.cddrivesmenu import CdDrivesMenu
from util.cdutil import CdUtil
from ui.navigator.cddrives import CdDrivesNavigator

# 480x320
PERCENT_TOP_HEIGHT = 14.0625
PERCENT_BOTTOM_HEIGHT = 14.0625

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
        self.bounding_box = util.screen_rect
        layout = BorderLayout(self.bounding_box)
        layout.set_percent_constraints(PERCENT_TOP_HEIGHT, PERCENT_BOTTOM_HEIGHT, 0, 0)
        Screen.__init__(self, util, "", PERCENT_TOP_HEIGHT, voice_assistant, "cd_drives_screen_title", True, layout.TOP)
        
        self.cd_drive_id = self.config[CD_PLAYBACK][CD_DRIVE_ID]
        self.cd_track = self.config[CD_PLAYBACK][CD_TRACK]
        self.cd_track_time = self.config[CD_PLAYBACK][CD_TRACK_TIME]
        self.screen_title.set_text(self.config[LABELS][KEY_CD_DRIVES])
        
        self.cd_drives_menu = CdDrivesMenu(util, layout.CENTER, listeners[KEY_CD_TRACKS])
        drives_info = self.cdutil.get_cd_drives_info()
        l = self.cd_drives_menu.get_layout(drives_info)
        bb = l.get_next_constraints()
        drives = self.cdutil.get_cd_drives(self.font_size, (bb.w, bb.h))
        self.cd_drives_menu.set_items(drives, 0, listeners[KEY_CD_TRACKS])

        for b in self.cd_drives_menu.buttons.values():
            b.parent_screen = self

        self.add_menu(self.cd_drives_menu)
        
        self.navigator = CdDrivesNavigator(util, self.layout.BOTTOM, listeners)
        self.navigator.get_button_by_name(KEY_HOME).set_selected(True)
        self.add_navigator(self.navigator)
        self.link_borders()
    
    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        Screen.add_screen_observers(self, update_observer, redraw_observer)
        
        self.cd_drives_menu.add_menu_observers(update_observer, redraw_observer)
        self.navigator.add_observers(update_observer, redraw_observer)
