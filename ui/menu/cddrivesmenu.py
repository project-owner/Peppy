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

from ui.menu.menu import Menu
from ui.layout.gridlayout import GridLayout
from ui.layout.borderlayout import BorderLayout
from ui.factory import Factory
from util.keys import KEY_PLAYER
from util.config import CD_PLAYBACK, CD_DRIVE_ID

PERCENT_ARROW_WIDTH = 16.0

class CdDrivesMenu(Menu):
    """ File browser navigator menu """
    
    def __init__(self, items, util, bgr, bounding_box, listener):
        """ Initializer
        
        :param util: utility object
        :param bounding_box: bounding box
        :param listeners: buttons listeners
        :param bgr: menu background        
        """ 
        self.factory = Factory(util)
        m = self.factory.create_cd_drive_menu_button
        Menu.__init__(self, util, bgr, bounding_box, None, None, create_item_method=m)
        self.name = "cd.drives.menu"
        self.content = bounding_box
        self.content_x = bounding_box.x
        self.content_y = bounding_box.y
        self.menu_buttons = []
        id = str(util.config[CD_PLAYBACK][CD_DRIVE_ID])
        if len(id) == 0:
            id = "0"
        self.select_by_index(int(id))
                
    def add_observers(self, update_observer, redraw_observer):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        for b in self.menu_buttons:
            self.add_button_observers(b, update_observer, redraw_observer)

        
