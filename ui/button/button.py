# Copyright 2016-2022 Peppy Player peppy.player@gmail.com
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
from util.keys import USER_EVENT_TYPE, SUB_TYPE_KEYBOARD, VOICE_EVENT_TYPE, SELECT_EVENT_TYPE, \
    MAXIMUM_FONT_SIZE, V_ALIGN, V_ALIGN_TOP, V_ALIGN_CENTER, V_ALIGN_BOTTOM, V_OFFSET, H_ALIGN, \
    H_ALIGN_LEFT, H_ALIGN_CENTER, H_ALIGN_RIGHT, REST_EVENT_TYPE, kbd_keys, KEY_LEFT, KEY_RIGHT, KEY_UP, \
    KEY_DOWN, KEY_SELECT

from util.config import USAGE, USE_LONG_PRESS_TIME
from ui.layout.buttonlayout import ButtonLayout

ELLIPSES = "..."

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
        self.set_state(state)
        self.press_listeners = []
        self.release_listeners = []
        self.label_listeners = []
        self.bounding_box = state.bounding_box
        self.bgr = getattr(state, "bgr", (0, 0, 0))
        self.selected = None
        self.press_time = 0
        self.LONG_PRESS_TIME = self.config[USAGE][USE_LONG_PRESS_TIME]
        self.parent_screen = None
        self.key_events = [kbd_keys[KEY_LEFT], kbd_keys[KEY_RIGHT], kbd_keys[KEY_UP], kbd_keys[KEY_DOWN]]
        self.enter_y = None
        self.ignore_enter_y = True
    
    def set_state(self, state):
        """ Set new button state
        
        :param state: new state
        """
        self.state = state
        self.components = []
        self.layout = ButtonLayout(state)
        self.show_img = getattr(state, "show_img", False)
        self.show_label = getattr(state, "show_label", False)
        self.wrap_labels = getattr(state, "wrap_labels", False)
        self.show_selection = getattr(state, "show_selection", False)
        
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
        
        if c.content and bb:
            c.content_x = bb.x + (bb.width - c.content.get_size()[0])/2
            c.content_y = bb.y + (bb.height - c.content.get_size()[1])/2

        self.add_component(c)
            
    def add_label(self, state, bb):
        """ Add button label
        
        :param state: button state
        :param bb: bounding box
        """
        if not self.show_label or bb == None:
            self.add_component(None)
            self.show_label = False
            return
        
        fixed_height = getattr(state, "fixed_height", None)
        if fixed_height:
            font_size = fixed_height
        else:
            font_size = int((bb.h * state.label_text_height)/100.0)
            
        if font_size > self.config[MAXIMUM_FONT_SIZE]:
            font_size = self.config[MAXIMUM_FONT_SIZE]
        
        if getattr(state, "show_img", False):
            padding = getattr(state, "padding", 5)
        else:
            padding = 0

        font = self.util.get_font(font_size)
        p_x = (bb.w / 100) * padding
        p_y = (bb.h / 100) * padding
        h_alignment = getattr(state, H_ALIGN, H_ALIGN_CENTER)
        if h_alignment != H_ALIGN_CENTER:
            r = pygame.Rect(bb.x + p_x, bb.y + p_y, bb.w - p_x * 2, bb.h - p_y * 2)
        else:
            r = pygame.Rect(bb.x, bb.y + p_y, bb.w, bb.h - p_y * 2)
        text = self.truncate_long_labels(state.l_name, r, font)

        if text.endswith(ELLIPSES) and not state.l_name.endswith(ELLIPSES) and self.wrap_labels:
            self.create_two_lines_label(state, r, font, font_size, state.l_name, text, padding)
        else:
            self.create_one_line_label(state, r, font, font_size, text, padding)

    def create_one_line_label(self, state, bb, font, font_size, text, padding):
        state.l_name = text
        size = font.size(text)

        if getattr(self, "selected", False):
            color = state.text_color_selected
        else:
            color = state.text_color_normal

        label = font.render(text, 1, color)
        c = Component(self.util, label)
        c.name = state.name + ".label"
        c.text = text
        c.text_size = font_size
        c.text_color_normal = state.text_color_normal
        c.text_color_selected = state.text_color_selected
        c.text_color_disabled = state.text_color_disabled
        c.text_color_current = color
        c.content_x = self.get_label_x(state, bb, size, padding)
        c.content_y = self.get_label_y(state, bb, size)
                
        if len(self.components) == 2:
            self.components.append(c)
        else:
            self.components[2] = c

    def create_two_lines_label(self, state, bb, font, font_size, text, text_with_ellipses, padding):
        length = len(text_with_ellipses) - 3
        first_line = text[0 : length]
        if first_line:
            first_line = first_line.strip()
        second_line = self.truncate_long_labels(text[length:], bb, font)
        if second_line:
            second_line = second_line.strip()

        size = font.size(first_line)
        label = font.render(first_line, 1, state.text_color_normal)
        c = Component(self.util, label)
        c.name = first_line + ".label"
        c.text = first_line
        c.text_size = font_size
        c.text_color_normal = state.text_color_normal
        c.text_color_selected = state.text_color_selected
        c.text_color_disabled = state.text_color_disabled
        c.text_color_current = c.text_color_normal
        c.content_x = self.get_label_x(state, bb, size, padding)
        padding = (bb.h / 100) * 5
        c.content_y = bb.y + padding
        if len(self.components) == 2:
            self.components.append(c)
        else:
            self.components[2] = c
        x = c.content_x

        f_size = font_size - int((font_size / 100) * 20)
        f = self.util.get_font(f_size)
        s = font.size(second_line)
        label = f.render(second_line, 1, state.text_color_disabled)
        c = Component(self.util, label)
        c.name = second_line + ".label"
        c.text = second_line
        c.text_size = f_size
        c.text_color_normal = state.text_color_disabled
        c.text_color_selected = state.text_color_selected
        c.text_color_disabled = state.text_color_disabled
        c.text_color_current = c.text_color_disabled
        c.content_x = x
        c.content_y = padding * 2 + bb.y + s[1] - s[1]/3
        self.components.append(c)

    def get_label_x(self, state, bb, size, padding):
        label_padding = (bb.w / 100) * padding
        h_align = getattr(state, H_ALIGN, H_ALIGN_CENTER)
        if h_align == H_ALIGN_LEFT:
            return bb.x
        elif h_align == H_ALIGN_RIGHT:
            return bb.x + bb.width - size[0] - label_padding
        else:
            return bb.x + (bb.width - size[0])/2

    def get_label_y(self, state, bb, size):
        v_align = getattr(state, V_ALIGN, V_ALIGN_CENTER)
        if v_align == V_ALIGN_TOP:
            v_offset = getattr(state, V_OFFSET, 0)
            if v_offset != 0:
                v_offset = int((bb.height / 100) * v_offset)
            return bb.y - v_offset
        elif v_align == V_ALIGN_BOTTOM:
            content_y = bb.y + bb.height - size[1]
            v_offset = getattr(state, V_OFFSET, 0)
            if v_offset != 0:
                content_y += v_offset
            return content_y
        else:
            d = math.ceil((bb.height - size[1])/2) + 2
            return bb.y + d

    def add_selection(self, state, bb):
        if not self.selected:
            return

        border = 2
        c = Component(self.util, t=border)
        c.name = state.name + ".selection"
        x = state.bounding_box.x + border/2
        y = state.bounding_box.y + border/2
        w = state.bounding_box.w - border
        h = state.bounding_box.h - border
        c.content = pygame.Rect(x, y, w, h)
        c.bgr = state.text_color_selected
        c.fgr = (0, 0, 0, 0)

        c.content_x = state.bounding_box.x
        c.content_y = state.bounding_box.y
        self.add_component(c)

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
        if listener and listener not in self.release_listeners:
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
            
    def set_selected(self, flag=False):
        """ Select button
        
        :param flag: selection flag True - selected, False - unselected
        """
        self.selected = flag
        
        if self.show_label:
            self.set_label()

        if self.selected:
            if self.show_selection:
                self.add_selection(self.state, self.bounding_box)
        else:
            length = len(self.components)
            c = self.components[length - 1]
            if c and c.name.endswith(".selection"):
                del self.components[length - 1]
            
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

        if self.show_selection:
            num = len(self.components) - 1
        else:
            num = len(self.components)
        
        if enabled:
            if self.selected:
                self.components[2].text_color_current = self.components[2].text_color_selected
                if num == 4:
                    self.components[2].text_color_current = self.components[2].text_color_selected
            else:
                self.components[2].text_color_current = self.components[2].text_color_normal
                if num == 4:
                    self.components[2].text_color_current = self.components[2].text_color_normal
        else:
            self.components[2].text_color_current = self.components[2].text_color_disabled
            if num == 4:
                self.components[2].text_color_current = self.components[2].text_color_disabled

        # Selected
        if num == 4:
            font = self.util.get_font(self.components[2].text_size)
            self.components[2].content = font.render(self.components[2].text, 1, self.components[2].text_color_current)
            font = self.util.get_font(self.components[num - 2].text_size)
            self.components[2].content = font.render(self.components[2].text, 1, self.components[2].text_color_current)
        else:
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
            k = event.keyboard_key
            if k in self.key_events and self.selected and event.action == pygame.KEYUP:
                self.handle_exit(k)
            elif k == kbd_keys[KEY_SELECT] and self.selected and event.action == pygame.KEYDOWN:
                self.press_action()
            elif k == kbd_keys[KEY_SELECT] and self.selected and event.action == pygame.KEYUP:
                self.release_action(False)
            else:
                self.user_event_action(event)
        elif event.type == VOICE_EVENT_TYPE:
            self.voice_event_action(event)
        elif event.type == REST_EVENT_TYPE:
            self.rest_event_action(event)
        elif event.type == SELECT_EVENT_TYPE:
            if not self.selected:
                self.select_action(event.x, event.y)
    
    def handle_exit(self, k):
        """ Handle button exit

        :param k: the key
        """
        if k == kbd_keys[KEY_UP] and self.exit_top_y:
            self.exit_top(self.exit_top_y)
        elif k == kbd_keys[KEY_DOWN] and self.exit_bottom_y:
            self.exit_bottom(self.exit_bottom_y)
        elif k == kbd_keys[KEY_LEFT] and self.exit_left_x:
            if not self.ignore_enter_y and self.enter_y != None:
                y = self.enter_y
            else:
                y = getattr(self, "exit_left_y", None)
            self.exit_left_right(self.exit_left_x, y)
            self.enter_y = None
        elif k == kbd_keys[KEY_RIGHT] and self.exit_right_x:
            if not self.ignore_enter_y and self.enter_y != None:
                y = self.enter_y
            else:
                y = getattr(self, "exit_right_y", None)
            self.exit_left_right(self.exit_right_x, y)
            self.enter_y = None

    def exit_top(self, exit_border):
        """ Exit through top border

        :param exit_border: border to exit
        """
        self.set_selected(False)
        if getattr(self, "exit_top_x", None):
            x = self.exit_top_x
        elif getattr(self, "exit_x", None):
            x = self.exit_x
        else:
            x = int(self.bounding_box.x + (self.bounding_box.w / 2))
        y = exit_border
        self.util.post_exit_event(x, y, self)
        self.clean_draw_update()

    def exit_bottom(self, exit_border):
        """ Exit through bottom border

        :param exit_border: border to exit
        """
        self.set_selected(False)
        if getattr(self, "exit_bottom_x", None):
            x = self.exit_bottom_x
        elif getattr(self, "exit_x", None):
            x = self.exit_x
        else:
            x = int(self.bounding_box.x + (self.bounding_box.w / 2))
        y = exit_border
        self.util.post_exit_event(x, y, self)
        self.clean_draw_update()

    def exit_left_right(self, exit_border, exit_border_y=None):
        """ Exit through left/right border

        :param exit_border: border to exit
        """
        self.set_selected(False)
        x = exit_border
        if exit_border_y:
            y = exit_border_y
        elif getattr(self, "exit_y", None):
            y = self.exit_y
        else:
            y = self.bounding_box.y + (self.bounding_box.h / 2)
        self.util.post_exit_event(x, y, self)
        self.clean_draw_update()

    def select_action(self, x, y):
        """ Handle select action

        :param x: x coordinate
        :param y: y coordinate
        """
        self.enter_y = y
        fit_1 = self.state.bounding_box.collidepoint((x, y))
        fit_2 = self.state.bounding_box.collidepoint((x - 1, y)) # if between components

        if not(fit_1 or fit_2):
            return

        self.set_selected(True)
        self.clean_draw_update()
        if getattr(self, "redraw_observer", None):
            self.redraw_observer()

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
            self.release_action(False)
    
    def user_event_action(self, event):
        """ User event dispatcher
        
        :param event: the event to handle
        """
        key = getattr(self.state, "keyboard_key", None)
        if event.sub_type == SUB_TYPE_KEYBOARD and key and key == event.keyboard_key:
            if event.action == pygame.KEYDOWN:
                self.press_action()
            elif event.action == pygame.KEYUP:
                self.release_action(False)
                
    def voice_event_action(self, event):
        """ Voice event dispatcher
        
        :param event: the event to handle
        """
        commands = getattr(self.state, "voice_commands", None)
        if commands and event.voice_command in commands:
            self.press_action()
            self.release_action(False)

    def rest_event_action(self, event):
        """ REST API call event dispatcher

        :param event: the event to handle
        """
        commands = getattr(self.state, "rest_commands", None)
        if commands and event.rest_command in commands:
            self.press_action()
            self.release_action(False)  
        
    def press_action(self):
        """ Press button event handler """
        
        enabled = getattr(self.state, "enabled", True)
        if not enabled or self.clicked:
            return
        
        self.set_selected(True)
        self.clicked = True
        if self.auto_update:
            self.clean_draw_update()
        else:
            self.draw()
        self.notify_press_listeners(self.state)
        
        self.press_time = pygame.time.get_ticks()
    
    def release_action(self, unselect=True):
        """ Release button event handler """
         
        enabled = getattr(self.state, "enabled", True)
        if not enabled:
            return
        
        if unselect:
            self.set_selected(False)
        else:
            self.set_selected(True)
        self.clicked = False
        if self.auto_update:
            self.clean_draw_update()
        else:
            self.draw()
        
        release_time = pygame.time.get_ticks()
        time_pressed = release_time - self.press_time

        if time_pressed >= self.LONG_PRESS_TIME:
            self.state.long_press = True
        else:
            self.state.long_press = False
            
        self.notify_release_listeners(self.state)
    
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
        ellipses_size = font.size(ELLIPSES)
        text_width = size[0]
        
        if text_width >= bb.w:
            return self.truncate_long_labels(text[0 : -1], bb, font, True)
        else:
            if truncated:
                if size[0] + ellipses_size[0] >= bb.w:
                    return self.truncate_long_labels(text[0 : -1], bb, font, True)
                else:
                    return text + ELLIPSES
            else:
                return text 
