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

LINES = 10

class MultiLineButtonLayout(object):
    """ Layout which arranges button components (icon and label) """
    
    def __init__(self, state, label_padding=2, image_padding=2):
        """ Initializer. Define bounding boxes for button label (if any) and icon (if any)
        
        :param state: button state
        :param label_padding: label padding
        :param image_padding: image padding
        """        
        self.bb = state.bounding_box
        self.top_lines = 2
        self.bottom_lines = 2
        self.label_padding = label_padding
        self.image_padding = image_padding        
        self.label_lines = self.top_lines + self.bottom_lines
        self.image_lines = LINES - self.label_lines        
        self.line_h = self.bb.h / LINES
        self.create_layout(self.bb)
        
    def create_layout(self, bb):
        """ Create button layout
        
        :param bb: bounding box
        """
        self.label_rectangles = {}
        img_w = bb.w - (self.image_padding * 2)
        img_h = (self.image_lines * self.line_h) - (self.image_padding * 2)
        img_x = bb.x + (bb.w - img_w)/2 
        img_y = bb.y + (self.line_h * 2) + self.image_padding + (self.label_padding * 2)
        
        self.image_rectangle = Rect(img_x, img_y, img_w, img_h)        
        self.add_label_rect(bb, self.line_h, 0, self.top_lines, self.label_padding)
        self.add_label_rect(bb, self.line_h, LINES - self.bottom_lines, LINES, self.label_padding)
            
    def add_label_rect(self, bb, line_h, start, stop, label_padding):
        """ Prepare labels rectangles
        
        :param bb: bounding box
        :param line_h: line height
        :param start: start line
        :param stop: stop line
        :param label_padding: padding
        """
        for n in range(start, stop):
            x = bb.x + label_padding
            if start > LINES - 3:
                y = bb.y + (n * line_h) - (label_padding * 3)
            else:
                y = bb.y + (n * line_h) + label_padding
            w = bb.w - (label_padding * 2)
            h = line_h
            r = Rect(x, y, w, h)
            self.label_rectangles[n] = r
        
    def get_image_rectangle(self):
        """ Return button image bounding box
        
        :return: image bounding box
        """
        return self.image_rectangle
        
    def get_label_rectangle(self, index):
        """ Return button label bounding box
        
        :return: label bounding box
        """
        return self.label_rectangles[index]

    def get_joint_label_rectangle(self, index):
        """ Create rectangle by merging two joint rectangles
        
        :param index: line index
        
        :return: merged rectangle
        """
        r = self.label_rectangles[index]
        n = Rect(r.x, r.y, r.w, r.h * 2)
        return n
        