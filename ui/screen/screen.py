# Copyright 2016-2024 Peppy Player peppy.player@gmail.com
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
import time

from pygame import Rect
from ui.component import Component
from ui.container import Container
from ui.factory import Factory
from ui.layout.borderlayout import BorderLayout
from util.keys import KEY_LOADING, LABELS
from util.config import COLORS, COLOR_CONTRAST, COLOR_BRIGHT, BACKGROUND, HEADER_BGR_COLOR, MENU_BGR_COLOR, GENERATED_IMAGE
from random import randrange
from threading import Thread

PERCENT_TOP_HEIGHT = 14.00
PERCENT_TITLE_FONT = 54.00

class Screen(Container):
    """ Base class for all screens with menu and navigator """
    
    def __init__(self, util, title_key, percent_bottom_height=0, screen_title_name="screen_title",
        create_dynamic_title=False, title_layout=None, title=None, bgr=None):
        """ Initializer
        
        :param util: utility object
        :param title_key: the resource bundle key for the screen title
        """
        self.util = util
        self.factory = Factory(util)
        self.config = util.config
        self.bounding_box = util.screen_rect

        if title_key:
            self.name = title_key
        else:
            self.name = "tmp"

        bg = self.util.get_background(self.name, bgr)
        self.bgr_type = bg[0]
        self.bgr = bg[1]
        self.bgr_key = bg[5]
        Container.__init__(self, util, bounding_box=self.bounding_box, background=bg[1], content=bg[2], image_filename=bg[3])
        self.original_image_filename = None
        try:
            self.original_image_filename = bg[4].replace("\\", "/")
        except:
            pass

        self.layout = BorderLayout(util.screen_rect)
        self.layout.set_percent_constraints(PERCENT_TOP_HEIGHT, percent_bottom_height, 0, 0)
        self.font_size = int((self.layout.TOP.h * PERCENT_TITLE_FONT)/100.0)
        self.header_bgr_color = self.config[BACKGROUND][HEADER_BGR_COLOR]
        self.contrast_color = self.config[COLORS][COLOR_CONTRAST]
        
        t_layout = self.layout.TOP
        if title_layout:
            t_layout = title_layout
        
        if create_dynamic_title:
            self.screen_title = self.factory.create_dynamic_text(screen_title_name, t_layout, self.header_bgr_color, self.contrast_color, self.font_size)
        else:
            self.screen_title = self.factory.create_output_text(screen_title_name, t_layout, self.header_bgr_color, self.contrast_color, self.font_size)
        
        if title:
            self.screen_title.set_text(title)
        else:    
            if title_key and len(title_key) > 0:
                try:
                    label = self.config[LABELS][title_key]
                    self.screen_title.set_text(label)
                except:
                    pass 
        self.add_component(self.screen_title)
        self.player_screen = False
        self.update_web_observer = None
        self.update_web_title = None

        self.loading_listeners = []
        self.LOADING = util.config[LABELS][KEY_LOADING]
        self.animated_title = False
        self.other_components = []
        self.update_component = True

        self.spectrum_frames = 6
        self.spectrum_running = False
        self.loading_spectrum = None
    
    def add_component(self, c):
        """ Add screen component

        :param c: component to add
        """
        if c and hasattr(c, "set_parent_screen"):
            c.set_parent_screen(self)
        Container.add_component(self, c)
    
    def add_menu(self, menu):
        """ Add menu to the screen
        
        :param menu: the menu to add
        """
        self.menu = menu
        self.add_component(menu)

    def add_navigator(self, navigator):
        """ Add navigator to the screen
        
        :param menu: the menu to add
        """
        self.navigator = navigator
        self.add_component(navigator)

    def enable_player_screen(self, flag):
        """ Enable player screen
        
        :param flag: enable/disable flag
        """
        pass
    
    def exit_screen(self):
        """ Complete actions required to save screen state """
        
        self.set_visible(False)

    def add_screen_observers(self, update_observer, redraw_observer, title_to_json=None):
        """ Add screen observers.
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        self.update_web_observer = redraw_observer
        self.update_web_title = title_to_json

    def set_loading(self, name=None, menu_bb=None, text=None):
        """ Show Loading... sign

        :param name: screen title
        :param menu_bb: menu bounding box
        :param text: screen text
        """
        pygame.event.set_blocked(None)
        bgr = self.config[BACKGROUND][MENU_BGR_COLOR]
        fgr = self.config[COLORS][COLOR_BRIGHT]
        font_size = int(self.bounding_box.h * 0.07)

        spectrum_size = 4
        spectrum_bar_width = int(font_size / 4)
        spectrum_bar_height = font_size
        spectrum_gap = 1
        spectrum_width = spectrum_bar_width * spectrum_size + spectrum_gap * (spectrum_size - 1)
        text_spectrum_gap = int(font_size / 3)

        bb = self.bounding_box
        bb = Rect(bb.x, bb.y + 1, bb.w, bb.h - 1)

        t = self.factory.create_output_text(KEY_LOADING, bb, bgr, fgr, font_size)
        if not text:
            t.set_text_no_draw(self.LOADING)
        else:
            t.set_text_no_draw(text)

        t.components[1].content_x -= int((spectrum_width + text_spectrum_gap) / 2)

        if name != None:
            self.screen_title.set_text(name)

        self.add_component(t)

        x = t.components[1].content.get_size()[0] + t.components[1].content_x + text_spectrum_gap

        if self.bounding_box.h <= 320:
            shift = 3
        elif self.bounding_box.h > 320 and self.bounding_box.h <= 480:
            shift = 5
        elif self.bounding_box.h > 480:
            shift = 9

        y = (self.bounding_box.h / 2) - shift
        spectrum = self.get_loading_spectrum(x, y, spectrum_size, spectrum_bar_width, spectrum_bar_height, spectrum_gap, spectrum_width)
        self.add_component(spectrum)

        self.spectrum_running = True
        thread = Thread(target = self.spectrum_thread)
        thread.start()

        if getattr(self, "menu", None) != None:
            self.menu.buttons = {}
            self.menu.components = []
        self.clean_draw_update()
        self.notify_loading_listeners()
        self.update_component = True

    def spectrum_thread(self):
        """ Spectrum animation thread"""

        while self.spectrum_running:
            if len(self.components) > 3:
                spectrum = self.components[len(self.components) - 1]
                f = randrange(0, self.spectrum_frames)
                for r in range(self.spectrum_frames):
                    if r == f and len(self.components) > 3:
                        spectrum.components[r].visible = True
                    elif len(self.components) > 3:
                        spectrum.components[r].visible = False
                self.clean_draw_update()
                if self.update_web_observer:
                    self.update_web_observer()
                time.sleep(0.1)

    def get_loading_spectrum(self, x, y, size, bar_width, bar_height, gap, spectrum_width):
        """ Create spectrum component

        :param x: x coordinate
        :param y: y coordinate
        :param size: number of bars in spectrum
        :param bar_width: bar width
        :param bar_height: bar height
        :param gap: gap between bars
        :param spectrum_width: total spectrum width

        :return: spectrum container
        """
        if self.loading_spectrum != None:
            return self.loading_spectrum

        bb = pygame.Rect(x, y, spectrum_width, bar_height)
        self.loading_spectrum = Container(self.util, bb)
        self.loading_spectrum.name = "loading_spectrum"

        for n in range(self.spectrum_frames):
            s = pygame.Surface((spectrum_width, bar_height), pygame.SRCALPHA, 32)
            c = Component(self.util)
            c.name = "layer" + str(n)
            c.filename = GENERATED_IMAGE + str(n)
            for i in range(size):
                h = randrange(1, bar_height)
                b = pygame.Surface((bar_width, h), pygame.SRCALPHA, 32)
                b.fill(self.config[COLORS][COLOR_BRIGHT])
                s.blit(b.convert_alpha(), (i * (bar_width + gap), bar_height - h))
            c.content = (c.filename, s.convert_alpha())
            c.content_x = x
            c.content_y = y - bar_height / 2 - 1
            c.bounding_box = pygame.Rect(0, 0, spectrum_width, bar_height)
            if n == 0:
                c.visible = True
            else:
                c.visible = False

            self.loading_spectrum.add_component(c)
        return self.loading_spectrum

    def reset_loading(self):
        """ Remove Loading label """

        pygame.event.clear()
        pygame.event.set_allowed(None)
        self.spectrum_running = False
        time.sleep(0.12)
        del self.components[-1] # spectrum
        del self.components[-1] # text
        self.clean()
        self.draw()

        self.notify_loading_listeners()
        self.update_component = True

    def add_loading_listener(self, listener):
        """ Add loading listener

        :param listener: event listener
        """
        if listener not in self.loading_listeners:
            self.loading_listeners.append(listener)

    def notify_loading_listeners(self):
        """ Notify all loading listeners """

        for listener in self.loading_listeners:
            listener(None)

    def handle_event(self, event):
        """ Event handler

        :param event: event to handle
        """
        if not self.visible: return

        mouse_events = [pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN]
        
        if event.type in mouse_events and getattr(self, "menu", None) and getattr(self, "navigator", None):
            event_component = None

            for comp in self.menu.components:
                if getattr(comp, "state", None):
                    bb = comp.state.bounding_box
                else:
                    bb = comp.bounding_box

                if bb == None:
                    continue

                if bb.collidepoint(event.pos):
                    event_component = comp
                    for c in self.menu.components:
                        if hasattr(c, "set_selected") and c != comp:
                            c.set_selected(False)
                    self.update_component = True

            if event_component:
                self.navigator.unselect()
                event_component.handle_event(event)
                if hasattr(self.menu, "current_slider"):
                    self.menu.current_slider = event_component.id
                if self.update_web_observer:
                    self.update_web_observer()
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
                for c in self.menu.components:
                    if getattr(c, "selected", False):
                        c.set_selected(False)
                        c.clean_draw_update()
                    elif hasattr(c, "slider"):
                        c.slider.set_knob_off()

                self.navigator.unselect()
                for comp in self.navigator.components:
                    comp.handle_event(event)

                if self.update_web_observer:
                    self.update_web_observer()

                self.update_component = True

            for comp in self.other_components:
                if comp.bounding_box.collidepoint(event.pos):
                    comp.handle_event(event)
                    self.update_component = True
                    break
        else:
            Container.handle_event(self, event)
            if self.update_web_observer:
                self.update_web_observer()

    def get_menu_bottom_exit_xy(self, x):
        """ Get bottom exit coordinates

        :param x: event x coordinate
        """
        button = None
        xy = None
        for b in self.menu.components:
            if not isinstance(b, Container):
                continue

            if getattr(b, "bounding_box", None) == None:
                continue
            y = b.bounding_box.y + 5
            if b.bounding_box.collidepoint((x, y)):
                button = b

        if button == None:
            num = len(self.menu.components)
            if num != 0:
                button = self.menu.components[num - 1]
        
        if button != None and getattr(button, "bounding_box", None) != None:
            xy = (button.bounding_box.x + (button.bounding_box.w / 2), button.bounding_box.y)    

        return xy

    def link_borders(self, navigator_top_bottom_exit=True, first_index=None, last_index=None):
        """ Link components borders for the arrow keys navigation 

        :param navigator_top_bottom_exit:
        """
        if not hasattr(self.navigator, "components"):
            return

        margin = 10
        num = len(self.navigator.components)
        first_menu_comp = last_menu_comp = None
        menu_length = 0

        if getattr(self, "menu", None) != None:
            for n in self.menu.components:
                if isinstance(n, Container):
                    menu_length += 1   

            self.menu.exit_top_y = self.menu.exit_bottom_y = self.menu.bounding_box.y + self.menu.bounding_box.h + margin
            
            first_nav_comp = self.navigator.components[0]
            last_nav_comp = self.navigator.components[num - 1]

            self.menu.exit_right_x = first_nav_comp.bounding_box.x + margin
            self.menu.exit_right_y = first_nav_comp.bounding_box.y + margin
            
            self.menu.exit_left_x = last_nav_comp.bounding_box.x + last_nav_comp.bounding_box.w - margin
            self.menu.exit_left_y = last_nav_comp.bounding_box.y + margin

            if first_index == None: 
                first_index = 0

            if last_index == None: 
                last_index = menu_length - 1

            if menu_length > 0:
                first_menu_comp = self.menu.components[first_index]
                last_menu_comp = self.menu.components[last_index]

        if menu_length == 0:
            navigator_top_bottom_exit = False    

        for index, comp in enumerate(self.navigator.components):
            if navigator_top_bottom_exit and getattr(self, "menu", None):
                xy = self.get_menu_bottom_exit_xy(comp.bounding_box.x + 5)
                if xy:
                    comp.exit_top_y = xy[1] + margin
                    comp.exit_bottom_y = self.menu.bounding_box.y + margin
                    comp.exit_x = xy[0]
            else:
                comp.exit_top_y = None
                comp.exit_bottom_y = None
                comp.exit_x = None

            if index == 0:
                if last_menu_comp != None:
                    comp.exit_left_x = last_menu_comp.bounding_box.x + margin
                    comp.exit_left_y = last_menu_comp.bounding_box.y + margin
                else:
                    comp.exit_left_x = self.navigator.components[num - 1].bounding_box.x + margin
                    comp.exit_left_y = self.navigator.components[num - 1].bounding_box.y + margin
                if len(self.navigator.components) > 1:
                    c = self.navigator.components[index + 1]
                    comp.exit_right_x = c.bounding_box.x + margin
                else:
                    c = self.navigator.components[0]
                    c.exit_right_x = first_menu_comp.bounding_box.x + margin
                    c.exit_right_y = first_menu_comp.bounding_box.y + margin
            elif index == (num - 1):
                c = self.navigator.components[num - 2]
                comp.exit_left_x = c.bounding_box.x + margin
                if first_menu_comp != None:
                    comp.exit_right_x = first_menu_comp.bounding_box.x + margin
                    comp.exit_right_y = first_menu_comp.bounding_box.y + margin
                else:
                    comp.exit_right_x = self.navigator.components[0].bounding_box.x + margin
                    comp.exit_right_y = self.navigator.components[0].bounding_box.y + margin
            else:
                c = self.navigator.components[index - 1]
                comp.exit_left_x = c.bounding_box.x + margin
                c = self.navigator.components[index + 1]
                comp.exit_right_x = c.bounding_box.x + margin

    def refresh(self):
        """ Refresh screen """

        if self.update_component:
            self.update_component = False
            return self.bounding_box
        
        return Container.refresh(self)
