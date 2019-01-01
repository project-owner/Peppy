# Copyright 2018 Peppy Player peppy.player@gmail.com
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

from ui.component import Component
from ui.eventcontainer import EventContainer

class Digit(EventContainer):
    """ Base class for the flip clock digit """
    
    def __init__(self, util, digits, digit, bb, increment_listener, decrement_listener, name):
        """ Initializer
        
        :param util: utility object
        :param digits: clock digits 0-9
        :param digit: the digit
        :param bb: digit bounding box
        :param increment_listener: increment listener
        :param decrement_listener: decrement listener
        :param name: component name
        """        
        self.util = util
        self.config = self.util.config
        EventContainer.__init__(self, util, bb)
        self.digits = digits
        self.digit = digit
        image = self.digits[self.digit][1]
        
        c = Component(self.util)
        c.name = name
        c.image_filename = self.digits[self.digit][0]
        c.content = image
        c.content_x = bb.x
        c.content_y = bb.y
        
        self.add_component(c)
        
        top = Rect(bb.x, bb.y, bb.w, bb.h/2)
        self.add_area_listener((top, increment_listener))
        bottom = Rect(bb.x, bb.y + (bb.h/2) + 1, bb.w, bb.h/2)
        self.add_area_listener((bottom, decrement_listener))
        
    def set_digit(self, digit):
        """ Set the digit
        
        :param digit: digit to set
        """
        self.digit = digit
        image = self.digits[digit][1]
        c = self.components[0]
        c.content = image
        c.image_filename = self.digits[digit][0]
        self.clean_draw_update()
        