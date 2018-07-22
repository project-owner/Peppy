# Copyright 2016-2018 Peppy Player peppy.player@gmail.com
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

from ui.screen.bookscreen import BookScreen, NEW_BOOKS
from util.keys import LABELS, KEY_NEW_BOOKS
from ui.screen.screen import Screen

class BookNew(BookScreen):
    """ New books screen """
    
    def __init__(self, util, listeners, go_site_playback, site_parser, voice_assistant, d):
        """ Initializer
        
        :param util: utility object
        :param listeners: screen listeners
        :param go_site_playback: playback callback
        :param site_parser: site parser
        :param d: dictionary with menu button flags 
        """ 
        title = util.config[LABELS][KEY_NEW_BOOKS]
        self.language_url = d[4]
        BookScreen.__init__(self, util, listeners, title, NEW_BOOKS, go_site_playback, self.get_books, site_parser, voice_assistant, d)               
    
    def get_books(self):
        """ Get new books
        
        :return: new books
        """ 
        p = self.current_page
        
        if self.language_url and len(self.language_url) != 0:
            parser = self.parser.language_parser
            parser.language_url = self.language_url
            url = parser.get_url(p)
        else:            
            parser = self.parser.news_parser
            url = parser.base_url + parser.page_url_prefix + str(p)
        
        in_cache = parser.is_in_cache(url, self.current_page)
        if not in_cache:
            self.set_loading(self.title)
            
        new_books = self.parser.get_books(p, language_url=self.language_url)
        
        if not in_cache:
            self.reset_loading()
        return new_books
    
    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        Screen.add_screen_observers(self, update_observer, redraw_observer)
        
        self.navigator.add_observers(update_observer, redraw_observer)
        self.book_menu.update_observer = update_observer
        self.book_menu.redraw_observer = redraw_observer
        self.book_menu.add_menu_loaded_listener(redraw_observer)
        self.book_menu.add_menu_observers(update_observer, redraw_observer)
        self.add_loading_listener(redraw_observer)
