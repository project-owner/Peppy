# Copyright 2018-2024 Peppy Player peppy.player@gmail.com
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

from util.lyricsutil import LyricsUtil
from ui.component import Component
from ui.container import Container
from random import randrange
from screensaver.screensaver import Screensaver
from util.keys import LABELS, LYRICS_NOT_FOUND, kbd_keys, KEY_SELECT, KEY_LEFT, KEY_RIGHT
from util.config import SCREEN_INFO, WIDTH, HEIGHT, COLORS, COLOR_CONTRAST, COLOR_BRIGHT, LYRICS, \
    GENERATED_IMAGE

class Lyrics(Container, Screensaver):
    """ Song Lyrics screensaver plug-in. 
    After delay it displays the song lyrics if found.
    If lyrics not found then 'Lyrics not found' message will be displayed instead.
    The message periodically changes on-screen position.
    The period in seconds can be defined in the configuration file. 
    """
    def __init__(self, util):
        """ Initializer
        
        :param util: utility object
        """        
        self.name = LYRICS
        plugin_folder = type(self).__name__.lower() 
        Screensaver.__init__(self, self.name, util, plugin_folder, True)
        Container.__init__(self, util, bounding_box=util.screen_rect, background=self.bg[1], content=self.bg[2], image_filename=self.bg[3])

        self.util = util
        self.config = util.config
        self.screen_w = self.config[SCREEN_INFO][WIDTH]
        self.screen_h = self.config[SCREEN_INFO][HEIGHT]
        self.lines = 12

        if self.screen_w <= 320:
            line_length = 44
        elif self.screen_w > 480 and self.screen_w <= 800:
            line_length = 64
        elif self.screen_w > 800 and self.screen_w <= 1280:
            line_length = 100
        else:
            line_length = 54

        font_vertical_percent = 5
        self.lyrics_util = LyricsUtil(util.k2, self.lines, line_length)
        self.lyrics_not_found_label = self.config[LABELS][LYRICS_NOT_FOUND]
        self.bounding_box = util.screen_rect
        font_size = int((font_vertical_percent * self.bounding_box.h)/100)    
        self.f = util.get_font(font_size)
        self.lyrics_not_found = True
        self.not_found_screen = self.get_not_found_screen(util)
        self.add_component(self.not_found_screen)
        self.current_page = 0
        self.next_page = 0
        self.current_song = ""
        exit_area_height = int(2 * self.bounding_box.h / self.lines)
        self.exit_area = pygame.Rect(0, 0, self.bounding_box.w, exit_area_height)
        half = int(self.bounding_box.w / 2)
        self.left_half = pygame.Rect(0, 0, half, self.bounding_box.h)
        self.right_half = pygame.Rect(half, 0, half, self.bounding_box.h)
        self.disable_auto_refresh = False
    
    def get_not_found_screen(self, util):
        """ Set 'Lyrics not found' message in the current language 
        
        :param util: utility object

        :return: component for lyrics not found screen
        """
        c = Component(util, bgr=self.bgr)
        c.name = "base"
        self.lyrics_not_found_label = self.config[LABELS][LYRICS_NOT_FOUND]
        str_size = self.f.size(self.lyrics_not_found_label)
        self.label_rect = pygame.Rect(0, 0, str_size[0], str_size[1])
        img = self.f.render(self.lyrics_not_found_label, 1, self.config[COLORS][COLOR_CONTRAST])
        name = GENERATED_IMAGE + "not.found"
        c.content = (name, img)
        c.name = name
        c.image_filename = name

        return c
    
    def set_song_info(self, state):
        """ Set song info. Called when track changes.  
        
        :param state: button state
        """
        if self.disable_auto_refresh:
            return

        song_info = getattr(state, "album", None)
        if song_info == None:
            song_info = getattr(state, "file_name", None)
        
        if song_info == None:
            self.update_when_not_found()
            return
        
        if song_info != None and song_info == self.current_song:
            return

        self.current_song = song_info
        lyrics = self.lyrics_util.get_lyrics(self.current_song)

        if lyrics == None:
            self.update_when_not_found()
            return            
        
        lyrics = song_info + "\n\n" + lyrics
        
        self.lyrics_not_found = False    
        pages = self.lyrics_util.format_lyrics(lyrics)
        self.current_page = 0
        self.next_page = 0
        self.components.clear()
        for n, page in enumerate(pages):
            self.add_page(n, page)        

    def update_when_not_found(self):
        """ Update the screen when lyrics not found """

        if self.components and self.components[0] and not isinstance(self.components[0], Container) and self.components[0].name == GENERATED_IMAGE + "not.found":
            return

        self.lyrics_not_found = True
        self.components.clear()
        self.add_component(self.not_found_screen)
        self.refresh()
    
    def add_page(self, page_num, page):
        """ Add lyrics page to the container
        
        :param page_num: lyrics page number
        :param page: lyrics page 
        """
        cont = Container(self.util, self.bounding_box, self.bgr)
        max_line_length = self.get_max_line_length(page)
        s = self.f.size("W")
        gap = (s[1] * 44) / 100
        page_height = self.lines * (s[1] + gap)
        offset_y = (self.screen_h - page_height) / 2
        offset_x = (self.screen_w - max_line_length) / 2
        
        for n, line in enumerate(page):
            c = Component(self.util, bgr=self.bgr)
            str_size = self.f.size(line)
            if page_num == 0 and n == 0:
                color = self.config[COLORS][COLOR_BRIGHT]
            else:
                color = self.config[COLORS][COLOR_CONTRAST]
            img = self.f.render(line, 1, color)
            name = GENERATED_IMAGE + str(n)
            c.content = (name, img)
            c.name = name
            c.image_filename = name
            c.content_y = offset_y + ((str_size[1] + gap) * n)
            c.content_x = offset_x
            cont.add_component(c)
            
        self.add_component(cont)    
    
    def get_max_line_length(self, page):
        """ Get maximum text line length in the page
        
        :param page: the lyrics page
        
        :return: maximum text line length
        """
        line_length = 0
        for _, line in enumerate(page):
            str_size = self.f.size(line)
            line_length = max(str_size[0], line_length)
        return line_length
    
    def reset(self):
        """ Reset screensaver """
        
        self.current_song = None         
        self.lyrics_not_found = True
        if len(self.components) > 1:
            del self.components[1:]
        c = self.components[0]
        c.visible = True
        c.content_x = randrange(1, self.screen_w - self.label_rect.w)
        c.content_y = randrange(1, self.screen_h - self.label_rect.h)
    
    def set_image_folder(self, state):
        """ Called upon station change

        :param: state object defining image folder
        """
        self.update_when_not_found()

    def start(self):
        """ Start screensaver """

        self.current_page = 0
        self.next_page = 0

    def update(self, area=None):
        """  Update screensaver """

        pass

    def refresh(self, init=False):
        """ Draw lyrics on screen 

        :param init: initial call
        """
        if self.disable_auto_refresh:
            return

        if self.lyrics_not_found:
            self.reset()
        else:
            self.current_page = self.next_page
            for n, c in enumerate(self.components):
                if n == self.current_page:
                    c.visible = True
                else:
                    c.visible = False

            if self.next_page == len(self.components) - 1:
                self.next_page = 0
            else:
                self.next_page += 1

        self.clean()
        super(Lyrics, self).draw()

        if init:
            Component.update(self, self.bounding_box)

        return self.bounding_box

    def is_exit_clicked(self, event):
        """ Handles clicks on screen
        
        :param event: mouse event

        :return: True - exit area clicked, False - exit area was not clicked
        """
        if event == None:
            return True

        if not self.disable_auto_refresh and self.lyrics_not_found and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            return True

        if event.type == pygame.KEYUP:
            if event.key == kbd_keys[KEY_SELECT]:
                return True
            elif event.key == kbd_keys[KEY_LEFT]:
                self.turn_left()
                return False
            elif event.key == kbd_keys[KEY_RIGHT]:
                self.turn_right()
                return False

        if not (event.type == pygame.MOUSEBUTTONUP and event.button == 1):
            return False

        pos = event.pos

        if self.exit_area.collidepoint(pos) and self.current_page == 0:
            self.disable_auto_refresh = False
            return True
        else:
            self.disable_auto_refresh = True

            if self.left_half.collidepoint(pos):
                self.turn_left()
            else:
                self.turn_right()
            
            return False

    def turn_left(self):
        """ Turn page left """

        if self.current_page == 0:
            self.current_page = len(self.components) - 1
        else:
            self.current_page -= 1
        self.update_screen()

    def turn_right(self):
        """ Turn page right """

        if self.current_page == len(self.components) - 1:
            self.current_page = 0
        else:
            self.current_page += 1
        self.update_screen()

    def update_screen(self):
        """ Update screen """

        for n, c in enumerate(self.components):
            if n == self.current_page:
                c.visible = True
            else:
                c.visible = False

        self.clean()
        super(Lyrics, self).draw()
        pygame.display.update(self.bounding_box)

    def set_util(self, util):
        """ Set utility object

        :param util: external utility object
        """
        self.util = util
        self.config = util.config
        self.not_found_screen = self.get_not_found_screen(util)
