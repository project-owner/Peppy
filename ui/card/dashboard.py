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

from ui.component import Component
from ui.container import Container
from ui.card.card import LABEL, ICON_LABEL, Card, CENTER, COLOR_THEME, VALUE, UNIT, TREND, SCREEN_BGR
from ui.layout.gridlayout import GridLayout

DASHBOARD = "dashboard"
VALUE_HEIGHT = 40

class Dashboard(Container):
    """ The card dashboard """
    
    def __init__(self, util, rows, columns, content, lcd=True):
        """ Initializer
        
        :param util: utility object
        :param rows: the rows
        :param columns: the columns
        :param content: the card content
        :param lcd: True - use LCD font
        """
        self.name = DASHBOARD
        self.util = util
        self.rect = util.screen_rect
        self.config = util.config
        self.rows = rows
        self.columns = columns
        self.cards_num = self.rows * self.columns
        self.dashboard_content = content
        self.lcd = lcd
        self.cards = []
        self.draw_dashboard()
        self.set_visible(False)

    def set_values(self, values, bgr_image=None):
        """ Set card dashboard data
        
        :param values: dashboard values
        :param bgr_image: the background image
        """
        if bgr_image != None:
            self.components[0].content = bgr_image

        for i, v in enumerate(values):
            self.cards[i].bgr = v[COLOR_THEME][SCREEN_BGR]
            self.cards[i].set_value(v[LABEL], v[ICON_LABEL], v[COLOR_THEME], v[VALUE], v[UNIT], trend=v[TREND])

    def draw_dashboard(self):
        """ Draw dashboard  """
        
        Container.__init__(self, self.util, self.rect, (0, 0, 0))
        
        c = Component(self.util)
        c.name = DASHBOARD + ".bgr"
        c.bounding_box = self.rect
        self.add_component(c)

        layout = GridLayout(self.util.screen_rect)
        layout.set_pixel_constraints(self.rows, self.columns)

        for c in self.dashboard_content:
            cache_name = DASHBOARD + c[0]
            bb = layout.get_next_constraints()
            card_name = c[0]
            icon_name = c[1]
            padding = c[2]
            border = False
            try:
                border = c[3]
            except:
                pass
            card = self.add_card(cache_name, bb, card_name, icon_name, padding, border)
            self.cards.append(card)

    def add_card(self, cache_name, bb, name, icon_name, padding, border):
        """ Add card to the dashboard
        
        :param cache_name: icon cache name
        :param bb: bounding box
        :param name: card name
        :param icon_name: icon name
        :param padding: padding
        :param border: border

        :return: the card
        """
        card = Card(cache_name, bb, name, self.util, icon_name=icon_name, lcd=self.lcd, show_details=False, 
            label_alignment=CENTER, padding=padding, show_border=border, value_height=VALUE_HEIGHT)
        card.set_visible(False)
        self.add_component(card)

        return card
    