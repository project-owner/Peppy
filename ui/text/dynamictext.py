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

from ui.component import Component
from ui.text.outputtext import OutputText
from util.config import SCREEN_INFO, WIDTH

MARGIN = 10
PERCENT_SMALL_FONT = 0.7

STATIC = 0
ANIMATED = 1
REFRESH_RATE = 1/30

class DynamicText(OutputText):
    """ Dynamic text UI component. Extends static OutputText class """
    def __init__(self, name, bb, util, font_size=None, bgr=None, fgr=None, halign=1, valign=4, shift_x=0, shift_y=0, font=None):
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
        :param font: the font
        """        
        OutputText.__init__(self, util, name, bb, font_size, bgr, fgr, halign, valign, shift_x, shift_y, True, font)
        self.name = name
        self.util = util
        self.config = util.config
        self.start_listeners = list()
        self.animate = False
        self.animated_text_length = None 
        self.comp1 = None
        self.comp2 = None
        self.w = self.config[SCREEN_INFO][WIDTH]      
    
    def set_text(self, text):
        """ Set text and draw component
        
        :param text: text to set
        """ 
          
        if text == self.text:
            return
        self.update_text(text)
        self.text = text
        self.notify_listeners()
            
    def update_text(self, text):
        """ Depending on text length and component width creates different set of components using the following rules:
        1. If text length less than component width creates one line label text
        2. If text length larger than component width reduces the font, if new text length is smaller creates one line label with new font
        3. If reduced text is still larger than component width reduce text and create two labels one above the other
        4. If two lines of text still don't fit to current componet size than use animation
        
        :param text: new text
        """
        if text == None or self.text == text:
            return
        
        self.animate = False
        font = self.util.get_font(self.default_font_size)                    
        size = font.size(text)        
        self.components = []
        self.add_bgr()                
         
        if (size[0] + MARGIN) > self.w:
            font_size = int(self.default_font_size * PERCENT_SMALL_FONT)
            font = self.util.get_font(font_size)        
            size = font.size(text)
  
            if (size[0] + MARGIN) > self.w:
                font_size = font_size - 2
                font = self.util.get_font(font_size)
                items = text.split(" - ")
                  
                if len(items) != 2:
                    self.start_animation(text)
                    return
                                  
                size_0 = font.size(items[0])
                size_1 = font.size(items[1])
                  
                if ((size_0[0] + MARGIN) > self.w) or ((size_1[0] + MARGIN) > self.w):
                    self.start_animation(text)
                    return
                  
                label = font.render(items[0], 1, self.fgr)
                x = self.bounding_box.x + self.get_x(size_0)
                y = -1
                self.add_label(1, label, x, y, items[0], font_size, STATIC)
                label = font.render(items[1], 1, self.fgr)
                  
                x = self.bounding_box.x + self.get_x(size_1)
                y = font_size
                self.add_label(2, label, x, y, items[1], font_size, STATIC)
            else:
                label = font.render(text, 1, self.fgr)
                x = self.bounding_box.x + self.get_x(size)
                y = self.bounding_box.y + self.get_y(size) + 2
                self.add_label(1, label, x, y, text, font_size, STATIC)
        else:
            label = font.render(text, 1, self.fgr)
            x = self.bounding_box.x + self.get_x(size)
            y = self.bounding_box.y + self.get_y(size)
            self.add_label(1, label, x, y, text, self.default_font_size, STATIC)

        self.clean_draw_update()

    def start_animation(self, text):
        """ Start animation
        
        :param text: text to animate
        """
        font = self.util.get_font(self.default_font_size)
        label = font.render(text, 1, self.fgr)
        size = font.size(text)
        self.add_label(1, label, 0, 0, text, self.default_font_size, ANIMATED, size[0])
        self.add_label(2, None, 0, 0, text, self.default_font_size, ANIMATED, size[0])
        self.animated_text_length = size[0]
        self.animate = True
        self.clean_draw_update()
        self.comp1 = self.components[1]
        self.comp2 = self.components[2]

    def refresh(self):
        """ Animation method """
        if not self.animate:
            return
        step = 1
        self.comp1.content_x = self.comp1.content_x - step
        self.comp2.content_x = self.comp2.content_x - step
        if abs(self.comp1.content_x) == (self.animated_text_length - self.w):
            self.comp2.content = self.comp1.content 
            self.comp2.content_x = self.w + 10
        elif abs(self.comp1.content_x) == self.animated_text_length:
            tmp = self.comp1.content_x
            self.comp1.content_x = self.comp2.content_x
            self.comp2.content_x = tmp            
        self.clean_draw_update()
    
    def add_label(self, index, label, x, y, text, text_size, label_type, text_width=None):
        """ Add text label to the component list
        
        :param index: label index
        :param label: rendered text
        :param x: X coordinate for new label
        :param y: Y coordinate for new label
        :param text: the text
        :param text_size: text size
        :param label_type: label type (STATIC or ANIMATED)
        :param text_width: the width of the rendered text
        """
        comp = Component(self.util, label)
        comp.label_type = label_type
        comp.name = self.name + ".text." + str(index)
        comp.content_x = x
        comp.content_y = y
        comp.text = text
        comp.text_size = text_size
        comp.fgr = self.fgr
        if text_width:
            comp.text_width = text_width
        self.components.append(comp)

    def add_listener(self, listener):
        """ Add event listener
        
        :param listener: the listener
        """
        if listener not in self.start_listeners:
            self.start_listeners.append(listener)
            
    def notify_listeners(self):
        """ Notify all event listeners """
        for listener in self.start_listeners:
            listener(self)
            
    def shutdown(self):
        """ Stop animation (if any) """
        self.animate = False
    