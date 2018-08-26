# Copyright 2016-2018 Peppy Player peppy.player@gmail.com
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
import math

from ui.component import Component
from ui.container import Container
from util.keys import USER_EVENT_TYPE, SUB_TYPE_KEYBOARD, VOICE_EVENT_TYPE, KEY_VOICE_COMMAND, \
    MAXIMUM_FONT_SIZE, V_ALIGN, V_ALIGN_TOP, V_OFFSET
from ui.layout.buttonlayout import ButtonLayout

class Button(Container):
    """ Base class for button objects """
    
    def __init__(self, util, state):
        """ Initializer
        
        :param util: utility object
        :param state: button state
        """        
        self.util = util
        self.config = self.util.config
        Container.__init__(self, util)
        self.LABEL_PADDING = 6 
        self.set_state(state)
        self.press_listeners = []
        self.release_listeners = []
        self.label_listeners = []
        self.long_press_listeners = []
        self.bounding_box = state.bounding_box
        self.bgr = getattr(state, "bgr", (0, 0, 0))
        self.selected = None
        self.press_time = 0
        self.LONG_PRESS_TIME = 1000 # in milliseconds
    
    def set_state(self, state):
        """ Set new button state
        
        :param state: new state
        """
        self.state = state
        self.components = []
        self.layout = ButtonLayout(state)
        self.show_img = getattr(state, "show_img", False)
        self.show_label = getattr(state, "show_label", False)
        
        self.selected = False
        self.add_background(state)
        self.add_image(state, self.layout.get_image_rectangle())
        self.add_label(state, self.layout.get_label_rectangle())
            
        self.name = None        
        self.auto_update = state.auto_update        
        self.clicked = False
        
        self.state.event_origin = self
    
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
        if len(self.components) > 0:
            self.components[0] = c
        else:
            self.add_component(c)
    
    def add_image(self, state, bb):
        """ Add image
        
        :param state: button state
        :param bb: bounding box
        """
        if not state.show_img or getattr(state, "icon_base", None) == None:
            self.add_component(None)
            return        
        c = Component(self.util)
        c.name = state.name + ".image"
        scaled = getattr(state, "scaled", False)
        enabled = getattr(state, "enabled", True)
        
        if not enabled:
            c.content = state.icon_disabled[1]
            c.image_filename = state.icon_disabled[0]
        else:
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
        
        fixed_height = getattr(state, "fixed_height", None)
        if fixed_height:
            font_size = fixed_height
        else:
            font_size = int((bb.h * state.label_text_height)/100.0)
            
        if font_size > self.config[MAXIMUM_FONT_SIZE]:
            font_size = self.config[MAXIMUM_FONT_SIZE]
        
        font = self.util.get_font(font_size)
        text = self.truncate_long_labels(state.l_name, bb, font)
        state.l_name = text
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
        
        v_align = getattr(state, V_ALIGN, None)
        if v_align and v_align == V_ALIGN_TOP:
            v_offset = getattr(state, V_OFFSET, 0)
            if v_offset != 0:
                v_offset = int((bb.height / 100) * v_offset)
            c.content_y = bb.y - v_offset
        else:
            c.content_y = bb.y + (bb.height - size[1])/2 + 1        
                
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
    
    def add_label_listener(self, listener):
        """ Add label listener
        
        :param listener: label listener
        """
        if listener not in self.label_listeners:
            self.label_listeners.append(listener)
        
    def notify_label_listeners(self, state):
        """ Notify label listeners
        
        :param state: button state
        """
        for listener in self.label_listeners:
            listener(state)
            
    def add_long_press_listener(self, listener):
        """ Add long press listener
        
        :param listener: long press listener
        """
        if listener not in self.long_press_listeners:
            self.long_press_listeners.append(listener)
        
    def notify_long_press_listeners(self, state):
        """ Notify long press listeners
        
        :param state: button state
        """
        for listener in self.long_press_listeners:
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
            icon_selected = getattr(self.state, "icon_selected", None)
            if self.selected and icon_selected and isinstance(icon_selected, tuple):
                self.components[1].image_filename = icon_selected[0]
            elif not self.selected:
                icon_base = getattr(self.state, "icon_base", None)
                if isinstance(icon_base, tuple):
                    self.components[1].image_filename = icon_base[0]
    
    def get_icon(self, selected, scaled, enabled):
        """ Get button icon
        
        :param selected: selection flag
        :param scaled: scaling flag
        :param enabled: enabled flag
        """
        icon_base = getattr(self.state, "icon_base", None)
        icon_base_scaled = getattr(self.state, "icon_base_scaled", icon_base)
        icon_selected = getattr(self.state, "icon_selected", icon_base)        
        icon_selected_scaled = getattr(self.state, "icon_selected_scaled", icon_base_scaled)
        icon_disabled = getattr(self.state, "icon_disabled", icon_base)
        icon_disabled_scaled = getattr(self.state, "icon_disabled_scaled", icon_base)
        
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
        elif event.type == VOICE_EVENT_TYPE:
            self.voice_event_action(event)
    
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
        key = getattr(self.state, "keyboard_key", None)
        if event.sub_type == SUB_TYPE_KEYBOARD and key and key == event.keyboard_key:
            if event.action == pygame.KEYDOWN:
                self.press_action()
            elif event.action == pygame.KEYUP:
                self.release_action()
                
    def voice_event_action(self, event):
        """ Voice event dispatcher
        
        :param event: the event to handle
        """
        commands = getattr(self.state, "voice_commands", None)
        if commands and event.voice_command in commands:
            self.press_action()
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
        
        self.press_time = pygame.time.get_ticks()
    
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
        
        release_time = pygame.time.get_ticks()
        time_pressed = release_time - self.press_time
        if time_pressed >= self.LONG_PRESS_TIME:
            self.notify_long_press_listeners(self.state)
    
    def set_enabled(self, flag):
        """ Set 'enabled' flag
        
        :param flag: True - enabled, False - disabled
        """
        self.state.enabled = flag
        self.set_selected(False)
    
    def change_label(self, new_label):
        """ Set new label
        
        :param new_label: new label
        """
        self.state.l_name = new_label
        self.add_label(self.state, self.layout.get_label_rectangle())             
        self.clean_draw_update()
        self.notify_label_listeners(self.state)
    
    def truncate_long_labels(self, text, bb, font, truncated=False):
        """ Truncate long labels
        
        :param text: label text
        :param bb: bounding box
        :param font: label font
        :param truncated: True-truncate, False-don't truncate
        :return: 
        """
        if len(text) < 5:
            return text
        
        size = font.size(text)
        suffix = "..."
        dot_suffix_size = font.size(suffix)
        margin = (bb.width/100) * self.LABEL_PADDING
        text_width = size[0] + margin * 2
        
        if text_width >= bb.w:
            return self.truncate_long_labels(text[0 : -1], bb, font, True)
        else:
            if truncated:
                if size[0] + (margin * 2) + dot_suffix_size[0] >= bb.w:
                    return self.truncate_long_labels(text[0 : -1], bb, font, True)
                else:
                    return text + suffix
            else:
                return text 
