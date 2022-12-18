# Copyright 2020-2022 Peppy Player peppy.player@gmail.com
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

from ui.component import Component
from ui.container import Container
from ui.factory import Factory
from ui.menu.menu import Menu, ALIGN_CENTER
from ui.layout.gridlayout import GridLayout
from util.keys import USER_EVENT_TYPE, SUB_TYPE_KEYBOARD, V_ALIGN_CENTER, H_ALIGN_CENTER
from util.config import NAME, COLORS, COLOR_BRIGHT, SCREEN_INFO, WIDTH, HEIGHT

IMAGE_SCALE = 0.49

class Popup(Container):
    """ Popup Menu class """

    def __init__(
        self,
        items,
        util,
        bounding_box,
        update_parent,
        callback,
        default_selection=None,
        disabled_items=None,
        align=ALIGN_CENTER,
        h_align=H_ALIGN_CENTER,
        v_align=V_ALIGN_CENTER,
        show_image=True,
        show_label=False,
        suffix=None,
        label_text_height=None,
        bgr=None,
        popup_selector=None,
        columns=1,
        wrap_lines=False,
        column_weights=None
    ):
        """ Initializer

        :param items: list of item names
        :param util: utility object
        :param bounding_box: bounding box
        :param update_parent: redraw parent function
        :param callback: menu selection callback
        :param default_selection: default selection
        :param disabled_items: disabled menu items
        """
        Container.__init__(self, util, bounding_box, (0, 0, 0))
        self.util = util
        self.factory = Factory(util)
        self.config = util.config
        self.update_parent = update_parent
        self.callback = callback
        self.show_label = show_label
        self.popup = True
        self.label_text_height = label_text_height
        self.popup_bgr=bgr

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

        self.columns = columns
        self.rows = int(len(items) / columns)

        m = self.create_popup_menu_button
        b = pygame.Rect(bounding_box.x, bounding_box.y, bounding_box.w, bounding_box.h - 2)
        self.menu = Menu(util, None, b, self.rows, columns, create_item_method=m, align=align, column_weights=column_weights)
        
        layout = GridLayout(self.menu.bb)
        layout.set_pixel_constraints(self.rows, columns, 1, 1)
        bounding_box = layout.get_next_constraints()
        self.modes = self.util.load_menu(
            items,
            NAME,
            disabled_items,
            h_align=h_align,
            v_align=v_align,
            bb=bounding_box,
            scale=IMAGE_SCALE,
            show_image=show_image,
            wrap_lines=wrap_lines
        )

        if self.modes and suffix:
            for m in self.modes.values():
                m.l_name += suffix

        if not default_selection:
            selection = self.modes[items[0]]
        else:
            selection = self.modes[default_selection]

        if popup_selector:
            selector = popup_selector
        else:
            selector = self.select_item

        self.menu.set_items(self.modes, 0, selector, False)
        self.menu.visible = False
        self.menu.item_selected(selection)

        self.add_component(self.menu)

        self.redraw_observer = None
        self.clicked = False
        self.visible = False

    def create_popup_menu_button(self, s, constr, action, scale, bgr=None, font_size=0):
        """ Create Popup Menu button

        :param s: button state
        :param constr: scaling constraints
        :param action: button event listener
        :param scale: True - scale images, False - don't scale images

        :return: home menu button
        """
        return self.factory.create_menu_button(
            s,
            constr,
            action,
            bgr=self.popup_bgr,
            scale=True,
            show_label=self.show_label,
            ignore_bgr_opacity=True,
            label_text_height=self.label_text_height
        )

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
            valid_keys = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]
            if event.sub_type == SUB_TYPE_KEYBOARD and event.keyboard_key not in valid_keys and event.action == pygame.KEYUP:
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
