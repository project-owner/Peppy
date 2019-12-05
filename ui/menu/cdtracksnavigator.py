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

from ui.container import Container
from ui.layout.gridlayout import GridLayout
from ui.layout.borderlayout import BorderLayout
from ui.factory import Factory
from util.util import IMAGE_PLAYER
from util.keys import GO_BACK, GO_LEFT_PAGE, GO_RIGHT_PAGE, GO_ROOT, GO_USER_HOME, GO_TO_PARENT, \
    KEY_HOME, KEY_BACK, KEY_MENU, KEY_PLAY_FILE, KEY_EJECT, KEY_ROOT, KEY_PARENT, KEY_PLAY_PAUSE, \
    GO_PLAYER, KEY_CD_PLAYERS, KEY_PLAYER, KEY_BACK, KEY_REFRESH, KEY_SETUP
from util.config import AUDIO, PLAYER_NAME
from player.proxy import VLC_NAME, MPD_NAME

PERCENT_ARROW_WIDTH = 16.0

class CdTracksNavigator(Container):
    """ File browser navigator menu """
    
    def __init__(self, util, connected_cd_drives, bounding_box, listeners, bgr):
        """ Initializer
        
        :param util: utility object
        :param bounding_box: bounding box
        :param listeners: buttons listeners
        :param bgr: menu background        
        """ 
        Container.__init__(self, util)
        self.factory = Factory(util)
        self.name = "navigator"
        self.content = bounding_box
        self.content_x = bounding_box.x
        self.content_y = bounding_box.y
        self.menu_buttons = []
        self.config = util.config

        arrow_layout = BorderLayout(bounding_box)
        arrow_layout.set_percent_constraints(0, 0, PERCENT_ARROW_WIDTH, PERCENT_ARROW_WIDTH)
        
        constr = arrow_layout.LEFT
        self.left_button = self.factory.create_page_down_button(constr, "0", 40, 100)
        self.left_button.add_release_listener(listeners[GO_LEFT_PAGE])
        self.add_component(self.left_button)
        self.menu_buttons.append(self.left_button)
        
        constr = arrow_layout.RIGHT
        self.right_button = self.factory.create_page_up_button(constr, "0", 40, 100)
        self.right_button.add_release_listener(listeners[GO_RIGHT_PAGE])
        self.add_component(self.right_button)
        self.menu_buttons.append(self.right_button)
        
        layout = GridLayout(arrow_layout.CENTER)
        p = self.config[AUDIO][PLAYER_NAME]
        show_drives = connected_cd_drives > 1 and (p == VLC_NAME or p == MPD_NAME)
        
        if show_drives:
            layout.set_pixel_constraints(1, 5, 1, 0)
        else:
            layout.set_pixel_constraints(1, 4, 1, 0)
        layout.current_constraints = 0
        image_size = 56
        
        constr = layout.get_next_constraints()
        self.home_button = self.factory.create_button(KEY_HOME, KEY_HOME, constr, listeners[KEY_HOME], bgr, image_size_percent=image_size)
        self.add_component(self.home_button)
        self.menu_buttons.append(self.home_button)
        
        if show_drives:
            constr = layout.get_next_constraints()
            self.cd_drives_button = self.factory.create_button(KEY_CD_PLAYERS, KEY_ROOT, constr, listeners[KEY_CD_PLAYERS], bgr, image_size_percent=image_size)
            self.add_component(self.cd_drives_button)
            self.menu_buttons.append(self.cd_drives_button)
        
        constr = layout.get_next_constraints()
        self.refresh_button = self.factory.create_button(KEY_REFRESH, KEY_SETUP, constr, listeners[KEY_REFRESH], bgr, image_size_percent=image_size)
        self.add_component(self.refresh_button)
        self.menu_buttons.append(self.refresh_button)
        
        constr = layout.get_next_constraints()
        self.eject_button = self.factory.create_button(KEY_EJECT, KEY_PARENT, constr, listeners[KEY_EJECT], bgr, image_size_percent=image_size)
        self.add_component(self.eject_button)
        self.menu_buttons.append(self.eject_button)

        constr = layout.get_next_constraints()
        self.back_button = self.factory.create_button(KEY_BACK, KEY_BACK, constr, None, bgr, image_size_percent=image_size)
        self.back_button.add_release_listener(listeners[GO_BACK])
        self.back_button.add_release_listener(listeners[KEY_PLAYER])
        self.add_component(self.back_button)
        self.menu_buttons.append(self.back_button)
                
    def add_observers(self, update_observer, redraw_observer):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        for b in self.menu_buttons:
            self.add_button_observers(b, update_observer, redraw_observer)

        
