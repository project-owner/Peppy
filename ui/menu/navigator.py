# Copyright 2016-2017 Peppy Player peppy.player@gmail.com
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
from util.keys import GO_BACK, GO_LEFT_PAGE, GO_RIGHT_PAGE, GO_ROOT, GO_USER_HOME, GO_TO_PARENT, \
    KEY_HOME, KEY_BACK, KEY_MENU, KEY_PLAY_FILE, KEY_ROOT, KEY_PARENT, KEY_USER_HOME

PERCENT_ARROW_WIDTH = 16.0

class Navigator(Container):
    """ File browser navigator menu """
    
    def __init__(self, util, bounding_box, listeners, bgr):
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

        arrow_layout = BorderLayout(bounding_box)
        arrow_layout.set_percent_constraints(0, 0, PERCENT_ARROW_WIDTH, PERCENT_ARROW_WIDTH)
        
        constr = arrow_layout.LEFT
        self.left_button = self.factory.create_page_down_button(constr, "0", 40, 100)
        self.left_button.add_release_listener(listeners[GO_LEFT_PAGE])
        self.add_component(self.left_button)
        
        constr = arrow_layout.RIGHT
        self.right_button = self.factory.create_page_up_button(constr, "0", 40, 100)
        self.right_button.add_release_listener(listeners[GO_RIGHT_PAGE])
        self.add_component(self.right_button)
        
        layout = GridLayout(arrow_layout.CENTER)
        layout.set_pixel_constraints(1, 5, 1, 0)        
        layout.current_constraints = 0
        
        constr = layout.get_next_constraints()
        self.home_button = self.factory.create_button(KEY_HOME, KEY_HOME, constr, listeners[KEY_HOME], bgr)
        self.add_component(self.home_button)
        
        constr = layout.get_next_constraints()
        self.user_home_button = self.factory.create_button(KEY_USER_HOME, KEY_MENU, constr, listeners[GO_USER_HOME], bgr)
        self.add_component(self.user_home_button)
        
        constr = layout.get_next_constraints()
        self.root_button = self.factory.create_button(KEY_ROOT, KEY_ROOT, constr, listeners[GO_ROOT], bgr)
        self.add_component(self.root_button)

        constr = layout.get_next_constraints()
        self.parent_button = self.factory.create_button(KEY_PARENT, KEY_PARENT, constr, listeners[GO_TO_PARENT], bgr)
        self.add_component(self.parent_button)

        constr = layout.get_next_constraints()
        self.back_button = self.factory.create_button(KEY_BACK, KEY_BACK, constr, None, bgr)
        self.back_button.add_release_listener(listeners[GO_BACK])
        self.back_button.add_release_listener(listeners[KEY_PLAY_FILE])
        self.add_component(self.back_button)

        
