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
    
    def draw_area(self, bb):
        if not self.visible: return
        Component.draw(self, bb)

    def is_empty(self):
        """ Check if container has components
        
        :return: True - container doesn't have components, False - container has components
        """
        return not hasattr(self, "components")

    def clean_draw_update(self):
        """ Clean, draw and update container """
        
        self.clean()
        self.draw()
        self.update()
            
    def handle_event(self, event):
        """ Handle container event. Don't handle event if container is invisible.
        
        :param event: the event to handle
        """
        if not self.visible or len(self.components) == 0: return

        for i in range(len(self.components) - 1, -1, -1):
            try:
                comp = self.components[i]

                if not hasattr(comp, "handle_event"):
                    continue

                if getattr(comp, "popup", None) == True:
                    if comp.visible == True:
                        comp.handle_event(event)
                        break
                else:
                    comp.handle_event(event)
            except:
                pass
    
    def set_current(self, state=None):
        """ Set container as current. Used by screens 
        
        :param state: button state (if any)
        """        
        pass
    
    def set_visible(self, flag):
        """ Set container visible/invisible. Set all components in container visible/invisible.
        
        :param flag: True - visible, False - invisible
        """
        Component.set_visible(self, flag)
        if self.is_empty(): return

        for comp in self.components:
            if not comp: continue
            
            if getattr(comp, "popup", None) == True:
                if not comp.visible:
                    continue
            else:
                comp.set_visible(flag)

    def refresh(self):
        """ Refresh container. Used for periodical updates for example for animation.
        This method will be called from the main event loop. 
        """
        if not self.visible: return
        
        for comp in self.components:
            try:
                comp.refresh()
            except AttributeError:
                pass      

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

    def items_per_line(self, width):
        """ Return the number of items in line for specified screen width
        
        :param width: screen width        
        :return: number of items per line
        """
        if width <= 102:
            return 1
        elif width <= 203:
            return 2
        elif width <= 304:
            return 3
        elif width <= 405:
            return 4
        elif width <= 506:
            return 5
        else:
            return 6
        
    def add_button_observers(self, button, update_observer, redraw_observer=None, press=True, release=True):
        """ Add button observers
        
        :param button: button to observer
        :param update_observer: observer for updating the button
        :param redraw_observer: observer to redraw the whole screen
        """
        if press and update_observer: button.add_press_listener(update_observer)
        if release and update_observer: button.add_release_listener(update_observer)
        if redraw_observer and redraw_observer: 
            button.add_release_listener(redraw_observer)
            button.redraw_observer = redraw_observer
