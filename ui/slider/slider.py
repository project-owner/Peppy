# Copyright 2016-2021 Peppy Player peppy.player@gmail.com
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

from util.keys import USER_EVENT_TYPE, SUB_TYPE_KEYBOARD, REST_EVENT_TYPE, SELECT_EVENT_TYPE, kbd_keys, \
    KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_VOLUME_UP, KEY_VOLUME_DOWN
from ui.component import Component
from ui.container import Container
from ui.state import State
from util.config import PLAYER_SETTINGS, PAUSE

HORIZONTAL = "1"
VERTICAL = "2"

class Slider(Container):
    """ Slider UI component """
    
    def __init__(self, util, name, bgr, slider_color, img_knob, img_knob_on, img_selected, key_incr, key_decr, key_knob, 
        bb, knob_selected=False, key_knob_alt=None, key_incr_alt=None, key_decr_alt=None, rest_commands=[]):
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
        :param knob_selected: True - knob selected, False - unselected
        :param key_knob_alt: alternative keyboard key associated with single click on knob
        :param key_incr_alt: alternative keyboard key associated with slider increment action
        :param key_decr_alt: alternative keyboard key associated with slider decrement action
        :param rest_command: the list of REST commands
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
        self.rest_commands = rest_commands
        
        self.knob_width = self.img_knob.get_size()[0]
        self.knob_height = self.img_knob.get_size()[1]
        self.knob_filename = img_knob[0]
        self.knob_on_filename = img_knob_on[0]
        self.dragging = False
        self.initial_level = 0
        self.check_pause = True
        self.handle_knob_events = True
        
        self.selected = False
        self.knob_selected = knob_selected
        if knob_selected:
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
        self.key_knob_alt = key_knob_alt
        self.key_incr_alt = key_incr_alt
        self.key_decr_alt = key_decr_alt
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

        # self.keyboard_keys = [self.key_incr, self.key_decr, self.key_knob]
        self.keyboard_keys = [self.key_knob]
        if self.key_knob_alt:
            self.keyboard_keys.append(self.key_knob_alt)
        if self.key_incr_alt:
            self.keyboard_keys.append(self.key_incr_alt)
        if self.key_decr_alt:
            self.keyboard_keys.append(self.key_decr_alt)
        # self.exit_keys = [kbd_keys[KEY_LEFT], kbd_keys[KEY_RIGHT]]
        self.exit_keys = [kbd_keys[KEY_LEFT], kbd_keys[KEY_RIGHT], kbd_keys[KEY_UP], kbd_keys[KEY_DOWN]]
        self.mouse_events = [pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION]
    
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
        if self.check_pause and self.util.config[PLAYER_SETTINGS][PAUSE] and event.type != USER_EVENT_TYPE:
            return

        if not self.visible:
            return        
        
        if event.type in self.mouse_events:
            self.mouse_action(event)
        elif event.type == USER_EVENT_TYPE:
            self.user_event_action(event)
        elif event.type == REST_EVENT_TYPE:
            self.rest_event_action(event)
        elif event.type == SELECT_EVENT_TYPE:
            self.rest_event_action(event)

    def mouse_action(self, event):
        """ Mouse event handler
        
        :param event: event to handle
        """
        pos = event.pos
        button_press_simulation = getattr(event, "p", None)
         
        if event.type == pygame.MOUSEBUTTONUP:
            if self.knob_selected:
                if self.orientation == HORIZONTAL and self.last_knob_position < pos[0] < (self.last_knob_position + self.knob_width) and pos[1] > self.bounding_box.y and self.dragging == False:
                    self.release_action(pos)
                    self.set_knob_on()       
            else:
                if self.clicked:
                    self.release_action(pos)
                    if not self.knob_selected:
                        self.set_knob_on()
        elif event.type == pygame.MOUSEBUTTONDOWN and self.bounding_box.collidepoint(pos):
            self.press_action()
        elif event.type == pygame.MOUSEMOTION and (pygame.mouse.get_pressed()[0] or button_press_simulation) and self.clicked:
            if not self.dragging and not self.bounding_box.collidepoint(pos):
                return
            else:
                self.motion_action(pos)

    def user_event_action(self, event):
        """ User event handler
        
        :param event: event to handle
        """
        k = event.keyboard_key
        if self.check_pause and self.util.config[PLAYER_SETTINGS][PAUSE] and k not in self.exit_keys:
            return

        if event.sub_type == SUB_TYPE_KEYBOARD:
            if k in self.keyboard_keys:
                self.keyboard_action(event)
            if k in self.exit_keys and self.selected and event.action == pygame.KEYUP:
                self.handle_exit(k)

    def rest_event_action(self, event):
        """ REST API call event dispatcher

        :param event: the event to handle
        """
        if len(self.rest_commands) > 0 and event.rest_command in self.rest_commands:
            c = event.rest_command
            if c == "mute":
                self.press_action()
                self.handle_knob_selection()
            elif c == "volume":
                v = event.value
                self.set_position(v)
                self.update_position()
                self.notify_slide_listeners()

    def keyboard_action(self, event):
        """ Keyboard event handler
        
        :param event: event to handle
        """
        knob_keys = [self.key_knob, self.key_knob_alt]

        if event.keyboard_key in knob_keys and self.handle_knob_events and self.selected:
            self.knob_event(event)
            return
         
        if event.action == pygame.KEYUP and self.selected:
            self.current_img = self.img_knob
            self.current_filename = self.knob_filename
            self.clicked = False
            self.update_position()
            self.update_knob_image()
            self.notify_slide_listeners()
            self.set_knob_on()
            return
        elif event.action == pygame.KEYDOWN and self.selected:
            self.press_action()
         
        if (event.keyboard_key == self.key_incr or event.keyboard_key == self.key_incr_alt) and self.selected:
            self.last_knob_position += self.step
        elif (event.keyboard_key == self.key_decr or event.keyboard_key == self.key_decr_alt) and self.selected:
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
        self.selected = True
        self.current_img = self.img_knob_on
        self.current_filename = self.knob_on_filename        
        self.update_knob_image()

    def set_knob_off(self):
        """ Set knob off without notifying listeners """
        
        self.clicked = False
        self.selected = False
        self.current_img = self.img_knob
        self.current_filename = self.knob_filename     
        self.update_knob_image()
            
    def press_action(self):
        """ Knob press event handler """
        
        if self.knob_selected and not self.clicked:
            return

        self.set_knob_on()
        self.notify_press_listeners()


    def get_knob_center(self):
        """ Return knob center coordinates

        :return: tuple (x, y)
        """
        knob = self.components[2]
        return (knob.content_x + int(self.knob_width / 2), knob.content_y + int(self.knob_height / 2))

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
        if (self.orientation == HORIZONTAL 
            and self.last_knob_position < pos[0] < (self.last_knob_position + self.knob_width)
            and pos[1] > self.bounding_box.y 
            and pos[1] < (self.bounding_box.y + self.bounding_box.h) 
            and self.dragging == False):
            self.handle_knob_selection()
            self.clicked = False
            return

        if self.dragging:
            self.dragging = False                    
        else:
            if not self.bounding_box.collidepoint(pos):
                self.clicked = False
                return

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
        self.dragging = True
        
        if self.orientation == HORIZONTAL:
            self.last_knob_position = pos[0] - self.knob_width/2
        else:
            self.last_knob_position = pos[1] - self.knob_height/2
        self.update_position()
        self.notify_motion_listeners()
   
    def handle_knob_selection(self, notify=True):
        """ Knob selection event handler """        
        
        self.selected = True

        if self.knob_selected or (not self.knob_selected and not self.img_selected):
            self.knob_selected = False
            self.set_knob_on()
        else:
            self.knob_selected = True
            self.current_img = self.img_selected
            self.update_knob_image()
            self.clicked = True

        if notify:
            self.notify_knob_listeners()

    def handle_exit(self, k):
        """ Exit slider

        :param k: the key
        """
        handled = False
        if (k == kbd_keys[KEY_UP] or k == kbd_keys[KEY_VOLUME_UP]) and self.exit_top_y:
            self.exit_top_bottom(self.exit_top_y)
            handled = True
        elif (k == kbd_keys[KEY_DOWN] or k == kbd_keys[KEY_VOLUME_DOWN]) and self.exit_bottom_y:
            self.exit_top_bottom(self.exit_bottom_y)
            handled = True
        elif k == kbd_keys[KEY_LEFT] and self.exit_left_x:
            self.exit_left_right(self.exit_left_x, self.exit_left_y)
            handled = True
        elif k == kbd_keys[KEY_RIGHT] and self.exit_right_x:
            self.exit_left_right(self.exit_right_x, self.exit_right_y)
            handled = True
        self.set_knob_off()
        self.clean_draw_update()
        return handled

    def exit_top_bottom(self, exit_border):
        """ Exit through top/bottom border

        :param exit_border: border to exit
        """
        if getattr(self, "exit_x", None):
            x = self.exit_x
        else:
            x = int(self.bounding_box.x + (self.bounding_box.w / 2))
        y = exit_border
        self.util.post_exit_event(x, y, self)

    def exit_left_right(self, x, y):
        """ Exit through left/right border

        :param exit_border: border to exit
        """
        self.util.post_exit_event(x, y, self)

    def set_selected(self, flag):
        """ Select/unselect slider

        :param flag: True - select, False - unselect
        """
        if not flag:
            self.set_knob_off()
        else:
            self.set_knob_on()
        self.clean_draw_update()

    def set_update_position(self, position):
        """ Combine set and update functions

        :param position: new position
        """
        self.set_position(position)
        self.update_position()

    def select_knob(self):
        """ Select knob """

        self.current_img = self.img_knob_on
        self.current_filename = self.knob_on_filename
        self.components[2].content = self.current_img
        self.components[2].image_filename = self.current_filename
        self.clicked = False
        self.selected = False
        self.knob_selected = False

    def unselect_knob(self):
        """ Unselect knob """

        self.current_img = self.img_knob
        self.current_filename = self.knob_filename
        self.components[2].content = self.current_img
        self.components[2].image_filename = self.current_filename
        self.clicked = False
        self.selected = False
        self.knob_selected = False
