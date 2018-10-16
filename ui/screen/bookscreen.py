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

from ui.screen.menuscreen import MenuScreen
from ui.menu.bookmenu import BookMenu
from ui.page import Page
from ui.layout.multilinebuttonlayout import LINES
from ui.state import State
from multiprocessing.dummy import Pool 
from websiteparser.siteparser import TOTAL_PAGES, BOOK_SUMMARIES, AUTHOR_NAME, IMG_URL, BOOK_URL, \
    GENRE_NAME, BOOK_TITLE

AUTHOR_BOOKS = "author.books"
GENRE_BOOKS = "genre.books"
NEW_BOOKS = "new.books"

class BookScreen(MenuScreen):
    """ Base class for book screens """
    
    def __init__(self, util, listeners, title, screen_type, go_site_playback, get_books, site_parser, voice_assistant, d):
        """ Initializer
        
        :param util: utility object
        :param listeners: screen listeners
        :param title: screen title
        :param screen_type: screen name
        :param go_site_playback: playback callback
        :param get_books: get books callback
        :param site_parser: site parser
        :param d: dictionary with menu button flags 
        """ 
        self.util = util
        self.config = util.config
        self.screen_type = screen_type
        self.go_site_playback = go_site_playback
        self.parser = site_parser
        self.get_books = get_books 
        self.rows = d[0]
        self.columns = d[1]
        self.show_author = d[2]
        self.show_genre = d[3]
        self.language_url = d[4]
        self.title = title      
        MenuScreen.__init__(self, util, listeners, self.rows, self.columns, voice_assistant, d, self.turn_page)        
        self.book_menu = BookMenu(util, self.next_page, self.previous_page, self.set_title, self.reset_title, self.go_to_page, go_site_playback, self.rows, self.columns, self.menu_button_layout, (0, 0, 0), self.menu_layout) 
        self.set_menu(self.book_menu)       
    
    def turn_page(self):
        """ Turn menu page """
        
        self.book_menu.set_items({}, 0, self.go_site_playback)
        books = self.get_books()
        book_list = self.set_books(self.current_page, books)
        d = self.book_menu.make_dict(book_list.items)
        self.book_menu.set_items(d, 0, self.go_site_playback)
        buttons = self.components[1].buttons
        size = len(buttons.values()) 
        
        if size == 0:
            return 
        
        pool = Pool(size)
        pool.map(self.set_image, buttons.values()) 
        pool.close() 
        pool.join()
        self.book_menu.select_by_index(0) 
    
    def set_image(self, b):
        """ Set button image
        
        :param b: button
        """
        self.menu_button_layout.create_layout(b.bounding_box)
        img_rect = self.menu_button_layout.image_rectangle
        img_y = img_rect.y
        
        comps = b.components
        im = comps[1]
        url = im.image_filename
        img = self.get_image_from_cache(url)
        if img:
            self.set_button_image(b, img, img_y)
        else:
            img = self.util.load_menu_screen_image(url, img_rect.w, img_rect.h)
            if img:
                self.set_button_image(b, img, img_y)
                self.put_image_to_cache(url, img)

    def set_books(self, page_index, books):
        """ Set books  
        
        :param page_index: page index
        :param books: books
        
        :return: books page
        """
        self.total_pages = books[TOTAL_PAGES]
        
        left = str(self.current_page - 1)
        right = str(self.total_pages - self.current_page)
        if self.total_pages == 0:
            right = "0"
        if int(right) < 0:
            right = left
        self.navigator.left_button.change_label(left)
        self.navigator.right_button.change_label(right)
        self.set_title(self.current_page)
        
        folder_content = self.get_books_objects(books[BOOK_SUMMARIES], self.rows, self.columns, self.menu_layout)  
        return Page(folder_content, self.rows, self.columns)        

    def get_books_objects(self, books, rows, cols, bounding_box):
        """ Prepare book objects  
        
        :param books: list of books
        :param rows: menu rows
        :param cols: menu columns
        :param bounding_box: bounding box
        
        :return: books objects
        """        
        items = []

        for index, b in enumerate(books):
            s = State()
            s.index = index
            s.name = {}
            title = b[BOOK_TITLE]
            s.l_name = title
            s.show_img = False
            s.show_bgr = True
            s.bgr = (255, 255, 255)
            s.book_url = b[BOOK_URL]
            s.comparator_item = index
            s.index_in_page = index % (cols * rows)
            s.show_label = True
            
            self.add_title(s.name, title)
            
            if self.show_author:
                self.add_author(b, s.name)
                
            if self.show_genre:
                self.add_genre(b, s.name)
            
            self.add_image(b, s, bounding_box, cols, rows)
            
            items.append(s)
        return items
    
    def add_title(self, d, title):
        """ Set book title
        
        :param d: dictionary
        :param title: book title
        """                 
        if " " in title:
            t = title.split()
            if len(t) == 2:
                d[0] = t[0]
                d[1] = t[1]
            else:
                n = t[0] + " " + t[1]
                d[0] = n
                d[1] = title[len(n):]
        else:    
            d[0] = title
            
    def add_author(self, b, d):
        """ Add author name to the button
        
        :param b: button
        :param d: dictionary
        """
        try:
            if self.language_url == None:
                d[LINES - 2] = b[AUTHOR_NAME]
            else:
                d[LINES - 1] = b[AUTHOR_NAME]
        except:
            pass
        
    def add_genre(self, b, d):
        """ Add genre to the button
        
        :param b: button
        :param d: dictionary
        """    
        g = b[GENRE_NAME]
        i = g.find(",")
        if i != -1:
            d[LINES - 1] = g[0 : i]
        else:
            d[LINES - 1] = g
    
    def add_image(self, b, s, bb, cols, rows):
        """ Add image to the button
        
        :param b: button
        :param s: button state
        :param bb: bounding box
        :param cols: columns
        :param rows: rows
        """
        w = int(bb.w / cols)
        h = int(bb.h / rows)    
        try:
            url = b[IMG_URL]
            s.url = url
        except:
            pass
        
        img = self.util.load_mono_svg_icon("audiobooks", self.util.COLOR_MAIN, bb, 0.2)
        
        if img:  
            s.show_img = True
            s.scaled = True
            s.icon_base = (url, img)
            s.icon_base_scaled = img[1]
