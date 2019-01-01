# Copyright 2018 Peppy Player peppy.player@gmail.com
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

import time
import pygame

from util.lyricsutil import LyricsUtil
from ui.component import Component
from container import Container
from random import randrange
from screensaver.screensaver import Screensaver
from util.keys import SCREEN_RECT, LABELS, LYRICS_NOT_FOUND
from util.config import SCREEN_INFO, WIDTH, HEIGHT, COLORS, COLOR_CONTRAST, COLOR_BRIGHT

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
        self.util = util
        self.config = util.config
        self.screen_w = self.config[SCREEN_INFO][WIDTH]
        self.screen_h = self.config[SCREEN_INFO][HEIGHT]
        self.lines = 12
        line_length = 52
        font_vertical_percent = 5
        
        self.lyrics_util = LyricsUtil(util.k2, self.lines, line_length)
        self.lyrics_not_found_label = self.config[LABELS][LYRICS_NOT_FOUND]
        
        plugin_folder = type(self).__name__.lower() 
        Screensaver.__init__(self, plugin_folder)
        self.bounding_box = self.config[SCREEN_RECT]
        Container.__init__(self, util, self.bounding_box, (0, 0, 0))
                
        font_size = int((font_vertical_percent * self.bounding_box.h)/100)    
        self.f = util.get_font(font_size)
        self.lyrics_not_found = True
        
        c = Component(util, bgr=(0, 0, 0))
        self.set_not_found(c)
        self.add_component(c)
        self.current_page = 1
        self.current_song = ""
    
    def set_not_found(self, c):
        """ Set 'Lyrics not found' message in the current language 
        
        :param c: component for message
        """
        self.lyrics_not_found_label = self.config[LABELS][LYRICS_NOT_FOUND]
        str_size = self.f.size(self.lyrics_not_found_label)
        self.label_rect = pygame.Rect(0, 0, str_size[0], str_size[1])
        img = self.f.render(self.lyrics_not_found_label, 1, self.config[COLORS][COLOR_CONTRAST])
        c.content = ("img", img)
    
    def start(self):
        """ Start screensaver """
        
        if self.lyrics_not_found_label != self.config[LABELS][LYRICS_NOT_FOUND]:
            self.set_not_found(self.components[0])
        
        if len(self.components) > 1:
            self.current_page = 1
        
    def set_song_info(self, state):
        """ Set song info. Called when track changes.  
        
        :param state: button state
        """
        song_info = getattr(state, "album", None)
        if song_info == None:
            song_info = getattr(state, "file_name", None)
        
        if song_info == None:
            self.reset()
            return
        
        if song_info != None and song_info == self.current_song:
            return
        
        self.current_song = song_info
        lyrics = self.lyrics_util.get_lyrics(self.current_song)

        if len(self.components) > 1:
            del self.components[1:]
        
        if lyrics == None:
            self.reset()
            return            
        
        lyrics = song_info + "\n\n" + lyrics
        
        self.lyrics_not_found = False    
        pages = self.lyrics_util.format_lyrics(lyrics)
        self.current_page = 1
        for n, page in enumerate(pages):
            self.add_page(n, page)
    
    def add_page(self, page_num, page):
        """ Add lyrics page to the container
        
        :param page_num: lyrics page number
        :param page: lyrics page 
        """
        cont = Container(self.util, self.bounding_box, (0, 0, 0))
        max_line_length = self.get_max_line_length(page)
        s = self.f.size("W")
        page_height = self.lines * s[1]
        offset_y = (self.screen_h - page_height) / 2
        offset_x = (self.screen_w - max_line_length) / 2
        
        for n, line in enumerate(page):
            c = Component(self.util, bgr=(0, 0, 0))
            str_size = self.f.size(line)
            if page_num == 0 and n == 0:
                color = self.config[COLORS][COLOR_BRIGHT]
            else:
                color = self.config[COLORS][COLOR_CONTRAST]
            img = self.f.render(line, 1, color)
            c.content = ("img", img)
            c.content_y = offset_y + (str_size[1] * n)
            c.content_x = offset_x
            cont.add_component(c)
        self.add_component(cont)    
    
    def get_max_line_length(self, page):
        """ Get maximum text line length in the page
        
        :param page: the lyrics page
        
        :return: maximum text line length
        """
        line_length = 0
        for n, line in enumerate(page):
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
    
    def refresh(self):
        """ Draw lyrics on screen """
        
        if self.lyrics_not_found:
            self.reset()
        else:    
            for n, c in enumerate(self.components):
                if n == self.current_page:
                    c.visible = True
                else:
                    c.visible = False
            if self.current_page == len(self.components) - 1:
                self.current_page = 1
            else:
                self.current_page += 1        
        self.clean()
        super(Lyrics, self).draw()
        self.update()
