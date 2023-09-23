# Copyright 2021-2023 Peppy Player peppy.player@gmail.com
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

from ui.component import Component
from ui.navigator.imageviewer import ImageViewerNavigator, MOVE_LEFT, MOVE_RIGHT, MOVE_UP, MOVE_DOWN, FIT, \
    ZOOM_IN, ZOOM_OUT, ROTATE
from ui.screen.screen import Screen, PERCENT_TOP_HEIGHT
from util.keys import IMAGE_VIEWER_SCREEN, KEY_BACK
from util.config import GENERATED_IMAGE
from threading import Thread

class ImageViewer(Screen):
    """ Image Viewer Screen """
    
    def __init__(self, util, listeners):
        """ Initializer
        
        :param util: utility object
        :param listener: screen menu event listener
        """
        Screen.__init__(self, util, IMAGE_VIEWER_SCREEN, PERCENT_TOP_HEIGHT, screen_title_name="image_viewer_screen_title", create_dynamic_title=True)
        self.animated_title = True
        self.image_util = util.image_util
        self.viewport_rect = self.layout.CENTER.copy()

        self.image_component = Component(util)
        self.image_component.content_x = self.layout.CENTER.x
        self.image_component.content_y = self.layout.CENTER.y
        self.image_component.bounding_box = self.layout.CENTER
        self.image_component.bounding_box.y = 0
        self.image_component.name = GENERATED_IMAGE + IMAGE_VIEWER_SCREEN
        self.image_component.image_filename = self.image_component.name
        self.add_component(self.image_component)

        listeners[FIT] = self.fit
        listeners[ZOOM_IN] = self.zoom_in
        listeners[ZOOM_OUT] = self.zoom_out
        listeners[MOVE_LEFT] = self.move_left
        listeners[MOVE_RIGHT] = self.move_right
        listeners[MOVE_UP] = self.move_up
        listeners[MOVE_DOWN] = self.move_down
        listeners[ROTATE] = self.rotate_cw

        self.mouse_events = [pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN]
        self.all_mouse_events = self.mouse_events.copy()
        self.all_mouse_events.append(pygame.MOUSEMOTION)
        
        self.navigator = ImageViewerNavigator(util, self.layout.BOTTOM, listeners)
        self.action_buttons_area = self.get_action_buttons_area()
        self.add_navigator(self.navigator)

        self.link_borders()
        self.image_url = None
        self.aspect_ratio = self.layout.CENTER.w / self.layout.CENTER.h
        self.window_size = (self.layout.CENTER.w, self.layout.CENTER.h)
        self.step = 30
        self.k_x = self.step * self.aspect_ratio
        self.k_y = self.step

        self.back_button = self.navigator.get_button_by_name(KEY_BACK)
        self.back_button.set_selected(True)
        self.max_size = 1000

        third = self.viewport_rect.w / 3
        half = self.viewport_rect.h / 2
        self.rect_move_up = pygame.Rect(third, self.viewport_rect.y + half, third, half)
        self.rect_move_down = pygame.Rect(third, self.viewport_rect.y, third, half)
        self.rect_move_left = pygame.Rect(third * 2, self.viewport_rect.y, third, self.viewport_rect.h)
        self.rect_move_right = pygame.Rect(0, self.viewport_rect.y, third, self.viewport_rect.h)

        self.run_navigator_thread = False
        self.button_pressed_in_viewer = False
        self.accelerator = 2
        self.mouse_x = None
        self.mouse_y = None
        self.in_motion = False

    def set_current(self, state):
        """ Set current screen.
        Avoid caching as it can consume a lot of memory in case of large images
        """
        if state.url == self.image_url:
            return

        self.screen_title.set_text(state.url)
        self.screen_title.link = True

        img = self.image_util.load_pygame_image(state.url, use_cache=False)
        if not img: return

        self.previous_position = (0, 0)
        self.url = state.url
        self.image_url = self.url
        self.image = img[1]

        self.image = self.reduce(self.image)

        self.image_w = self.image.get_width()
        self.image_h = self.image.get_height()

        k_w = self.image_w / self.layout.CENTER.w
        k_h = self.image_h / self.layout.CENTER.h
        self.k = max(k_w, k_h)

        self.fit()

    def get_action_buttons_area(self):
        """ Get the area occupied by action buttons

        :return: rectangle representing area
        """
        start = end = None
        for button in self.navigator.buttons:
            name = button.state.name
            if name == ZOOM_IN:
                start = button
            if name == MOVE_DOWN:
                end = button
        x = start.bounding_box.x
        y = start.bounding_box.y
        w = end.bounding_box.x + end.bounding_box.w - start.bounding_box.x
        h = end.bounding_box.h
        return pygame.Rect(x, y, w, h)

    def reduce(self, image):
        """ Reduce image size if exceeds max values

        :param image: image to reduce

        :return: reduced image
        """
        image_w = image.get_width()
        image_h = image.get_height()

        if image_w > self.max_size or image_h > self.max_size:
            if image_w >= image_h:
                window = (self.max_size, int((image_h / image_w) * self.max_size))
            else:
                window = (int((image_w / image_h) * self.max_size), self.max_size)
            return pygame.transform.smoothscale(image, window)     
        else:
            return image

    def fit(self, state=None):
        """ Fit image to the bounding box """
        
        w = self.layout.CENTER.w * self.k
        h = self.layout.CENTER.h * self.k
        x = (w - self.image_w) / 2
        y = (h - self.image_h) / 2
        self.viewport = pygame.Rect(-x, -y, w, h)
        self.image_previous_box = pygame.Rect(0, 0, 1, 1)
        self.delta_x = self.delta_y = 0

        self.redraw()

    def redraw(self):
        """ Redraw image """

        if self.viewport == self.image_previous_box or self.viewport.width == 0 or self.viewport.height == 0:
            return

        base = pygame.Surface((self.viewport.width, self.viewport.height))
        base.blit(self.image, (0, 0), self.viewport)

        self.image_previous_box = self.viewport.copy()
        self.image_component.content = pygame.transform.smoothscale(base, self.window_size)
        self.clean_draw_update()

    def move_left(self, state):
        """ Move image left """

        self.viewport.x += self.step
        self.redraw()

    def move_right(self, state):
        """ Move image right """
        
        self.viewport.x -= self.step
        self.redraw()

    def move_up(self, state):
        """ Move image up """
        
        self.viewport.y += self.step
        self.redraw()

    def move_down(self, state):
        """ Move image down """
        
        self.viewport.y -= self.step
        self.redraw()

    def zoom_in(self, state):
        """ Zoom-in """
        
        if (self.viewport.width - self.step) < 0 or (self.viewport.height - self.step) < 0:
            return

        self.viewport.inflate_ip(-self.k_x, -self.k_y)
        self.redraw()

    def zoom_out(self, state):
        """ Zoom-out """
        
        self.viewport.inflate_ip(self.k_x, self.k_y)
        self.redraw()

    def rotate_cw(self, state):
        """ Rotate clockwise """
        
        self.image = pygame.transform.rotate(self.image, -90)
        self.image_w = self.image.get_width()
        self.image_h = self.image.get_height()
        self.fit()

    def handle_viewer_event(self, event):
        """ Handle viewport action event

        :param event: mouse event
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.button_pressed_in_viewer = True
            self.mouse_x = event.pos[0]
            self.mouse_y = event.pos[1]
        elif event.type == pygame.MOUSEBUTTONUP:
            self.button_pressed_in_viewer = False
            self.run_navigator_thread = False

            if self.in_motion:
                dx = (self.mouse_x - event.pos[0]) * self.accelerator
                dy = (self.mouse_y - event.pos[1]) * self.accelerator
                self.viewport.move_ip((dx, dy))
                self.mouse_x = event.pos[0]
                self.mouse_y = event.pos[1]
                self.in_motion = False
                self.redraw()
                self.update_web_observer()

            self.mouse_x = None
            self.mouse_y = None
        elif event.type == pygame.MOUSEMOTION and self.button_pressed_in_viewer:
            if hasattr(event, "rel"):
                self.viewport.move_ip((-event.rel[0] * self.accelerator, -event.rel[1] * self.accelerator))
                self.redraw()
                self.update_web_observer()
            else: # browser
                if not self.in_motion:
                    self.in_motion = True

    def navigator_thread(self, event):
        """ Action thread function

        :param event: mouse event
        """
        x = event.pos[0]
        y = event.pos[1]
        while self.run_navigator_thread:
            new_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN)
            new_event.pos = [x, y]
            new_event.button = 1
            self.navigator.handle_event(new_event)
            new_event = pygame.event.Event(pygame.MOUSEBUTTONUP)
            new_event.pos = [x, y]
            new_event.button = 1
            self.navigator.handle_event(new_event)
            time.sleep(0.02)

    def handle_navigator_event(self, event):
        """ Handle navigator buttons events

        :param event: mouse event
        """
        if self.button_pressed_in_viewer and event.type == pygame.MOUSEBUTTONUP:
            self.button_pressed_in_viewer = False
            return

        if self.action_buttons_area.collidepoint(event.pos):
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.navigator.unselect()
                self.run_navigator_thread = True
                thread = Thread(target=self.navigator_thread, args=[event])
                thread.start()
            elif event.type == pygame.MOUSEBUTTONUP:
                self.run_navigator_thread = False
        else:
            if event.type in self.mouse_events:
                self.run_navigator_thread = False
                clicked_button = self.navigator.get_clicked_button(event)
                if clicked_button != None:
                    self.navigator.unselect()
                    clicked_button.handle_event(event)
                    clicked_button.set_selected(True)

    def handle_event(self, event):
        """ Event handler

        :param event: event to handle
        """
        if not self.visible: return

        if (self.button_pressed_in_viewer or self.run_navigator_thread) and not hasattr(event, "pos"):
            self.button_pressed_in_viewer = False
            self.run_navigator_thread = False
            return

        if hasattr(event, "pos"):
            if self.viewport_rect.collidepoint(event.pos):
                self.handle_viewer_event(event)
            elif self.layout.BOTTOM.collidepoint(event.pos):
                self.handle_navigator_event(event)
            else:
                if event.type == pygame.MOUSEBUTTONUP:
                    self.button_pressed_in_viewer = False
                    self.run_navigator_thread = False
            return

        self.navigator.handle_event(event)

    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        Screen.add_screen_observers(self, update_observer, redraw_observer)
        self.navigator.add_observers(update_observer, redraw_observer)
