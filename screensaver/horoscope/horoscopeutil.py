# Copyright 2022 Peppy Player peppy.player@gmail.com
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

import pyaztro
import logging
import requests

from datetime import date
from ui.card.card import HEADER_FOOTER_BGR, LABEL, DETAIL_VALUE, SCREEN_BGR, ICON, DETAIL_LABEL, VALUE, ICON_2
from util.config import CURRENT, LANGUAGE

BLUE_THEME = {
    SCREEN_BGR: (0, 0, 0),
    HEADER_FOOTER_BGR: (0, 47, 117, 100),
    LABEL: (180, 210, 255),
    ICON: (130, 150, 200),
    ICON_2: (100, 120, 180),
    VALUE: (180, 210, 255),
    DETAIL_LABEL: (140, 150, 194),
    DETAIL_VALUE: (180, 210, 255)
}

ORANGE_THEME = {
    SCREEN_BGR: (0, 0, 0),
    HEADER_FOOTER_BGR: (80, 50, 30, 110),
    LABEL: (255, 150, 70),
    ICON: (210, 110, 30),
    ICON_2: (190, 90, 10),
    VALUE: (255, 150, 70),
    DETAIL_LABEL: (200, 105, 45),
    DETAIL_VALUE: (255, 130, 60)
}

GREEN_THEME = {
    SCREEN_BGR: (0, 0, 0),
    HEADER_FOOTER_BGR: (30, 60, 50, 130),
    LABEL: (180, 240, 220),
    ICON: (130, 190, 180),
    ICON_2: (110, 170, 160),
    VALUE: (180, 255, 220),
    DETAIL_LABEL: (130, 190, 170),
    DETAIL_VALUE: (180, 255, 220)
}

PINK_THEME = {
    SCREEN_BGR: (0, 0, 0),
    HEADER_FOOTER_BGR: (60, 30, 50, 130),
    LABEL: (240, 180, 220),
    ICON: (190, 130, 180),
    ICON_2: (170, 110, 160),
    VALUE: (240, 180, 220),
    DETAIL_LABEL: (190, 130, 170),
    DETAIL_VALUE: (240, 180, 220)
}

SILVER_THEME = {
    SCREEN_BGR: (0, 0, 0),
    HEADER_FOOTER_BGR: (40, 40, 50, 120),
    LABEL: (200, 200, 210),
    ICON: (160, 160, 170),
    ICON_2: (140, 140, 150),
    VALUE: (200, 200, 210),
    DETAIL_LABEL: (150, 150, 160),
    DETAIL_VALUE: (200, 200, 210)
}

GOLD_THEME = {
    SCREEN_BGR: (0, 0, 0),
    HEADER_FOOTER_BGR: (60, 40, 20, 130),
    LABEL: (250, 180, 50),
    ICON: (215, 145, 10),
    ICON_2: (195, 125, 5),
    VALUE: (250, 180, 50),
    DETAIL_LABEL: (200, 130, 0),
    DETAIL_VALUE: (250, 180, 50)
}

class HoroscopeUtil(object):
    """ Horoscope utility class """

    def __init__(self, util, signs=None):
        """ Initializer 
        
        :param util: utility object
        :param signs: zodiac signs
        """
        self.util = util
        self.config = util.config
        self.signs = signs
        self.cache = {}

    def get_current_language_code(self):
        """ Get the current language code
        
        :return: two symbols language code
        """
        code = self.util.get_weather_language_code(self.util.config[CURRENT][LANGUAGE])
        if code == "cz":
            code = "cs"
        return code

    def get_time(self, t):
        """ Get time in military format
        
        :param t: time received from aztro service

        :return: time in military format
        """
        m = t.replace("am", ":00")
        if "pm" in m:
            n = t.replace("pm", "")
            t = int(n) + 12
            m = str(t) + ":00"

        return m

    def get_daily_horoscope(self, sign):
        """ Get daily horoscope from Aztro service
        
        :param sign: zodiac sign

        :return: horoscope dictionary with strings translated for the current language
        """
        today = date.today()
        lang = self.get_current_language_code()
        today_formatted = today.strftime("%D")
        key = sign + lang + today_formatted

        try:
            h = self.cache[key]
            return h
        except:
            pass

        try:
            h = pyaztro.Aztro(sign=sign)
        except:
            return None
            
        h.description = self.translate(h.description)
        h.description = self.cleanup_string(h.description)
        
        h.color = self.translate(h.color)
        h.color = self.cleanup_string(h.color)

        h.mood = self.translate(h.mood)
        h.mood = self.cleanup_string(h.mood)

        h.lucky_time = self.get_time(h.lucky_time)

        self.cache[key] = h

        return h

    def cleanup_string(self, s):
        """ Remove special characters from the strings

        :param s: string to process
        
        :return: clean string
        """
        r = s.replace("»", "")

        first = r[0]
        if first == "'" or first == "«" or first == "„" or first == "\"":
            r = r[1:]

        last = r[len(r) - 1]
        if last == "'" or last == "“" or last == "\"":
            r = r[0:len(r) - 1]

        return r

    def translate(self, text):
        """ Translate text using Google translate API

        :param text: text to translate

        :return: translated text
        """
        if text == None:
            return None

        lang = self.get_current_language_code()
        if lang == "en":
            return text

        url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en" + "&tl=" + lang + "&dt=t&q='" + text + "'"
        try:
            content = requests.get(url, timeout=(2, 2))
        except Exception as e:
            logging.debug(e)

        if content == None:
            return None

        j = content.json()
        top = j[0]
        s = ""
        for n in range(len(top)):
            s += top[n][0]

        return s
