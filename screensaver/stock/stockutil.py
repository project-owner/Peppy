# Copyright 2022-2024 Peppy Player peppy.player@gmail.com
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

import threading

from yahooquery import Ticker # yahooquery-2.3.7
from ui.card.card import HEADER_FOOTER_BGR, LABEL, DETAIL_VALUE, SCREEN_BGR, ICON_LABEL, SHADOW, UNIT, DETAILS, \
    DETAIL_LABEL, TREND_UP_COLOR, TREND_DOWN_COLOR, VALUE, COLOR_THEME, TREND, TREND_UP, BLACK, TREND_DOWN, \
    CHANGE_VALUE, CHANGE_PERCENT
from util.config import LABELS
from itertools import cycle

class StockUtil(object):
    """ Stock utility class """

    lock = threading.RLock()

    def __init__(self, util, tickers):
        """ Initializer 
        
        :param util: utility object
        :param tickers: list of tickers
        """
        self.util = util
        self.config = util.config
        self.tickers = tickers
        self.thread_flags = {}
        for t in self.tickers:
            self.thread_flags[t] = False    

        original_theme = {
            SCREEN_BGR: (0, 0, 0, 0),
            HEADER_FOOTER_BGR: (20, 90, 100, 100),
            LABEL: (160, 190, 210),
            VALUE: (255, 190, 120),
            SHADOW: BLACK,
            DETAIL_LABEL: (160, 190, 210),
            DETAIL_VALUE: (255, 190, 120),
            TREND_UP_COLOR: (80, 210, 140),
            TREND_DOWN_COLOR: (230, 100, 180)
        }
        pink_theme = {
            SCREEN_BGR: (0, 0, 0, 0),
            HEADER_FOOTER_BGR: (50, 20, 50, 100),
            LABEL: (210, 180, 210),
            VALUE:  (210, 180, 210),
            SHADOW: BLACK,
            DETAIL_LABEL: (170, 140, 170),
            DETAIL_VALUE:  (210, 180, 210),
            TREND_UP_COLOR: (80, 210, 140),
            TREND_DOWN_COLOR: (230, 100, 180)
        }
        blue_theme = {
            SCREEN_BGR: (0, 0, 0, 0),
            HEADER_FOOTER_BGR: (20, 20, 60, 100),
            LABEL: (110, 150, 190),
            VALUE: (140, 180, 220),
            SHADOW: BLACK,
            DETAIL_LABEL: (110, 150, 190),
            DETAIL_VALUE: (140, 180, 220),
            TREND_UP_COLOR: (80, 210, 140),
            TREND_DOWN_COLOR: (230, 100, 180)
        }
        orange_theme = {
            SCREEN_BGR: (0, 0, 0, 0),
            HEADER_FOOTER_BGR: (80, 20, 0, 100),
            LABEL: (220, 160, 120),
            VALUE: (255, 180, 160),
            SHADOW: BLACK,
            DETAIL_LABEL: (220, 160, 120),
            DETAIL_VALUE: (255, 180, 160),
            TREND_UP_COLOR: (80, 210, 140),
            TREND_DOWN_COLOR: (230, 100, 180)
        }

        self.color_theme = [original_theme, pink_theme, blue_theme, orange_theme]
        self.color_theme_indexes = cycle(range(len(self.color_theme)))

    def get_color_theme(self):
        """ Get next color theme
        
        :return: color theme dictionary
        """
        i = next(self.color_theme_indexes)
        return self.color_theme[i]

    def get_formatted_value(self, value):
        """ Get formatted value string
        
        :param value: value to format

        :return: formatted value
        """
        return f"{value:5.2f}"

    def get_stock_info(self, ticker):
        """ Start thread to get stock information
        
        :param ticker: stock ticker
        """
        info = None
        try:
            info = Ticker(ticker).price[ticker]
        except:
            pass

        if info == None:
            return
        
        details = []
        details.append((self.config[LABELS]["open"], self.get_formatted_value(info["regularMarketOpen"]), ""))
        details.append((self.config[LABELS]["close"], self.get_formatted_value(info["regularMarketPreviousClose"]), ""))
        details.append((self.config[LABELS]["high"], self.get_formatted_value(info["regularMarketDayHigh"]), ""))
        details.append((self.config[LABELS]["low"], self.get_formatted_value(info["regularMarketDayLow"]), ""))

        current = None
        try:
            current = info["currentPrice"]
        except:
            current = info["regularMarketPrice"]

        if current == None:
            current = 0.0

        old_price = info["regularMarketPreviousClose"]
        change = old_price - current
        change_value = self.get_formatted_value(abs(change))
        change_percent = self.get_formatted_value((abs(change) * 100) / old_price)

        if change < 0:
            trend = TREND_UP
        elif change > 0:
            trend = TREND_DOWN
        else:
            trend = None

        return {
            LABEL: info["shortName"],
            ICON_LABEL: info["symbol"],
            COLOR_THEME: self.get_color_theme(),
            VALUE: current,
            UNIT: info["currency"],
            DETAILS: details,
            TREND: trend,
            CHANGE_VALUE: change_value,
            CHANGE_PERCENT: change_percent
        }
