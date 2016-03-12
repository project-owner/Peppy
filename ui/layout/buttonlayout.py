# Copyright 2016 Peppy Player peppy.player@gmail.com
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

TOP = 0
BOTTOM = 1
CENTER = 2
LEFT = 3
RIGHT = 4

class ButtonLayout(object):
    """ Layout which arranges button components (icon and label) """
    
    def __init__(self, state):
        """ Initializer. Defines bounding boxes for button label (if any) and icon (if any)
        
        :param state: button state
        """        
        s = state
        bb = s.bounding_box
        self.show_image = getattr(s, "show_img", None)
        self.show_label = getattr(s, "show_label", False)
        self.image_location = getattr(s, "image_location", CENTER)
        self.label_location = getattr(s, "label_location", BOTTOM)
        self.image_area_percent = getattr(s, "image_area_percent", 0)
        self.label_area_percent = getattr(s, "label_area_percent", 0)        
        self.layout = BorderLayout(bb)
        top = bottom = left = right = 0
        self.image_rectangle = self.label_rectangle = None
        
        if self.show_image and self.show_label:
            if self.image_location == TOP and self.label_location == CENTER:
                top = self.image_area_percent
                self.layout.set_percent_constraints(top, bottom, left, right)
                self.image_rectangle = self.layout.TOP
                self.label_rectangle = self.layout.CENTER
            elif self.image_location == BOTTOM and self.label_location == CENTER:
                bottom = self.image_area_percent
                self.layout.set_percent_constraints(top, bottom, left, right)
                self.image_rectangle = self.layout.BOTTOM
                self.label_rectangle = self.layout.CENTER
            elif self.image_location == CENTER and self.label_location == TOP:
                top = self.label_area_percent
                self.layout.set_percent_constraints(top, bottom, left, right)
                self.image_rectangle = self.layout.CENTER
                self.label_rectangle = self.layout.TOP
            elif self.image_location == CENTER and self.label_location == BOTTOM:
                bottom = self.label_area_percent
                self.layout.set_percent_constraints(top, bottom, left, right)
                self.image_rectangle = self.layout.CENTER
                self.label_rectangle = self.layout.BOTTOM                
            elif self.image_location == LEFT and self.label_location == CENTER:
                left = self.image_area_percent
                self.layout.set_percent_constraints(top, bottom, left, right)
                self.image_rectangle = self.layout.LEFT
                self.label_rectangle = self.layout.CENTER
            elif self.image_location == RIGHT and self.label_location == CENTER:
                right = self.image_area_percent
                self.layout.set_percent_constraints(top, bottom, left, right)
                self.image_rectangle = self.layout.RIGHT
                self.label_rectangle = self.layout.CENTER
            elif self.image_location == CENTER and self.label_location == LEFT:
                left = self.label_area_percent
                self.layout.set_percent_constraints(top, bottom, left, right)
                self.image_rectangle = self.layout.CENTER
                self.label_rectangle = self.layout.LEFT
            elif self.image_location == CENTER and self.label_location == RIGHT:
                right = self.label_area_percent
                self.layout.set_percent_constraints(top, bottom, left, right)
                self.image_rectangle = self.layout.CENTER
                self.label_rectangle = self.layout.RIGHT
        elif self.show_image and not self.show_label:
            self.layout.set_percent_constraints(top, bottom, left, right)
            self.image_rectangle = self.layout.CENTER
        elif not self.show_image and self.show_label:
            self.layout.set_percent_constraints(top, bottom, left, right)
            self.label_rectangle = self.layout.CENTER
        
    def get_image_rectangle(self):
        """ Return button image bounding box
        
        :return: image bounding box
        """
        return self.image_rectangle
        
    def get_label_rectangle(self):
        """ Return button label bounding box
        
        :return: label bounding box
        """
        return self.label_rectangle
