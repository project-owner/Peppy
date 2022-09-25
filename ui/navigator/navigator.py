# Copyright 2021-2022 Peppy Player peppy.player@gmail.com
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
from util.config import BACKGROUND, FOOTER_BGR_COLOR

PERCENT_ARROW_WIDTH = 16.0
LEFT = "left"
LISTENER = "listener"
IMAGE_NAME = "image name"
KEYBOARD_KEY = "keyboard key"
WIDTH = "width"
SOURCE = "source"

class Navigator(Container):
    """ Base class for all navigators """
    
    def __init__(self, util, bounding_box, name, items, arrow_items=None):
        """ Initializer
        
        :param util: utility object
        :param bounding_box: bounding box
        :param name: navigator name
        :param items: dictionary with button details
        :param arrow_items: dictionary with arrow buttons details
        """ 
        Container.__init__(self, util)
        self.factory = Factory(util)
        self.name = name
        self.content = bounding_box
        self.content_x = bounding_box.x
        self.content_y = bounding_box.y
        self.buttons = []

        if arrow_items:
            arrow_layout = BorderLayout(bounding_box)
            left_arrow = arrow_items[0]
            listeners = left_arrow[LISTENER]
            arrow_layout.set_percent_constraints(0, 0, PERCENT_ARROW_WIDTH, PERCENT_ARROW_WIDTH)
            constr = arrow_layout.LEFT
            button = self.factory.create_page_down_button(constr, "0", 40, 100)
            button.add_release_listener(listeners[0])
            self.add_component(button)
            self.buttons.append(button)
            layout = GridLayout(arrow_layout.CENTER)
        else:
            layout = GridLayout(bounding_box)
            
        layout.set_pixel_constraints(1, len(items), 1, 0)        
        layout.current_constraints = 0
        image_size = 64 
        b = util.config[BACKGROUND][FOOTER_BGR_COLOR]

        for item in items:
            constr = layout.get_next_constraints()
            image_name = item[IMAGE_NAME]
            listeners = item[LISTENER]
            keybiard_key = item[KEYBOARD_KEY]
            source = item[SOURCE]

            if len(listeners) == 1:
                button = self.factory.create_button(image_name, keybiard_key, constr, listeners[0], b, image_size_percent=image_size, source=source)
            else:
                button = self.factory.create_button(image_name, keybiard_key, constr, None, b, image_size_percent=image_size, source=source)
                for listener in listeners:
                    button.add_release_listener(listener)
                    
            self.add_component(button)
            self.buttons.append(button)
        
        if arrow_items:
            right_arrow = arrow_items[1]
            listeners = right_arrow[LISTENER]
            constr = arrow_layout.RIGHT
            button = self.factory.create_page_up_button(constr, "0", 40, 100)
            button.add_release_listener(listeners[0])
            self.add_component(button)
            self.buttons.append(button)

    def add_button(self, items, name, key, listeners, source=None):
        """ Add button definition

        :param items: list of items
        :param name: button image name
        :param key: keyboard key (if any)
        :param listeners: list of listeners
        """
        item = {}
        item[IMAGE_NAME] = name
        item[LISTENER] = listeners
        item[KEYBOARD_KEY] = key
        item[SOURCE] = source
        items.append(item)

    def set_parent_screen(self, scr):
        """ Add parent screen

        :param scr: parent screen
        """
        if not hasattr(self, "buttons"):
            return

        for b in self.buttons:
            b.parent_screen = scr

    def unselect(self):
        """ Unselect all navigator buttons """

        for b in self.buttons:
            b.set_selected(False)
            b.clean_draw_update()

    def get_clicked_button(self, event):
        """ Get the clicked button

        :param event: mouse event
        """
        for b in self.buttons:
            if b.bounding_box.collidepoint(event.pos):
                return b
        return None

    def get_button_by_name(self, name):
        """ Get the button by its name

        :param name: button name
        """
        for b in self.buttons:
            if b.state.name == name:
                return b
        return None

    def is_selected(self):
        """ Check if any button is selected
        
        :return: True - selected, False - unselected
        """
        if not hasattr(self, "buttons"):
            return False

        for b in self.buttons:
            if b and getattr(b, "selected", False):
                return True
        return False

    def add_observers(self, update_observer, redraw_observer):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        if not hasattr(self, "buttons"): return

        for b in self.buttons:
            self.add_button_observers(b, update_observer, redraw_observer)
