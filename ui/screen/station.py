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

from ui.container import Container
from ui.menu.stationmenu import StationMenu
from ui.page import Page
from ui.layout.borderlayout import BorderLayout
from ui.factory import Factory
from ui.state import State
from ui.menu.menu import Menu
from ui.screen.screen import Screen
from util.config import STREAM, COLORS, COLOR_DARK_LIGHT, COLOR_CONTRAST, CURRENT, LANGUAGE, \
    PLAYER_SETTINGS, VOLUME, STATIONS, CURRENT_STATIONS
from util.keys import kbd_keys, KEY_MENU, KEY_HOME, KEY_STATIONS, KEY_GENRES, \
    KEY_SHUTDOWN, KEY_PLAY_PAUSE, KEY_FAVORITES, KEY_SET_VOLUME, KEY_SET_CONFIG_VOLUME, \
    KEY_SET_SAVER_VOLUME, KEY_MUTE, KEY_PLAY, KEY_LANGUAGES, NAME, KEY_STOP
from util.favoritesutil import FavoritesUtil

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
PERCENT_GENRE_IMAGE_AREA = 33.0

STATION = "station"

class StationScreen(Screen):
    """ Station Screen """
    
    def __init__(self, listeners, util, voice_assistant, screen_mode=STATION):
        """ Initializer
        
        :param util: utility object
        :param listener: screen menu event listener
        """
        self.util = util
        self.config = util.config
        self.factory = Factory(util)
        self.screen_mode = screen_mode
        self.bounding_box = util.screen_rect
        self.favorites_util = FavoritesUtil(self.util)
        layout = BorderLayout(self.bounding_box)
        k = self.bounding_box.w/self.bounding_box.h
        percent_menu_width = (100.0 - PERCENT_TOP_HEIGHT - PERCENT_BOTTOM_HEIGHT)/k
        panel_width = (100.0 - percent_menu_width)/2.0
        layout.set_percent_constraints(PERCENT_TOP_HEIGHT, PERCENT_BOTTOM_HEIGHT, panel_width, panel_width)
        Screen.__init__(self, util, "", PERCENT_TOP_HEIGHT, voice_assistant, "station_screen_title", True, layout.TOP)
        
        tmp = Menu(util, (0, 0, 0), self.bounding_box, None, None)
        folders = self.util.get_stations_folders()
        if folders:
            panel_layout = BorderLayout(layout.RIGHT)
            panel_layout.set_percent_constraints(PERCENT_SIDE_BOTTOM_HEIGHT, PERCENT_SIDE_BOTTOM_HEIGHT, 0, 0)
            self.genres = util.load_stations_folders(panel_layout.BOTTOM)
            self.genres[KEY_FAVORITES] = self.favorites_util.get_favorites_button_state(panel_layout.BOTTOM) 
            current_genre_name = list(self.genres.keys())[0]
            self.current_genre = self.genres[current_genre_name]        
        self.items_per_line = self.items_per_line(layout.CENTER.w)
        items = []
        if self.screen_mode == STATION:            
            k = STATIONS + "." + self.config[CURRENT][LANGUAGE]
            try:
                self.config[k]
                self.current_genre = self.genres[self.config[k][CURRENT_STATIONS]]
            except:
                self.config[k] = {}
                self.config[k][CURRENT_STATIONS] = self.current_genre.name
            items = self.load_stations(self.config[CURRENT][LANGUAGE], self.current_genre.name, self.items_per_line * self.items_per_line)                
        elif self.screen_mode == STREAM:
            items = util.load_streams(self.items_per_line * self.items_per_line)

        self.playlist = Page(items, self.items_per_line, self.items_per_line)
        
        self.station_menu = StationMenu(self.playlist, util, screen_mode, (0, 0, 0), layout.CENTER)
        if self.station_menu.is_button_defined():
            d = {"current_title" : self.station_menu.button.state.l_name}
            self.screen_title.set_text(d)        
        Container.add_component(self, self.station_menu)
        
        self.stop_player = listeners[KEY_STOP]
        self.create_left_panel(layout, listeners)
        self.create_right_panel(layout, listeners)
        
        self.home_button.add_release_listener(listeners[KEY_HOME])
        if self.screen_mode == STATION:
            self.genres_button.add_release_listener(listeners[KEY_GENRES])
        self.shutdown_button.add_release_listener(self.favorites_util.save_favorites)
        self.shutdown_button.add_release_listener(listeners[KEY_SHUTDOWN])
        self.left_button.add_release_listener(self.station_menu.switch_to_previous_station)
        self.left_button.add_release_listener(self.update_arrow_button_labels)
        self.page_down_button.add_release_listener(self.station_menu.switch_to_previous_page)
        self.page_down_button.add_release_listener(self.update_arrow_button_labels)
        self.right_button.add_release_listener(self.station_menu.switch_to_next_station)
        self.right_button.add_release_listener(self.update_arrow_button_labels)
        self.page_up_button.add_release_listener(self.station_menu.switch_to_next_page)
        self.page_up_button.add_release_listener(self.update_arrow_button_labels)               
        self.station_menu.add_listener(listeners[KEY_PLAY])
        self.station_menu.add_listener(self.screen_title.set_state)
        self.station_menu.add_listener(self.update_arrow_button_labels)        
        self.station_menu.add_mode_listener(self.mode_listener)
        
        self.volume = self.factory.create_volume_control(layout.BOTTOM)
        self.volume.add_slide_listener(listeners[KEY_SET_VOLUME])
        self.volume.add_slide_listener(listeners[KEY_SET_CONFIG_VOLUME])
        self.volume.add_slide_listener(listeners[KEY_SET_SAVER_VOLUME])
        self.volume.add_knob_listener(listeners[KEY_MUTE])        
        Container.add_component(self, self.volume)
        self.player_screen = True

        if self.current_genre.name == KEY_FAVORITES:        
            self.favorites_mode = True
        else:
            self.favorites_mode = False
    
        self.favorites_util.set_favorites_in_config(self.items_per_line)
    
    def load_stations(self, language, genre, stations_per_page):
        """ Load stations for specified language and genre
        
        :param language: the language
        :param genre: the genre
        :param stations_per_page: stations per page used to assign indexes 
               
        :return: list of button state objects. State contains station icons, index, genre, name etc.
        """
        if genre == KEY_FAVORITES:
            return self.favorites_util.get_favorites_playlist(language, stations_per_page)
        else:
            return self.util.get_stations_playlist(language, genre, stations_per_page)        
    
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
        if self.playlist.length == 0:
            self.stop_player()
            left = right = "0"
            self.page_down_button.set_enabled(False)
            self.page_up_button.set_enabled(False)
            self.left_button.set_enabled(False)
            self.right_button.set_enabled(False)
        else:    
            left = str(self.station_menu.button.state.index)
            right = str(self.playlist.length - self.station_menu.button.state.index - 1)
            self.page_down_button.set_enabled(True)
            self.page_up_button.set_enabled(True)
            self.left_button.set_enabled(True)
            self.right_button.set_enabled(True)


        self.left_button.change_label(left)
        self.right_button.change_label(right)
        
        self.page_down_button.change_label(left)
        self.page_up_button.change_label(right)
        
    def create_left_panel(self, layout, listeners):
        """ Create Station Screen left panel. Include Shutdown button, Left button and Home button.
        
        :param layout: left panel layout
        :param listeners: event listeners
        """
        panel_layout = BorderLayout(layout.LEFT)
        panel_layout.set_percent_constraints(PERCENT_SIDE_BOTTOM_HEIGHT, PERCENT_SIDE_BOTTOM_HEIGHT, 0, 0)
        left = 0
        if self.station_menu.is_button_defined():
            left = self.station_menu.button.state.index
        self.left_button = self.factory.create_left_button(panel_layout.CENTER, str(left), 40, 100)
        self.page_down_button = self.factory.create_page_down_button(panel_layout.CENTER, str(left), 40, 100)
        self.page_down_button.set_visible(False)
        self.shutdown_button = self.factory.create_shutdown_button(panel_layout.TOP)
        self.home_button = self.factory.create_button(KEY_HOME, KEY_HOME, panel_layout.BOTTOM, image_size_percent=36)
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
        if self.screen_mode == STATION:
            self.genres_button = self.factory.create_genre_button(panel_layout.BOTTOM, self.current_genre, PERCENT_GENRE_IMAGE_AREA)            
        elif self.screen_mode == STREAM:
            self.genres_button = self.factory.create_stream_button(panel_layout.BOTTOM)
        right = 0
        if self.station_menu.is_button_defined():
            right = self.playlist.length - self.station_menu.button.state.index - 1 
        self.right_button = self.factory.create_right_button(panel_layout.CENTER, str(right), 40, 100)
        self.page_up_button = self.factory.create_page_up_button(panel_layout.CENTER, str(right), 40, 100)
        self.page_up_button.set_visible(False)
        self.play_button = self.factory.create_play_pause_button(panel_layout.TOP, listeners[KEY_PLAY_PAUSE])  
        panel = Container(self.util, layout.RIGHT)
        panel.add_component(self.genres_button)
        panel.add_component(self.right_button)
        panel.add_component(self.page_up_button)
        panel.add_component(self.play_button)
        Container.add_component(self, panel)
    
    def set_genre_button_image(self, genre):
        """ Set genre button image
        
        :param genre: genre button
        """
        if self.favorites_mode:
            favorites_button_state = self.favorites_util.get_favorites_button_state(self.genres_button.state.bounding_box)
            self.genres_button.selected = False
            self.genres_button.set_state(favorites_button_state)
        else:        
            s = State()
            s.__dict__ = genre.__dict__
            s.bounding_box = self.genres_button.state.bounding_box
            s.bgr = self.genres_button.bgr
            s.show_label = False
            s.keyboard_key = kbd_keys[KEY_MENU]
            self.factory.scale_genre_button_image(s, PERCENT_GENRE_IMAGE_AREA)
            self.genres_button.set_state(s)
        
    def set_current(self, state=None):
        """ Set current station by index defined in current playlist 
        
        :param state: button state (if any)
        """
        items = []
        current_language = self.config[CURRENT][LANGUAGE]
        selected_genre = None
        self.favorites_mode = False
        
        if self.screen_mode == STATION:
            key = STATIONS + "." + current_language
            s1 = state != None and getattr(state, "source", None) == KEY_FAVORITES
            s2 = state == None and self.config[key][CURRENT_STATIONS] == KEY_FAVORITES
            if s1 or s2:
                self.favorites_mode = True
                self.config[key][CURRENT_STATIONS] = KEY_FAVORITES
            
            try:
                k = self.config[key][CURRENT_STATIONS]
                selected_genre = self.genres[k]            
                self.store_previous_station(current_language)
            except:
                self.config[key] = {}
                selected_genre = self.current_genre
            
            genre = selected_genre.name
            size = self.items_per_line * self.items_per_line            
            items = self.load_stations(current_language, genre, size)
        elif self.screen_mode == STREAM:
            items = self.util.load_streams(self.items_per_line * self.items_per_line)
            
        self.playlist = Page(items, self.items_per_line, self.items_per_line)
         
        if self.playlist.length == 0:
            return
         
        self.station_menu.set_playlist(self.playlist)
        
        if self.screen_mode == STATION:
            self.station_menu.genre = selected_genre.name
            previous_station_index = 0 
            try:
                previous_station_index = self.config[STATIONS + "." + current_language][selected_genre.name]
            except KeyError:
                pass            
            self.station_menu.set_station(previous_station_index)
            self.station_menu.set_station_mode(None)
            self.set_genre_button_image(selected_genre)
            
            if self.favorites_mode:
                self.current_genre = self.favorites_util.get_favorites_button_state(self.genres_button.state.bounding_box)
            else:       
                self.current_genre = selected_genre
        elif self.screen_mode == STREAM:
            previous_station_index = 0 
            try:
                previous_station_index = self.config[CURRENT][STREAM]
            except KeyError:
                pass 
            self.station_menu.set_station(previous_station_index) 
            self.station_menu.set_station_mode(None)
            self.config[CURRENT][STREAM] = previous_station_index
        n = self.station_menu.get_current_station_name()
        self.screen_title.set_text(n)
        
        config_volume_level = int(self.config[PLAYER_SETTINGS][VOLUME])
        if self.volume.get_position() != config_volume_level:
            self.volume.set_position(config_volume_level)
            self.volume.update_position()
            
    def store_previous_station(self, lang):
        """ Store previous station for the current language 
        
        :param lang: previous language
        """
        k = STATIONS + "." + lang
        try:
            self.config[k]
        except:
            self.config[k] = {}
        try:
            i = self.station_menu.get_current_station_index()
            self.config[k][self.current_genre.name] = i
        except:
            pass
        
    def set_visible(self, flag):
        """ Set visibility flag
        
        :param flag: True - screen visible, False - screen invisible
        """
        self.visible = flag
        self.screen_title.set_visible(flag)
        self.station_menu.set_visible(flag)

    def enable_player_screen(self, flag):
        """ Enable player screen
        
        :param flag: enable/disable flag
        """
        self.screen_title.active = flag            

    def add_screen_observers(self, update_observer, redraw_observer, title_to_json):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        Screen.add_screen_observers(self, update_observer, redraw_observer, title_to_json)
        
        self.add_button_observers(self.shutdown_button, update_observer, redraw_observer=None)    
        self.shutdown_button.add_cancel_listener(redraw_observer)
        self.screen_title.add_listener(title_to_json)
                
        self.add_button_observers(self.play_button, update_observer, redraw_observer=None)
        self.add_button_observers(self.home_button, update_observer, redraw_observer, release=False)
        
        self.add_button_observers(self.left_button, update_observer, redraw_observer, release=False)
        self.add_button_observers(self.right_button, update_observer, redraw_observer, release=False)
        
        self.add_button_observers(self.page_down_button, update_observer, redraw_observer)
        self.add_button_observers(self.page_up_button, update_observer, redraw_observer)
                        
        self.volume.add_slide_listener(update_observer)
        self.volume.add_knob_listener(update_observer)
        self.volume.add_press_listener(update_observer)
        self.volume.add_motion_listener(update_observer)
        
        self.add_button_observers(self.genres_button, update_observer, redraw_observer, release=False)
        self.station_menu.add_listener(update_observer)
        self.station_menu.add_change_logo_listener(redraw_observer)
        
        