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

from pygame import Rect

from ui.layout.borderlayout import BorderLayout

# image location
TOP = "top"
BOTTOM = "bottom"
CENTER = "center"
LEFT = "left"
RIGHT = "right"

class ButtonLayout(object):
    """ Layout which arranges button components (icon and label) """
    
    def __init__(self, state):
        """ Initializer. Define bounding boxes for button label (if any) and icon (if any)
        
        :param state: button state
        """        
        s = state
        self.padding = getattr(s, "padding", 0)
        gap = int((s.bounding_box.h / 100) * self.padding)
        x = s.bounding_box.x + gap
        y = s.bounding_box.y + gap
        w = s.bounding_box.w - (gap * 2)
        h = s.bounding_box.h - (gap * 2)
        bb = Rect(x, y, w, h)

        self.show_image = getattr(s, "show_img", None)
        self.show_label = getattr(s, "show_label", False)
        self.image_location = getattr(s, "image_location", CENTER)
        self.image_area_percent = getattr(s, "image_area_percent", 0)
        self.layout = BorderLayout(bb)
        top = bottom = left = right = 0
        self.image_rectangle = self.label_rectangle = None
        
        if self.show_image and self.show_label:
            if self.image_location == TOP:
                top = self.image_area_percent
                bottom = 100 - top
                self.layout.set_percent_constraints(top, bottom, left, right)
                self.image_rectangle = self.layout.TOP
                self.label_rectangle = self.layout.BOTTOM
            elif self.image_location == BOTTOM:
                bottom = self.image_area_percent
                top = 100 - bottom
                self.layout.set_percent_constraints(top, bottom, left, right)
                self.image_rectangle = self.layout.BOTTOM
                self.label_rectangle = self.layout.TOP
            elif self.image_location == LEFT:
                left = self.image_area_percent
                right = 100 - left
                self.layout.set_percent_constraints(top, bottom, left, right)
                self.image_rectangle = self.layout.LEFT
                self.label_rectangle = self.layout.RIGHT
            elif self.image_location == RIGHT:
                right = self.image_area_percent
                left = 100 - right
                self.layout.set_percent_constraints(top, bottom, left, right)
                self.image_rectangle = self.layout.RIGHT
                self.label_rectangle = self.layout.LEFT
        elif self.show_image and not self.show_label:
            self.layout.set_percent_constraints(top, bottom, left, right)
            self.image_rectangle = self.layout.CENTER
        elif not self.show_image and self.show_label:
            self.layout.set_percent_constraints(0, 0, gap, gap)
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
