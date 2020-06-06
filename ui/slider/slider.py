# Copyright 2016-2020 Peppy Player peppy.player@gmail.com
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
# along with Peppy Player.  If not, see <http://www.gnu.org/licenses/>.

import pygame
import math

from util.keys import USER_EVENT_TYPE, SUB_TYPE_KEYBOARD
from ui.component import Component
from ui.container import Container
from ui.state import State
from util.config import PLAYER_SETTINGS, PAUSE

HORIZONTAL = "1"
VERTICAL = "2"

class Slider(Container):
    """ Slider UI component """
    
    def __init__(self, util, name, bgr, slider_color, img_knob, img_knob_on, img_selected, key_incr, key_decr, key_knob, bb, knob_selected=False):
        """ Initializer
        
        :param util: utility object
        :param name: slider name
        :param bgr: slider background color
        :param slider_color: slider center line color
        :param img_knob: knob image
        :param img_knob_on: knob image in on state
        :param img_selected: knob image in selected state
        :param key_incr: keyboard key associated with slider increment action
        :param key_decr: keyboard key associated with slider decrement action
        :param key_knob: keyboard key associated with single click on knob
        :param bb: slider bounding box
        """
        Container.__init__(self, util, background=bgr, bounding_box=bb)
        self.content = None
        if bb.h > bb.w:
            self.orientation = VERTICAL
        else:
            self.orientation = HORIZONTAL 
        self.util = util
        self.name = name
        self.img_knob = img_knob[1]
        self.img_knob_on = img_knob_on[1]
        self.img_selected = img_selected
        
        self.knob_width = self.img_knob.get_size()[0]
        self.knob_height = self.img_knob.get_size()[1]
        self.knob_filename = img_knob[0]
        self.knob_on_filename = img_knob_on[0]
        self.dragging = False
        self.initial_level = 0
        self.check_pause = True
        self.handle_knob_events = True
        
        self.selected = False
        if knob_selected:
            self.selected = knob_selected
            self.current_img = self.img_selected[1]
        else:
            self.current_img = self.img_knob
        
        self.current_filename = self.knob_filename
        self.clicked = False
        self.press_listeners = list()
        self.slide_listeners = list()
        self.knob_listeners = list()
        self.motion_listeners = list()
        pygame.key.set_repeat(50, 10)
        self.step = 10
        self.key_incr = key_incr
        self.key_decr = key_decr
        self.key_knob = key_knob
        h = self.current_img.get_size()[1]
        
        if self.orientation == HORIZONTAL:
            slider_x = self.bounding_box.x + self.knob_width/2
            slider_y = self.bounding_box.y + self.bounding_box.height/2
            slider_width = self.bounding_box.width - self.knob_width
            slider_height = 1
            self.slider = pygame.Rect(slider_x, slider_y, slider_width, slider_height)
            self.slider_max_x = self.bounding_box.x + self.bounding_box.width - self.knob_width/2
            self.slider_min_x = self.bounding_box.x + self.knob_width/2
            self.slide_increment = (self.slider_max_x - self.slider_min_x)/100.0
            self.last_knob_position = bb.x
            self.knob_y = self.bounding_box.y + self.bounding_box.height/2 - self.knob_height/2
        else:
            slider_x = self.bounding_box.x + self.bounding_box.width/2 - 1
            slider_y = self.bounding_box.y + self.knob_height/2
            slider_width = 1
            slider_height = self.bounding_box.height - self.knob_height
            self.slider = pygame.Rect(slider_x, slider_y, slider_width, slider_height)
            self.slider_max_y = self.bounding_box.y + self.bounding_box.height - self.knob_height/2
            self.slider_min_y = self.bounding_box.y + self.knob_height/2
            self.slide_increment = (self.slider_max_y - self.slider_min_y)/100.0
            self.last_knob_position = bb.y + bb.h - self.knob_height
            self.knob_x = self.bounding_box.x + self.bounding_box.width/2 - self.knob_width/2
        
        comp = Component(self.util, self.bounding_box)
        comp.name = self.name + ".bgr"
        comp.bgr = bgr
        self.add_component(comp)
        
        comp = Component(self.util, self.slider)
        comp.name = self.name + ".slider"
        comp.thickness = 1
        comp.content_x = slider_x
        comp.content_y = slider_y
        comp.bgr = slider_color
        self.add_component(comp)
        
        comp = Component(self.util, self.current_img)
        comp.name = self.name + ".knob"
        
        if self.orientation == HORIZONTAL:
            comp.content_x = bb.x
            comp.content_y = bb.y + (bb.h - h)/2 + 1
        else:
            comp.content_x = self.knob_x
            comp.content_y = self.last_knob_position
            
        comp.image_filename = self.knob_filename
        self.add_component(comp)
    
    def add_press_listener(self, listener):
        """ Add press event listener
        
        :param listener: the listener
        """
        if listener not in self.press_listeners:
            self.press_listeners.append(listener)
            
    def notify_press_listeners(self):
        """ Notify all press event listeners """ 
        
        state = State()
        state.event_origin = self
        state.position = self.get_position()     
        for listener in self.press_listeners:
            listener(state)
    
    def add_slide_listener(self, listener):
        """ Add event listener for clicking on slider line
        
        :param listener: the listener
        """
        if listener not in self.slide_listeners:
            self.slide_listeners.append(listener)
            
    def notify_slide_listeners(self):
        """ Notify event listeners for clicking on slider line event """ 

        state = State()
        state.event_origin = self
        state.position = self.get_position()              
        for listener in self.slide_listeners:
            listener(state)
                
    def add_knob_listener(self, listener):
        """ Add knob event listener
        
        :param listener: the listener
        """
        if not self.handle_knob_events:
            return

        if listener not in self.knob_listeners:
            self.knob_listeners.append(listener)
            
    def notify_knob_listeners(self):
        """ Notify all knob event listeners """ 
        
        if not self.handle_knob_events:
            return

        for listener in self.knob_listeners:
            n = listener.__name__
            if "mute" in n:
                listener()
            elif "update_web_ui" in n:
                state = State()
                state.event_origin = self
                listener(state)
            else:
                listener(self.get_position())
            
    def add_motion_listener(self, listener):
        """ Add motion event listener
        
        :param listener: the listener
        """
        if listener not in self.motion_listeners:
            self.motion_listeners.append(listener)
            
    def notify_motion_listeners(self):
        """ Notify all motion event listeners """
        
        state = State()
        state.event_origin = self
        state.position = self.get_position() 
        for listener in self.motion_listeners:
            listener(state)        
    
    def set_position(self, position):
        """ Set knob position
        
        :param position: new knob position
        """
        if self.orientation == HORIZONTAL:
            self.set_horizontal_position(position)
        else:
            self.set_vertical_position(position)
             
    def set_horizontal_position(self, position):
        """ Set horizontal knob position
        
        :param position: new knob position
        """
        level = int(position * self.slide_increment)
        if level < 0:
            self.last_knob_position = self.bounding_box.x
        elif level > (100 * self.slide_increment):
            self.last_knob_position = self.slider_max_x - self.knob_width/2
        else:
            self.last_knob_position = level + self.bounding_box.x
            
    def set_vertical_position(self, position):
        """ Set vertical knob position
        
        :param position: new knob position
        """
        level = int(position * self.slide_increment)
        if level < 0:
            self.last_knob_position = self.bounding_box.y + self.bounding_box.height
        elif level > (100 * self.slide_increment):
            self.last_knob_position = self.slider_max_y - self.knob_height/2
        else:
            self.last_knob_position = int(self.bounding_box.y + self.bounding_box.height - level - self.knob_height)
    
    def get_position(self):
        """ Return the current knob position
        
        :return: knob position in range 0-100
        """
        if self.orientation == HORIZONTAL:
            level = int((self.last_knob_position - self.bounding_box.x) / self.slide_increment)
        else:
            level = math.ceil(100.0 - (self.last_knob_position - self.bounding_box.y) / self.slide_increment)
        
        if level < 0:
            return 0
        elif level > 100:
            return 100
        else:
            return level
        
    def update_position(self):
        """ Update the knob position - redraw slider """
        
        if self.orientation == HORIZONTAL:
            self.update_horizontal_position()
        else:
            self.update_vertical_position()
        
        self.draw()
        self.update()        
    
    def update_horizontal_position(self):
        """ Update slider position when orientation is horizontal """
        
        if self.last_knob_position > self.slider_max_x - self.knob_width/2:
            self.last_knob_position = self.slider_max_x - self.knob_width/2
        elif self.last_knob_position <= self.bounding_box.x:
            self.last_knob_position = self.bounding_box.x
        
        x = self.last_knob_position        
        self.clean()
        knob = self.components[2]
        knob.content_x = x
        
    def update_vertical_position(self):
        """ Update slider position when orientation is vertical """
        
        if self.last_knob_position > self.slider_max_y - self.knob_height/2:
            self.last_knob_position = self.slider_max_y - self.knob_height/2
        elif self.last_knob_position <= self.bounding_box.y:
            self.last_knob_position = self.bounding_box.y
        
        y = self.last_knob_position        
        self.clean()
        knob = self.components[2]
        knob.content_y = y
    
    def handle_event(self, event):
        """ Slider event handler
        
        :param event: event to handle
        """
        if self.check_pause and self.util.config[PLAYER_SETTINGS][PAUSE]:
            return

        if not self.visible:
            return
        mouse_events = [pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION]        
        
        if event.type in mouse_events:
            self.mouse_action(event)
        elif event.type == USER_EVENT_TYPE:
            self.user_event_action(event)

    def mouse_action(self, event):
        """ Mouse event handler
        
        :param event: event to handle
        """
        pos = event.pos
        
        if self.selected and not(self.last_knob_position < pos[0] < self.last_knob_position + self.knob_width and pos[1] > self.bounding_box.y) and \
            event.type != pygame.KEYUP and self.handle_knob_events:
            return
        
        button_press_simulation = getattr(event, "p", None)
         
        if event.type == pygame.MOUSEBUTTONUP:
            if self.clicked:            
                self.release_action(pos)
            else:
                pass                
        elif event.type == pygame.MOUSEBUTTONDOWN and self.bounding_box.collidepoint(pos):
            self.press_action()            
        elif event.type == pygame.MOUSEMOTION and (pygame.mouse.get_pressed()[0] or button_press_simulation) and self.clicked:
            self.motion_action(pos)

    def user_event_action(self, event):
        """ User event handler
        
        :param event: event to handle
        """
        keyboard_keys = [self.key_incr, self.key_decr, self.key_knob]
        
        if event.sub_type == SUB_TYPE_KEYBOARD and (event.keyboard_key in keyboard_keys):
            self.keyboard_action(event)

    def keyboard_action(self, event):
        """ Keyboard event handler
        
        :param event: event to handle
        """
        if event.keyboard_key == self.key_knob and self.handle_knob_events:
            self.knob_event(event)
            return
         
        if event.action == pygame.KEYUP:
            self.current_img = self.img_knob
            self.current_filename = self.knob_filename
            self.clicked = False
            self.update_position()
            self.update_knob_image()
            self.notify_slide_listeners()
            return
        elif event.action == pygame.KEYDOWN:
            self.press_action()
         
        if event.keyboard_key == self.key_incr:
            self.last_knob_position += self.step
        elif event.keyboard_key == self.key_decr:
            self.last_knob_position -= self.step
 
        if self.img_selected:
            self.current_img = self.img_selected
        else:
            self.current_img = self.img_knob_on
    
    def knob_event(self, event):
        """ Knob event handler
        
        :param event: event to handle
        """
        if event.action == pygame.KEYDOWN:
            self.press_action()
        elif event.action == pygame.KEYUP:
            self.handle_knob_selection()
    
    def set_knob_on(self):
        """ Set knob on without notifying listeners """
        
        self.clicked = True
        self.current_img = self.img_knob_on
        self.current_filename = self.knob_on_filename        
        self.update_knob_image()
        
    def set_knob_off(self):
        """ Set knob off without notifying listeners """
        
        self.clicked = False
        self.current_img = self.img_knob
        self.current_filename = self.knob_filename     
        self.update_knob_image()
            
    def press_action(self):
        """ Knob press event handler """
        
        self.set_knob_on()
        self.notify_press_listeners()

    def update_knob_image(self):
        """ Update knob image """
        
        knob = self.components[2]
        knob.content = self.current_img
        knob.image_filename = self.current_filename
        self.update_position()

    def release_action(self, pos):
        """ Knob release event handler
        
        :param pos: new knob position
        """
        if self.orientation == HORIZONTAL and self.last_knob_position < pos[0] < (self.last_knob_position + self.knob_width) and pos[1] > self.bounding_box.y and self.dragging == False:
            self.handle_knob_selection()
            self.clicked = False
            return

        if self.dragging:
            self.dragging = False                    
        else:
            if self.orientation == HORIZONTAL:
                if self.last_knob_position != pos[0]:
                    self.last_knob_position = pos[0] - self.knob_width/2
            else:
                if self.last_knob_position != pos[1]:
                    self.last_knob_position = pos[1] - self.knob_height/2
                    
        self.current_img = self.img_knob
        self.current_filename = self.knob_filename
        self.clicked = False
        self.update_knob_image()        
        self.notify_slide_listeners()
        
    def motion_action(self, pos):
        """ Knob motion event handler
        
        :param pos: new knob position
        """ 
        if self.selected == True:
            if self.img_selected:
                self.current_img = self.img_selected
            else:
                self.current_img = self.img_knob_on            
            return
        else:
            self.current_img = self.img_knob_on
            self.current_filename = self.knob_on_filename
        self.dragging = True
        
        if self.orientation == HORIZONTAL:
            self.last_knob_position = pos[0] - self.knob_width/2
        else:
            self.last_knob_position = pos[1] - self.knob_height/2
        self.update_position()
        self.notify_motion_listeners()
   
    def handle_knob_selection(self):
        """ Knob selection event handler """        
        
        if self.selected or (not self.selected and not self.img_selected):
            self.selected = False
            self.current_img = self.img_knob
            self.current_filename = self.knob_filename
            self.update_knob_image()
        else:    
            self.selected = True
            self.current_img = self.img_selected
            self.update_knob_image() 
            
        self.notify_knob_listeners()
        
