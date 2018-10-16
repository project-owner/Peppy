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
import os
import urllib

from util.util import IMAGE_SHADOW, IMAGE_SELECTION, FOLDER_ICONS, EXT_PNG, DEFAULT_CD_IMAGE
from ui.factory import Factory
from ui.menu.menu import Menu
from ui.component import Component
from builtins import isinstance
from util.config import SCREEN_INFO, WIDTH, HEIGHT, CURRENT, PLAYER_SETTINGS, VOLUME, MUTE, \
    PAUSE, LANGUAGE, STATIONS, CURRENT_STATIONS, MODE, RADIO, STREAM, MODE, RADIO
from util.keys import kbd_keys, USER_EVENT_TYPE, \
    SUB_TYPE_KEYBOARD, KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN, KEY_BACK, KEY_SELECT  

class StationMenu(Menu):
    """ Station Menu class. Extends base Menu class """
    
    PAGE_MODE = 0
    STATION_MODE = 1
    STATION = "station"
    LOGO_SCALE_FACTOR = 200 / 228
    
    def __init__(self, playlist, util, mode=STATION, bgr=None, bounding_box=None):
        """ Initializer
        
        :param playlist: playlist object
        :param util: utility object
        :param bgr: menu background
        :param bounding_box: bounding box
        """ 
        self.factory = Factory(util)
        self.util = util
        self.config = self.util.config
        m = self.factory.create_station_menu_button
        bb = bounding_box
        self.menu_mode = mode
        Menu.__init__(self, util, bgr, bb, playlist.rows, playlist.columns, create_item_method=m)
        self.bounding_box = bb
        self.playlist = playlist
        self.current_mode = self.STATION_MODE
        
        path = os.path.join(FOLDER_ICONS, IMAGE_SHADOW + EXT_PNG)                
        self.original_shadow = self.util.load_image(path, bounding_box=(bb.w, bb.h))
        screen_height = self.config[SCREEN_INFO][HEIGHT]
        h = self.bounding_box.h
        self.shadow = (self.original_shadow[0], self.util.scale_image(self.original_shadow[1], (h, h)))
        self.shadow_component = None
        
        path = os.path.join(FOLDER_ICONS, IMAGE_SELECTION + EXT_PNG)  
        self.selection = self.util.load_image(path)
        self.station_button = None
        self.menu_click_listeners = []
        self.mode_listeners = []
        self.change_logo_listeners = []
        self.page_turned = False
        self.genre = None
        self.current_logo_image = None
        self.current_logo_filename = None
        self.current_album_image = None
    
    def set_playlist(self, playlist):
        """ Set playlist
        
        :param playlist: the playlist to set
        """
        self.playlist = playlist        
    
    def init_station(self, index):
        """ Initialize the station specified by its index
        
        :param index: station index
        """
        self.current_album_image = None
        self.playlist.set_current_item(index)
        index = self.playlist.current_item_index
        index_on_page = self.playlist.current_item_index_in_page
        page = self.playlist.get_current_page()        
        self.set_page(index, index_on_page, page)

    def set_page(self, index, index_on_page, page):
        """ Set new page of stations
        
        :param index: current station index in playlist
        :param index_on_page: station index on page
        :param page: list of stations
        """
        self.set_items(self.make_dict(page), index_on_page, self.switch_mode)
        self.shadow_component = self.get_shadow()
        self.add_component(self.shadow_component)
        
        self.station_button = self.get_logo_button(index)
        if self.current_album_image == None:
            self.large_station_button = self.get_logo_button(index)
            
        self.add_component(self.large_station_button)
        if not self.is_button_defined():
            return
        self.add_component(self.get_selection_frame(self.button))

    def is_button_defined(self):
        """ Check if ''button' object was defined
        
        :return: true - button object defined, false - not defined
        """
        return getattr(self, "button", None) != None           

    def get_shadow(self):
        """ Return the button shadow component
        
        :return: shadow component
        """
        c = Component(self.util, self.shadow[1])
        c.name = "station_menu.shadow"
        c.image_filename = self.shadow[0]
        c.content_x = self.bounding_box.x
        c.content_y = self.bounding_box.y
        return c

    def get_logo_button(self, index):
        """ Return the button of the station specified by its index
        
        :param index: button index in the playlist
        
        :return: current station button
        """
        
        try:
            self.button = self.buttons[str(index)]
        except:
            pass
        
        if not self.is_button_defined():
            return
        
        b = self.factory.create_station_button(self.button.state, self.bounding_box, self.switch_mode)
        b.components[1].content = self.button.state.icon_base
        img = b.components[1].content
        if isinstance(img, tuple):
            self.current_logo_filename = img[0]
            img = img[1]
        bb = self.bounding_box
        
        logo_height = int(bb.h * self.LOGO_SCALE_FACTOR)
        self.current_logo_image = self.util.scale_image(img, (logo_height, logo_height))
        b.components[1].content = self.current_logo_image            
        b.components[1].content_x = bb.x + bb.w/2 - self.current_logo_image.get_size()[0]/2
        b.components[1].content_y = bb.y + bb.h/2 - self.current_logo_image.get_size()[1]/2
        
        return b
    
    def get_selection_frame(self, button):
        """ Create the selection frame used in Page mode
        
        :param button: button for which the selection frame should be created
        
        :return: selection frame component
        """
        x = button.components[0].content.x
        y = button.components[0].content.y
        w = button.components[0].content.w
        h = button.components[0].content.h
        i = self.util.scale_image(self.selection[1], (w, h))
        c = Component(self.util, i)
        c.content_x = x
        c.content_y = y
        c.name = "station_menu.selection"
        c.image_filename = self.selection[0]
        c.visible = False
        c.selection_index = button.state.index_in_page
        return c
    
    def set_station(self, index, save=True):
        """ Set new station specified by its index
        
        :param index: the index of new station
        :param save: flag defining if index should be saved in configuration object, True - save, False - don't save
        """
        try:
            self.init_station(index)
            self.draw()
            self.button.state.volume = self.config[PLAYER_SETTINGS][VOLUME]
            self.button.state.mute = self.config[PLAYER_SETTINGS][MUTE]
            self.button.state.pause = self.config[PLAYER_SETTINGS][PAUSE]
            self.notify_listeners(self.button.state)
            if save:
                self.save_station_index(self.button.state.index)
        except KeyError:
            pass
    
    def save_station_index(self, index):
        """ Save station/stream index in configuration object
        
        :param index: the index
        """
        lang = self.config[CURRENT][LANGUAGE]
        mode = self.config[CURRENT][MODE]
        
        if mode == RADIO:
            k = STATIONS + "." + lang
            try:
                self.config[k]
            except:
                self.config[k] = {}
                self.config[k][CURRENT_STATIONS] = self.genre
                
            self.config[k][self.genre] = index
        elif mode == STREAM:
            try:
                self.config[CURRENT][STREAM] = index
            except:
                pass
    
    def get_current_station_name(self):
        """ Return the current station name
        
        :return: localized name of the current station
        """
        index = self.playlist.current_item_index
        button = self.buttons[str(index)]
        return button.state.l_name
    
    def get_current_station_index(self):
        """ Return the index of the current station
        
        :return: the index
        """
        return self.playlist.current_item.index
        
    def switch_to_next_station(self, state):
        """ Switch to the next station
        
        :param state: button state
        """
        if len(self.playlist.get_current_page()) == (self.playlist.current_item_index_in_page + 1):
            self.switch_to_next_page(state)
            if self.playlist.current_item_index == self.playlist.length - 1:
                self.playlist.current_item_index = 0
            else:
                self.playlist.current_item_index += 1
        else:
            self.playlist.current_item_index += 1
        self.set_station(self.playlist.current_item_index)             
            
    def switch_to_previous_station(self, state):
        """ Switch to the previous station
        
        :param state: button state
        """
        if self.playlist.current_item_index == 0:
            self.switch_to_previous_page(state)
            l = len(self.components)
            self.playlist.current_item_index = self.get_button_by_index_in_page(l - 4).state.index
        else:
            self.playlist.current_item_index -= 1
        self.set_station(self.playlist.current_item_index)
    
    def switch_to_next_page(self, state):
        """ Switch to the next page
        
        :param state: button state
        """
        next_page = self.playlist.next_page()        
        self.set_page(self.playlist.current_item_index, self.playlist.current_page_index, next_page)
        if state != None:
            l = len(self.components)
            next_selected_button = self.get_button_by_index_in_page(0)
            self.components[l - 1] = self.get_selection_frame(next_selected_button)        
        self.draw()
        self.page_turned = True  
            
    def switch_to_previous_page(self, state):
        """ Switch to the previous page
        
        :param state: button state
        """
        next_page = self.playlist.previous_page()
        self.set_page(self.playlist.current_item_index, self.playlist.current_page_index, next_page)
        if state != None:
            l = len(self.components)
            next_selected_button = self.get_button_by_index_in_page(0)
            self.components[l - 1] = self.get_selection_frame(next_selected_button) 
        self.draw()
        self.page_turned = True 
    
    def switch_mode(self, state):
        """ Switch menu mode. There are two modes - Station and Page
        
        :param state: button state
        """
        if self.current_mode == self.STATION_MODE:
            self.set_page_mode()            
        else:
            self.set_station_mode(state)
    
    def set_page_mode(self):
        """ Set Page mode """
         
        self.current_mode = self.PAGE_MODE
        self.draw()
        self.notify_mode_listeners(self.current_mode)

    def set_station_mode(self, state):
        """ Set Station mode
        
        :param state: button state
        """
        self.current_mode = self.STATION_MODE
        
        if self.page_turned:
            l = len(self.components)
            self.components[l - 1] = self.get_selection_frame(self.button)
            self.page_turned = False
                                
        if state and state.index != self.playlist.current_item_index:
            self.set_station(state.index)
        else:
            self.draw()
        self.notify_mode_listeners(self.current_mode)        
    
    def get_button_by_index_in_page(self, index):
        """ Return the button by its index on page
        
        :param index: button index
        :return: the button
        """
        for button in self.buttons.values():
            if button.state.index_in_page == index:
                return button
        return None
    
    def handle_event(self, event):
        """ Station menu event handler
        
        :param event: event to handle
        """
        if not self.visible: return
        
        if self.current_mode == self.STATION_MODE:            
            self.station_button.handle_event(event)            
        else:
            if event.type == USER_EVENT_TYPE and event.sub_type == SUB_TYPE_KEYBOARD and event.action == pygame.KEYUP:
                l = len(self.components)
                selection = self.components[l - 1]
                key_event = False
                
                col = int(selection.selection_index % self.cols)
                row = int(selection.selection_index / self.cols)
                 
                if event.keyboard_key == kbd_keys[KEY_LEFT]:
                    if col == 0 and row == 0:
                        self.switch_to_previous_page(None)
                        l = len(self.components)
                        selection.selection_index = l - 4                        
                    else:
                        selection.selection_index = selection.selection_index - 1
                    key_event = True
                elif event.keyboard_key == kbd_keys[KEY_RIGHT]:
                    if col == self.cols - 1 and row == self.rows - 1:
                        self.switch_to_next_page(None)
                        selection.selection_index = 0
                        l = len(self.components)
                    else:
                        m = selection.selection_index + 1
                        if self.get_button_by_index_in_page(m):
                            selection.selection_index = m
                        else:
                            self.switch_to_next_page(None)
                            selection.selection_index = 0
                            l = len(self.components)
                    key_event = True
                elif event.keyboard_key == kbd_keys[KEY_UP]:
                    if row == 0:
                        for n in range(self.rows):
                            m = selection.selection_index + (self.rows - 1 - n) * self.cols
                            if self.get_button_by_index_in_page(m):
                                selection.selection_index = m
                    else:
                        selection.selection_index = selection.selection_index - self.cols
                    key_event = True
                elif event.keyboard_key == kbd_keys[KEY_DOWN]:
                    if row == self.rows - 1:
                        selection.selection_index = int(selection.selection_index % self.cols)
                    else:
                        m = selection.selection_index + self.cols
                        if self.get_button_by_index_in_page(m):
                            selection.selection_index = m
                        else:
                            selection.selection_index = int(selection.selection_index % self.cols)
                    key_event = True
                elif event.keyboard_key == kbd_keys[KEY_BACK]:
                    self.init_station(self.station_button.state.index)
                    self.switch_mode(self.station_button.state)
                    self.draw()
                    key_event = False
                    
                if key_event:
                    next_selected_button = self.get_button_by_index_in_page(selection.selection_index)
                    self.components[l - 1] = self.get_selection_frame(next_selected_button)
                    self.draw()
                
                if event.keyboard_key == kbd_keys[KEY_SELECT]:
                    selected_button = self.get_button_by_index_in_page(selection.selection_index)
                    self.item_selected(selected_button.state)
                    self.switch_mode(selected_button.state)
                    
                self.notify_menu_click_listeners(event)
            else:
                Menu.handle_event(self, event)
            
        if self.visible and event.type == pygame.MOUSEBUTTONUP and self.bounding_box.collidepoint(event.pos):
            self.notify_menu_click_listeners(event)

    def draw(self):
        """ Draw Station Menu """
        
        self.clean()        
        l = len(self.components)
        
        if l > 2 and self.current_mode == self.STATION_MODE:         
            self.components[l - 3].set_visible(True)
            self.components[l - 2].set_visible(True)
            self.components[l - 2].components[0].set_visible(False)
            self.components[l - 1].set_visible(False)
        elif l > 2:
            self.components[l - 3].set_visible(False)
            self.components[l - 2].set_visible(False)
            self.components[l - 1].set_visible(True)
        super(StationMenu, self).draw()        
        self.update()
     
    def add_menu_click_listener(self, listener):
        """ Add menu button click listener
        
        :param listener: event listener
        """
        if listener not in self.menu_click_listeners:
            self.menu_click_listeners.append(listener)     

    def notify_menu_click_listeners(self, event):
        """ Notify all menu button click event listeners
        
        :param event: event to handle
        """
        for listener in self.menu_click_listeners:
            listener(event)
            
    def add_mode_listener(self, listener):
        """ Add change mode listener
        
        :param listener: event listener
        """
        if listener not in self.mode_listeners:
            self.mode_listeners.append(listener)     

    def notify_mode_listeners(self, mode):
        """ Notify all menu change mode event listeners
        
        :param mode: the mode
        """
        for listener in self.mode_listeners:
            listener(mode)
            
    def add_change_logo_listener(self, listener):
        """ Add change logo listener
        
        :param listener: event listener
        """
        if listener not in self.change_logo_listeners:
            self.change_logo_listeners.append(listener)     

    def notify_change_logo_listeners(self, state):
        """ Notify change logo event listeners
        
        :param state: state object with new image in 'icon_base'
        """
        for listener in self.change_logo_listeners:
            listener(state)

    def show_logo(self):
        """ Show station logo image """
        
        b = self.large_station_button
        bb = self.bounding_box        
        logo_height = int(bb.h * self.LOGO_SCALE_FACTOR)
        b.components[1].image_filename = self.current_logo_filename
        b.components[1].content = self.current_logo_image            
        b.components[1].content_x = bb.x + bb.w/2 - self.current_logo_image.get_size()[0]/2
        b.components[1].content_y = bb.y + bb.h/2 - self.current_logo_image.get_size()[1]/2
        if self.visible:
            self.draw()
        self.notify_change_logo_listeners(b.state)

    def show_album_art(self, status):
        """ Show album art from discogs.com
        
        :param status: object having artist & track names
        """
        self.current_album_image = None
        
        if self.config[CURRENT][MODE] != RADIO or status == None or self.current_mode == self.PAGE_MODE:
            return
        
        album = status['current_title']
        
        if len(album) < 10 or "jingle" in album.lower(): 
            self.show_logo()          
            return
        
        bb_w = self.bounding_box.w * self.LOGO_SCALE_FACTOR
        bb_h = bb_w
        bb_x = self.bounding_box.x + (self.bounding_box.w - bb_w) / 2
        bb_y = self.bounding_box.y + (self.bounding_box.h - bb_h) / 2
        bb = pygame.Rect(bb_x, bb_y, bb_w, bb_w)
        
        r = pygame.Rect(0, 0, self.config[SCREEN_INFO][WIDTH], self.config[SCREEN_INFO][HEIGHT])
        full_screen_image = self.util.get_cd_album_art(album, r)
        
        scale_ratio = self.util.get_scale_ratio((bb.w, bb.h), full_screen_image[1])
        album_art = (full_screen_image[0], self.util.scale_image(full_screen_image, scale_ratio))
        
        if album_art and album_art[0] != None and album_art[0].endswith(DEFAULT_CD_IMAGE) or album_art[1] == None:
            self.show_logo()
            return
        
        if album_art and album_art[0] != None and album_art[0].endswith(DEFAULT_CD_IMAGE) or album_art[1] == None:
            self.show_logo()
            return
        
        size = album_art[1].get_size()
        self.current_album_image = album_art[1] 
        b = self.large_station_button
        img = b.components[1] 
        img.content = album_art[1]        
        img.content_x = int(bb_x + (bb_w - size[0]) / 2)
        img.content_y = int(bb_y + (bb_h - size[1]) / 2)
                
        url = self.util.encode_url(album_art[0])
        
        img.image_filename = url
        b.state.icon_base = album_art
        if full_screen_image:
            b.state.full_screen_image = full_screen_image[1]
        
        k = 17 / 15
        w = int(size[0] * k)
        h = int(size[1] * k)
        shadow = self.util.scale_image(self.original_shadow[1], (w, h))
        self.shadow_component.content = shadow
        size = shadow.get_size()
        x = int(self.bounding_box.x + (self.bounding_box.w - w) / 2)
        y = int(self.bounding_box.y + (self.bounding_box.h - h) / 2)
        w = size[0]
        h = size[1]
        self.shadow_component.content_x = x
        self.shadow_component.content_y = y
        self.shadow_component.bounding_box = pygame.Rect(x, y, w, h)
        
        if self.visible:    
            self.draw()
            
        self.notify_change_logo_listeners(b.state)
        