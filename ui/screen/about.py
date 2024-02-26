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

import os
import pygame

from ui.component import Component
from ui.container import Container
from ui.layout.borderlayout import BorderLayout
from ui.layout.gridlayout import GridLayout
from event.dispatcher import USER_EVENT_TYPE, SUB_TYPE_KEYBOARD
from ui.factory import Factory
from util.config import COLOR_LOGO, COLOR_CONTRAST, COLORS, COLOR_WEB_BGR, RELEASE, EDITION_NAME, USAGE, \
    USE_CHECK_FOR_UPDATES, RELEASE_YEAR, RELEASE_MONTH, RELEASE_DAY, BACKGROUND, MENU_BGR_OPACITY
from util.util import V_ALIGN_TOP, V_ALIGN_BOTTOM

PERCENT_FOOTER_HEIGHT = 20.00
PERCENT_NAME_LONG_HEIGHT = 10.00
PERCENT_FOOTER_FONT = 26.00

class AboutScreen(Container):
    """ About Screen. Extends Container class """
    
    def __init__(self, util):
        """ Initializer
        
        :param util: utility object
        """        
        self.util = util
        self.config = util.config
        self.config_class = util.config_class
        factory = Factory(util)
        self.name = "about.screen"

        self.color_web_bgr = self.config[COLORS][COLOR_WEB_BGR]
        color_logo = self.config[COLORS][COLOR_CONTRAST]
        color_status = self.config[COLORS][COLOR_LOGO]
        opacity = self.config[BACKGROUND][MENU_BGR_OPACITY]
        c = (self.color_web_bgr[0], self.color_web_bgr[1], self.color_web_bgr[2], opacity)
        
        cont = util.screen_rect
        img_filename = None
        bg = self.util.get_background("about", c)

        self.bgr_type = bg[0]
        if bg[2]:
            self.bgr = bg[1]
            cont = bg[2]
        else:
            self.bgr = (bg[1][0], bg[1][1], bg[1][2])
        
        img_filename = bg[3]
        self.bgr_key = bg[5]
            
        Container.__init__(self, util, bounding_box=util.screen_rect, background=self.color_web_bgr, content=cont, image_filename=img_filename)
        
        self.start_listeners = []
        
        self.installed_release = self.config[RELEASE]
        self.installed_edition = self.installed_release[EDITION_NAME]
        self.installed_year = self.installed_release[RELEASE_YEAR]
        self.installed_month = self.installed_release[RELEASE_MONTH]
        self.installed_day = self.installed_release[RELEASE_DAY]
        
        layout = BorderLayout(self.bounding_box)
        layout.set_percent_constraints(0, PERCENT_FOOTER_HEIGHT, 0, 0)
        font_size = int((layout.BOTTOM.h * PERCENT_FOOTER_FONT)/100.0)

        button = factory.create_image_button(".." + os.sep + "peppy", bounding_box=layout.CENTER, bgr=bg[1], image_size_percent=68, selected=False)
        if bg[2]:
            button.parent_screen = bg[2]
        else:
            button.parent_screen = layout.CENTER
        x = layout.CENTER.w/2 - button.components[1].content.get_size()[0]/2
        y = layout.CENTER.h/2 - button.components[1].content.get_size()[1]/2        
        button.components[1].content_x = x
        button.components[1].content_y = y
        self.add_component(button)
        
        bottom_bgr = pygame.Rect(layout.BOTTOM.x, layout.BOTTOM.y - 1, layout.BOTTOM.w, layout.BOTTOM.h + 2)
        comp = Component(self.util, bottom_bgr, bb=bottom_bgr, bgr=bg[1])
        comp.name = "txt.bgr"
        self.add_component(comp)

        text_layout = pygame.Rect(layout.BOTTOM.x, layout.BOTTOM.y - int((self.bounding_box.h * 5) / 100), layout.BOTTOM.w, layout.BOTTOM.h)

        if self.util.connected_to_internet and self.config[USAGE][USE_CHECK_FOR_UPDATES]:
            bottom_layout = GridLayout(text_layout)
            bottom_layout.set_pixel_constraints(2, 1)
            line_top = bottom_layout.get_next_constraints()
            line_bottom = bottom_layout.get_next_constraints()
        else:
            line_top = text_layout

        transparent = (0, 0, 0, 0)
        self.release = factory.create_output_text("installed", line_top, transparent, color_logo, font_size, full_width=True, valign=V_ALIGN_BOTTOM)
        self.release.parent_screen = bg[2]
        if bg[2]:
            self.release.parent_screen = bg[2]
        else:
            self.release.parent_screen = line_top
        self.add_component(self.release)

        if self.util.connected_to_internet and self.config[USAGE][USE_CHECK_FOR_UPDATES]:
            self.status = factory.create_output_text("status", line_bottom, transparent, color_status, font_size, full_width=True, valign=V_ALIGN_TOP)
            self.status.parent_screen = bg[2]
            self.add_component(self.status)
            self.new_release = self.get_new_release()
    
    def set_current(self, state=None):
        """ Set current screen

        :param state: button state
        """
        self.release.set_text_no_draw(self.installed_edition)
        if self.util.connected_to_internet and self.config[USAGE][USE_CHECK_FOR_UPDATES]:
            if self.new_release:
                template = self.util.get_labels()["new.version.released"]
                status_msg = template.replace("{edition}", self.new_release)
            else:
                status_msg = self.util.get_labels()["player.is.up.to.date"]
            self.status.set_text_no_draw(status_msg)

    def get_new_release(self):
        """ Check if new release is avaialble on github

        :return: name of new release if any, None otherwise
        """
        github_release = self.config_class.load_release(False)
        github_edition = github_release[EDITION_NAME]
        github_release_year = github_release[RELEASE_YEAR]
        github_release_month = github_release[RELEASE_MONTH]
        github_release_day = github_release[RELEASE_DAY]

        if (github_edition != self.installed_edition or
            (github_edition == self.installed_edition and (github_release_year != self.installed_year or
            github_release_month != self.installed_month or github_release_day != self.installed_day ))):
            return github_edition
        else:
            return None

    def add_listener(self, listener):
        """ Add About Screen event listener
        
        :param listener: event listener
        """
        if listener not in self.start_listeners:
            self.start_listeners.append(listener)
            
    def notify_listeners(self, state):
        """ Notify all About Screen event listeners
        
        :param state: button state
        """
        if not self.visible:
            return
        
        for listener in self.start_listeners:
            listener(state)

    def handle_event(self, event):
        """ About Screen event handler
        
        :param evenr: event to hanle
        """
        if not self.visible: return
        
        if (event.type == pygame.MOUSEBUTTONUP) or (event.type == USER_EVENT_TYPE and event.sub_type == SUB_TYPE_KEYBOARD and event.action == pygame.KEYUP):
            self.notify_listeners(None)
    
    def exit_screen(self):
        """ Complete actions required to save screen state """
        
        self.set_visible(False)
        
    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        self.add_listener(redraw_observer)
