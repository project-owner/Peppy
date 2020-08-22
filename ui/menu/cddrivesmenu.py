# Copyright 2016-2020 Peppy Player peppy.player@gmail.com
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

from pygame import Rect
from ui.menu.menu import Menu
from ui.layout.gridlayout import GridLayout
from ui.layout.borderlayout import BorderLayout
from ui.factory import Factory
from util.keys import KEY_PLAYER
from util.config import CD_PLAYBACK, CD_DRIVE_ID

PERCENT_ARROW_WIDTH = 16.0
ICON_AREA = 70
FONT_HEIGHT = 30

class CdDrivesMenu(Menu):
    """ File browser navigator menu """
    
    def __init__(self, util, bounding_box, listener):
        """ Initializer
        
        :param util: utility object
        :param bounding_box: bounding box
        :param listeners: buttons listeners
        """ 
        self.factory = Factory(util)
        m = self.create_cd_drive_menu_button
        label_area = (bounding_box.h / 100) * (100 - ICON_AREA)
        font_size = int((label_area / 100) * FONT_HEIGHT)
        r = Rect(bounding_box.x, bounding_box.y, bounding_box.w, bounding_box.h + 1)
        Menu.__init__(self, util, None, r, None, None, create_item_method=m, font_size=font_size)
        self.name = "cd.drives.menu"
        self.content = bounding_box
        self.content_x = bounding_box.x
        self.content_y = bounding_box.y
        self.menu_buttons = []
        id = str(util.config[CD_PLAYBACK][CD_DRIVE_ID])
        if len(id) == 0:
            id = "0"
        self.select_by_index(int(id))

    def create_cd_drive_menu_button(self, s, constr, action, scale, font_size):
        """ Create CD drive button

        :param s: button state
        :param constr: scaling constraints
        :param action: button event listener
        :param scale: True - scale images, False - don't scale images

        :return: file menu button
        """
        s.image_area_percent = ICON_AREA

        return self.factory.create_menu_button(s, constr, action, scale, font_size=font_size)

    def add_observers(self, update_observer, redraw_observer):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        for b in self.menu_buttons:
            self.add_button_observers(b, update_observer, redraw_observer)
