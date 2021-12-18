# Copyright 2021 Peppy Player peppy.player@gmail.com
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

from pygame import Rect
from ui.factory import Factory
from ui.container import Container
from ui.screen.screen import Screen
from ui.menu.popup import Popup
from ui.layout.borderlayout import BorderLayout
from util.config import *
from util.keys import *

class PlayerScreen(Screen):
    """ The Parent for all player screens """
    
    def __init__(self, util, listeners, screen_title, show_arrow_labels=True, show_order=True, show_info=True, 
        show_time_control=True, voice_assistant=None, volume_control=None):
        """ Initializer
        
        :param util: utility object
        :param listeners: screen event listeners
        :param screen_title: screen title/id
        :param show_arrow_labels: True - show arrow lables, False - don't show
        :param show_order: True - show the order button/popup, False - don't show
        :param show_info: True - show the info button/popup, False - don't show
        :param show_time_control: True - show the time control, False - don't show
        :param voice_assistant: the voice assistant
        """
        self.util = util
        self.config = util.config
        self.factory = Factory(util)
        self.player = listeners[KEY_PLAY]
        self.bounding_box = util.screen_rect
        self.show_order = show_order
        self.show_info = show_info
        self.show_time_control = show_time_control
        self.volume_control = volume_control
        self.order_button = None
        self.info_button = None
        self.order_popup = None
        self.info_popup = None

        self.top_height = self.config[PLAYER_SCREEN][TOP_HEIGHT_PERCENT]
        self.bottom_height = self.config[PLAYER_SCREEN][BOTTOM_HEIGHT_PERCENT]
        self.button_height = self.config[PLAYER_SCREEN][BUTTON_HEIGHT_PERCENT]
        self.popup_width = self.config[PLAYER_SCREEN][POPUP_WIDTH_PERCENT]
        self.image_location = self.config[PLAYER_SCREEN][IMAGE_LOCATION]

        self.layout = self.get_layout()
        Screen.__init__(self, util, "", self.top_height, voice_assistant, screen_title, True, self.layout.TOP)
        self.layout = self.get_layout()

        self.custom_button = None
        self.center_button = None
        self.create_left_panel(self.layout, show_arrow_labels)
        self.create_right_panel(self.layout, show_arrow_labels)
        self.create_bottom_panel(self.layout.BOTTOM)

        self.player_screen = True
        self.animated_title = True
        self.arrow_keys = [kbd_keys[KEY_LEFT], kbd_keys[KEY_RIGHT], kbd_keys[KEY_UP], kbd_keys[KEY_DOWN]]
        self.player_keys = [kbd_keys[KEY_PLAY_PAUSE], kbd_keys[KEY_MUTE]]
        self.volume_keys = [kbd_keys[KEY_VOLUME_UP], kbd_keys[KEY_VOLUME_DOWN]]
        self.previous_next_keys = [kbd_keys[KEY_PAGE_DOWN], kbd_keys[KEY_PAGE_UP]]
        self.playlist = []
        self.current_index = 0

        self.volume_control.add_volume_listener(self.volume.set_update_position)
        self.volume_control.add_mute_listener(self.handle_mute_key)
        self.volume_control.add_play_pause_listener(self.handle_play_key)
        self.volume_control.add_previous_next_listener(self.handle_previous_next_key)

    def set_listeners(self, listeners):
        """ Set event listeners

        :param listeners: the dictionary of the listeners
        """
        self.shutdown_button.add_release_listener(listeners[KEY_SHUTDOWN])
        self.home_button.add_release_listener(listeners[KEY_HOME])
        self.stop_player = listeners[KEY_STOP]
        self.start_screensaver = listeners[SCREENSAVER]

        self.volume.add_slide_listener(listeners[KEY_SET_VOLUME])
        self.volume.add_slide_listener(listeners[KEY_SET_CONFIG_VOLUME])
        self.volume.add_slide_listener(listeners[KEY_SET_SAVER_VOLUME])
        self.volume.add_knob_listener(listeners[KEY_MUTE])

        if KEY_SEEK in listeners.keys():
            self.time_control.add_seek_listener(listeners[KEY_SEEK])

        if self.show_order and self.show_info:
            self.go_info_screen = listeners[KEY_INFO]

    def link_borders(self):
        """ Link components borders for the arrow keys navigation """

        if self.show_order:
            order_x = self.order_button.bounding_box.x
            order_y = self.order_button.bounding_box.y
        else:
            order_x = None
            order_y = None

        if self.show_info:
            info_x = self.info_button.bounding_box.x
            info_y = self.info_button.bounding_box.y
        else:
            info_x = None
            info_y = None

        self.center_button.ignore_enter_y = False
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
        volume_x = self.volume.bounding_box.x
        volume_y = self.volume.bounding_box.y

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
        if top != None and top[0] != None and top[1] != None: 
            button.exit_top_x = top[0] + margin
            button.exit_top_y = top[1] + margin
        if bottom != None and bottom[0] != None and bottom[1] != None: 
            button.exit_bottom_x = bottom[0] + margin
            button.exit_bottom_y = bottom[1] + margin

    def get_layout(self):
        """ Get the layout of the center area of the screen for image and buttons

        :return: layout rectangle
        """
        layout = BorderLayout(self.bounding_box)

        top = int(self.bounding_box.h * self.top_height / 100)
        bottom = int(self.bounding_box.h * self.bottom_height / 100)
        center = self.bounding_box.h - top - bottom
        if center % 2 != 0:
            top -= 1
            center += 1
        left = right = (self.bounding_box.w - center) / 2

        if self.image_location == LOCATION_CENTER:
            layout.set_pixel_constraints(top, bottom, left, right)
        elif self.image_location == LOCATION_LEFT:
            layout.set_pixel_constraints(top, bottom, 0, right * 2)
        elif self.image_location == LOCATION_RIGHT:
            layout.set_pixel_constraints(top, bottom, right * 2, 0)

        layout.LEFT.h -= 1
        layout.RIGHT.h -= 1
        layout.BOTTOM.y -= 1
        layout.BOTTOM.h += 1

        return layout

    def get_panel_layout(self, layout, panel_location):
        """ Get the layout of the panel for buttons

        :param layout: layout of the whole central area
        :param panel_location: panel location - left or right

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

    def create_left_panel(self, layout, arrow_labels):
        """ Create left side buttons panel
        
        :param layout: panel layout 
        :param arrow_labels: show arrow label or not
        """
        panel_layout = self.get_panel_layout(layout, LOCATION_LEFT)
        panel_layout.set_percent_constraints(self.button_height, self.button_height, 0, 0)
        self.left_button = self.factory.create_left_button(panel_layout.CENTER, '', 40, 100, arrow_labels)
        self.left_button.add_release_listener(self.go_left)
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

    def create_right_panel(self, layout, arrow_labels):
        """ Create right side buttons panel
        
        :param layout: panel layout 
        :param arrow_labels: show arrow label or not
        """
        panel_layout = self.get_panel_layout(layout, LOCATION_RIGHT)
        panel_layout.set_percent_constraints(self.button_height, self.button_height, 0, 0)
        panel_layout.TOP.y += 1
        panel_layout.TOP.h -= 2
        self.play_button = self.factory.create_play_pause_button(panel_layout.TOP, self.listeners[KEY_PLAY_PAUSE])
        self.right_button = self.factory.create_right_button(panel_layout.CENTER, '', 40, 100, arrow_labels)
        self.right_button.add_release_listener(self.go_right)
        panel_layout.BOTTOM.h += 1
        self.custom_button_layout = panel_layout.BOTTOM
        panel = Container(self.util, layout.RIGHT)
        panel.add_component(self.play_button)
        panel.add_component(self.right_button)
        self.right_panel = panel
        self.add_component(panel)

    def create_bottom_panel(self, layout):
        """ Create bottom panel
        
        :param layout: panel layout 
        """
        self.playback_order = self.config[PLAYER_SETTINGS][PLAYBACK_ORDER]

        if self.show_order or self.show_info:
            self.add_popups(layout)
            self.bottom_center_layout.x -= 1
            self.bottom_center_layout.y += 1
            self.bottom_center_layout.w += 1
            self.bottom_center_layout.h -= 1
            self.volume = self.factory.create_volume_control(self.bottom_center_layout)
        else:
            layout.y += 1
            layout.h -= 1
            self.volume = self.factory.create_volume_control(layout)

        self.add_component(self.volume)
        
        if self.show_time_control:
            self.volume_visible = False
            self.volume.set_visible(self.volume_visible)
            self.time_control = self.factory.create_time_control(self.bottom_center_layout)
            if self.config[PLAYER_SETTINGS][PAUSE]:
                self.time_control.pause()
            self.time_control.slider.handle_knob_events = False
            self.add_component(self.time_control)
            self.play_button.add_listener(PAUSE, self.time_control.pause)
            self.play_button.add_listener(KEY_PLAY, self.time_control.resume)
        else:
            self.time_control = None

    def add_popups(self, layout):
        """ Add popup menus - playback order & info 
        
        :param layout: bottom panel layout
        """
        self.bottom_layout = BorderLayout(layout)
        
        if self.show_order and not self.show_info:
            self.bottom_layout.set_percent_constraints(0, 0, self.popup_width, 0)
            self.order_button = self.factory.create_order_button(self.bottom_layout.LEFT, self.handle_order_button, self.playback_order)
            self.order_popup = self.get_order_popup(self.bounding_box)
            self.add_component(self.order_button)
        elif self.show_order and self.show_info:
            self.bottom_layout.set_percent_constraints(0, 0, self.popup_width, self.popup_width)
            self.bottom_layout.LEFT.w -= 1
            self.bottom_layout.LEFT.y += 1
            self.bottom_layout.LEFT.h -= 1
            self.bottom_layout.RIGHT.y += 1
            self.bottom_layout.RIGHT.h -= 1
            self.order_button = self.factory.create_order_button(self.bottom_layout.LEFT, self.handle_order_button, self.playback_order)
            self.info_button = self.factory.create_info_button(self.bottom_layout.RIGHT, self.handle_info_button)
            self.order_popup = self.get_order_popup(self.bounding_box)
            self.info_popup = self.get_info_popup(self.bounding_box)
            self.add_component(self.order_button)
            self.add_component(self.info_button)
        elif not self.show_order and self.show_info:
            self.bottom_layout.set_percent_constraints(0, 0, 0, self.popup_width)
            self.bottom_layout.RIGHT.y += 1
            self.bottom_layout.RIGHT.h -= 1
            self.info_button = self.factory.create_info_button(self.bottom_layout.RIGHT, self.handle_info_button)
            self.info_popup = self.get_info_popup(self.bounding_box)
            self.add_component(self.info_button)
            
        self.bottom_layout.CENTER.w -= 2
        self.bottom_layout.CENTER.x += 1
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

        if not self.util.connected_to_internet:
            disabled_items = [WEATHER, LYRICS]
        else:
            disabled_items = None       
        
        layout = BorderLayout(bb)
        layout.set_percent_constraints(self.top_height, 0, 0, self.popup_width)
        popup = Popup(items, self.util, layout.RIGHT, self.update_screen, self.handle_info_popup_selection, disabled_items=disabled_items)

        return popup

    def update_screen(self):
        """ Update the screen """

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

    def get_listener(self, listeners, name):
        """ Return listener by name/key in the dictionary

        :param listeners: all listeners
        :param name: listener name

        :return: listener if avaialble, None - otherwise
        """
        if name in listeners.keys():
            return listeners[name]
        else:
            return None

    def set_current(self, state=None):
        """ Player specific function

        :param state: the source button state
        """
        pass

    def set_visible(self, flag):
        """ Set visibility flag
         
        :param flag: True - screen visible, False - screen invisible
        """
        Container.set_visible(self, flag)

        if self.volume_visible and not self.config[PLAYER_SETTINGS][MUTE]:
            self.volume.unselect_knob()

        if self.time_control == None or not flag:
            return

        if self.volume_visible:
            self.volume.set_visible(True)
            if self.show_time_control:
                self.time_control.set_visible(False)
        else:
            self.volume.set_visible(False)
            if self.show_time_control:
                self.time_control.set_visible(True)
    
    def add_screen_observers(self, update_observer, redraw_observer, start_time_control=None, stop_time_control=None, title_to_json=None):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        :param title_to_json:
        :param start_time_control:
        :param stop_time_control:        
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

        if self.center_button: 
            self.add_button_observers(self.center_button, update_observer, redraw_observer, press=False, release=False)

        if self.order_popup:
            self.order_popup.add_menu_observers(update_observer, redraw_observer)

        if self.info_popup:
            self.info_popup.add_menu_observers(update_observer, redraw_observer)

        if self.show_time_control:
            self.add_button_observers(self.custom_button, update_observer, redraw_observer, release=False)
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
        if not self.visible and event.type != USER_EVENT_TYPE:
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
            self.handle_mouse_down(event, button)    
        elif button and event.type == pygame.MOUSEBUTTONUP:
            self.handle_mouse_up(event, button)
        elif event.type == pygame.MOUSEMOTION:
            self.handle_mouse_motion(event)
            return  
        
        Container.handle_event(self, event)
        self.redraw_observer()

    def handle_mouse_down(self, event, button):
        """ Handle mouse button down event

        :param event: the event to handle
        :param button: the clicked button
        """
        if not ((self.time_control and button == self.time_control.slider) or button == self.volume):
            if hasattr(self, "current_button") and self.time_control and self.current_button == self.time_control.slider:
                self.time_control.slider.set_knob_off()
            elif hasattr(self, "current_button") and self.current_button == self.volume:
                self.volume.set_knob_off()
            elif hasattr(self, "current_button") and self.current_button != self.center_button:
                self.current_button.set_selected(False)
                self.current_button.clean_draw_update()
                pass
        else:
            if hasattr(self, "current_button") and (button != self.volume or (button == self.volume and not self.volume.knob_selected)):
                self.current_button.set_selected(False)
                self.current_button.clean_draw_update()

        if self.current_button != button:
            self.current_button.set_selected(False)
            self.current_button.clean_draw_update()

        self.current_button = button

    def handle_mouse_up(self, event, button):
        """ Handle mouse button up event

        :param event: the event to handle
        :param button: the clicked button
        """
        if self.config[PLAYER_SETTINGS][MUTE] and button != self.volume:
            prev_pos = event.pos
            event.pos = self.volume.get_knob_center()
            self.volume.selected = True
            self.volume.knob_selected = True
            self.volume.mouse_action(event)
            event.pos = prev_pos
            self.volume.selected = False
            self.volume.clicked = False
            self.volume.set_knob_off()

        if ((self.time_control and button == self.time_control.slider) or button == self.volume) and self.current_button != self.volume and self.time_control and self.current_button != self.time_control.slider:
            self.current_button.set_selected(False)
            self.current_button.clean_draw_update()
            
        self.current_button = button

    def handle_mouse_motion(self, event):
        """ Handle mouse button up event

        :param event: the event to handle
        """
        if self.volume.clicked:
            self.volume.handle_event(event)
        elif self.time_control and self.time_control.slider.clicked:
            self.time_control.handle_event(event)

    def handle_user_event(self, event):
        """ User event dispatcher
        
        :param event: the event to handle
        """
        k = event.keyboard_key

        if k in self.arrow_keys:
            self.handle_arrow_key(event)
        elif k in self.volume_keys:
            self.handle_volume_key(event)
        elif k == kbd_keys[KEY_HOME]:
            self.handle_home_key(event)
        elif k == kbd_keys[KEY_SELECT]:
            self.handle_select_key(event)
        elif k == kbd_keys[KEY_END]:
            self.handle_shutdown_key(event)

    def handle_shutdown_key(self, event):
        """ Shutdown key handler
        
        :param event: the event to handle
        """
        self.current_button.set_selected(False)
        self.current_button.clean_draw_update()
        self.current_button = self.shutdown_button
        self.select_button(self.shutdown_button)
        self.update_web_observer()
        
        Container.handle_event(self, event)    

    def handle_previous_next_key(self, event):
        """ Next/previous keys handler
        
        :param event: the event to handle
        """
        if not self.screen_title.active:
            return

        k = event.keyboard_key
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

            button.release_action(False)
            button.clean_draw_update()
            self.current_button = button
            self.update_web_observer()

    def handle_arrow_key(self, event):
        """ Arrow keys handler
        
        :param event: the event to handle
        """
        Container.handle_event(self, event)
        if self.config[PLAYER_SETTINGS][MUTE] and event.action == pygame.KEYUP:
            event.keyboard_key = kbd_keys[KEY_MUTE]
            self.volume.selected = True
            self.volume.handle_event(event)
            self.current_button = self.volume
        self.update_web_observer()

    def handle_play_key(self, event):
        """ Play/pause keys handler
        
        :param event: the event to handle
        """
        if event.action != pygame.KEYUP: return

        if self.show_time_control:
            self.time_control.pause()

        self.current_button.set_selected(False)
        self.current_button.clean_draw_update()
        self.play_button.release_action(False)
        self.current_button = self.play_button
        self.update_web_observer()

    def handle_mute_key(self, event):
        """ Mute key handler
        
        :param event: the event to handle
        """
        if event.action != pygame.KEYUP or not self.volume_visible: return

        self.current_button.set_selected(False)
        self.current_button.clean_draw_update()
        self.volume.handle_knob_selection(notify=False)
        self.volume.clicked = False
        self.current_button = self.volume
        self.current_button.clean_draw_update()
        self.update_web_observer()

    def handle_volume_key(self, event):
        """ Volume Up/Down keys handler
        
        :param event: the event to handle
        """
        if not self.volume.visible:
            return

        if self.order_button and self.order_popup.visible:
            self.order_popup.handle_outside_event(event)
        
        if self.info_button and self.info_popup.visible:
            self.info_popup.handle_outside_event(event)

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

    def handle_home_key(self, event):
        """ Home key handler
        
        :param event: the event to handle
        """
        if self.current_button != self.home_button:
            self.current_button.set_selected(False)

        self.home_button.handle_event(event)
        self.current_button = self.home_button
        self.current_button.set_selected(True)

    def handle_select_key(self, event):
        """ Select key handler
        
        :param event: the event to handle
        """
        if event.action == pygame.KEYUP:
            if self.order_button and self.order_button.selected and not self.order_popup.visible:
                self.order_button.handle_event(event)
            elif self.info_button and self.info_button.selected and not self.info_popup.visible:
                self.info_button.handle_event(event)
            else:
                if not ((self.order_button and self.order_popup.visible) or (self.info_button and self.info_popup.visible)):
                    if hasattr(self, "current_button"):
                        self.current_button.handle_event(event)
                else:
                    Container.handle_event(self, event)
                self.update_web_observer()
        elif event.action == pygame.KEYDOWN:
            if hasattr(self, "current_button"):
                self.current_button.handle_event(event)

    def get_collided_button(self, event):
        """ Get clicked button by click point coordinates
        
        :param event: the event

        :return: the button clicked
        """
        if (self.order_popup and self.order_popup.visible) or (self.info_popup and self.info_popup.visible):
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
        elif self.order_button and self.order_button.bounding_box.collidepoint(pos):
            button = self.order_button
        elif self.play_button.bounding_box.collidepoint(pos):
            button = self.play_button
        elif self.right_button.bounding_box.collidepoint(pos):
            button = self.right_button
        elif self.custom_button and self.custom_button.bounding_box.collidepoint(pos):
            button = self.custom_button
        elif self.info_button and self.info_button.bounding_box.collidepoint(pos):
            button = self.info_button
        elif self.center_button and self.center_button.bounding_box.collidepoint(pos):
            button = self.center_button
        else:
            if self.time_control and self.time_control.visible and self.time_control.bounding_box.collidepoint(pos):
                button = self.time_control.slider
            elif self.volume.visible and self.volume.bounding_box.collidepoint(pos):
                button = self.volume

        return button

    def handle_select_action(self, event):
        """ Handle select action

        :param event: the event
        """
        button = self.get_collided_button(event)
        if button:
            if self.time_control and button == self.time_control.slider:
                self.time_control.slider.set_knob_on()
            elif button == self.volume:
                self.volume.set_knob_on()
            else:
                button.enter_y = event.y
                self.select_button(button)

            self.current_button = button
            self.update_web_observer()

    def select_button(self, button):
        """ Select button
        
        :param button: the button to select
        """
        if hasattr(self.current_button, "set_selected"):
            self.current_button.set_selected(False)
        if hasattr(button, "set_selected"):
            button.set_selected(True)
        button.clean_draw_update()

    def update_arrow_button_labels(self):
        """ Update arrow buttons state """

        if len(self.playlist) == 0:
            left = right = "0"
        else:    
            left = str(self.current_index)
            right = str(len(self.playlist) - self.current_index - 1)

        self.left_button.change_label(left)
        self.right_button.change_label(right)

    def go_left(self, state):
        """ Switch to the previous item
        
        :param state: not used state object
        """
        playlist_size = len(self.playlist)

        if playlist_size == 0:
            return

        if self.current_index == 0:
            self.current_index = playlist_size - 1
        else:
            self.current_index -= 1

        self.change_item()

    def go_right(self, state):
        """ Switch to the next item
        
        :param state: not used state object
        """
        playlist_size = len(self.playlist)

        if playlist_size == 0:
            return

        if self.current_index == playlist_size - 1:
            self.current_index = 0
        else:
            self.current_index += 1

        self.change_item()

    def change_item(self):
        """ Update item """

        self.play_button.draw_default_state(None)
        self.set_current_item(self.current_index)
        self.update_arrow_button_labels()
        self.update_center_button()
        self.update_web_observer()
        self.play()

    def set_current_item(self, index):
        """ Spsecific for each player. Sets config item """

        pass

    def set_title(self, current_item):
        """ Set screen title

        :param current_item: the current button state object
        """
        d = {"current_title" : getattr(current_item, "comparator_item", "")}
        flag = self.screen_title.active
        self.enable_player_screen(True)
        self.screen_title.set_text(d)
        self.enable_player_screen(flag)

    def update_center_button(self):
        """ Update the center button """

        current_state = self.playlist[self.current_index]
        current_state.bounding_box = self.layout.CENTER
        self.util.add_icon(current_state)

        button = self.get_center_button(current_state)
        self.center_button.state = button.state
        self.center_button.components = button.components
        self.center_button.clean_draw_update()
        self.set_title(current_state)

    def play(self):
        """ Start playback """

        if hasattr(self, "center_button") and self.center_button != None and hasattr(self.center_button, "state"):
            self.center_button.state.volume = self.config[PLAYER_SETTINGS][VOLUME]
            self.play_button.draw_default_state(None)
            self.config[PLAYER_SETTINGS][PAUSE] = False
            self.player(self.center_button.state)

    def enable_player_screen(self, flag):
        """ Enable player screen
        
        :param flag: enable/disable flag
        """
        self.screen_title.active = flag

    def go_back(self):
        """ Go back """
        pass
    