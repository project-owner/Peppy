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
from ui.menu.stationmenu import StationMenu
from player.playlist import Playlist
from ui.layout.borderlayout import BorderLayout
from ui.factory import Factory
from ui.state import State
from ui.component import Component
from util.keys import kbd_keys, KEY_MENU
from util.keys import SCREEN_RECT, PLAYLIST, COLOR_DARK, COLOR_CONTRAST, COLORS, PREVIOUS, \
    STATION, CURRENT, LANGUAGE, GENRE
from util.util import GENRE_ITEMS

# 480x320
PIXELS_TOP_HEIGHT = 45
PIXELS_BOTTOM_HEIGHT = 46
PIXELS_SIDE_TOP_HEIGHT = 91
PIXELS_SIDE_BOTTOM_HEIGHT = 91
PIXELS_SIDE_WIDTH = 126

PERCENT_TOP_HEIGHT = 14.0625
PERCENT_BOTTOM_HEIGHT = 14.375
PERCENT_SIDE_TOP_HEIGHT = 39.738
PERCENT_SIDE_BOTTOM_HEIGHT = 39.738

PERCENT_TITLE_FONT = 66.66

class StationScreen(Container):
    """ Station Screen. Extends Container class """
    
    def __init__(self, listeners, util):
        """ Initializer
        
        :param util: utility object
        :param listener: screen menu event listener
        """
        self.util = util
        self.config = util.config
        Container.__init__(self, util, background=(0, 0, 0))
        self.factory = Factory(util)
        self.bounding_box = self.config[SCREEN_RECT]
        layout = BorderLayout(self.bounding_box)
        k = self.bounding_box.w/self.bounding_box.h
        percent_menu_width = (100.0 - PERCENT_TOP_HEIGHT - PERCENT_BOTTOM_HEIGHT)/k
        panel_width = (100.0 - percent_menu_width)/2.0
        layout.set_percent_constraints(PERCENT_TOP_HEIGHT, PERCENT_BOTTOM_HEIGHT, panel_width, panel_width)
        self.genres = util.load_menu(GENRE_ITEMS, GENRE)        
        self.current_genre = self.genres[self.config[CURRENT][PLAYLIST]]
        self.items_per_line = self.items_per_line(layout.CENTER.w)
        self.playlist = Playlist(self.config[CURRENT][LANGUAGE], self.current_genre.genre, util, self.items_per_line)
        
        font_size = (layout.TOP.h * PERCENT_TITLE_FONT)/100.0
        color_dark = self.config[COLORS][COLOR_DARK]
        color_contrast = self.config[COLORS][COLOR_CONTRAST]
        self.screen_title = self.factory.create_dynamic_text("station_screen_title", layout.TOP, color_dark, color_contrast, int(font_size))
        Container.add_component(self, self.screen_title)

        self.station_menu = StationMenu(self.playlist, util, (0, 0, 0), layout.CENTER)
        self.screen_title.set_text(self.station_menu.button.state.l_name)        
        Container.add_component(self, self.station_menu)
        
        self.create_left_panel(layout, listeners)
        self.create_right_panel(layout, listeners)        

        self.home_button.add_release_listener(listeners["go home"])
        self.genres_button.add_release_listener(listeners["go genres"])
        self.shutdown_button.add_release_listener(listeners["shutdown"])
        self.left_button.add_release_listener(self.station_menu.switch_to_previous_station)
        self.left_button.add_release_listener(self.update_arrow_button_labels)
        self.page_down_button.add_release_listener(self.station_menu.switch_to_previous_page)
        self.page_down_button.add_release_listener(self.update_arrow_button_labels)
        self.right_button.add_release_listener(self.station_menu.switch_to_next_station)
        self.right_button.add_release_listener(self.update_arrow_button_labels)
        self.page_up_button.add_release_listener(self.station_menu.switch_to_next_page)
        self.page_up_button.add_release_listener(self.update_arrow_button_labels)               
        self.station_menu.add_listener(listeners["play"])
        self.station_menu.add_listener(self.screen_title.set_state)
        self.station_menu.add_listener(self.update_arrow_button_labels)        
        self.station_menu.add_mode_listener(self.mode_listener)
        
        self.volume = self.factory.create_volume_control(layout.BOTTOM)
        self.volume.add_slide_listener(listeners["set volume"])
        self.volume.add_slide_listener(listeners["set config volume"])
        self.volume.add_slide_listener(listeners["set screensaver volume"])
        self.volume.add_knob_listener(listeners["mute"])        
        Container.add_component(self, self.volume)
    
    def mode_listener(self, mode):
        """ Station screen menu mode event listener
        
        :param mode: menu mode
        """
        if mode == self.station_menu.STATION_MODE:
            self.left_button.set_visible(True)
            self.right_button.set_visible(True)
            self.page_down_button.set_visible(False)
            self.page_up_button.set_visible(False)
            self.left_button.clean_draw_update()
            self.right_button.clean_draw_update()
        else:
            self.left_button.set_visible(False)
            self.right_button.set_visible(False)
            self.page_down_button.set_visible(True)
            self.page_up_button.set_visible(True)            
            if self.playlist.total_pages == 1:
                self.page_down_button.set_enabled(False)
                self.page_up_button.set_enabled(False)
            else:
                self.page_down_button.set_enabled(True)
                self.page_up_button.set_enabled(True)
            self.page_down_button.clean_draw_update()
            self.page_up_button.clean_draw_update()
    
    def update_arrow_button_labels(self, state):
        """ Update arrow buttons state
        
        :param state: button state used for update
        """
        if not self.station_menu.STATION_MODE: return
        
        left = self.station_menu.button.state.index
        right = self.playlist.length - self.station_menu.button.state.index - 1
        
        self.left_button.state.l_name = str(left)
        self.left_button.add_label(self.left_button.state, self.left_button.layout.get_label_rectangle())        
        self.page_down_button.state.l_name = str(left)
        self.page_down_button.add_label(self.page_down_button.state, self.page_down_button.layout.get_label_rectangle())        
        self.right_button.state.l_name = str(right)
        self.right_button.add_label(self.right_button.state, self.right_button.layout.get_label_rectangle())
        self.page_up_button.state.l_name = str(right)
        self.page_up_button.add_label(self.page_up_button.state, self.page_up_button.layout.get_label_rectangle())
        
        if self.station_menu.current_mode == self.station_menu.STATION_MODE:            
            self.left_button.clean_draw_update()
            self.right_button.clean_draw_update()
        else:
            self.page_down_button.clean_draw_update()
            self.page_up_button.clean_draw_update()        
        
    def create_left_panel(self, layout, listeners):
        """ Create Station Screen left panel. Include Shutdown button, Left button and Home button.
        
        :param layout: left panel layout
        :param listeners: event listeners
        """
        panel_layout = BorderLayout(layout.LEFT)
        panel_layout.set_percent_constraints(PERCENT_SIDE_BOTTOM_HEIGHT, PERCENT_SIDE_BOTTOM_HEIGHT, 0, 0)
        left = self.station_menu.button.state.index
        self.left_button = self.factory.create_left_button(panel_layout.CENTER, str(left))
        self.page_down_button = self.factory.create_page_down_button(panel_layout.CENTER, str(left))
        self.page_down_button.set_visible(False)
        self.shutdown_button = self.factory.create_shutdown_button(panel_layout.TOP)
        self.home_button = self.factory.create_home_button(panel_layout.BOTTOM)
        panel = Container(self.util, layout.LEFT)
        panel.add_component(self.shutdown_button)
        panel.add_component(self.left_button)
        panel.add_component(self.page_down_button)
        panel.add_component(self.home_button)
        Container.add_component(self, panel)
    
    def create_right_panel(self, layout, listeners):
        """ Create Station Screen right panel. Include Genre button, right button and Play/Pause button
        
        :param layout: right panel layout
        :param listeners: event listeners
        """
        panel_layout = BorderLayout(layout.RIGHT)
        panel_layout.set_percent_constraints(PERCENT_SIDE_BOTTOM_HEIGHT, PERCENT_SIDE_BOTTOM_HEIGHT, 0, 0)
        self.genres_button = self.factory.create_genre_button(panel_layout.TOP, self.current_genre)
        right = self.playlist.length - self.station_menu.button.state.index - 1 
        self.right_button = self.factory.create_right_button(panel_layout.CENTER, str(right))
        self.page_up_button = self.factory.create_page_up_button(panel_layout.CENTER, str(right))
        self.page_up_button.set_visible(False)
        self.play_button = self.factory.create_play_pause_button(panel_layout.BOTTOM, listeners["play-pause"])  
        panel = Container(self.util, layout.RIGHT)
        panel.add_component(self.genres_button)
        panel.add_component(self.right_button)
        panel.add_component(self.page_up_button)
        panel.add_component(self.play_button)
        Container.add_component(self, panel)
    
    def items_per_line(self, width):
        """ Return the number of station menu items in line for specified screen width
        
        :param width: screen width
        
        :return: number of menu items per line
        """
        if width <= 102:
            return 1
        elif width <= 203:
            return 2
        elif width <= 304:
            return 3
        elif width <= 405:
            return 4
        elif width <= 506:
            return 5
        else:
            return 6
    
    def set_genre_button_image(self, genre):
        """ Set genre button image
        
        :param genre: genre button
        """
        s = State()
        s.__dict__ = genre.__dict__
        s.bounding_box = self.genres_button.state.bounding_box
        s.bgr = self.genres_button.bgr
        s.show_label = False
        s.keyboard_key = kbd_keys[KEY_MENU]
        self.genres_button.set_state(s)
        
    def set_current(self):
        """ Set current station by index defined in current playlist """
        
        selected_genre = self.genres[self.config[CURRENT][PLAYLIST]]          
        if selected_genre == self.current_genre: return
          
        self.config[PREVIOUS][self.station_menu.playlist.genre] = self.station_menu.get_current_station_index()         
        self.playlist = Playlist(self.config[CURRENT][LANGUAGE], selected_genre.genre, self.util, self.items_per_line)
        
        if self.playlist.length == 0:
            return
        
        self.station_menu.set_playlist(self.playlist)
        previous_station_index = 0 
        try:
            previous_station_index = self.config[PREVIOUS][selected_genre.name.lower()]
        except KeyError:
            pass
        self.station_menu.set_station(previous_station_index)
        self.station_menu.set_station_mode(None)
        self.config[CURRENT][STATION] = previous_station_index        
        self.set_genre_button_image(selected_genre)        
        self.current_genre = selected_genre
        self.screen_title.set_text(self.station_menu.get_current_station_name())
        pass
    
    def get_clickable_rect(self):
        """ Return the list of rectangles which define the clickable areas on screen. Used for web browser. 
        
        :return: list of rectangles
        """
        bb = self.screen_title.bounding_box
        x = 0
        y = bb.h
        w = bb.width
        h = self.station_menu.bounding_box.height
        c = Component(self.util)
        c.name = "clickable_rect"
        c.content = pygame.Rect(x, y, w, h)
        c.bgr = c.fgr = (0, 0, 0)
        c.content_x = c.content_y = 0
        d = [c]       
        return d
    
    def set_visible(self, flag):
        """ Set visibility flag
        
        :param flag: True - screen visible, False - screen invisible
        """
        self.visible = flag
        self.screen_title.set_visible(flag)

