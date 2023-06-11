# Copyright 2016-2023 Peppy Player peppy.player@gmail.com
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

from ui.screen.bookscreen import BookScreen, GENRE_BOOKS
from websiteparser.siteparser import GENRE_URL

class BookGenreBooks(BookScreen):
    """ Genre books screen """
    
    def __init__(self, util, listeners, title, go_site_playback, genre, site_parser, d):
        """ Initializer
        
        :param util: utility object
        :param listeners: screen listeners
        :param title: screen title
        :param go_site_playback: playback callback
        :param genre: genre
        :param site_parser: site parser
        :param d: dictionary with menu button flags 
        """ 
        self.current_genre = genre
        self.parser = site_parser
        self.title = title
        self.language_url = d[4]
        BookScreen.__init__(self, util, listeners, title, GENRE_BOOKS, go_site_playback, self.get_books, site_parser, d)
    
    def get_books(self):
        """ Get genre books
        
        :return: genre books
        """ 
        p = self.current_page
        gp = self.parser.genre_books_parser
         
        if getattr(gp, GENRE_URL, None) == None or gp.genre_url != self.current_genre:
            gp.site_total_pages = 0
         
        url = gp.get_url(p, self.current_genre)
         
        in_cache = gp.is_in_cache(url)

        if not in_cache:
            self.set_loading(self.title)
        new_books = self.parser.get_books_by_genre(self.current_genre, self.current_page)
        if not in_cache:
            self.reset_loading()

        self.book_menu.current_page = self.current_page

        return new_books
    
    def set_current(self, state):
        """ Set genre books
        
        :param state: button state object
        """   
        g = getattr(state, "genre", None)        
        if not g or g == self.current_genre:
            return
        
        self.current_genre = g
        self.title = state.name
        self.total_pages = 0
        self.current_page = 1
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
 
