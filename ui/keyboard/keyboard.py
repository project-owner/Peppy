# Copyright 2019-2021 Peppy Player peppy.player@gmail.com
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
from ui.state import State
from ui.button.button import Button
from util.config import COLORS, COLOR_DARK, BACKGROUND, MENU_BGR_COLOR
from util.keys import USER_EVENT_TYPE, SUB_TYPE_KEYBOARD, kbd_keys, \
    KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN, KEY_SELECT

KEYBOARD_1 = ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p",
              "", "a", "s", "d", "f", "g", "h", "j", "k", "l", "",
              "Caps", "z", "x", "c", "v", "b", "n", "m", "Del",
              "123", "Space", "Enter"
              ]
KEYBOARD_2 = ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P",
              "", "A", "S", "D", "F", "G", "H", "J", "K", "L", "",
              "Caps", "Z", "X", "C", "V", "B", "N", "M", "Del",
              "123", "Space", "Enter"
              ]
KEYBOARD_3 = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0",
              "", "-", "/", ":", ";", "(", ")", "€", "£", "¥", "",
              "#+=", ".", ",", "?", "!", "'", "\"", "Del",
              "ABC", "Space", "Enter"
              ]
KEYBOARD_4 = ["[", "]", "{", "}", "#", "%", "^", "*", "+", "=",
              "", "_", "\\", "|", "~", "<", ">", "$", "&", "@", "",
              "123", ".", ",", "?", "!", "'", "Del",
              "ABC", "Space", "Enter"
              ]

LAYOUT_1 = [
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [3, 2, 2, 2, 2, 2, 2, 2, 3],
    [5, 10, 5]
]
LAYOUT_2 = [
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [4, 2, 2, 2, 2, 2, 2, 4],
    [5, 10, 5]
]
LAYOUT_3 = [
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [5, 2, 2, 2, 2, 2, 5],
    [5, 10, 5]
]

# (left, right, up, down)
TRANSITION_MAP_1 = [(-3, 1, -1, 11), (0, 2, -1, 12), (1, 3, -1, 13), (2, 4, -1, 14), (3, 5, -1, 15), (4, 6, -1, 16), (5, 7, -1, 17), (6, 8, -1, 18), (7, 9, -1, 19), (8, 11, -1, 19),
                    (), (9, 12, 0, 21), (11, 13, 1, 22), (12, 14, 2, 23), (13, 15, 3, 24), (14, 16, 4, 25), (15, 17, 5, 26), (16, 18, 6, 27), (17, 19, 7, 28), (18, 21, 8, 29), (),
                    (19, 22, 11, 30), (21, 23, 12, 30), (22, 24, 13, 31), (23, 25, 14, 31), (24, 26, 15, 31), (25, 27, 16, 31), (26, 28, 17, 31), (27, 29, 18, 32), (28, 30, 19, 32),
                    (29, 31, 21, -2), (30, 32, 25, -2), (31, -4, 29, -5)
                    ]
TRANSITION_MAP_2 = [(-3, 1, -1, 11), (0, 2, -1, 12), (1, 3, -1, 13), (2, 4, -1, 14), (3, 5, -1, 15), (4, 6, -1, 16), (5, 7, -1, 17), (6, 8, -1, 18), (7, 9, -1, 19), (8, 11, -1, 19),
                    (), (9, 12, 0, 21), (11, 13, 1, 22), (12, 14, 2, 23), (13, 15, 3, 24), (14, 16, 4, 25), (15, 17, 5, 26), (16, 18, 6, 27), (17, 19, 7, 28), (18, 21, 8, 28), (),
                    (19, 22, 11, 29), (21, 23, 12, 30), (22, 24, 13, 30), (23, 25, 14, 30), (24, 26, 15, 30), (25, 27, 16, 30), (26, 28, 17, 31), (27, 29, 19, 31),
                    (28, 30, 21, -2), (29, 31, 25, -2), (30, -4, 28, -5)
                    ]
TRANSITION_MAP_3 = [(-3, 1, -1, 11), (0, 2, -1, 12), (1, 3, -1, 13), (2, 4, -1, 14), (3, 5, -1, 15), (4, 6, -1, 16), (5, 7, -1, 17), (6, 8, -1, 18), (7, 9, -1, 19), (8, 11, -1, 19),
                    (), (9, 12, 0, 21), (11, 13, 1, 21), (12, 14, 2, 22), (13, 15, 3, 23), (14, 16, 4, 24), (15, 17, 5, 25), (16, 18, 6, 26), (17, 19, 7, 27), (18, 21, 8, 27), (),
                    (19, 22, 11, 28), (21, 23, 13, 29), (22, 24, 14, 29), (23, 25, 15, 29), (24, 26, 16, 29), (25, 27, 17, 29), (26, 28, 19, 30),
                    (27, 29, 21, -2), (28, 30, 24, -2), (29, -4, 27, -5)
                    ]
