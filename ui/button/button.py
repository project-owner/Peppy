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

import pygame
from ui.component import Component
from ui.container import Container
from util.keys import USER_EVENT_TYPE, SUB_TYPE_KEYBOARD
from ui.layout.buttonlayout import ButtonLayout

class Button(Container):
    """ Base class for button functionality """
    
    def __init__(self, util, state):
        """ Initializer
        
        :param util: utility object
        :param state: button state
        """        
        self.util = util
        Container.__init__(self, util)
        self.set_state(state)
        self.press_listeners = list()
        self.release_listeners = list()
        self.bounding_box = state.bounding_box
        self.bgr = getattr(state, "bgr", (0, 0, 0))       
    
    def set_state(self, state):
        """ Set new button state
        
        :param state: new state
        """
        self.state = state
        self.components = []
        self.layout = ButtonLayout(state)
        self.show_img = getattr(state, "show_img", False)
        self.show_label = getattr(state, "show_label", False)
        
        self.add_background(state)
        self.add_image(state, self.layout.get_image_rectangle())
        self.add_label(state, self.layout.get_label_rectangle())
            
        self.name = None        
        self.auto_update = state.auto_update        
        self.selected = False
        self.clicked = False
    
    def add_background(self, state):
        """ Add button background bounding box
        
        :param state: button state
        """
        if not state.show_bgr:
            self.add_component(None)
            return
        c = Component(self.util)
        c.name = state.name + ".bgr"
        c.content = state.bounding_box
        c.bgr = c.fgr = getattr(state, "bgr", (0, 0, 0))
        c.content_x = state.bounding_box.x
        c.content_y = state.bounding_box.y
        self.add_component(c)
    
    def add_image(self, state, bb):
        """ Add image
        
        :param state: button state
        :param bb: bounding box
        """
        if not state.show_img:
            self.add_component(None)
            return        
        c = Component(self.util)
        c.name = state.name + ".image"
        scaled = getattr(state, "scaled", False)
        
        if scaled:    
            c.content = state.icon_base_scaled                 
        else:
            c.content = state.icon_base[1]
            
        c.image_filename = state.icon_base[0]
        w = c.content.get_size()[0]
        h = c.content.get_size()[1]
        c.content_x = bb.x + (bb.width - w)/2
        c.content_y = bb.y + (bb.height - h)/2
            
        self.add_component(c)
            
    def add_label(self, state, bb):
        """ Add button label
        
        :param state: button state
        :param bb: bounding box
        """
        if not self.show_label:
            self.add_component(None)
            return
        font_size = int((bb.h * state.label_text_height)/100.0)
        font = self.util.get_font(font_size)
        text = state.l_name
        size = font.size(text)
        label = font.render(text, 1, state.text_color_normal)
        c = Component(self.util, label)
        c.name = state.name + ".label"
        c.text = text
        c.text_size = font_size
        c.text_color_normal = state.text_color_normal
        c.text_color_selected = state.text_color_selected
        c.text_color_disabled = state.text_color_disabled
        c.text_color_current = c.text_color_normal
        c.content_x = bb.x + (bb.width - size[0])/2
        c.content_y = bb.y + (bb.height - size[1])/2
                
        if len(self.components) == 2:
            self.components.append(c)
        else:
            self.components[2] = c
    
    def set_img_coord(self):
        """ Center image in bounding box """
        
        c = self.components[1]
        bb = self.bounding_box
        img = c.content
        w = img.get_size()[0]
        h = img.get_size()[1]
        c.content_x = bb.x + (bb.width - w)/2
        c.content_y = bb.y + (bb.height - h)/2
        
    def add_press_listener(self, listener):
        """ Add button press listener
        
        :param listener: press button listener
        """
        if listener not in self.press_listeners:
            self.press_listeners.append(listener)
        
    def notify_press_listeners(self, state):
        """ Notify button press listeners
        
        :param state: button state
        """
        for listener in self.press_listeners:
            listener(state)
            
    def add_release_listener(self, listener):
        """ Add button release listener
        
        :param listener: release button listener
        """
        if listener not in self.release_listeners:
            self.release_listeners.append(listener)
        
    def notify_release_listeners(self, state):
        """ Notify button release listeners
        
        :param state: button state
        """
        for listener in self.release_listeners:
            listener(state)
    
    def set_selected(self, flag=False):
        """ Select button
        
        :param flag: selection flag True - selected, False - unselected
        """
        self.selected = flag
        
        if self.show_label:
            self.set_label()
            
        self.set_icon()
    
    def set_icon(self):
        """ Set icon as button component """
         
        scaled = getattr(self.state, "scaled", False)
        enabled = getattr(self.state, "enabled", True)
        if self.components[1]:
            self.components[1].content = self.get_icon(self.selected, scaled, enabled)
    
    def get_icon(self, selected, scaled, enabled):
        """ Get button icon
        
        :param selected: selection flag
        :param scaled: scaling flag
        :param enabled: enabled flag
        """
        icon_base = getattr(self.state, "icon_base", None)
        icon_base_scaled = getattr(self.state, "icon_base_scaled", None)
        icon_selected = getattr(self.state, "icon_selected", None)
        icon_selected_scaled = getattr(self.state, "icon_selected_scaled", None)
        icon_disabled = getattr(self.state, "icon_disabled", None)
        icon_disabled_scaled = getattr(self.state, "icon_disabled_scaled", None)
        
        if not enabled:
            if not scaled:
                return icon_disabled
            else:
                return icon_disabled_scaled
            
        if not selected:
            if not scaled:
                return icon_base
            else:
                return icon_base_scaled
        else:
            if not scaled:
                return icon_selected
            else:
                return icon_selected_scaled
    
    def set_label(self):
        """ Set label color depending on 'enabled' flag """
        
        enabled = getattr(self.state, "enabled", True)
        
        if enabled:
            if self.selected:
                self.components[2].text_color_current = self.components[2].text_color_selected                
            else:
                self.components[2].text_color_current = self.components[2].text_color_normal                        
        else:
            self.components[2].text_color_current = self.components[2].text_color_disabled
        font = self.util.get_font(self.components[2].text_size)
        self.components[2].content = font.render(self.state.l_name, 1, self.components[2].text_color_current)
                    
    def handle_event(self, event):
        """ Handle button event
        
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
        """ Mouse event dispatcher
        
        :param event: the event to handle
        """
        pos = event.pos
        
        if not self.state.bounding_box.collidepoint(pos):
            return
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:            
            self.press_action()            
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.clicked:
            self.release_action()
    
    def user_event_action(self, event):
        """ User event dispatcher
        
        :param event: the event to handle
        """
        if event.sub_type == SUB_TYPE_KEYBOARD and self.state.keyboard_key == event.keyboard_key:
            if event.action == pygame.KEYDOWN:
                self.press_action()
            elif event.action == pygame.KEYUP:
                self.release_action()  
        
    def press_action(self):
        """ Press button event handler """
        
        enabled = getattr(self.state, "enabled", True)
        if not enabled:
            return
        
        self.set_selected(True)
        self.clicked = True
        if self.auto_update:
            self.clean_draw_update()
        else:
            self.draw()
        self.notify_press_listeners(self.state)
    
    def release_action(self):
        """ Release button event handler """
         
        enabled = getattr(self.state, "enabled", True)
        if not enabled:
            return
        
        self.set_selected(False)
        self.clicked = False
        if self.auto_update:
            self.clean_draw_update()
        else:
            self.draw()
        self.notify_release_listeners(self.state)
    
    def set_enabled(self, flag):
        """ Set 'enabled' flag
        
        :param flag: True - enabled, False - disabled
        """
        self.state.enabled = flag
        self.set_selected(False)
           
