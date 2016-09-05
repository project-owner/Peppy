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
from ui.container import Container
from ui.layout.gridlayout import GridLayout
from ui.factory import Factory
from operator import attrgetter
from util.keys import USER_EVENT_TYPE, SUB_TYPE_KEYBOARD, kbd_keys, \
    KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN, KEY_SELECT

class Menu(Container):
    """ Base class for all menu components.     
    Extends Component class. 
    Consists of Button components 
    """    
    def __init__(self, util, bgr=None, bb=None, rows=3, cols=3, create_item_method=None):
        """ Initializer
        
        :param util: utility object
        :param bgr: menu background
        :param bb: bounding box
        :param rows: number of rows in menu
        :param cols: number of columns in menu
        :param create_item_method: factory method for menu item creation
        """        
        Container.__init__(self, util, bb, bgr)
        self.rows = rows
        self.cols = cols
        self.start_listeners = []
        self.move_listeners = []
        self.layout = GridLayout(bb)
        self.layout.set_pixel_constraints(self.rows, self.cols, 1, 1)        
        self.items = {}
        self.buttons = {}
        self.factory = Factory(util)
        self.create_item_method = create_item_method
        self.selected_index = None
        
    def set_items(self, it, page_index, listener, scale=True, order=None):
        """ Set menu items
        
        :param it: menu items
        :param page_index: menu page number
        :param listener: event listener
        :param scale: True - scale menu items, False - don't scale menu items
        :param order: map defining the order or menu items
        """
        self.layout.current_constraints = 0
        self.components = []
        self.items = it        
        self.buttons = dict()
        if not order:
            sorted_items = sorted(it.values(), key=attrgetter('index'))
        else:
            sorted_items = self.sort_items(it.items(), order)         
        
        for index, item in enumerate(sorted_items):
            i = getattr(item, "index", None)
            if not i:
                item.index = index
            constr = self.layout.get_next_constraints()
            button = self.create_item_method(item, constr, listener, scale)
            button.add_release_listener(self.item_selected)
            comp_name = ""
            if item.name:
                comp_name = item.name
            self.add_component(button)
            self.buttons[comp_name] = button

    def sort_items(self, d, order):
        """ Sort items according to the specified order
        
        :param d: items to sort
        :param order: order of menu items
        """
        sorted_items = [None] * len(d)
        for t in d:
            k = t[0]
            index = int(order[k.lower()]) - 1            
            sorted_items[index] = t[1]
        return sorted_items 

    def item_selected(self, state):
        """ Handle menu item selection
        
        :param state: button state
        """
        for button in self.buttons.values():
            b_comp = getattr(button.state, "comparator_item", None)
            s_comp = getattr(state, "comparator_item", None)
            if b_comp != None and s_comp != None and b_comp == s_comp:
                button.set_selected(True)
                self.selected_index = button.state.index                
            else:
                button.set_selected(False)
                
    def add_listener(self, listener):
        """ Add menu event listener
        
        :param listener: event listener
        """
        if listener not in self.start_listeners:
            self.start_listeners.append(listener)
            
    def notify_listeners(self, state):
        """ Notify all menu listeners
        
        :param state: button state
        """
        for listener in self.start_listeners:
            listener(state)
            
    def add_move_listener(self, listener):
        """ Add arrow button event listener
        
        :param listener: event listener
        """
        if listener not in self.move_listeners:
            self.move_listeners.append(listener)
            
    def notify_move_listeners(self):
        """ Notify arrow button event listeners
        
        :param state: button state
        """
        for listener in self.move_listeners:
            listener(None)
            
    def unselect(self):
        """ Unselect currently selected button
        
        :return: index of the button which was selected
        """
        for button in self.buttons.values():
            if button.selected:
                button.set_selected(False)
                button.clean_draw_update()
                return button.state.index
    
    def get_selected_index(self):
        """ Return the index of the button which was selected
        
        :return: index of the selected button
        """
        for button in self.buttons.values():
            if button.selected:
                return button.state.index
        return None
    
    def select_by_index(self, index):
        """ Select button by specified index
        
        :param index: button index
        """
        for button in self.buttons.values():
            if button.state.index == index:
                button.set_selected(True)
                button.clean_draw_update()
                self.selected_index = index
                self.notify_move_listeners()
                break
    
    def select_action(self):
        """ Notify listeners of the selected button """
        
        for button in self.buttons.values():
            if button.state.index == self.selected_index:
                button.notify_release_listeners(button.state)
                break
            
    def is_enabled(self, i):
        """ Check if the button is enabled. 
        Disabled buttons have enabled flag set to False. 
        Enabled buttons don't have this flag  
        
        :param index: button index
        :return: True - button enabled, False - button disabled
        """
        for button in self.buttons.values():
            enabled = getattr(button.state, "enabled", None)
            if button.state.index == i and enabled == None:
                return True
        return False
       
    def handle_event(self, event):
        """ Menu event handler
        
        :param event: menu event
        """
        if not self.visible: return
        
        if event.type == USER_EVENT_TYPE and event.sub_type == SUB_TYPE_KEYBOARD and event.action == pygame.KEYUP:
            key_events = [kbd_keys[KEY_LEFT], kbd_keys[KEY_RIGHT], kbd_keys[KEY_UP], kbd_keys[KEY_DOWN]]            
            if event.keyboard_key in key_events:
                i = self.get_selected_index()
                if i == None:
                    return
                col = int(i % self.cols)
                row = int(i / self.cols)
            
            if event.keyboard_key == kbd_keys[KEY_SELECT]:
                self.select_action()
                return
             
            if event.keyboard_key == kbd_keys[KEY_LEFT]:                              
                if col == 0:
                    i = i + self.cols - 1
                else:
                    i = i - 1                
            elif event.keyboard_key == kbd_keys[KEY_RIGHT]:
                if col == self.cols - 1:
                    i = i - self.cols + 1
                else:
                    i = i + 1
            elif event.keyboard_key == kbd_keys[KEY_UP]:
                if row == 0:
                    i = i + (self.rows - 1) * self.cols
                else:
                    i = i - self.cols
            elif event.keyboard_key == kbd_keys[KEY_DOWN]:
                if row == self.rows - 1:
                    i = int(i % self.cols)
                else:
                    i = i + self.cols
                
            if self.is_enabled(i):
                self.unselect()
                self.select_by_index(i)                  
        else:
            Container.handle_event(self, event) 

            