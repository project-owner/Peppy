# Copyright 2019-2020 Peppy Player peppy.player@gmail.com
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
from util.keys import GO_LEFT_PAGE, GO_RIGHT_PAGE, KEY_HOME, KEY_PLAYER, \
    KEY_PLAY_PAUSE, KEY_BACK, GO_BACK
from util.config import BACKGROUND, FOOTER_BGR_COLOR

PERCENT_ARROW_WIDTH = 16.0

class PodcastNavigator(Container):
    """ Podcasts screen navigator menu """
    
    def __init__(self, util, bounding_box, listeners, pages):
        """ Initializer
        
        :param util: utility object
        :param bounding_box: bounding box
        :param listeners: buttons listeners
        :param pages: number of podcasts menu pages       
        """ 
        Container.__init__(self, util)
        self.config = util.config
        self.factory = Factory(util)
        self.name = "podcasts.navigator"
        self.content = bounding_box
        self.content_x = bounding_box.x
        self.content_y = bounding_box.y
        self.menu_buttons = []

        arrow_layout = BorderLayout(bounding_box)
        arrow_layout.set_percent_constraints(0, 0, PERCENT_ARROW_WIDTH, PERCENT_ARROW_WIDTH)
        
        if pages > 1:
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
        else:
            layout = GridLayout(bounding_box)
            
        layout.set_pixel_constraints(1, 3, 1, 0)        
        layout.current_constraints = 0
        image_size = 64
        bgr = self.config[BACKGROUND][FOOTER_BGR_COLOR]
        
        constr = layout.get_next_constraints()
        self.home_button = self.factory.create_button(KEY_HOME, KEY_HOME, constr, listeners[KEY_HOME], bgr, image_size_percent=image_size)
        self.add_component(self.home_button)
        self.menu_buttons.append(self.home_button)
        
        constr = layout.get_next_constraints()
        self.back_button = self.factory.create_button(KEY_BACK, KEY_BACK, constr, listeners[GO_BACK], bgr, image_size_percent=image_size)
        self.add_component(self.back_button)
        self.menu_buttons.append(self.back_button)
        
        constr = layout.get_next_constraints()
        self.player_button = self.factory.create_button(KEY_PLAYER, KEY_PLAY_PAUSE, constr, listeners[KEY_PLAYER], bgr, image_size_percent=image_size)       
        self.add_component(self.player_button)
        self.menu_buttons.append(self.player_button)

    def set_parent_screen(self, scr):
        """ Add parent screen

        :param scr: parent screen
        """
        for b in self.menu_buttons:
            b.parent_screen = scr

    def add_observers(self, update_observer, redraw_observer):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        for b in self.menu_buttons:
            self.add_button_observers(b, update_observer, redraw_observer)
