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
# along with Peppy Player. If not, see <http://www.gnu.org/licenses/>.

import os
import time
import random
import pygame

from pygame import Rect
from ui.state import State
from ui.container import Container
from ui.layout.borderlayout import BorderLayout
from ui.factory import Factory
from ui.screen.screen import Screen
from util.keys import *
from util.config import *
from util.fileutil import FILE_AUDIO, FILE_PLAYLIST, FOLDER, FILE_RECURSIVE
from util.cdutil import CdUtil
from ui.menu.popup import Popup

class FilePlayerScreen(Screen):
    """ File Player Screen """
    
    def __init__(self, listeners, util, get_current_playlist, voice_assistant, player_stop=None, arrow_labels=True, 
        active_file_button=True, show_time_control=True, show_order=True, show_info=True):
        """ Initializer
        
        :param listeners: screen listeners
        :param util: utility object
        :param get_current_playlist: current playlist getter
        :param voice_assistant:   voice assistant
        :param player_stop: stop player function
        """
        self.util = util
        self.config = util.config
        self.cdutil = CdUtil(util)
        self.factory = Factory(util)
        self.image_util = util.image_util

        self.top_height = self.config[PLAYER_SCREEN][TOP_HEIGHT_PERCENT]
        self.bottom_height = self.config[PLAYER_SCREEN][BOTTOM_HEIGHT_PERCENT]
        self.button_height = self.config[PLAYER_SCREEN][BUTTON_HEIGHT_PERCENT]
        self.popup_width = self.config[PLAYER_SCREEN][POPUP_WIDTH_PERCENT]
        self.image_location = self.config[PLAYER_SCREEN][IMAGE_LOCATION]

        self.stop_player = player_stop
        self.get_current_playlist = get_current_playlist
        self.show_time_control = show_time_control

        self.bounding_box = util.screen_rect
        self.layout = self.get_layout()

        self.voice_assistant = voice_assistant
        Screen.__init__(self, util, "", self.top_height, voice_assistant, "file_player_screen_title", True, self.layout.TOP)
        self.layout = self.get_layout()
        
        self.create_left_panel(self.layout, listeners, arrow_labels)
        self.create_right_panel(self.layout, listeners, arrow_labels)
        
        if not active_file_button:
            listeners[AUDIO_FILES] = None

        self.file_button = self.factory.create_file_button(self.layout.CENTER, listeners[AUDIO_FILES])
        self.file_button.selected = True
        self.add_component(self.file_button)
        
        self.audio_files = self.get_audio_files()
        self.home_button.add_release_listener(listeners[KEY_HOME])
        self.shutdown_button.add_release_listener(listeners[KEY_SHUTDOWN])
        self.left_button.add_release_listener(self.go_left)
        self.right_button.add_release_listener(self.go_right)
        
        self.show_order = show_order
        self.show_info = show_info
        self.order_button = None
        self.info_button = None
        self.order_popup = None
        self.info_popup = None
        self.playback_order = self.config[PLAYER_SETTINGS][PLAYBACK_ORDER]
        self.bottom_center_layout = self.layout.BOTTOM
        
        if self.show_order or self.show_info:
            self.start_screensaver = listeners[SCREENSAVER]
            self.go_info_screen = listeners[KEY_INFO]
            self.add_popups()

        self.volume = self.factory.create_volume_control(self.bottom_center_layout)
        self.volume.add_slide_listener(self.get_listener(listeners, KEY_SET_VOLUME))
        self.volume.add_slide_listener(self.get_listener(listeners, KEY_SET_CONFIG_VOLUME))
        self.volume.add_slide_listener(self.get_listener(listeners, KEY_SET_SAVER_VOLUME))
        self.volume.add_knob_listener(self.get_listener(listeners, KEY_MUTE))
        self.volume_visible = False
        self.volume.set_visible(self.volume_visible)
        self.add_component(self.volume)
        
        if self.show_time_control:
            self.time_control = self.factory.create_time_control(self.bottom_center_layout)
            if KEY_SEEK in listeners.keys():
                self.time_control.add_seek_listener(listeners[KEY_SEEK])

            self.play_button.add_listener(PAUSE, self.time_control.pause)
            self.play_button.add_listener(KEY_PLAY, self.time_control.resume)

            if self.config[PLAYER_SETTINGS][PAUSE]:
                self.time_control.pause()
            self.time_control.slider.handle_knob_events = False
            self.add_component(self.time_control)

        self.left_button.add_release_listener(self.play_button.draw_default_state)
        self.right_button.add_release_listener(self.play_button.draw_default_state)

        self.play_listeners = []
        self.add_play_listener(self.get_listener(listeners, KEY_PLAY))
        
        self.current_folder = self.config[FILE_PLAYBACK][CURRENT_FOLDER]
        self.file_button.state.cover_art_folder = self.util.file_util.get_cover_art_folder(self.current_folder)
        self.playlist_size = 0
        self.player_screen = True
        self.cd_album = None
        self.animated_title = True

        if self.order_popup:
            Container.add_component(self, self.order_popup)

        if self.info_popup:
            Container.add_component(self, self.info_popup)

        self.link_borders()
        self.current_button = self.file_button
        self.key_events = [kbd_keys[KEY_LEFT], kbd_keys[KEY_RIGHT], kbd_keys[KEY_UP], kbd_keys[KEY_DOWN]]
        self.arrow_keys = [kbd_keys[KEY_LEFT], kbd_keys[KEY_RIGHT], kbd_keys[KEY_UP], kbd_keys[KEY_DOWN]]
        self.player_keys = [kbd_keys[KEY_PLAY_PAUSE], kbd_keys[KEY_MUTE]]
        self.volume_keys = [kbd_keys[KEY_VOLUME_UP], kbd_keys[KEY_VOLUME_DOWN]]
        self.previous_next_keys = [kbd_keys[KEY_PAGE_DOWN], kbd_keys[KEY_PAGE_UP]]
    
    def link_borders(self):
        """ Link components borders for the arrow keys navigation """

        self.custom_button = self.time_volume_button
        self.center_button = self.file_button
        self.center_button.ignore_enter_y = False
        volume_x = self.volume.bounding_box.x + (self.volume.bounding_box.w / 2)
        volume_y = self.volume.bounding_box.y

        if self.show_order:
            order_x = self.order_button.bounding_box.x
            order_y = self.order_button.bounding_box.y
        else:
            order_x = volume_x
            order_y = volume_y

        if self.show_info:
            info_x = self.info_button.bounding_box.x
            info_y = self.info_button.bounding_box.y
        else:
            info_x = volume_x
            info_y = volume_y

        shutdown_x = self.shutdown_button.bounding_box.x
        shutdown_y = self.shutdown_button.bounding_box.y
        left_x = self.left_button.bounding_box.x
        left_y = self.left_button.bounding_box.y
        home_x = self.home_button.bounding_box.x
        home_y = self.home_button.bounding_box.y
        play_x = self.play_button.bounding_box.x
        play_y = self.play_button.bounding_box.y
        right_x = self.right_button.bounding_box.x
        right_y = self.right_button.bounding_box.y
        custom_x = self.custom_button.bounding_box.x
        custom_y = self.custom_button.bounding_box.y
        if self.center_button:
            center_x = self.center_button.bounding_box.x
            center_y = self.center_button.bounding_box.y
        else:
            center_x = None

        if self.image_location == LOCATION_CENTER:
            if info_x == None:
                x = volume_x           
                y = volume_y
            else:
                x = info_x
                y = info_y

            if self.show_order:
                x_top = order_x
                y_top = order_y
            else:
                x_top = volume_x
                y_top = volume_y

            self.set_button_borders(self.shutdown_button, (x, y), (x_top, y_top), (center_x, center_y), (left_x, left_y))
            self.set_button_borders(self.left_button, (play_x, play_y), (shutdown_x, shutdown_y), (center_x, left_y), (home_x, home_y))
            self.set_button_borders(self.home_button, (right_x, right_y), (left_x, left_y), (center_x, home_y), (x_top, y_top))
            self.set_button_borders(self.play_button, (center_x, center_y), (info_x, info_y), (left_x, left_y), (right_x, right_y))
            self.set_button_borders(self.right_button, (center_x, right_y), (play_x, play_y), (home_x, home_y), (custom_x, custom_y))

            if order_x == None:
                x = volume_x           
                y = volume_y
            else:
                x = order_x
                y = order_y

            self.set_button_borders(self.custom_button, (center_x, custom_y), (right_x, right_y), (x, y), (info_x, info_y))
            if self.center_button:
                self.set_button_borders(self.center_button, (left_x, left_y), (volume_x, volume_y), (right_x, right_y), (volume_x, volume_y))

            if order_x == None:
                x_left = custom_x           
                y_left = custom_y
            else:
                x_left = order_x           
                y_left = order_y

            if info_x == None:
                x_right = shutdown_x
                y_right = shutdown_y
            else:
                x_right = info_x
                y_right = info_y  

            self.set_button_borders(self.volume, (x_left, y_left), (center_y, center_y), (x_right, y_right), (center_y, center_y))
            if self.show_order:
                self.set_button_borders(self.order_button, (custom_x, custom_y), (home_x, home_y), (volume_x, volume_y), (shutdown_x, shutdown_y))
            if self.show_time_control:
                self.set_button_borders(self.time_control.slider, (x_left, y_left), (center_y, center_y), (x_right, y_right), (center_y, center_y))
            if self.show_info:
                self.set_button_borders(self.info_button, (volume_x, volume_y), (custom_x, custom_y), (shutdown_x, shutdown_y), (play_x, play_y))
        elif self.image_location == LOCATION_LEFT:
            if self.center_button:
                self.center_button.ignore_enter_y = True
            self.set_button_borders(self.shutdown_button, (center_x, center_y), (volume_x, volume_y), (play_x, play_y), (left_x, left_y))
            self.set_button_borders(self.left_button, (play_x, play_y), (shutdown_x, shutdown_y), (right_x, right_y), (home_x, home_y))
            self.set_button_borders(self.home_button, (right_x, right_y), (left_x, left_y), (custom_x, custom_y), (volume_x, volume_y))
            if self.show_info:
                x_top = info_x
                y_top = info_y
            else:
                x_top = volume_x
                y_top = volume_y
            self.set_button_borders(self.play_button, (shutdown_x, shutdown_y), (x_top, y_top), (left_x, left_y), (right_x, right_y))
            self.set_button_borders(self.right_button, (left_x, left_y), (play_x, play_y), (home_x, home_y), (custom_x, custom_y))
            if self.show_order:
                x_right = order_x
                y_right = order_y
            else:
                x_right = volume_x
                y_right = volume_y
            self.set_button_borders(self.custom_button, (home_x, home_y), (right_x, right_y), (x_right, y_right), (info_x, info_y))
            if self.center_button:
                if self.show_info:
                    x_left = info_x
                    y_left = info_y
                else:
                    x_left = volume_x
                    y_left = volume_y
                self.set_button_borders(self.center_button, (x_left, y_left), (volume_x, volume_y), (shutdown_x, shutdown_y), (volume_x, volume_y))
            if self.show_order and self.show_info:
                x_left = order_x
                y_left = order_y
                x_right = info_x
                y_right = info_y
            elif self.show_order and not self.show_info:
                x_left = order_x
                y_left = order_y
                x_right = center_x
                y_right = center_y
            elif not self.show_order and self.show_info:
                x_left = custom_x
                y_left = custom_y
                x_right = info_x
                y_right = info_y
            elif not self.show_order and not self.show_info:
                x_left = custom_x
                y_left = custom_y
                x_right = center_x
                y_right = center_y
            self.set_button_borders(self.volume, (x_left, y_left), (center_x, center_y), (x_right, y_right), (center_x, center_y))
            if self.show_time_control:
                self.set_button_borders(self.time_control.slider, (x_left, y_left), (center_x, center_y), (x_right, y_right), (center_x, center_y))
            if self.show_order:
                self.set_button_borders(self.order_button, (custom_x, custom_y), (center_x, center_y), (volume_x, volume_y), (center_x, center_y))
            if self.show_info:
                self.set_button_borders(self.info_button, (volume_x, volume_y), (custom_x, custom_y), (center_x, center_y), (play_x, play_y))
        elif self.image_location == LOCATION_RIGHT:
            if self.center_button:
                self.center_button.ignore_enter_y = True
            if self.show_info:
                x_left = info_x
                y_left = info_y
            else:
                x_left = volume_x
                y_left = volume_y

            if self.show_order:
                x_top = order_x
                y_top = order_y
            else:
                x_top = volume_x
                y_top = volume_y

            self.set_button_borders(self.shutdown_button, (x_left, y_left), (x_top, y_top), (play_x, play_y), (left_x, left_y))
            self.set_button_borders(self.left_button, (center_x, center_y), (shutdown_x, shutdown_y), (right_x, right_y), (home_x, home_y))
            self.set_button_borders(self.home_button, (right_x, right_y), (left_x, left_y), (custom_x, custom_y), (x_top, y_top))
            self.set_button_borders(self.play_button, (shutdown_x, shutdown_y), (volume_x, volume_y), (center_x, center_y), (right_x, right_y))
            self.set_button_borders(self.right_button, (left_x, left_y), (play_x, play_y), (home_x, home_y), (custom_x, custom_y))
            if self.show_order:
                x_right = order_x
                y_right = order_y
            else:
                x_right = volume_x
                y_right = volume_y
            self.set_button_borders(self.custom_button, (home_x, home_y), (right_x, right_y), (x_right, y_right), (volume_x, volume_y))
            if self.center_button:
                if self.show_info:
                    x_left = info_x
                    y_left = info_y
                else:
                    x_left = volume_x
                    y_left = volume_y
                self.set_button_borders(self.center_button, (play_x, play_y), (volume_x, volume_y), (left_x, left_y), (volume_x, volume_y))
            if self.show_order and self.show_info:
                x_left = order_x
                y_left = order_y
                x_right = info_x
                y_right = info_y
            elif self.show_order and not self.show_info:
                x_left = order_x
                y_left = order_y
                x_right = center_x
                y_right = center_y
            elif not self.show_order and self.show_info:
                x_left = custom_x
                y_left = custom_y
                x_right = info_x
                y_right = info_y
            elif not self.show_order and not self.show_info:
                x_left = custom_x
                y_left = custom_y
                x_right = center_x
                y_right = center_y
            self.set_button_borders(self.volume, (x_left, y_left), (custom_x, custom_y), (x_right, y_right), (play_x, play_y))
            if self.show_time_control:
                self.set_button_borders(self.time_control.slider, (x_left, y_left), (custom_x, custom_y), (x_right, y_right), (play_x, play_y))
            if self.show_order:
                self.set_button_borders(self.order_button, (custom_x, custom_y), (home_x, home_y), (volume_x, volume_y), (shutdown_x, shutdown_y))

            if self.show_info:
                self.set_button_borders(self.info_button, (volume_x, volume_y), (center_x, center_y), (shutdown_x, shutdown_y), (center_x, center_y))

    def set_button_borders(self, button, left, top, right, bottom):
        """ Set button borders

        :param button: target button
        :param left: left border
        :param top: top border
        :param right: right border
        :param bottom: bottom border
        """
        margin = 10
        if left != None: 
            button.exit_left_x = left[0] + margin
            button.exit_left_y = left[1] + margin
        if right != None: 
            button.exit_right_x = right[0] + margin
            button.exit_right_y = right[1] + margin
        if top != None: 
            button.exit_top_x = top[0] + margin
            button.exit_top_y = top[1] + margin
        if bottom != None: 
            button.exit_bottom_x = bottom[0] + margin
            button.exit_bottom_y = bottom[1] + margin

    def get_layout(self):
        """ Get the layout of the center area of the screen for image and buttons

        :return: layout rectangle
        """
        layout = BorderLayout(self.bounding_box)
        k = self.bounding_box.w/self.bounding_box.h
        percent_menu_width = (100.0 - self.top_height - self.bottom_height)/k
        panel_width = (100.0 - percent_menu_width)/2.0

        if self.image_location == LOCATION_CENTER:
            layout.set_percent_constraints(self.top_height, self.bottom_height, panel_width, panel_width)
        elif self.image_location == LOCATION_LEFT:
            layout.set_percent_constraints(self.top_height, self.bottom_height, 0, panel_width * 2)
        elif self.image_location == LOCATION_RIGHT:
            layout.set_percent_constraints(self.top_height, self.bottom_height, panel_width * 2, 0)

        return layout

    def get_panel_layout(self, layout, panel_location):
        """ Get the layout of the panel for buttons

        :param layout: layout of the whole central area
        :param panel_location: panel location: left or right

        :return: panel layout rectangle
        """
        if self.image_location == LOCATION_CENTER:
            if panel_location == LOCATION_LEFT:                
                return BorderLayout(layout.LEFT)
            else:
                return BorderLayout(layout.RIGHT)
        elif self.image_location == LOCATION_LEFT:
            r = layout.RIGHT
            if panel_location == LOCATION_LEFT:
                return BorderLayout(Rect(r.x, r.y, r.w/2, r.h))
            else:
                return BorderLayout(Rect(r.x + r.w/2 + 1, r.y, r.w/2 - 1, r.h))
        elif self.image_location == LOCATION_RIGHT:
            r = layout.LEFT
            if panel_location == LOCATION_LEFT:
                return BorderLayout(Rect(r.x, r.y, r.w/2, r.h))
            else:
                return BorderLayout(Rect(r.x + r.w/2 + 1, r.y, r.w/2 - 1, r.h))

    def add_popups(self):
        """ Add popup menus: playback order & info """

        self.bottom_layout = BorderLayout(self.layout.BOTTOM)
        if self.show_order and not self.show_info:
            self.bottom_layout.set_percent_constraints(0, 0, self.popup_width, 0)
            self.order_button = self.factory.create_order_button(self.bottom_layout.LEFT, self.handle_order_button, self.playback_order)
            self.order_popup = self.get_order_popup(self.bounding_box)
            self.add_component(self.order_button)
        elif self.show_order and self.show_info:
            self.bottom_layout.set_percent_constraints(0, 0, self.popup_width, self.popup_width)
            self.order_button = self.factory.create_order_button(self.bottom_layout.LEFT, self.handle_order_button, self.playback_order)
            self.info_button = self.factory.create_info_button(self.bottom_layout.RIGHT, self.handle_info_button)
            self.order_popup = self.get_order_popup(self.bounding_box)
            self.info_popup = self.get_info_popup(self.bounding_box)
            self.add_component(self.order_button)
            self.add_component(self.info_button)
        elif not self.show_order and self.show_info:
            self.bottom_layout.set_percent_constraints(0, 0, 0, self.popup_width)
            self.info_button = self.factory.create_info_button(self.bottom_layout.RIGHT, self.handle_info_button)
            self.info_popup = self.get_info_popup(self.bounding_box)
            self.add_component(self.info_button)
            
        self.bottom_layout.CENTER.w -=2
        self.bottom_layout.CENTER.x +=1
        self.bottom_center_layout = self.bottom_layout.CENTER

    def handle_order_button(self, state):
        """ Handle playback order button

        :param state: button state
        """
        self.order_popup.set_visible(True)
        self.clean_draw_update()

    def handle_info_button(self, state):
        """ Handle info button

        :param state: button state
        """
        self.info_popup.set_visible(True)
        self.clean_draw_update()

    def get_order_popup(self, bb):
        """ Create playback order popup menu

        :param bb: bounding box

        :return: popup menu
        """
        items = []
        items.append(PLAYBACK_CYCLIC)
        items.append(PLAYBACK_REGULAR)
        items.append(PLAYBACK_SINGLE_TRACK)
        items.append(PLAYBACK_SHUFFLE)
        items.append(PLAYBACK_SINGLE_CYCLIC)
        
        layout = BorderLayout(bb)
        layout.set_percent_constraints(self.top_height, 0, self.popup_width, 0)
        popup = Popup(items, self.util, layout.LEFT, self.update_screen, 
            self.handle_order_popup_selection, default_selection=self.playback_order)
        self.left_button.add_label_listener(popup.update_popup)

        return popup

    def get_info_popup(self, bb):
        """ Create info popup menu

        :param bb: bounding box

        :return: popup menu
        """
        items = []
        mode = self.config[CURRENT][MODE]

        items.append(CLOCK)
        items.append(WEATHER)
        items.append(LYRICS)

        if mode == AUDIO_FILES or mode == COLLECTION:
            items.append(FILE_INFO)        
        
        layout = BorderLayout(bb)
        layout.set_percent_constraints(self.top_height, 0, 0, self.popup_width)
        popup = Popup(items, self.util, layout.RIGHT, self.update_screen, self.handle_info_popup_selection)
        self.right_button.add_label_listener(popup.update_popup)

        return popup

    def update_screen(self):
        """ Update screen """

        self.clean_draw_update()
        self.redraw_observer()

    def handle_order_popup_selection(self, state):
        """ Handle playback order menu selection

        :param state: button state
        """
        b = self.factory.create_order_button(self.bottom_layout.LEFT, self.handle_order_button, state.name)
        i = self.components.index(self.order_button)
        self.components[i] = b
        self.order_button = b
        self.add_button_observers(self.order_button, self.update_observer, self.redraw_observer)
        self.order_button.set_selected(True)
        self.order_button.clean_draw_update()
        self.current_button = self.order_button
        self.link_borders()
        self.config[PLAYER_SETTINGS][PLAYBACK_ORDER] = state.name

    def handle_info_popup_selection(self, state):
        """ Handle info menu selection

        :param state: button state
        """
        n = state.name

        if n == CLOCK or n == WEATHER:
            self.start_screensaver(n)
        elif n == LYRICS:
            a = None
            try:
                m = self.util.get_file_metadata()
                a = m["artist"] + " - " + m["title"]
            except:
                pass
            if a != None:
                s = State()
                s.album = a
                self.start_screensaver(n, s)
            else:
                self.start_screensaver(n)
        else:
            self.go_info_screen(state)

    def get_audio_files(self):
        """ Return the list of audio files in current folder
        
        :return: list of audio files
        """
        files = []
        if self.config[CURRENT][MODE] == CD_PLAYER:
            af = getattr(self, "audio_files", None)
            if af == None:
                cd_drive_name = self.config[CD_PLAYBACK][CD_DRIVE_NAME]
                files = self.cdutil.get_cd_tracks_summary(cd_drive_name)
            else:
                return self.audio_files
        else:
            folder = self.config[FILE_PLAYBACK][CURRENT_FOLDER]
            files = self.util.get_audio_files_in_folder(folder)

        return files
    
    def get_current_track_index(self, state=None):
        """ Return current track index.
        In case of files goes through the file list.
        In case of playlist takes track index from the state object.
        
        :param state: button state

        :return: current track index
        """
        if self.config[CURRENT][MODE] == AUDIOBOOKS:
            t = None
            try:
                t = state["file_name"]
            except:
                pass
            
            if t == None:
                try:
                    t = state["current_title"]
                except:
                    pass
            
            if t == None:
                try:
                    t = state
                except:
                    pass
            
            for i, f in enumerate(self.audio_files):
                try:
                    s = f["file_name"]
                except:
                    pass
                
                if getattr(f, "file_name", None):
                    s = getattr(f, "file_name", None)
                
                if s.endswith(t):
                    return i
            return 0
        
        mode = self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE]       
        if state and mode == FILE_PLAYLIST:
            try:
                n = state["Track"]
                if n: return int(n) - 1
            except:
                pass

        if self.config[CURRENT][MODE] == CD_PLAYER:
            cmp = int(self.config[CD_PLAYBACK][CD_TRACK]) - 1
        else:
            cmp = self.config[FILE_PLAYBACK][CURRENT_FILE]
            if state and isinstance(state, State):
                cmp = state.file_name

        for f in self.audio_files:
            if self.config[CURRENT][MODE] == CD_PLAYER:
                if f.index == cmp:
                    return f.index
            else:
                if f.file_name == cmp:
                    return f.index
        return 0
    
    def stop_recursive_playback(self):
        """ Stop recursive playback """
        
        self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] = FILE_AUDIO
        self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYLIST] = None
        self.config[FILE_PLAYBACK][CURRENT_TRACK_TIME] = None
        self.stop_timer()
        if self.show_time_control:
            self.time_control.stop_thread()
            self.time_control.reset()
        if self.stop_player != None:
            self.stop_player()
        
    def go_left(self, state):
        """ Switch to the previous track
        
        :param state: not used state object
        """        
        if getattr(self, "current_track_index", None) == None:
            return
        
        filelist_size = self.get_filelist_size()
        
        if self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] == FILE_RECURSIVE:
            self.stop_recursive_playback()
            return
        
        if self.current_track_index == 0:
            self.current_track_index = filelist_size - 1
        else:
            self.current_track_index -= 1
        self.change_track(self.current_track_index)
    
    def go_right(self, state):
        """ Switch to the next track
        
        :param state: not used state object
        """
        if getattr(self, "current_track_index", None) == None:
            return
        
        filelist_size = self.get_filelist_size()
        
        if self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] == FILE_RECURSIVE and self.current_track_index == filelist_size - 1:
            self.stop_timer()
            if self.show_time_control:
                self.time_control.stop_thread()
            self.recursive_change_folder()
            self.current_track_index = 0
            self.change_track(self.current_track_index)
            self.file_button.clean_draw_update()
            return
         
        if self.current_track_index == filelist_size - 1:
            self.current_track_index = 0
        else:
            self.current_track_index += 1
        
        self.change_track(self.current_track_index)
    
    def get_filelist_size(self):
        """ Return the file list size
        
        :return: file list size
        """
        if self.audio_files:
            return len(self.audio_files)
        else:
            return 0
    
    def change_track(self, track_index):
        """ Change track
        
        :param track_index: index track
        """
        a = [AUDIOBOOKS, CD_PLAYER]
        m = self.config[CURRENT][MODE]
        if not (m in a):
            self.config[FILE_PLAYBACK][CURRENT_FILE] = self.get_filename(track_index)
            
        self.stop_timer()
        time.sleep(0.3)
        s = State()
        if m == FILE_PLAYBACK:
            s.playback_mode = self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE]

        s.playlist_track_number = track_index
        s.index = track_index
        s.source = ARROW_BUTTON
        s.file_name = self.get_filename(track_index)
        
        if self.cd_album != None:
            s.album = self.cd_album

        if self.config[CURRENT][MODE] == AUDIO_FILES:
            folder = self.current_folder
            if not folder.endswith(os.sep):
                folder += os.sep
            s.url = folder + s.file_name
        
        self.set_current(True, s)
    
    def stop_timer(self):
        """ Stop time control timer """
        
        if self.show_time_control:
            self.time_control.stop_timer()
    
    def get_filename(self, index):
        """ Get filename by index
        
        :param index: file index
        
        :return: filename
        """        
        for b in self.audio_files:
            if b.index == index:
                return b.file_name
        return ""

    def is_valid_mode(self):
        current_mode = self.config[CURRENT][MODE]
        modes = [AUDIO_FILES, AUDIOBOOKS, CD_PLAYER]
        if current_mode in modes:
            return True
        else:
            return False
    
    def update_arrow_button_labels(self, state=None):
        """ Update left/right arrow button labels
        
        :param state: state object representing current track
        """
        if (not self.is_valid_mode()) or (not self.screen_title.active): return
        
        self.set_current_track_index(state)
        left = self.current_track_index
        right = 0
        
        if self.audio_files and len(self.audio_files) > 1: 
            right = len(self.audio_files) - self.current_track_index - 1
            
        self.left_button.change_label(str(left))
        self.right_button.change_label(str(right))
        
    def set_current_track_index(self, state):
        """ Set current track index
        
        :param state: state object representing current track
        """
        if not self.is_valid_mode(): return
        
        if self.config[CURRENT][MODE] == CD_PLAYER and getattr(state, "cd_track_id", None):
            self.config[CD_PLAYBACK][CD_TRACK] = state["cd_track_id"]
        
        self.current_track_index = 0
        
        if self.playlist_size == 1:            
            return
        
        if not self.audio_files:
            self.audio_files = self.get_audio_files()            
            if not self.audio_files: return
        
        i = self.get_current_track_index(state)
        self.current_track_index = i
    
    def create_left_panel(self, layout, listeners, arrow_labels):
        """ Create left side buttons panel
        
        :param layout: panel layout 
        :param listeners: button listeners
        :param arrow_labels: show arrow label or not
        """
        panel_layout = self.get_panel_layout(layout, LOCATION_LEFT)
        panel_layout.set_percent_constraints(self.button_height, self.button_height, 0, 0)
        self.left_button = self.factory.create_left_button(panel_layout.CENTER, '', 40, 100, arrow_labels)
        panel_layout.TOP.y += 1
        panel_layout.TOP.h -= 2
        self.shutdown_button = self.factory.create_shutdown_button(panel_layout.TOP)
        panel_layout.BOTTOM.h += 1
        self.home_button = self.factory.create_button(KEY_HOME, KEY_HOME, panel_layout.BOTTOM, image_size_percent=36)
        panel = Container(self.util, layout.LEFT)
        panel.add_component(self.shutdown_button)
        panel.add_component(self.left_button)
        panel.add_component(self.home_button)
        self.add_component(panel)
    
    def create_right_panel(self, layout, listeners, arrow_labels):
        """ Create right side buttons panel
        
        :param layout: panel layout 
        :param listeners: button listeners
        :param arrow_labels: show arrow label or not
        """
        panel_layout = self.get_panel_layout(layout, LOCATION_RIGHT)
        panel_layout.set_percent_constraints(self.button_height, self.button_height, 0, 0)
        panel_layout.TOP.y += 1
        panel_layout.TOP.h -= 2
        self.play_button = self.factory.create_play_pause_button(panel_layout.TOP, self.get_listener(listeners, KEY_PLAY_PAUSE))
        self.right_button = self.factory.create_right_button(panel_layout.CENTER, '', 40, 100, arrow_labels)
        panel_layout.BOTTOM.h += 1
        self.time_volume_button = self.factory.create_time_volume_button(panel_layout.BOTTOM, self.toggle_time_volume)
        panel = Container(self.util, layout.RIGHT)
        panel.add_component(self.play_button)
        panel.add_component(self.right_button)
        panel.add_component(self.time_volume_button)
        self.add_component(panel)

    def get_listener(self, listeners, name):
        """ Return listener

        :param listeners: all listeners
        :param name: listener name

        :return: listener if avaialble, None - otherwise
        """
        if name in listeners.keys():
            return listeners[name]
        else:
            return None

    def toggle_time_volume(self):
        """ Switch between time and volume controls """
        
        if self.volume_visible:
            self.volume.set_visible(False)
            if self.show_time_control:
                self.time_control.set_visible(True)                
            self.volume_visible = False
        else:
            volume_level = int(self.config[PLAYER_SETTINGS][VOLUME])
            self.volume.set_position(volume_level)
            self.volume.update_position()
            self.volume.set_visible(True)
            if self.show_time_control:
                self.time_control.set_visible(False)
            self.volume_visible = True
        self.clean_draw_update()
        if hasattr(self, "time_control"):
            self.time_control.slider.clean_draw_update()
    
    def eject_cd(self, state):
        """ Eject CD
        
        :param state: button state object
        """
        self.audio_files = []
        self.screen_title.set_text(" ")
        self.update_arrow_button_labels(state)
        if self.show_time_control:
            self.time_control.reset()
        self.cd_album = None
        self.set_cd_album_art_image()   
    
    def set_current(self, new_track=False, state=None):
        """ Set current file or playlist
        
        :param new_track: True - new audio file
        :param state: button state
        """
        self.cd_album = getattr(state, "album", None)
        
        if self.config[CURRENT][MODE] == AUDIO_FILES:
            if getattr(state, "url", None) is None:
                state.url = None
        elif self.config[CURRENT][MODE] == CD_PLAYER and getattr(state, "source", None) != INIT:
            state.full_screen_image = self.set_cd_album_art_image()
            state.image_base = self.file_button.components[1].content
                        
        config_volume_level = int(self.config[PLAYER_SETTINGS][VOLUME])
        if state:
            if self.config[VOLUME_CONTROL][VOLUME_CONTROL_TYPE] == VOLUME_CONTROL_TYPE_PLAYER:
                state.volume = config_volume_level
            else:
                state.volume = None
            
        self.set_audio_file(new_track, state)
        
        if self.volume.get_position() != config_volume_level:
            self.volume.set_position(config_volume_level)
            self.volume.update_position()
    
    def set_audio_file_image(self, url=None, folder=None):
        """ Set audio file image

        :param url: audio file name
        :param folder: folder name

        :return: image
        """
        if folder:
            f = folder
        else:
            f = self.config[FILE_PLAYBACK][CURRENT_FOLDER]

        if not f: return None
        
        img_tuple = self.image_util.get_audio_file_icon(f, self.bounding_box, url)
        self.set_file_button(img_tuple)
        self.file_button.clean_draw_update()
        
        return img_tuple[1]
    
    def set_cd_album_art_image(self):
        """ Set CD album art image """
        
        img_tuple = self.image_util.get_cd_album_art(self.cd_album, self.bounding_box)
        if img_tuple == None:
            return None
        self.set_file_button(img_tuple)
        self.file_button.clean_draw_update()
        
        return img_tuple[1]
    
    def set_file_button(self, img_tuple):
        """ Set image in file button
        
        :param img_tuple: tuple where first element is image location, second element image itself 
        """
        full_screen_image = img_tuple[1]
        self.file_button.state.full_screen_image = full_screen_image
        
        scale_ratio = self.image_util.get_scale_ratio((self.layout.CENTER.w, self.layout.CENTER.h), full_screen_image)
        img = self.image_util.scale_image(full_screen_image, scale_ratio)
        
        self.file_button.components[1].content = img
        self.file_button.state.icon_base = img
        self.file_button.components[1].image_filename = self.file_button.state.image_filename = img_tuple[0]
        
        self.file_button.components[1].content_x = self.layout.CENTER.x + (self.layout.CENTER.w - img.get_size()[0]) / 2
        
        if self.layout.CENTER.h > img.get_size()[1]:
            self.file_button.components[1].content_y = self.layout.CENTER.y + int((self.layout.CENTER.h - img.get_size()[1])/2) + 1
        else:
            self.file_button.components[1].content_y = self.layout.CENTER.y
        
    def set_audio_file(self, new_track, s=None):
        """ Set new audio file
        
        :param new_track: True - new audio file
        "param s" button state object
        """
        state = State()
        
        if s:
            state.playback_mode = getattr(s, "playback_mode", FILE_AUDIO)
            state.playlist_track_number = getattr(s, "playlist_track_number", None)
            if self.config[CURRENT][MODE] == CD_PLAYER and getattr(s, "source", None) != INIT:
                image_base = getattr(s, "image_base", None)
                if image_base != None:
                    state.image_base = image_base
        else:
            m = self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE]
            if m:
                state.playback_mode = m
            else:
                state.playback_mode = FILE_AUDIO
        
        if self.config[CURRENT][MODE] == AUDIO_FILES:            
            self.current_folder = self.config[FILE_PLAYBACK][CURRENT_FOLDER]
            if not self.current_folder:
                return
            state.folder = self.current_folder
            state.file_name = self.config[FILE_PLAYBACK][CURRENT_FILE]
            if state.folder[-1] == os.sep:
                state.folder = state.folder[:-1]
                
            if os.sep in state.file_name:
                state.url = "\"" + state.file_name + "\""
            else:
                state.url = "\"" + state.folder + os.sep + state.file_name + "\""
            
            state.full_screen_image = self.set_audio_file_image(state.url.replace('\"', ""))

            state.music_folder = self.config[AUDIO][MUSIC_FOLDER]
        elif self.config[CURRENT][MODE] == CD_PLAYER:
            state.file_name = s.file_name
            state.url = getattr(s, "url", s.file_name)
            parts = s.file_name.split()
            self.config[CD_PLAYBACK][CD_DRIVE_NAME] = parts[0][len("cdda:///"):]
            id = self.cdutil.get_cd_drive_id_by_name(self.config[CD_PLAYBACK][CD_DRIVE_NAME]) 
            self.config[CD_PLAYBACK][CD_DRIVE_ID] = int(id)
            self.config[CD_PLAYBACK][CD_TRACK] = int(parts[1].split("=")[1])             

        self.config[PLAYER_SETTINGS][PAUSE] = False
        state.mute = self.config[PLAYER_SETTINGS][MUTE]
        state.pause = self.config[PLAYER_SETTINGS][PAUSE]
        self.play_button.draw_default_state(None)
        state.file_type = FILE_AUDIO
        state.dont_notify = True
        state.source = FILE_AUDIO
        
        if self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] == FILE_AUDIO or self.config[CURRENT][MODE] == CD_PLAYER:
            self.audio_files = self.get_audio_files()            
        elif self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] == FILE_PLAYLIST:
            state.file_name = self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYLIST]
            self.load_playlist(state)
            state.file_name = self.config[FILE_PLAYBACK][CURRENT_FILE]
            self.audio_files = self.get_audio_files_from_playlist()
            state.playback_mode = FILE_PLAYLIST
            n = getattr(s, "file_name", None)
            if n:
                state.file_name = n
            
            try:
                state.playlist_track_number = int(state.file_name) - 1
            except:
                state.playlist_track_number = self.get_current_track_index(state)

        source = None
        if s:
            source = getattr(s, "source", None)

        if new_track:
            tt = 0.0
        else:        
            if self.config[CURRENT][MODE] == CD_PLAYER:
                tt = self.config[CD_PLAYBACK][CD_TRACK_TIME] 
            else:
                tt = self.config[FILE_PLAYBACK][CURRENT_TRACK_TIME]
                    
        if (isinstance(tt, str) and len(tt) != 0) or (isinstance(tt, float) or (source and source == RESUME)) or isinstance(tt, int):
            state.track_time = tt
        
        if self.show_time_control:
            self.time_control.slider.set_position(0)
            
        if self.file_button and self.file_button.components[1] and self.file_button.components[1].content:
            state.icon_base = self.file_button.components[1].content
        
        if s and hasattr(s, "volume"):
            state.volume = s.volume
            
        if self.config[CURRENT][MODE] == CD_PLAYER and s and getattr(s, "source", None) == INIT:
            try:
                self.cd_album = self.util.cd_titles[self.config[CD_PLAYBACK][CD_DRIVE_NAME]]
                self.set_cd_album_art_image()
                state.image_base = self.file_button.components[1].content
            except:
                self.cd_album = None
                
        if getattr(s, "full_screen_image", None) != None:
             state.full_screen_image = s.full_screen_image
        
        song_name = self.get_song_name(s)
        if song_name != None:
            state.album = song_name

        self.notify_play_listeners(state)

    def get_song_name(self, state):
        """ Get song name in the format: Artist - Song name
        
        :param state: state object
        """
        album = getattr(state, "album", None)
        if album == None:
            return None
        
        artist = album
        if "/" in album:
            artist = album.split("/")[0].strip()
        
        if artist == None or len(artist) == 0:
            return None
        
        name = getattr(state, "l_name", None)
        file_name = getattr(state, "file_name", None)
        if name == None:
            if file_name == None:
                return None
            else:
                if file_name.startswith("cdda:"):
                    id = int(file_name.split("=")[1].strip())
                    name = self.audio_files[id - 1].name
                else:
                    name = file_name
        
        pos = name.find(".")
        if pos != -1:
            tokens = name.split(".")
            if tokens[0].strip().isdigit():
                name = name[pos + 1:].strip()
        
        if name == None or len(name) == 0:
            return None
        else:
            return artist + " - " + name
    
    def get_audio_files_from_playlist(self):
        """ Call player for files in the playlist 
        
        :return: list of files from playlist
        """
        playlist = self.get_current_playlist()
        files = []
        if playlist:
            for n in range(len(playlist)):
                st = State()
                st.index = st.comparator_item = n
                st.file_type = FILE_AUDIO
                st.file_name = playlist[n]
                files.append(st)

        return files
    
    def restore_current_folder(self, state=None):
        """ Set current folder in config object
        
        :param state: not used
        """
        self.config[FILE_PLAYBACK][CURRENT_FOLDER] = self.current_folder
    
    def set_audio_file_playlist(self, index):
        """ Set file in playlist
        
        :param index: file index in playlist
        """
        state = State()
        state.playback_mode = FILE_PLAYLIST
        state.playlist_track_number = index
        state.file_type = FILE_AUDIO
        self.current_folder = self.config[FILE_PLAYBACK][CURRENT_FOLDER]
        self.notify_play_listeners(state)
    
    def go_back(self):
        """ Go back """
        pass

    def recursive_change_folder(self):
        start_folder = self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYLIST]
        current_folder = self.config[FILE_PLAYBACK][CURRENT_FOLDER]
        f = self.util.file_util.get_next_folder_with_audio_files(start_folder, current_folder)
        if f == None or (f != None and f[0] == None):
            self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] = FILE_AUDIO
            self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYLIST] = None
            return False
            
        self.config[FILE_PLAYBACK][CURRENT_FOLDER] = f[0]
        self.config[FILE_PLAYBACK][CURRENT_FILE] = f[1] 
        self.config[FILE_PLAYBACK][CURRENT_TRACK_TIME] = None
        state = State()
        state.file_type = FOLDER
        state.url = f[0]
        state.long_press = True
        state.playback_mode = FILE_RECURSIVE
        self.current_track_index = 0
        state.dont_notify = True
        self.audio_files = self.get_audio_files()
        self.recursive_notifier(f[0])
        return True
            
    def end_of_track(self):
        """ Handle end of track """

        if not self.screen_title.active:
            return

        i = getattr(self, "current_track_index", None)
        if i == None: return
        self.stop_timer()
        mode = self.config[CURRENT][MODE]
        if mode == RADIO or mode == STREAM or not self.audio_files:
            return
        
        if self.show_time_control:
            self.time_control.stop_thread()

        playback_mode = self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE]
        if playback_mode == FILE_RECURSIVE:
            if self.current_track_index == (len(self.audio_files) - 1):
                if not self.recursive_change_folder():
                    self.stop_recursive_playback()
                    return
                else:
                    index = 0
            else:
                index = self.current_track_index + 1
        else:
            index = self.get_next_index()

        if index == None:
            self.time_control.stop_thread()
            self.time_control.reset()
            return
        else:
            self.current_track_index = index

        if mode == AUDIO_FILES:          
            self.config[FILE_PLAYBACK][CURRENT_TRACK_TIME] = None
        elif mode == AUDIOBOOKS:
            self.config[AUDIOBOOKS][BROWSER_BOOK_TIME] = None

        self.change_track(index)

        if playback_mode == FILE_RECURSIVE:
            self.file_button.clean_draw_update()
    
    def get_next_index(self):
        """ Return next file index

        :return: file index or None
        """
        order = self.config[PLAYER_SETTINGS][PLAYBACK_ORDER]
        n = self.current_track_index
        last = len(self.audio_files) - 1

        if order == PLAYBACK_SINGLE_TRACK:
            return None

        if order == PLAYBACK_SINGLE_CYCLIC:
            return n

        if order == PLAYBACK_CYCLIC:
            if n == last:
                return 0
            else:
                return n + 1
        elif order == PLAYBACK_REGULAR:
            if n == last:
                return None
            else:
                return n + 1
        elif order == PLAYBACK_SHUFFLE:
            if len(self.audio_files) == 1:
                return n
            else:
                return random.randint(0, last)

    def set_playlist_size(self, size):
        """ Set playlist size
        
        :param size: playlist size
        """
        self.playlist_size = size
        self.stop_timer()
    
    def set_visible(self, flag):
        """ Set visibility flag
         
        :param flag: True - screen visible, False - screen invisible
        """
        Container.set_visible(self, flag)
        
        if flag:
            if self.volume_visible:
                self.volume.set_visible(True)
                if self.show_time_control:
                    self.time_control.set_visible(False)
            else:
                self.volume.set_visible(False)
                if self.show_time_control:
                    self.time_control.set_visible(True)

    def add_play_listener(self, listener):
        """ Add play listener
        
        :param listener: event listener
        """
        if listener not in self.play_listeners:
            self.play_listeners.append(listener)
            
    def notify_play_listeners(self, state):
        """ Notify all play listeners
        
        :param state: button state
        """
        if not self.screen_title.active:
            return
        
        m = getattr(state, "playback_mode", None)
        if m != None and m != FILE_PLAYLIST:
            state.icon_base = self.file_button.state.icon_base
        folder = getattr(state, "folder", None)
        if folder:
            state.cover_art_folder = self.util.file_util.get_cover_art_folder(state.folder)

        for listener in self.play_listeners:
            listener(state)
    
    def enable_player_screen(self, flag):
        """ Enable player screen
        
        :param flag: enable/disable flag
        """
        self.screen_title.active = flag
        if self.show_time_control:
            self.time_control.active = flag

    def add_screen_observers(self, update_observer, redraw_observer, start_time_control, stop_time_control, title_to_json):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        :param start_time_control:
        :param stop_time_control:
        :param title_to_json:
        """
        self.update_observer = update_observer
        self.redraw_observer = redraw_observer
        Screen.add_screen_observers(self, update_observer, redraw_observer, title_to_json)
        
        self.add_button_observers(self.shutdown_button, update_observer, redraw_observer=None)    
        self.shutdown_button.add_cancel_listener(redraw_observer)
        self.screen_title.add_listener(redraw_observer)
                 
        self.add_button_observers(self.play_button, update_observer, redraw_observer=None)
        self.add_button_observers(self.home_button, update_observer, redraw_observer)

        if self.order_button:
            self.add_button_observers(self.order_button, update_observer, redraw_observer)
        if self.info_button:
            self.add_button_observers(self.info_button, update_observer, redraw_observer)
         
        self.add_button_observers(self.left_button, update_observer, redraw_observer=None)
        self.left_button.add_label_listener(update_observer)
        self.add_button_observers(self.right_button, update_observer, redraw_observer=None)
        self.right_button.add_label_listener(update_observer)
                         
        self.volume.add_slide_listener(update_observer)
        self.volume.add_knob_listener(update_observer)
        self.volume.add_press_listener(update_observer)
        self.volume.add_motion_listener(update_observer)
         
        self.add_button_observers(self.file_button, update_observer, redraw_observer, press=False, release=False)

        if self.order_popup:
            self.order_popup.add_menu_observers(update_observer, redraw_observer)

        if self.info_popup:
            self.info_popup.add_menu_observers(update_observer, redraw_observer)

        if self.show_time_control:
            self.add_button_observers(self.time_volume_button, update_observer, redraw_observer, release=False)
            self.time_control.web_seek_listener = update_observer
            if start_time_control:
                self.time_control.add_start_timer_listener(start_time_control)
            if stop_time_control:
                self.time_control.add_stop_timer_listener(stop_time_control)
            self.time_control.slider.add_slide_listener(update_observer)
            self.time_control.slider.add_knob_listener(update_observer)
            self.time_control.slider.add_press_listener(update_observer)
            self.time_control.slider.add_motion_listener(update_observer)

    def handle_event(self, event):
        """ Handle screen event

        :param event: the event to handle
        """
        if not self.visible:
            return
        
        mouse_events = [pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION]        
        
        if event.type in mouse_events:            
            self.handle_mouse(event)
        elif event.type == USER_EVENT_TYPE:
            self.handle_user_event(event)
        elif event.type == SELECT_EVENT_TYPE:
            self.handle_select_action(event)

    def handle_mouse(self, event):
        """ Mouse event dispatcher
        
        :param event: the event to handle
        """
        button = self.get_collided_button(event)
        if button and event.type == pygame.MOUSEBUTTONDOWN:
            if not ((getattr(self, "time_control", None) != None and button == self.time_control.slider) or (getattr(self, "volume", None) != None and button == self.volume)):
                if getattr(self, "time_control", None) != None and self.current_button == self.time_control.slider:
                    self.time_control.slider.set_knob_off()
                elif getattr(self, "volume", None) != None and self.current_button == self.volume:
                    self.volume.set_knob_off()
                else:
                    self.current_button.set_selected(False)
                    self.current_button.clean_draw_update()
            else:
                if button != self.volume or (button == self.volume and not self.volume.knob_selected):
                    self.current_button.set_selected(False)
                    self.current_button.clean_draw_update()

            self.current_button = button
        elif button and event.type == pygame.MOUSEBUTTONUP:
            if self.config[PLAYER_SETTINGS][MUTE] and button != self.volume:
                prev_pos = event.pos
                event.pos = self.volume.get_knob_center()
                self.volume.selected = True
                self.volume.handle_event(event)
                event.pos = prev_pos
                self.volume.selected = False
                self.volume.clicked = False
                self.volume.set_knob_off()

            if ((getattr(self, "time_control", None) != None and self.current_button != self.time_control.slider and button == self.time_control.slider) or
                (getattr(self, "volume", None) != None and self.current_button != self.volume and button == self.volume)):
                self.current_button.set_selected(False)
                self.current_button.clean_draw_update()
                self.current_button = button

        Container.handle_event(self, event)
        self.redraw_observer()

    def handle_user_event(self, event):
        """ User event handler
        
        :param event: the event to handle
        """
        k = event.keyboard_key

        if k in self.arrow_keys:
            Container.handle_event(self, event)
            if self.config[PLAYER_SETTINGS][MUTE] and event.action == pygame.KEYUP:
                event.keyboard_key = kbd_keys[KEY_MUTE]
                self.volume.selected = True
                self.volume.handle_event(event)
                self.current_button = self.volume
            self.update_web_observer()
        elif k == kbd_keys[KEY_HOME]:
            if self.current_button != self.home_button:
                self.current_button.set_selected(False)

            self.home_button.handle_event(event)
            self.current_button = self.home_button
            self.current_button.set_selected(True)
        elif k == kbd_keys[KEY_PLAY_PAUSE]:
            if event.action == pygame.KEYDOWN:
                self.current_button.set_selected(False)
                self.current_button.clean_draw_update()
                self.update_web_observer()
                self.current_button = self.play_button
            Container.handle_event(self, event)
        elif k == kbd_keys[KEY_MUTE]:
            if self.volume.visible:
                if event.action == pygame.KEYDOWN:
                    self.current_button.set_selected(False)
                    self.current_button.clean_draw_update()
                    self.update_web_observer()
                    self.volume.set_knob_on()
                    self.current_button = self.volume
                Container.handle_event(self, event)
        elif k in self.volume_keys:
            if self.order_button and self.order_popup.visible:
                self.order_popup.handle_outside_event(event)
            
            if self.info_button and self.info_popup.visible:
                self.info_popup.handle_outside_event(event)

            if self.volume.visible:
                if not self.config[PLAYER_SETTINGS][MUTE] and event.action == pygame.KEYDOWN:
                    if self.current_button != self.volume:
                        self.current_button.set_selected(False)
                        self.current_button.clean_draw_update()
                    self.volume.selected = True
                    self.volume.handle_event(event)
                    self.current_button = self.volume
                elif not self.config[PLAYER_SETTINGS][MUTE] and event.action == pygame.KEYUP:
                    self.volume.handle_event(event)
                
                self.update_web_observer()
            elif self.time_control.visible:
                self.time_control.handle_event(event)
                self.update_web_observer()
        elif k in self.previous_next_keys:
            button = None

            if k == kbd_keys[KEY_PAGE_DOWN]:
                button = self.left_button
            elif k == kbd_keys[KEY_PAGE_UP]:
                button = self.right_button

            if button:
                if self.current_button == self.volume:
                    self.volume.set_knob_off()
                else:
                    self.current_button.set_selected(False)
                    self.current_button.clean_draw_update()
                button.handle_event(event)
                button.clean_draw_update()
                self.current_button = button   
        elif k == kbd_keys[KEY_HOME]:
            self.home_button.handle_event(event)
        elif k == kbd_keys[KEY_SELECT]:
            if event.action == pygame.KEYUP:
                if self.order_button.selected and not self.order_popup.visible:
                    self.order_button.handle_event(event)
                elif self.info_button.selected and not self.info_popup.visible:
                    self.info_button.handle_event(event)
                else:
                    if not (self.order_popup.visible or self.info_popup.visible):
                        self.current_button.handle_event(event)
                    else:
                        Container.handle_event(self, event)

    def get_collided_button(self, event):
        """ Get clicked button
        
        :param event: the event
        """
        if (getattr(self, "order_popup", None) != None and self.order_popup.visible) or (getattr(self, "info_popup", None) != None and self.info_popup.visible):
            return None

        pos = getattr(event, "pos", None)
        if pos == None:
            pos = (event.x, event.y)
        button = None

        if self.shutdown_button.bounding_box.collidepoint(pos):
            button = self.shutdown_button
        elif self.left_button.bounding_box.collidepoint(pos):
            button = self.left_button
        elif self.home_button.bounding_box.collidepoint(pos):
            button = self.home_button
        elif self.play_button.bounding_box.collidepoint(pos):
            button = self.play_button
        elif self.right_button.bounding_box.collidepoint(pos):
            button = self.right_button
        elif self.file_button.bounding_box.collidepoint(pos):
            button = self.file_button
        
        if getattr(self, "order_button", None) != None and self.order_button.bounding_box.collidepoint(pos):
            button = self.order_button

        if getattr(self, "info_button", None) != None and self.info_button.bounding_box.collidepoint(pos):
            button = self.info_button

        if getattr(self, "time_volume_button", None) != None and self.time_volume_button.bounding_box.collidepoint(pos): 
            button = self.time_volume_button

        if getattr(self, "time_control", None) != None and self.time_control.visible and self.time_control.slider.bounding_box.collidepoint(pos):
            button = self.time_control.slider

        if getattr(self, "volume", None) != None and self.volume.visible and self.volume.bounding_box.collidepoint(pos):
            button = self.volume

        return button

    def handle_select_action(self, event):
        """ Handle select action

        :param event: the event
        """
        button = self.get_collided_button(event)
        if button:
            if button == self.time_control.slider:
                self.time_control.slider.set_knob_on()
            elif button == self.volume:
                self.volume.set_knob_on()
            else:
                button.enter_y = event.y
                self.select_button(button)

            self.current_button = button
            self.update_web_observer()

    def select_button(self, button):
        """ Selected provided button

        :param button: the button to select
        """
        if hasattr(self.current_button, "set_selected"):
            self.current_button.set_selected(False)
        if hasattr(button, "set_selected"):
            button.set_selected(True)
        button.clean_draw_update()
