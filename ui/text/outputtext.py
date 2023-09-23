# Copyright 2016-2023 Peppy Player peppy.player@gmail.com
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

import pygame

from ui.state import State
from ui.component import Component
from ui.container import Container
from util.keys import H_ALIGN_LEFT, H_ALIGN_CENTER, H_ALIGN_RIGHT, V_ALIGN_TOP, V_ALIGN_CENTER, V_ALIGN_BOTTOM, \
    USER_EVENT_TYPE, SUB_TYPE_KEYBOARD, kbd_keys, KEY_AUDIO

class OutputText(Container):
    """ Static output text UI component. Extends Container class """
    
    def __init__(self, util, name, bb, font_size=None, bgr=None, fgr=None, halign=1, valign=4, 
                 shift_x=0, shift_y=0, full_width=False, font=None, show_cursor=False, cursor_color=(255, 255, 255)):
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
        Container.__init__(self, util, background=bgr, bounding_box=bb, content="text")
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
        self.show_cursor = show_cursor
        self.cursor_color = cursor_color
        self.add_bgr()

        if self.show_cursor:
            self.draw_cursor(self.bounding_box.x + self.shift_x)
            self.current_cursor_position = 0

        self.active = True
        self.DIGITS = "1234567890"
        self.select_listeners = []
        self.obfuscate_flag = False
        self.cursor_listeners = []

    def add_bgr(self):
        """ Add background rectangle """
        
        comp = Component(self.util, self.bounding_box)
        comp.name = self.name + ".bgr"
        comp.bgr = self.bgr
        self.add_component(comp)

    def draw_cursor(self, x):
        """ Draw cursor

        :param x: X coordinate of the cursor
        """
        txt = Component(self.util, self.bounding_box)
        txt.name = self.name + ".text"
        self.add_component(txt)
        gap_y = int((self.bounding_box.h - (self.bounding_box.h * 60 / 100)) / 2)
        rect = pygame.Rect(x, self.bounding_box.y + gap_y + 1, 1, self.bounding_box.h - (gap_y * 2))
        comp = Component(self.util, c=rect, bb=self.bounding_box, bgr=self.cursor_color, t=0)
        comp.name = "cursor"
        self.add_component(comp)
    
    def set_text(self, text, update=True, cursor_position=None):
        """ Set text and draw component
        
        :param text: text to set
        :param refresh: update screen
        """        
        self.text = text
        self.prepare_label(cursor_position)
        if update:
            self.clean_draw_update()
        
    def set_text_no_draw(self, text):
        """ Set text without drawing component
        
        :param text: text to set
        """
        self.text = text
        self.prepare_label()

    def obfuscate(self, state):
        """ Switch obfuscation on/off

        :param state: button state
        """
        self.obfuscate_flag = not self.obfuscate_flag
        self.prepare_label()
        self.clean_draw_update()

    def prepare_label(self, cursor_position=None):
        """ Prepare label component representing this output text. Used for web. """

        text = self.text
        if text is None:
            return

        if self.obfuscate_flag:
            text = "".join(["\u2022"] * len(self.text))

        if self.font == None:
            return

        size = self.font.size(text)
        label = self.font.render(text, 1, self.fgr)
        comp = Component(self.util, label)
        comp.name = self.name + ".text"
        text_length = size[0]

        delta = (size[0] + self.shift_x + 2) - self.bounding_box.w
        text_x = self.bounding_box.w - size[0] - self.shift_x

        if delta > 0: #overflow
            comp.content_x = self.bounding_box.w - size[0] - self.shift_x
            overflow = True
        else:
            comp.content_x = self.bounding_box.x + self.get_x(size)
            overflow = False

        comp.content_y = self.bounding_box.y + self.get_y(size)
        comp.text = text
        comp.text_size = self.default_font_size
        comp.fgr = self.fgr

        if len(self.components) == 1:
            self.add_component(comp)
        else:
            self.components[1] = comp

        if self.show_cursor:
            if cursor_position != None:
                self.current_cursor_position = cursor_position
                if not overflow:
                    txt = text[: self.current_cursor_position]
                    size = self.font.size(txt)
                    self.components[2].content.x = self.bounding_box.x + self.shift_x + size[0]
                else:
                    txt = text[: self.current_cursor_position]
                    size = self.font.size(txt)
                    self.components[2].content.x = text_x + size[0]
            else:
                if not overflow:
                    self.current_cursor_position += 1
                    txt = text[: self.current_cursor_position]
                    size = self.font.size(txt)
                    self.components[2].content.x = self.bounding_box.x + self.shift_x + size[0]
                else:
                    txt = text[: self.current_cursor_position]
                    size = self.font.size(txt)
                    self.components[2].content.x = comp.content_x + text_length
            
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
        if not obj: return t

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

    def add_select_listener(self, listener):
        """ Add select event listener
        
        :param listener: event listener
        """
        if listener not in self.select_listeners:
            self.select_listeners.append(listener)
            
    def notify_select_listeners(self):
        """ Notify select event listeners """
        
        for listener in self.select_listeners:
            listener()

    def add_cursor_listener(self, listener):
        """ Add cursor event listener

        :param listener: event listener
        """
        if listener not in self.cursor_listeners:
            self.cursor_listeners.append(listener)

    def notify_cursor_listeners(self):
        """ Notify cursor event listeners """

        for listener in self.cursor_listeners:
            listener(self.current_cursor_position)

    def handle_event(self, event):
        """ Handle event.

        :param event: the event to handle
        """
        if not self.visible: return

        mouse_event = event.type == pygame.MOUSEBUTTONUP and self.bounding_box.collidepoint(event.pos)
        keyboard_event = event.type == USER_EVENT_TYPE and event.sub_type == SUB_TYPE_KEYBOARD and event.action == pygame.KEYUP

        if self.show_cursor and self.visible and event.type == pygame.MOUSEBUTTONUP and getattr(self, "text", None):
            txt = getattr(self, "text", None)
            size = self.font.size(txt)
            delta = (size[0] + self.shift_x + 2) - self.bounding_box.w
            text_x = self.bounding_box.w - size[0] - self.shift_x

            if delta > 0: #overflow
                overflow = True
            else:
                overflow = False

            cursor_x = self.bounding_box.x + self.shift_x
            if event.pos[0] > cursor_x:
                prev_x = 0
                for n in range(len(txt) + 1):
                    size = self.font.size(txt[0 : n])
                    if overflow:
                        eol = text_x + size[0]
                    else:
                        eol = self.bounding_box.x + self.shift_x + size[0]

                    self.current_cursor_position = n
                    if event.pos[0] >= prev_x and event.pos[0] < eol:
                        cursor_x = eol
                        break
                    else:
                        prev_x = cursor_x = eol
                self.components[2].content.x = cursor_x
                self.clean_draw_update()
                self.notify_cursor_listeners()
            else:
                if not overflow:
                    self.components[2].content.x = self.bounding_box.x + self.shift_x
                    self.clean_draw_update()
                    self.current_cursor_position = -1
                    self.notify_cursor_listeners()
            
        if mouse_event or (keyboard_event and event.keyboard_key == kbd_keys[KEY_AUDIO]):
            self.notify_select_listeners()
