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

import logging
import discogs_client

class DiscogsUtil(object):
    """ Discogs.com utility class """
    
    def __init__(self):
        """ Initializer. Create Discogs Client """
        
        self.peppy_player_user_agent = "PeppyPlayer +https://github.com/project-owner/Peppy"
        self.peppy_player_token = "RtZmsbvvoXVQxBwXtYDkbNIOXWkeGILJeyriGmDL"
        
        self.client = discogs_client.Client(self.peppy_player_user_agent, user_token=self.peppy_player_token)
        
    def search(self, query):
        """ Search through Discogs database
        
        :param query: search query string
        
        :return: search results
        """
        result = None
        
        try:
            result = self.client.search(query)
        except Exception as e:
            logging.error(str(e))
            return None
        
        if result == None or result.pages == 0:
            return None
        
        return result
        
    def get_release_id(self, query):
        """ Get release ID
        
        :param query: search query
        
        :return: tuple where first element is 'm' for master, 'r' for release, 
                second element is ID
        """
        result = self.search(query)
        
        if len(result.page(1)) == 0:
            return None
        
        record = result.page(1)[0]
        
        if type(record) is discogs_client.Master:
            return ("m", str(record.id))
        elif type(record) is discogs_client.Release:
            return ("r", str(record.id))
    
    def get_album_art_url(self, query):
        """ Get album art URL
        
        :param query: search query
        
        :return: album art URL
        """
        if query == None:
            return None
        
        record = self.get_release_id(query)
        
        if record == None:
            return None
        
        if record[0] == "m":
            release = self.client.master(record[1])
        else:
            release = self.client.release(record[1])
        
        if release == None:
            return None
        
        images = release.images[0]
        
        if images == None:
            return None
        
        url = images["uri"]
        logging.debug(url)
        
        return url
    