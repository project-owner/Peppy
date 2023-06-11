# Copyright 2018-2023 Peppy Player peppy.player@gmail.com
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
from ui.layout.borderlayout import BorderLayout
from ui.layout.gridlayout import GridLayout
from ui.screen.screen import Screen
from ui.navigator.timer import TimerNavigator
from ui.menu.sleepmenu import SleepMenu
from ui.menu.wakeupmenu import WakeUpMenu
from util.config import TIMER, WAKE_UP, SLEEP, POWEROFF, SLEEP_NOW
from util.keys import kbd_keys, LABELS, USER_EVENT_TYPE, SUB_TYPE_KEYBOARD, KEY_LEFT, KEY_RIGHT, \
    KEY_UP, KEY_DOWN, KEY_SELECT, SELECT_EVENT_TYPE, KEY_HOME, KEY_PLAYER

PERCENT_TITLE = 14
PERCENT_NAV_HEIGHT = 14
PERCENT_CLOCK = 80

HOURS_INCREMENT_SLEEP = 0
MINUTES_INCREMENT_SLEEP = 1
HOURS_DECREMENT_SLEEP = 2
MINUTES_DECREMENT_SLEEP = 3
HOURS_INCREMENT_WAKE_UP = 4
MINUTES_INCREMENT_WAKE_UP = 5
HOURS_DECREMENT_WAKE_UP = 6
MINUTES_DECREMENT_WAKE_UP = 7


