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

from ui.screen.bookscreen import BookScreen, AUTHOR_BOOKS
from websiteparser.siteparser import TOTAL_PAGES

class BookAuthorBooks(BookScreen):
    """ Authors' books screen """
    
    def __init__(self, util, listeners, title, go_site_playback, author_url, site_parser, voice_assistant, d):
        """ Initializer
        
        :param util: utility object
        :param listeners: screen listeners
        :param title: screen title
        :param go_site_playback: playback callback
        :param author_url: url
        :param site_parser: site parser
        :param d: dictionary with menu button flags 
        """ 
        self.author_name = title
        self.author_url = author_url
        self.parser = site_parser
        BookScreen.__init__(self, util, listeners, title, AUTHOR_BOOKS, go_site_playback, self.get_books, site_parser, voice_assistant, d)               
    
    def get_books(self):
        """ Get author books
        
        :return: author books
        """        
        p = self.current_page
        np = self.parser.news_parser
        url = self.author_url + np.page_url_prefix + str(p)
        author_books = self.parser.get_author_books(self.author_name, self.author_url, p)
        author_books[TOTAL_PAGES] = self.parser.news_parser.pages[url]             
        return author_books
    
    def turn_page(self):
        """ Turn author books page """
        
        p = self.current_page
        np = self.parser.news_parser
        url = self.author_url + np.page_url_prefix + str(p)
        in_cache = self.parser.news_parser.is_in_cache(url)
        if not in_cache:
            self.set_loading(self.author_name)
    
        BookScreen.turn_page(self)
            
        if not in_cache:
            self.reset_loading() 

    def set_current(self, state):
        """ Set author books
        
        :param state: button state object
        """        
        u = getattr(state, "url", None)        
        if not u or u == self.author_url:
            return
        
        self.author_name = state.name
        self.author_url = u
        self.title = state.name
        self.total_pages = 0
        self.current_page = 1
        self.current_page = 0
        self.turn_page()

    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        self.navigator.add_observers(update_observer, redraw_observer)
        self.book_menu.add_menu_loaded_listener(redraw_observer)
        self.book_menu.add_menu_observers(update_observer, redraw_observer)
        self.add_loading_listener(redraw_observer)


        
