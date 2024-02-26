# Copyright 2016-2024 Peppy Player peppy.player@gmail.com
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

from component import Component

class Container(Component):
    """ This container class keeps the list of components and executes group methods on them """
    
    def __init__(self, util, bounding_box=None, background=None, visible=True, content=None, image_filename=None):
        """ Initializer
        
        :param util: utility object
        :param bounding_box: container bounding box
        :param background: container background color
        :param visible: visibility flag, True - visible, False - invisible
        """
        if content:
            cnt = content
        else:
            cnt = bounding_box
            
        Component.__init__(self, util, c=cnt, bb=bounding_box, bgr=background, v=visible)
        self.components = list()
        if image_filename:
            self.image_filename = image_filename

        self.exit_top_y = self.exit_bottom_y = self.exit_left_x = self.exit_right_x = None
        
    def add_component(self, component):
        """ Add component to the container
        
        :param component: component to add
        """
        self.components.append(component)

    def set_parent_screen(self, scr):
        """ Add parent screen

        :param scr: parent screen
        """
        if self.is_empty(): return

        self.parent_screen = scr
        for c in self.components:
            if c: 
                c.parent_screen = scr
        
    def draw(self):
        """ Draw all components in container. Doesn't draw invisible container. """
        
        if not self.visible: return

        Component.draw(self)

        if self.is_empty(): return

        for comp in self.components:
            if comp: comp.draw()
    
    def is_empty(self):
        """ Check if container has components
        
        :return: True - container doesn't have components, False - container has components
        """
        return not hasattr(self, "components")

    def is_selected(self):
        """ Check if conatiner has selected component

        :return: True - container has selected component, False - doesn't have
        """
        s = False
        for c in self.components:
            if c and getattr(c, "selected", False):
                s = True
                break
        return s