class TimerScreen(Screen):
    """ Timer Screen """

    def __init__(self, util, listeners, timer_lock, start_timer_thread):
        """ Initializer

        :param util: utility object
        :param listeners: screen navigator listeners
        :param timer_lock: lock object
        :param start_timer_thread: start timer thread function
        """
        self.util = util
        self.timer_lock = timer_lock
        self.start_timer_thread = start_timer_thread
        self.config = util.config
        self.screen_layout = BorderLayout(util.screen_rect)
        self.screen_layout.set_percent_constraints(PERCENT_TITLE, PERCENT_NAV_HEIGHT, 0, 0)
        Screen.__init__(self, util, "", PERCENT_NAV_HEIGHT, "timer_title", title_layout=self.screen_layout.TOP)
        self.bounding_box = util.screen_rect
        label = self.config[LABELS][TIMER]
        self.screen_title.set_text(label)

        try:
            self.config[TIMER]
        except:
            self.config[TIMER] = {}

        c = GridLayout(self.screen_layout.CENTER)
        c.set_pixel_constraints(2, 1)
        layout = BorderLayout(c.get_next_constraints())
        layout.set_percent_constraints(0, 0, PERCENT_CLOCK, 100 - PERCENT_CLOCK)
        gap = layout.h * 0.1
        layout.LEFT.w -= gap * 3
        layout.LEFT.h -= gap
        digits = util.image_util.get_flipclock_digits(layout.LEFT)

        change_codes = [HOURS_INCREMENT_SLEEP, MINUTES_INCREMENT_SLEEP, HOURS_DECREMENT_SLEEP, MINUTES_DECREMENT_SLEEP]
        self.sleep_menu = SleepMenu(util, layout, gap, digits, self.handle_button, timer_lock, self.sleep_change_callback, change_codes)
        self.active_key_menu = self.sleep_menu
        self.add_component(self.sleep_menu)
        self.menu_index = -1
        self.sleep_menu.clock.add_change_listener(self.handle_clock_change)

        layout = BorderLayout(c.get_next_constraints())
        layout.set_percent_constraints(0, 0, PERCENT_CLOCK, 100 - PERCENT_CLOCK)

        change_codes = [HOURS_INCREMENT_WAKE_UP, MINUTES_INCREMENT_WAKE_UP, HOURS_DECREMENT_WAKE_UP, MINUTES_DECREMENT_WAKE_UP]
        self.wake_up_menu = WakeUpMenu(util, layout, gap, digits, self.handle_button, timer_lock, self.wake_up_change_callback, change_codes)
        self.add_component(self.wake_up_menu)
        self.wake_up_menu.clock.add_change_listener(self.handle_clock_change)

        self.navigator = TimerNavigator(self.util, self.screen_layout.BOTTOM, listeners)
        self.navigator.components[0].set_selected(True)
        self.add_component(self.navigator)
        self.home_button = self.navigator.get_button_by_name(KEY_HOME)
        self.sleep_now_button = self.navigator.get_button_by_name(SLEEP_NOW)
        self.player_button = self.navigator.get_button_by_name(KEY_PLAYER)

        self.menu_functions = {
            HOURS_INCREMENT_SLEEP: self.sleep_menu.clock.increment_hours,
            MINUTES_INCREMENT_SLEEP: self.sleep_menu.clock.increment_minutes,
            HOURS_DECREMENT_SLEEP: self.sleep_menu.clock.decrement_hours,
            MINUTES_DECREMENT_SLEEP: self.sleep_menu.clock.decrement_minutes,
            HOURS_INCREMENT_WAKE_UP: self.wake_up_menu.clock.increment_hours,
            MINUTES_INCREMENT_WAKE_UP: self.wake_up_menu.clock.increment_minutes,
            HOURS_DECREMENT_WAKE_UP: self.wake_up_menu.clock.decrement_hours,
            MINUTES_DECREMENT_WAKE_UP: self.wake_up_menu.clock.decrement_minutes
        }

        self.current_button = None
        self.link_borders()
        self.clean_draw_update()

    def link_borders(self):
        """ Link components borders for the arrow keys navigation """

        margin = 10
        self.enter_naviagtor_x = self.navigator.components[0].bounding_box.x + margin
        self.enter_naviagtor_y = self.navigator.components[0].bounding_box.y + margin
        self.exit_naviagtor_x = self.navigator.components[2].bounding_box.x + margin
        self.exit_naviagtor_y = self.navigator.components[2].bounding_box.y + margin
        self.enter_poweroff_x = self.sleep_menu.poweroff_button.bounding_box.x + margin
        self.enter_poweroff_y = self.sleep_menu.poweroff_button.bounding_box.y + margin
        self.enter_sleep_x = self.sleep_menu.sleep_button.bounding_box.x + margin
        self.enter_sleep_y = self.sleep_menu.sleep_button.bounding_box.y + margin
        self.enter_wake_up_x = self.wake_up_menu.button.bounding_box.x + margin
        self.enter_wake_up_y = self.wake_up_menu.button.bounding_box.y + margin

        self.exit_sleep_x = self.sleep_menu.bounding_box.x + self.sleep_menu.bounding_box.w + margin
        self.exit_sleep_incr_y = self.sleep_menu.bounding_box.y + margin
        self.exit_sleep_decr_y = self.sleep_menu.bounding_box.y + self.sleep_menu.bounding_box.h - margin

        self.exit_wake_up_x = self.wake_up_menu.bounding_box.x + self.wake_up_menu.bounding_box.w + margin
        self.exit_wake_up_y = self.wake_up_menu.bounding_box.y + margin

        self.exit_sleep_top_hour_x = self.exit_wake_up_bottom_hour_x = self.sleep_menu.clock.h1.bounding_box.x + self.sleep_menu.clock.h1.bounding_box.w
        self.exit_sleep_top_min_x = self.exit_wake_up_bottom_min_x = self.sleep_menu.clock.m1.bounding_box.x + self.sleep_menu.clock.m1.bounding_box.w
        self.exit_wake_up_bottom_y = self.wake_up_menu.bounding_box.y + self.wake_up_menu.bounding_box.h + margin

        self.sleep_menu.sleep_button.exit_top_y = self.screen_layout.BOTTOM.y + margin
        self.sleep_menu.sleep_button.exit_bottom_y = self.sleep_menu.poweroff_button.bounding_box.y + margin
        self.sleep_menu.sleep_button.exit_left_x = self.sleep_menu.clock.m2.top.x + self.sleep_menu.clock.m2.top.w - margin
        self.sleep_menu.sleep_button.exit_right_x = self.sleep_menu.clock.h1.top.x + margin
        self.sleep_menu.sleep_button.exit_right_y = self.sleep_menu.clock.h1.bottom.y + margin

        self.sleep_menu.poweroff_button.exit_top_y = self.sleep_menu.sleep_button.bounding_box.y + self.sleep_menu.sleep_button.bounding_box.h - margin
        self.sleep_menu.poweroff_button.exit_bottom_y = self.wake_up_menu.button.bounding_box.y + margin
        self.sleep_menu.poweroff_button.exit_left_x = self.sleep_menu.clock.m2.bottom.x + self.sleep_menu.clock.m2.bottom.w - margin
        self.sleep_menu.poweroff_button.exit_right_x = self.sleep_menu.clock.h1.bottom.x + margin
        self.sleep_menu.poweroff_button.exit_right_y = self.wake_up_menu.clock.h1.top.y + margin

        self.wake_up_menu.button.exit_top_y = self.sleep_menu.poweroff_button.bounding_box.y + self.sleep_menu.poweroff_button.bounding_box.h - margin
        self.wake_up_menu.button.exit_bottom_y = self.screen_layout.BOTTOM.y + margin
        self.wake_up_menu.button.exit_left_x = self.wake_up_menu.clock.m2.top.x + margin
        self.wake_up_menu.button.exit_left_y = self.wake_up_menu.clock.m2.top.y + margin
        self.wake_up_menu.button.exit_right_x = self.wake_up_menu.clock.h1.bottom.x + margin
        self.wake_up_menu.button.exit_right_y = self.wake_up_menu.clock.h1.bottom.y + margin

        for index, comp in enumerate(self.navigator.components):
            comp.exit_top_y = self.wake_up_menu.clock.h1.bounding_box.y + self.wake_up_menu.clock.h1.bounding_box.h - margin
            comp.exit_bottom_y = self.sleep_menu.clock.h1.bounding_box.y + margin
            if index == 0:
                comp.exit_left_x = self.wake_up_menu.clock.m2.bottom.x + margin
                comp.exit_left_y = self.wake_up_menu.clock.m2.bottom.y + margin
                comp.exit_right_x = self.sleep_now_button.bounding_box.x + margin
            elif index == 1:
                comp.exit_left_x = self.home_button.bounding_box.x + margin
                comp.exit_right_x = self.player_button.bounding_box.x + margin
            elif index == 2:
                comp.exit_left_x = self.sleep_now_button.bounding_box.x + margin
                comp.exit_right_x = self.sleep_menu.clock.h1.top.x + margin
                comp.exit_right_y = self.sleep_menu.clock.h1.top.y + margin

    def set_parent_screen(self, scr):
        """ Add parent screen

        :param scr: parent screen
        """
        self.sleep_menu.set_parent_screen(scr)
        self.wake_up_menu.set_parent_screen(scr)
        self.navigator.set_parent_screen(scr)

    def sleep_change_callback(self):
        """ Callback for sleep menu  """

        if self.active_key_menu != self.sleep_menu:
            self.wake_up_menu.clock.reset_key()
            self.active_key_menu = self.sleep_menu
        self.unselect_sleep_buttons()

    def wake_up_change_callback(self):
        """ Callback for wake up menu  """

        if self.active_key_menu != self.wake_up_menu:
            self.sleep_menu.clock.reset_key()
            self.active_key_menu = self.wake_up_menu
        self.unselect_wake_up()

    def handle_event(self, event):
        """ Handle screen event

        :param event: the event to handle
        """
        if not self.visible or event.type == pygame.MOUSEMOTION:
            return

        mouse_events = [pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN]

        if event.type in mouse_events:
            self.handle_mouse_event(event)
            return

        if event.type == SELECT_EVENT_TYPE:
            self.handle_select_action(event)
            return

        if not (event.type == USER_EVENT_TYPE and event.sub_type == SUB_TYPE_KEYBOARD and event.action == pygame.KEYUP):
            Container.handle_event(self, event)
            return

        keys = [kbd_keys[KEY_SELECT], kbd_keys[KEY_LEFT], kbd_keys[KEY_RIGHT], kbd_keys[KEY_UP], kbd_keys[KEY_DOWN]]
        if event.keyboard_key in keys and self.menu_index == -1:
            if self.current_button == self.sleep_menu.sleep_button:
                self.sleep_menu.sleep_button.handle_event(event)
                if self.config[TIMER][SLEEP]:
                    self.sleep_menu.sleep_button.set_selected(True)
                    self.sleep_menu.sleep_button.clean_draw_update()
                else:
                    if event.keyboard_key == kbd_keys[KEY_SELECT]:
                        self.select_home()
            elif self.current_button == self.sleep_menu.poweroff_button:
                self.sleep_menu.poweroff_button.handle_event(event)
                if self.config[TIMER][POWEROFF]:
                    self.sleep_menu.poweroff_button.set_selected(True)
                    self.sleep_menu.poweroff_button.clean_draw_update()
                else:
                    if event.keyboard_key == kbd_keys[KEY_SELECT]:
                        self.select_home()
            elif self.current_button == self.wake_up_menu.button:
                self.wake_up_menu.button.handle_event(event)
                if self.config[TIMER][WAKE_UP]:
                    self.wake_up_menu.button.set_selected(True)
                    self.wake_up_menu.button.clean_draw_update()
                else:
                    if event.keyboard_key == kbd_keys[KEY_SELECT]:
                        self.select_home()
            else:
                self.navigator.handle_event(event)
            return

        if event.keyboard_key == kbd_keys[KEY_SELECT]:
            self.menu_functions[self.menu_index]()
        elif event.keyboard_key == kbd_keys[KEY_RIGHT]:
            if self.menu_index == MINUTES_INCREMENT_WAKE_UP:
                self.wake_up_menu.clock.reset_key()
                self.menu_index = -1
                self.util.post_exit_event(self.enter_wake_up_x, self.enter_wake_up_y, self.wake_up_menu)
            elif self.menu_index == MINUTES_DECREMENT_WAKE_UP:
                self.wake_up_menu.clock.reset_key()
                self.menu_index = -1
                self.util.post_exit_event(self.enter_naviagtor_x, self.enter_naviagtor_y, self.wake_up_menu)
            elif self.menu_index == MINUTES_INCREMENT_SLEEP:
                self.sleep_menu.clock.reset_key()
                self.menu_index = -1
                self.util.post_exit_event(self.exit_sleep_x, self.exit_sleep_incr_y, self.sleep_menu)
            elif self.menu_index == MINUTES_DECREMENT_SLEEP:
                self.sleep_menu.clock.reset_key()
                self.menu_index = -1
                self.util.post_exit_event(self.exit_sleep_x, self.exit_sleep_decr_y, self.sleep_menu)
            else:
                self.menu_index += 1
                self.wake_up_menu.clock.set_key_position(self.menu_index)
                self.sleep_menu.clock.set_key_position(self.menu_index)
        elif event.keyboard_key == kbd_keys[KEY_LEFT]:
            if self.menu_index == HOURS_INCREMENT_WAKE_UP:
                self.wake_up_menu.clock.reset_key()
                self.menu_index = -1
                self.util.post_exit_event(self.enter_poweroff_x, self.enter_poweroff_y, self.wake_up_menu)
            elif self.menu_index == HOURS_DECREMENT_WAKE_UP:
                self.wake_up_menu.clock.reset_key()
                self.menu_index = -1
                self.util.post_exit_event(self.exit_wake_up_x, self.exit_wake_up_y, self.wake_up_menu)
            elif self.menu_index == HOURS_INCREMENT_SLEEP:
                self.sleep_menu.clock.reset_key()
                self.menu_index = -1
                self.util.post_exit_event(self.exit_naviagtor_x, self.exit_naviagtor_y, self.sleep_menu)
            elif self.menu_index == HOURS_DECREMENT_SLEEP:
                self.sleep_menu.clock.reset_key()
                self.menu_index = -1
                self.util.post_exit_event(self.enter_sleep_x, self.enter_sleep_y, self.sleep_menu)
            else:
                self.menu_index -= 1
                self.wake_up_menu.clock.set_key_position(self.menu_index)
                self.sleep_menu.clock.set_key_position(self.menu_index)
        elif event.keyboard_key == kbd_keys[KEY_UP]:
            if self.menu_index == HOURS_INCREMENT_SLEEP:
                self.sleep_menu.clock.reset_key()
                self.menu_index = -1
                self.util.post_exit_event(self.exit_sleep_top_hour_x, self.exit_wake_up_bottom_y, self.sleep_menu)
            elif self.menu_index == MINUTES_INCREMENT_SLEEP:
                self.sleep_menu.clock.reset_key()
                self.menu_index = -1
                self.util.post_exit_event(self.exit_sleep_top_min_x, self.exit_wake_up_bottom_y, self.sleep_menu)
            elif self.menu_index == HOURS_DECREMENT_SLEEP:
                self.handle_up_down(HOURS_INCREMENT_SLEEP, self.sleep_menu)
            elif self.menu_index == MINUTES_DECREMENT_SLEEP:
                self.handle_up_down(MINUTES_INCREMENT_SLEEP, self.sleep_menu)
            elif self.menu_index == HOURS_INCREMENT_WAKE_UP:
                self.handle_up_down(HOURS_DECREMENT_SLEEP, self.sleep_menu, self.wake_up_menu, self.sleep_menu)
            elif self.menu_index == MINUTES_INCREMENT_WAKE_UP:
                self.handle_up_down(MINUTES_DECREMENT_SLEEP, self.sleep_menu, self.wake_up_menu, self.sleep_menu)
            elif self.menu_index == HOURS_DECREMENT_WAKE_UP:
                self.handle_up_down(HOURS_INCREMENT_WAKE_UP, self.wake_up_menu)
            elif self.menu_index == MINUTES_DECREMENT_WAKE_UP:
                self.handle_up_down(MINUTES_INCREMENT_WAKE_UP, self.wake_up_menu)
        elif event.keyboard_key == kbd_keys[KEY_DOWN]:
            if self.menu_index == HOURS_INCREMENT_SLEEP:
                self.handle_up_down(HOURS_DECREMENT_SLEEP, self.sleep_menu)
            elif self.menu_index == MINUTES_INCREMENT_SLEEP:
                self.handle_up_down(MINUTES_DECREMENT_SLEEP, self.sleep_menu)
            elif self.menu_index == HOURS_DECREMENT_SLEEP:
                self.handle_up_down(HOURS_INCREMENT_WAKE_UP, self.wake_up_menu, self.sleep_menu, self.wake_up_menu)
            elif self.menu_index == MINUTES_DECREMENT_SLEEP:
                self.handle_up_down(MINUTES_INCREMENT_WAKE_UP, self.wake_up_menu, self.sleep_menu, self.wake_up_menu)
            elif self.menu_index == HOURS_INCREMENT_WAKE_UP:
                self.handle_up_down(HOURS_DECREMENT_WAKE_UP, self.wake_up_menu)
            elif self.menu_index == MINUTES_INCREMENT_WAKE_UP:
                self.handle_up_down(MINUTES_DECREMENT_WAKE_UP, self.wake_up_menu)
            elif self.menu_index == HOURS_DECREMENT_WAKE_UP:
                self.wake_up_menu.clock.reset_key()
                self.menu_index = -1
                self.util.post_exit_event(self.exit_wake_up_bottom_hour_x, self.exit_wake_up_bottom_y, self.wake_up_menu)
            elif self.menu_index == MINUTES_DECREMENT_WAKE_UP:
                self.wake_up_menu.clock.reset_key()
                self.menu_index = -1
                self.util.post_exit_event(self.exit_wake_up_bottom_min_x, self.exit_wake_up_bottom_y, self.wake_up_menu)
        else:
            Container.handle_event(self, event)

        if event.keyboard_key in keys and self.update_web_observer != None:
            self.update_web_observer()

    def select_home(self):
        """ Select home button """

        self.current_button = None
        self.home_button.set_selected(True)
        self.home_button.clean_draw_update()

    def handle_select_action(self, event):
        """ Handle select action

        :param event: the event
        """
        pos = (event.x - 3, event.y)
        if self.sleep_menu.clock.h1.top.collidepoint(pos) or self.sleep_menu.clock.h2.top.collidepoint(pos):
            self.handle_up_down(HOURS_INCREMENT_SLEEP, self.sleep_menu)
        elif self.sleep_menu.clock.m1.top.collidepoint(pos) or self.sleep_menu.clock.m2.top.collidepoint(pos):
            self.handle_up_down(MINUTES_INCREMENT_SLEEP, self.sleep_menu)
        elif self.sleep_menu.clock.h1.bottom.collidepoint(pos) or self.sleep_menu.clock.h2.bottom.collidepoint(pos):
            self.handle_up_down(HOURS_DECREMENT_SLEEP, self.sleep_menu)
        elif self.sleep_menu.clock.m1.bottom.collidepoint(pos) or self.sleep_menu.clock.m2.bottom.collidepoint(pos):
            self.handle_up_down(MINUTES_DECREMENT_SLEEP, self.sleep_menu)
        elif self.wake_up_menu.clock.h1.top.collidepoint(pos) or self.wake_up_menu.clock.h2.top.collidepoint(pos):
            self.handle_up_down(HOURS_INCREMENT_WAKE_UP, self.wake_up_menu)
        elif self.wake_up_menu.clock.m1.top.collidepoint(pos) or self.wake_up_menu.clock.m2.top.collidepoint(pos):
            self.handle_up_down(MINUTES_INCREMENT_WAKE_UP, self.wake_up_menu)
        elif self.wake_up_menu.clock.h1.bottom.collidepoint(pos) or self.wake_up_menu.clock.h2.bottom.collidepoint(pos):
            self.handle_up_down(HOURS_DECREMENT_WAKE_UP, self.wake_up_menu)
        elif self.wake_up_menu.clock.m1.bottom.collidepoint(pos) or self.wake_up_menu.clock.m2.bottom.collidepoint(pos):
            self.handle_up_down(MINUTES_DECREMENT_WAKE_UP, self.wake_up_menu)
        elif self.screen_layout.BOTTOM.collidepoint(pos):
            self.navigator.handle_event(event)
            for c in self.navigator.components:
                if c.selected:
                    self.current_button = c
        elif self.sleep_menu.sleep_button.bounding_box.collidepoint(pos):
            self.sleep_menu.sleep_button.handle_event(event)
            self.current_button = self.sleep_menu.sleep_button
        elif self.sleep_menu.poweroff_button.bounding_box.collidepoint(pos):
            self.sleep_menu.poweroff_button.handle_event(event)
            self.current_button = self.sleep_menu.poweroff_button
        elif self.wake_up_menu.button.bounding_box.collidepoint(pos):
            self.wake_up_menu.button.handle_event(event)
            self.current_button = self.wake_up_menu.button
            
        self.update_web_observer()

    def handle_mouse_event(self, event):
        """ Handle mouse event

        :param event: the event
        """
        event_component = None

        for comp in self.sleep_menu.components:
            bb = comp.bounding_box
            if bb.collidepoint(event.pos):
                event_component = comp
                if comp == self.sleep_menu.sleep_button or comp == self.sleep_menu.poweroff_button:
                    if comp == self.sleep_menu.sleep_button:
                        self.current_button = self.sleep_menu.sleep_button
                    elif comp == self.sleep_menu.poweroff_button:
                        self.current_button = self.sleep_menu.poweroff_button
                    self.sleep_menu.clock.reset_key()
                    self.wake_up_menu.clock.reset_key()
                break

        for comp in self.wake_up_menu.components:
            bb = comp.bounding_box
            if bb.collidepoint(event.pos):
                event_component = comp
                if comp == self.wake_up_menu.button:
                    self.current_button = self.wake_up_menu.button
                    self.sleep_menu.clock.reset_key()
                    self.wake_up_menu.clock.reset_key()
                    self.menu_index = -1
                break

        if event_component:
            self.navigator.unselect()
            event_component.handle_event(event)
            return

        for comp in self.navigator.components:
            if getattr(comp, "state", None):
                bb = comp.state.bounding_box
            else:
                bb = comp.bounding_box

            if bb == None:
                continue

            if bb.collidepoint(event.pos):
                event_component = comp
                break

        if event_component:
            self.sleep_menu.clock.reset_key()
            self.wake_up_menu.clock.reset_key()
            self.menu_index = -1
            self.navigator.unselect()
            event_component.handle_event(event)

    def handle_up_down(self, position, set_menu, reset_menu=None, active_menu=None):
        """ Handle up and down keys

        :param position: key position
        :param set_menu: menu to set key position
        :param reset_menu: menu to reset
        :param active_menu:  active menu
        """
        if reset_menu != None:
            reset_menu.clock.reset_key()

        if active_menu != None:
            self.active_key_menu = active_menu

        set_menu.clock.set_key_position(position)
        self.menu_index = position

    def handle_clock_change(self, change_code):
        """ Clock change handler

        :param change_code: change code
        """
        if change_code == HOURS_INCREMENT_SLEEP:
            self.menu_index = HOURS_INCREMENT_SLEEP
        elif change_code == MINUTES_INCREMENT_SLEEP:
            self.menu_index = MINUTES_INCREMENT_SLEEP
        elif change_code == HOURS_DECREMENT_SLEEP:
            self.menu_index = HOURS_DECREMENT_SLEEP
        elif change_code == MINUTES_DECREMENT_SLEEP:
            self.menu_index = MINUTES_DECREMENT_SLEEP
        elif change_code == HOURS_INCREMENT_WAKE_UP:
            self.menu_index = HOURS_INCREMENT_WAKE_UP
        elif change_code == MINUTES_INCREMENT_WAKE_UP:
            self.menu_index = MINUTES_INCREMENT_WAKE_UP
        elif change_code == HOURS_DECREMENT_WAKE_UP:
            self.menu_index = HOURS_DECREMENT_WAKE_UP
        elif change_code == MINUTES_DECREMENT_WAKE_UP:
            self.menu_index = MINUTES_DECREMENT_WAKE_UP

    def handle_button(self, state):
        """ Button event handler

        :param state: button state
        """
        button = state.event_origin
        name = button.state.name

        if name == SLEEP:
            self.handle_sleep_button(button)
        elif name == POWEROFF:
            self.handle_poweroff_button(button)
        elif name == WAKE_UP:
            self.handle_wake_up_button(button)

    def handle_sleep_button(self, button):
        """ Sleep button handler

        :button: sleep button
        """
        if self.sleep_menu.sleep_selected:
            button.set_selected(False)
            with self.timer_lock:
                self.config[TIMER][SLEEP] = False
            self.sleep_menu.sleep_selected = False
            if self.wake_up_menu.button_selected:
                self.unselect_wake_up()
        else:
            button.set_selected(True)
            with self.timer_lock:
                self.config[TIMER][SLEEP] = True
                self.config[TIMER][POWEROFF] = False
            self.sleep_menu.sleep_selected = True
            self.sleep_menu.poweroff_selected = False
            self.sleep_menu.poweroff_button.set_selected(False)
            self.sleep_menu.poweroff_button.clean_draw_update()
            self.start_timer_thread()
        button.clean_draw_update()

    def handle_poweroff_button(self, button):
        """ Poweroff button handler

        :button: poweroff button
        """
        if self.sleep_menu.poweroff_selected:
            button.set_selected(False)
            with self.timer_lock:
                self.config[TIMER][POWEROFF] = False
            self.sleep_menu.poweroff_selected = False
        else:
            button.set_selected(True)
            with self.timer_lock:
                self.config[TIMER][POWEROFF] = True
                self.config[TIMER][SLEEP] = False
            self.sleep_menu.poweroff_selected = True
            self.sleep_menu.sleep_selected = False
            self.sleep_menu.sleep_button.set_selected(False)
            self.sleep_menu.sleep_button.clean_draw_update()
            if self.wake_up_menu.button_selected:
                self.unselect_wake_up()
            self.start_timer_thread()
        button.clean_draw_update()

    def handle_wake_up_button(self, button):
        """ Wake up button handler

        :button: wake up button
        """
        if self.wake_up_menu.button_selected:
            self.unselect_wake_up()
        else:
            button.set_selected(True)
            with self.timer_lock:
                self.config[TIMER][WAKE_UP] = True
            self.wake_up_menu.button_selected = True
            self.wake_up_menu.button.clean_draw_update()

    def unselect_sleep_buttons(self):
        """ Unselect sleep and poweroff buttons """

        with self.timer_lock:
            self.config[TIMER][SLEEP] = False
            self.config[TIMER][POWEROFF] = False
            self.sleep_menu.sleep_button.set_selected(False)
            self.sleep_menu.poweroff_button.set_selected(False)
            self.sleep_menu.sleep_selected = False
            self.sleep_menu.poweroff_selected = False
            self.sleep_menu.sleep_button.clean_draw_update()
            self.sleep_menu.poweroff_button.clean_draw_update()

    def unselect_wake_up(self):
        """ Unselect wake up button """

        self.wake_up_menu.button.set_selected(False)
        with self.timer_lock:
            self.config[TIMER][WAKE_UP] = False
        self.wake_up_menu.button_selected = False
        self.wake_up_menu.button.clean_draw_update()

    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers

        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        Screen.add_screen_observers(self, update_observer, redraw_observer)
        self.sleep_menu.add_menu_observers(update_observer, redraw_observer)
        self.wake_up_menu.add_menu_observers(update_observer, redraw_observer)
        self.navigator.add_observers(update_observer, redraw_observer)
