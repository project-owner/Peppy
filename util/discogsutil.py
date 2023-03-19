# Copyright 2018-2022 Peppy Player peppy.player@gmail.com
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
import requests

class DiscogsUtil(object):
    """ Discogs.com utility class """
    
    def __init__(self, t):
        """ Initializer. Create Discogs Client 
        
        :param t: token
        """
        self.peppy_player_user_agent = "PeppyPlayer +https://github.com/project-owner/Peppy"
        self.init_client(t)

    def init_client(self, token):
        """ Initialize Discogs Client 
        
        :param token: the API token
        """
        self.token = token
        self.client = discogs_client.Client(self.peppy_player_user_agent, user_token=token)

    def search(self, query):
        """ Search through Discogs database
        
        :param query: search query string
        
        :return: search results
        """
        result = None
        tokens = query.split("-")
        if tokens == None or len(tokens) == 1:
            return None

        a = tokens[0].strip()
        t = tokens[1].strip()

        try:
            result = self.client.search(query, type="master", artist=a, track=t)
            if result == None:
                return None
        except Exception as e:
            logging.error(str(e))
            self.init_client()
            return None
        
        return result
        
    def get_album_art_url(self, query, per_page=12):
        """ Get album art URL
        
        :param query: search query
        
        :return: album art URL
        """
        if query == None:
            return None
        
        result = self.search(query)
        if result == None: return None

        result._per_page = per_page
        url = result._url_for_page(1)
        
        headers = {
            'Accept-Encoding': 'gzip',
            'User-Agent': self.peppy_player_user_agent,
        }

        parameters = {
            'token': self.token    
        }
        
        url += "&token=" + self.token
        content = None
        tout = 6

        try:
            content = requests.get(url, headers=headers, params=parameters, timeout=(tout, tout))
        except:
            pass

        if content:
            j = content.json()
            results = j["results"]
            if len(results) == 0:
                return None
            else:
                r = results[0]
                return r["cover_image"]
        else:
            return None