KEYBOARD_abc = "abc"
KEYBOARD_ABC = "ABC"
KEYBOARD_123 = "123"
KEYBOARD_symbol = "symbol"

class Keyboard(Container):
    """ Keyboard class. """

    def __init__(self, util, bb, callback, screen):
        """ Initializer

        :param util: utility object
        :param bb: bounding box
        :param callback: function to call on Enter
        :param screen: parent screen
        """
        Container.__init__(self, util, bb, (0, 0, 0))
        self.content = None
        self.screen = screen
        self.bb = bb
        self.util = util
        self.config = util.config
        self.callback = callback
        self.move_listeners = []
        self.text_listeners = []
        self.buttons = {}
        self.factory = Factory(util)
        self.caps = False
        self.text = ""

        self.controls = ["Caps", "Del", "abc", "ABC", "123", "#+=", "Enter"]
        self.keyboards = {}
        self.current_keyboard_type = None
        self.create_keyboard(KEYBOARD_abc, LAYOUT_1, TRANSITION_MAP_1)

    def get_layout(self, span):
        """ Create layout

        :param span:
        :return: layout
        """
        h = int(self.bb.h / 4)
        u = int((self.bb.w) / 20)
        g = self.bb.h - (h * 4)

        layout = []
        for k, n in enumerate(span):
            z = 0
            for i, m in enumerate(n):
                x = (z * u) + 1
                y = self.bb.y + (k * h) + 1
                w = (u * m) - 1
                d = h - 1
                if k == 3 and (g - 1) > 0:
                    d += (g - 1)
                if (k == 0 and i == 9) or (k == 1 and i == 10) or (k == 2 and i == 8) or (k == 3 and i == 2):
                    w -= 1
                layout.append(pygame.Rect(x, y, w, d))
                z += m

        return layout

    def create_keyboard(self, keyboard_type, span, transition_map):
        """ Create keyboard

        :param keyboard_type: type
        :param span: span
        :param transition_map: transition map
        """
        layout = self.get_layout(span)
        buttons = []
        keys = None
        self.current_keyboard_type = keyboard_type

        try:
            buttons = self.keyboards[keyboard_type]
            self.components = buttons
            return
        except:
            pass

        if keyboard_type == KEYBOARD_abc:
            keys = KEYBOARD_1
        elif keyboard_type == KEYBOARD_ABC:
            keys = KEYBOARD_2
        elif keyboard_type == KEYBOARD_123:
            keys = KEYBOARD_3
        elif keyboard_type == KEYBOARD_symbol:
            keys = KEYBOARD_4

        for i, k in enumerate(keys):
            if not k:
                c = Component(self.util, layout[i], bgr=self.config[BACKGROUND][MENU_BGR_COLOR])
                c.parent_screen = self.screen
                c.name = "gap" + str(i)
                buttons.append(c)
                continue
            s = State()
            s.index = i
            s.name = k
            s.l_name = k
            s.comparator_item = s.index
            s.bgr = self.config[COLORS][COLOR_DARK]
            s.show_bgr = True
            s.bounding_box = layout[i]
            s.key_map = transition_map[i]
            button = self.factory.create_menu_button(s, layout[i], self.press_key, False, 50, 100, False, True)
            buttons.append(button)
        buttons[0].set_selected(True)
        self.keyboards[keyboard_type] = buttons
        self.components = buttons

        if keyboard_type != KEYBOARD_abc:
            self.set_observers()

        self.buttons = {i : item for i, item in enumerate(buttons)}

    def press_key(self, state):
        """ Key press handler

        :param state: button state
        """
        if state.name not in self.controls and len(self.text) == 64:
            return

        self.unselect()
        state.event_origin.set_selected(True)

        if state.name == "Caps" or state.name == "ABC":
            if state.name == "Caps":
                self.caps = not self.caps
            if self.caps:
                self.create_keyboard(KEYBOARD_ABC, LAYOUT_1, TRANSITION_MAP_1)
            else:
                self.create_keyboard(KEYBOARD_abc, LAYOUT_1, TRANSITION_MAP_1)
        elif state.name == "123":
            self.create_keyboard(KEYBOARD_123, LAYOUT_2, TRANSITION_MAP_2)
        elif state.name == "#+=":
            self.create_keyboard(KEYBOARD_symbol, LAYOUT_3, TRANSITION_MAP_3)
        elif state.name == "Space":
            self.text += " "
            self.notify_text_listeners(self.text)
        elif state.name == "Del":
            if len(self.text) > 0:
                self.text = self.text[0: -1]
                self.notify_text_listeners(self.text)
        elif state.name == "Enter":
            if len(self.text) == 0:
                return
            s = State()
            s.source = "search"
            s.callback_var = self.text
            self.callback(s)
        else:
            self.text += state.name
            self.notify_text_listeners(self.text)

        self.clean_draw_update()

    def delete(self, state):
        """ Delete character

        :param state: button state
        """
        self.text = ""
        self.notify_text_listeners(self.text)

    def add_move_listener(self, listener):
        """ Add arrow button event listener

        :param listener: event listener
        """
        if listener not in self.move_listeners:
            self.move_listeners.append(listener)

    def notify_move_listeners(self):
        """ Notify arrow button event listeners """

        for listener in self.move_listeners:
            listener(None)

    def add_text_listener(self, listener):
        """ Add text event listener

        :param listener: event listener
        """
        if listener not in self.text_listeners:
            self.text_listeners.append(listener)

    def notify_text_listeners(self, text):
        """ Notify all text listeners

        :param state: button state
        """
        for listener in self.text_listeners:
            listener(text)

    def unselect(self):
        """ Unselect currently selected button """

        for c in self.components:
            if isinstance(c, Button) and c.selected:
                c.set_selected(False)
                return

    def is_selected(self):
        """ Check if keyboard has selected key

        :return: True - has selected key, False - doesn't have
        """
        selected = False
        for c in self.components:
            if isinstance(c, Button) and c.selected:
                selected = True
                break
        return selected

    def get_current_key(self):
        """ Get currently selected key

        :return: selected component
        """
        for c in self.components:
            if isinstance(c, Button) and c.selected:
                return c
        return self.components[0]

    def select_key_by_index(self, index):
        """ Slecte key by index

        :param index:
        :return:
        """
        for c in self.components:
            if isinstance(c, Button) and c.state.index == index:
                c.set_selected(True)
                return

    def handle_event(self, event):
        """ Menu event handler

        :param event: menu event
        """
        if not self.visible: return

        if event.type == USER_EVENT_TYPE and event.sub_type == SUB_TYPE_KEYBOARD and event.action == pygame.KEYUP:
            key_events = [kbd_keys[KEY_LEFT], kbd_keys[KEY_RIGHT], kbd_keys[KEY_UP], kbd_keys[KEY_DOWN], kbd_keys[KEY_SELECT]]

            if event.keyboard_key not in key_events or not self.is_selected():
                Container.handle_event(self, event)
                return

            current_key = self.get_current_key()

            if event.keyboard_key == kbd_keys[KEY_SELECT]:
                self.press_key(current_key.state)
                self.notify_move_listeners()
                return

            transition_map = current_key.state.key_map
            next_key_index = 0
            self.unselect()

            if event.keyboard_key == kbd_keys[KEY_LEFT]:
                index = transition_map[0]
                if index == -3:
                    b = self.get_button_by_index(9)
                    self.exit_keyboard(b)
                    return
                next_key_index = index
            elif event.keyboard_key == kbd_keys[KEY_RIGHT]:
                index = transition_map[1]
                if index == -4:
                    b = self.get_button_by_index(current_key.state.index - 2)
                    self.exit_keyboard(b)
                    return
                next_key_index = index
            elif event.keyboard_key == kbd_keys[KEY_UP]:
                index = transition_map[2]
                if index == -1:
                    self.exit_keyboard(current_key)
                    return    
                else:
                    next_key_index = index
            elif event.keyboard_key == kbd_keys[KEY_DOWN]:
                index = transition_map[3]
                if index == -2 or index == -5:
                    self.exit_keyboard(current_key)
                    return    
                else:
                    next_key_index = index

            self.select_key_by_index(next_key_index)
            self.clean_draw_update()
            self.notify_move_listeners()
        else:
            Container.handle_event(self, event)
            self.notify_move_listeners()

    def get_button_by_index(self, index):
        for b in self.components:
            if isinstance(b, Button):
                if b.state.index == index:
                    return b
        return None

    def exit_keyboard(self, key):
        """ Exit keyboard

        :param key: current key
        """
        x = int(key.bounding_box.x + (key.bounding_box.w / 2))
        y = self.bb.y + self.bb.h + 10
        self.util.post_exit_event(x, y, self)
        self.clean_draw_update()

    def set_observers(self):
        """ Set observers """

        for b in self.components:
            if not isinstance(b, Button):
                continue
            if self.update_observer and self.press:
                b.add_press_listener(self.update_observer)
            if self.update_observer and self.release:
                b.add_release_listener(self.update_observer)
            if self.redraw_observer:
                b.add_release_listener(self.redraw_observer)
        if self.redraw_observer:
            self.add_move_listener(self.redraw_observer)

    def add_menu_observers(self, update_observer, redraw_observer=None, press=True, release=True):
        """ Add menu observer

        :param update_observer: observer for updating menu
        :param redraw_observer: observer to redraw the whole screen
        :param press: True - add observer as press listener (default)
        :param release: True - add observer as release listener (default)
        """
        self.update_observer = update_observer
        self.redraw_observer = redraw_observer
        self.press = press
        self.release = release

        self.set_observers()
