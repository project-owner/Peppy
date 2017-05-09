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

from ui.state import State
from ui.component import Component
from ui.container import Container
from util.keys import H_ALIGN_LEFT, H_ALIGN_CENTER, H_ALIGN_RIGHT, V_ALIGN_TOP, V_ALIGN_CENTER, V_ALIGN_BOTTOM

class OutputText(Container):
    """ Static output text UI component. Extends Container class """
    
    def __init__(self, util, name, bb, font_size=None, bgr=None, fgr=None, halign=1, valign=4, shift_x=0, shift_y=0, full_width=False, font=None):
        """ Initializer
        
        :param util: utility object
        :param name: component name
        :param bb: bounding box
        :param bgr: background color
        :param fgr: text color
        :param font_size: font size
        :param halign: horizontal alignment
        :param valign: vertical alignment
        :param shift_x: X axis shift
        :param shift_y: Y axis shift
        :param full_width: True - use the whole bounding box width, False - use reduced width
        :param font: the font
        """
        Container.__init__(self, util, background=bgr, bounding_box=bb)
        self.util = util
        self.name = name
        self.default_font_size = font_size       
        self.font = font
        self.fgr = fgr
        self.bgr = bgr
        self.halign = halign
        self.valign = valign
        self.shift_x, self.shift_y = shift_x, shift_y
        self.full_width = full_width
        self.add_bgr()
        self.active = True
        self.DIGITS = "1234567890"
    
    def add_bgr(self):
        """ Add background rectangle """
        
        if not self.full_width:
            self.bounding_box.x += 1
            self.bounding_box.y += 1
            self.bounding_box.w -= 2
            self.bounding_box.h -= 1            
        comp = Component(self.util, self.bounding_box)
        comp.name = self.name + ".bgr"
        comp.bgr = self.bgr
        self.add_component(comp)
    
    def set_text(self, text):
        """ Set text and draw component
        
        :param text: text to set
        """        
        self.text = text
        self.prepare_label()
        self.clean_draw_update()
        
    def set_text_no_draw(self, text):
        """ Set text without drawing component
        
        :param text: text to set
        """
        self.text = text
        self.prepare_label()
        
    def prepare_label(self):
        """ Prepare label component representing this output text. Used for web. """
        
        if self.text == None:
            return            
        size = self.font.size(self.text)
        label = self.font.render(self.text, 1, self.fgr)
        comp = Component(self.util, label)
        comp.name = self.name + ".text"
        comp.content_x = self.bounding_box.x + self.get_x(size)
        comp.content_y = self.bounding_box.y + self.get_y(size)
        comp.text = self.text
        comp.text_size = self.default_font_size
        comp.fgr = self.fgr
        if len(self.components) == 1:
            self.add_component(comp)
        else:
            self.components[1] = comp
            
    def set_state(self, state):
        """ Set new localized text
        
        :param state: button state
        """
        self.set_text(self.fetch_text(state))        
    
    def fetch_text(self, obj):
        """ Fetch text from provided object
        
        :param obj: input object
        :return: unicode string
        """
        t = ""
        if isinstance(obj, State):
            t = obj.l_name
        elif isinstance(obj, dict):
            try:
                t = obj["current_title"]
            except:
                pass
        else:
            t = obj
        
        if "&#" in t and ";" in t:
            t = self.get_unicode(t)
            
        return t
    
    def get_unicode(self, t):
        """ Replace string with unicode codes by characters
        
        :param t: input string with codes
        :return: output string with characters
        """
        t = t.split(";")
        r = ""
        
        for s in t:
            m = s.split("&#")
            if len(m) == 2:
                if len(m[0]) != 0:
                    r += m[0]
                if len(m[1]) != 0:
                    r += chr(int(m[1]))
            elif len(m) == 1:
                if len(m[0]) != 0:
                    a = m[0]
                    if a in self.DIGITS:
                        r += chr(int(a))
                    else:
                        r += a
        return r
    
    def get_x(self, size):
        """ Return text X coordinate taking into account shift and alignment values
        
        :param size: text size
        """
        x = 0
        if self.halign == H_ALIGN_LEFT:
            x = self.shift_x
        elif self.halign == H_ALIGN_CENTER:                
            x = self.bounding_box.width/2 - size[0]/2 + self.shift_x
        elif self.halign == H_ALIGN_RIGHT:
            x = self.bounding_box.width - size[0] - self.shift_x
        return x
    
    def get_y(self, size):
        """ Return text Y coordinate taking into account shift and alignment values
        
        :param size: text size
        """
        y = 0
        if self.valign == V_ALIGN_TOP:
            y = self.shift_y
        elif self.valign == V_ALIGN_CENTER:                
            y = self.bounding_box.height/2 - size[1]/2 + self.shift_y
        elif self.valign == V_ALIGN_BOTTOM:
            y = self.bounding_box.height - size[1] - self.shift_y
        return y
    
    def set_visible(self, flag):
        """ Set visibility flag
        
        :param flag: True - visible, False - invisible
        """
        Container.set_visible(self, flag)

