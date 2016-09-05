# Copyright 2016 Peppy Player peppy.player@gmail.com
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

""" Playlist module """

from util.keys import CURRENT, STATION

class Playlist(object):
    """ Keep the info about current playlist, current station etc """
    
    def __init__(self, language, genre, util, items_per_line=3):
        """ Initializer
        
        :param language: the language
        :param genre: the genre
        :param util: utility object
        :param items_per_line: items per line in station menu
        """
        self.genre = genre
        self.config = util.config
        self.items_per_line = items_per_line
        self.stations_per_page = items_per_line * items_per_line
        self.items = util.load_stations(language, genre, self.stations_per_page)
        self.current_page_index = 0
        self.current_station_index = 0
        self.playing_station_page_index = 0
        self.current_station_index_in_page = 0 
        self.current_station = None
        self.length = len(self.items)
        self.total_pages = 0
        self.grid_size = 0
        self.start_listeners = list()        
        self.grid_size = 3
        self.total_pages = int(self.length/self.stations_per_page)
        if(self.length % self.stations_per_page):
            self.total_pages += 1
            
    def set_current_station(self, index):
        """ Set the current station by its index
        
        :param index: the station index to be set 
        """        
        if index > self.length - 1:
            index = self.length - 1
            
        self.config[CURRENT][STATION] = index
        self.current_station_index = index
        self.current_station_index_in_page = index % self.stations_per_page
        self.current_page_index = int(index/self.stations_per_page)
        self.playing_station_page_index = self.current_page_index
        page = self.get_current_page()
        index_in_page = index % self.stations_per_page
        self.current_station = page[index_in_page]    
    
    def next_station(self):
        """ Move to the next station in the list """
                
        self.current_station_index += 1
        self.current_station_index_in_page = self.current_station_index
        self.playing_station_page_index = int(self.current_station_index/self.stations_per_page)        
    
    def get_current_page(self):
        """ Get the current page for the current station
         
        :return: list of the stations representing the page where the current station belongs to
        """        
        start = self.current_page_index * self.stations_per_page
        stop = start + self.stations_per_page
        if len(self.items) > stop:
            return self.items[start:stop]            
        else: 
            return self.items[start:]
    
    def next_page(self):
        """ Move to the next page of stations. Move to the first page if the current page is the last one.
        
        :return: list of the stations representing the next page
        """
        if self.current_page_index + 1 == self.total_pages:
            self.current_page_index = 0
        else:
            self.current_page_index += 1
        return self.get_current_page()
    
    def previous_page(self):
        """ Move to the previous page of stations. Move to the last page if the current page is the first one.
        
        :return: list of stations representing the previous page
        """        
        if self.current_page_index == 0:
            self.current_page_index = self.total_pages - 1
        else:
            self.current_page_index -= 1
        return self.get_current_page()    
        
