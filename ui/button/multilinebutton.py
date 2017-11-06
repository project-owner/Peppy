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

import pygame

from ui.component import Component
from ui.button.button import Button
from ui.layout.multilinebuttonlayout import LINES
from util.keys import USER_EVENT_TYPE

class MultiLineButton(Button):
    """ Multi-line button class """
    
    def __init__(self, util, state, padding=2):
        """ Initializer
        
        :param util: utility object
        :param state: button state 
        """
        self.state = state
        self.config = util.config
        self.padding = padding
        Button.__init__(self, util, self.state)
        
    def set_state(self, state):
        """ Set new button state
        
        :param state: new state
        """
        self.state = state
        self.components = []
        self.layout = self.state.layout
        self.show_img = getattr(state, "show_img", False)
        self.show_label = getattr(state, "show_label", False)
        labels = state.name
        self.text_color_normal = state.text_color_normal
        self.text_color_selected = state.text_color_selected
        self.text_color_disabled = state.text_color_disabled
        
        state.name = state.l_name
        
        self.add_background(state)
        r = self.layout.get_image_rectangle()
        
        self.add_image(state, r)
        self.state.label_text_height = self.layout.line_h      
        
        for k, v in labels.items():
            state.l_name = v
            next_label = None
            previous_label = None
            if k == 0:
                try:
                    next_label = labels[1]                    
                except:
                    pass
                if next_label == None:
                    r = self.layout.get_joint_label_rectangle(k)
                else:
                    r = self.layout.get_label_rectangle(k)
            elif k == (LINES - 1):
                try:
                    previous_label = labels[k - 1]                    
                except:
                    pass
                if previous_label == None:                 
                    r = self.layout.get_joint_label_rectangle(k - 1)
                else:
                    r = self.layout.get_label_rectangle(k)
            elif k == (LINES - 2):
                try:
                    next_label = labels[k + 1]                    
                except:
                    pass
                if next_label == None:                 
                    r = self.layout.get_joint_label_rectangle(k)
                else:
                    r = self.layout.get_label_rectangle(k)
            else:
                r = self.layout.get_label_rectangle(k)
            self.add_label(self.state, r)
            
        self.name = None        
        self.auto_update = state.auto_update        
        self.selected = False
        self.clicked = False
        
    def add_label(self, state, bb):
        """ Add button label
        
        :param state: button state
        :param bb: bounding box
        """
        if not self.show_label:
            self.add_component(None)
            return
        font_size = int(state.label_text_height)
        font = self.util.get_font(font_size)
        
        label = state.l_name
        
        text = self.truncate_long_labels(label, bb, font)
        size = font.size(text)
        rendered_label = font.render(text, 1, self.text_color_normal)
        c = Component(self.util, rendered_label)
        c.name = label + ".label"
        c.text = text
        c.text_size = font_size
        c.text_color_normal = self.text_color_normal
        c.text_color_selected = self.text_color_selected
        c.text_color_disabled = self.text_color_disabled
        c.text_color_current = c.text_color_normal
        c.content_x = bb.x + (bb.width - size[0])/2
        c.content_y = bb.y + (bb.height - size[1])/2 + self.padding * 1.5               
        self.components.append(c)
        
    def handle_event(self, event):
        """ Button event dispatcher
        
        :param event: the event to handle
        """
        if not self.visible:
            return        
        mouse_events = [pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN]                
        if event.type in mouse_events:
            self.mouse_action(event)
        elif event.type == USER_EVENT_TYPE:
            self.user_event_action(event)

    def mouse_action(self, event):
        """ Mouse event handler
        
        :param event: the event to handle
        """
        pos = event.pos        
        if self.bounding_box.collidepoint(pos) and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:            
            self.press_action()
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.clicked:
            self.release_action()
            
    def press_action(self):
        """ Button press event handler """
        
        self.set_selected(True)
        self.clicked = True
        super(MultiLineButton, self).clean_draw_update()
        self.notify_press_listeners(self.state)

    def release_action(self):
        """ Button release event handler """
        
        self.set_selected(False)
        self.clicked = False
        super(MultiLineButton, self).clean_draw_update()
        self.notify_release_listeners(self.state)
        
    def set_selected(self, flag=False):
        """ Select button
        
        :param flag: selection flag True - selected, False - unselected
        """
        self.selected = flag
        
        if self.show_label:
            self.set_label_color()
        
    def set_label_color(self):
        """ Set label color depending on 'enabled' flag """
        
        comps = self.components[2:]
        if self.selected:
            self.components[0].bgr = self.state.bgr_selected
        else:
            self.components[0].bgr = self.state.bgr
            
        for comp in comps:
            if self.selected:
                comp.text_color_current = comp.text_color_selected                
            else:
                comp.text_color_current = comp.text_color_normal                          
            font = self.util.get_font(comp.text_size)
            comp.content = font.render(comp.text, 1, comp.text_color_current)
        
