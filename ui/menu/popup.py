# Copyright 2020 Peppy Player peppy.player@gmail.com
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
import logging

from ui.component import Component
from ui.container import Container
from ui.factory import Factory
from ui.menu.menu import Menu
from ui.layout.gridlayout import GridLayout
from util.keys import V_ALIGN_TOP, USER_EVENT_TYPE, SUB_TYPE_KEYBOARD
from util.config import NAME, COLORS, COLOR_BRIGHT, SCREEN_INFO, WIDTH, HEIGHT

IMAGE_SCALE = 0.49

class Popup(Container):
    """ Popup Menu class """

    def __init__(self, items, util, bounding_box, update_parent, callback, default_selection=None):
        """ Initializer

        :param items: list of item names
        :param util: utility object
        :param bounding_box: bounding box
        :param update_parent: redraw parent function
        :param callback: menu selection callback
        """
        Container.__init__(self, util, bounding_box, (0, 0, 0))
        self.util = util
        self.factory = Factory(util)
        self.config = util.config
        self.update_parent = update_parent
        self.callback = callback
        self.popup = True

        c = Component(self.util)
        w = self.config[SCREEN_INFO][WIDTH]
        h = self.config[SCREEN_INFO][HEIGHT]
        c.content = pygame.Rect(0, 0, w, h)
        c.content_x = 0
        c.content_y = 0
        c.bounding_box = c.content
        c.bgr = (0, 0, 0, 0)
        c.name = "popup.overlay.bgr"
        c.handle_event = self.handle_outside_event
        self.add_component(c)

        c = Component(self.util)
        c.content = pygame.Rect(bounding_box.x, bounding_box.y, bounding_box.w, bounding_box.h - 1)
        c.content_x = 0
        c.content_y = 0
        c.bounding_box = c.content
        c.bgr = self.config[COLORS][COLOR_BRIGHT]
        c.name = "popup.bgr"
        self.add_component(c)

        self.cols = 1
        self.rows = len(items)

        m = self.create_popup_menu_button
        b = pygame.Rect(bounding_box.x, bounding_box.y, bounding_box.w, bounding_box.h - 2)
        self.menu = Menu(util, None, b, self.rows, self.cols, create_item_method=m)
        
        layout = GridLayout(self.menu.bb)
        layout.set_pixel_constraints(self.rows, self.cols, 1, 1)
        bounding_box = layout.get_next_constraints()
        self.modes = self.util.load_menu(items, NAME, [], V_ALIGN_TOP, bb=bounding_box, scale=IMAGE_SCALE)

        if not default_selection:
            selection = self.modes[items[0]]
        else:
            selection = self.modes[default_selection]

        self.menu.set_items(self.modes, 0, self.select_item, False)
        self.menu.visible = False
        self.menu.item_selected(selection)
        self.add_component(self.menu)

        self.redraw_observer = None
        self.clicked = False
        self.visible = False

    def create_popup_menu_button(self, s, constr, action, scale, font_size=0):
        """ Create Popup Menu button

        :param s: button state
        :param constr: scaling constraints
        :param action: button event listener
        :param scale: True - scale images, False - don't scale images

        :return: home menu button
        """
        return self.factory.create_menu_button(s, constr, action, scale=True, show_label=False, ignore_bgr_opacity=True)

    def handle_outside_event(self, event):
        """ Handle popup event
        
        :param event: the event to handle
        """
        if not self.visible: return

        mouse_events = [pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN]
        
        if event.type in mouse_events and event.button == 1 and not self.menu.bb.collidepoint(event.pos):
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.clicked = True
            elif event.type == pygame.MOUSEBUTTONUP and self.clicked:
                self.clicked = False
                self.set_visible(False)
                self.update_parent()
                if self.redraw_observer:
                    self.redraw_observer()
        elif event.type == USER_EVENT_TYPE:
            if event.sub_type == SUB_TYPE_KEYBOARD and event.keyboard_key == pygame.K_ESCAPE:
                self.set_visible(False)
                self.update_parent()

    def select_item(self, state):
        """ Select menu item

        :param state: button state
        """
        self.set_visible(False)
        self.update_parent()
        self.callback(state)

    def update_popup(self, state):
        if not self.visible: return

        self.clean_draw_update()

    def add_menu_observers(self, update_observer, redraw_observer):
        """ Add menu observer
        
        :param update_observer: observer for updating menu
        :param redraw_observer: observer to redraw the whole screen
        """
        for b in self.menu.buttons.values():
            b.add_press_listener(update_observer)
            b.add_release_listener(redraw_observer)

        self.menu.add_move_listener(redraw_observer)
        self.menu.add_listener(redraw_observer)

        self.redraw_observer = redraw_observer
