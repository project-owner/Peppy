# Copyright 2022-2023 Peppy Player peppy.player@gmail.com
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

import requests
from bs4 import BeautifulSoup

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

BASE_URL = "https://www.horoscope.com/us/horoscopes/general/horoscope-general-daily-today.aspx?sign="

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

    def get_daily_horoscope(self, sign_index):
        """ Get daily horoscope from Aztro service
        
        :param sign: zodiac sign

        :return: horoscope dictionary with strings translated for the current language
        """
        today = date.today()
        lang = self.get_current_language_code()
        today_formatted = today.strftime("%D")
        key = str(sign_index) + lang + today_formatted
        h = {}
        txt = ""

        try:
            h = self.cache[key]
            return h
        except:
            pass

        try:
            url = BASE_URL + str(sign_index + 1)
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')
            c = soup.find("p")
            txt = c.text.strip()
            txt = txt[txt.find("-") + 1:].strip()
        except:
            return None

        lang = self.get_current_language_code()

        if lang == "en":
            h["description"] = txt
        else:
            translated = self.util.translate(txt, "en", lang)
            if translated[len(translated) - 1] != "." and translated[len(translated) - 1] != "!" and translated[len(translated) - 1] != "?":
                translated = translated + "."
            h["description"] = translated

        h["current_date"] = today_formatted
        self.cache[key] = h

        return h
