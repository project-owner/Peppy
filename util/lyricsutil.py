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

import json
from urllib import request
from urllib.parse import quote

class LyricsUtil(object):
    """ Lyrics utility class """
    
    def __init__(self, t, lines, line_length):
        """ Initializer
        
        :param t: token
        :param lines: number of lyrics lines on screen
        :param line_length: maximum line length
        """
        self.key = t
        self.lines = lines
        self.line_length = line_length
        self.musixmatch_url_template = "https://api.musixmatch.com/ws/1.1/matcher.lyrics.get?format=jsonp&callback=callback&q_artist={artist}&q_track={track}&apikey={key}"

    def get_lyrics(self, query_string):
        """ Get lyrics
        First try lyrics wikia if not found there try musixmatch
        
        :param query_string: query string which should include artist and song names
        
        :return: lyrics text on None if lyrics not found
        """
        lyrics = self.get_musixmatch_lyrics(query_string)
            
        return lyrics

    def get_musixmatch_lyrics(self, query_string):
        """ Get lyrics from musixmatch
        
        :param query_string: query string
        
        :return: lyrics text
        """
        lyrics = None
        tokens = query_string.split("-")
        if tokens == None or len(tokens) == 1:
            return None

        artist = tokens[0].strip()
        track = tokens[1].strip()

        url = self.musixmatch_url_template.format(artist=quote(artist), track=quote(track), key=self.key)
        response = self.get_response(url)
        
        if response == None:
            return None
        
        j = json.loads(response[9:-2])
        
        status_code = j["message"]["header"]["status_code"]
        
        if status_code == 200:
            lyrics = j["message"]["body"]["lyrics"]["lyrics_body"]
            if lyrics != None and len(lyrics.strip()) == 0:
                lyrics = None
        elif status_code == 401:
            print("limit reached")
        
        return lyrics
    
    def get_response(self, url):
        """ Get HTTP response for provided URL
        
        :param url: the query URL
        
        :return: HTTP response in the form of JSON object
        """
        req = request.Request(url)
        site = None
        
        try:
            site = request.urlopen(req)
        except:
            pass
            
        if site == None:
            return None
               
        charset = site.info().get_content_charset()
        html = site.read()
        response = None
        try:
            response = html.decode(charset)
        except:
            pass
        
        return response
    
    def format_lyrics(self, lyrics):
        """ Format lyrics text using provided number of lines and maximum line length
        
        :param lyrics:
        
        :return: list of pages with formatted lyrics text
        """
        page = []
        pages = []
        n = 0
        lines = lyrics.splitlines()
        total_lines = len(lines)
        
        for i, line in enumerate(lines):
            if not (line.startswith("(") and line.endswith(")") and len(line) > 5 and line[2].isdigit()):
                if line.startswith("*******") and line.endswith("*******"):
                    line = line[8 : -8]
                if len(line) > self.line_length:
                    line = line[0 : self.line_length] + "..."
                page.append(line)
                
            n = i + 1
            if n == total_lines:
                if not(len(page) == 1 and len(page[0].strip()) == 0):
                    pages.append(page)
                break
            else:
                if n % self.lines == 0:
                    pages.append(page)
                    page = []
        return pages
