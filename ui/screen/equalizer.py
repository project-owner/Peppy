# Copyright 2018-2021 Peppy Player peppy.player@gmail.com
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

from ui.screen.screen import Screen, PERCENT_TOP_HEIGHT
from ui.navigator.equalizer import EqualizerNavigator
from ui.menu.equalizermenu import EqualizerMenu
from util.config import EQUALIZER, CURRENT

class EqualizerScreen(Screen):
    """ Equalizer Screen """
    
    def __init__(self, util, listeners, voice_assistant):
        """ Initializer
        
        :param util: utility object
        :param listener: screen menu event listener
        """
        self.util = util
        self.config = util.config
        self.current_values = util.get_equalizer()
            
        Screen.__init__(self, util, EQUALIZER, PERCENT_TOP_HEIGHT, voice_assistant)
        
        self.equalizer_menu = EqualizerMenu(util, self.handle_slider_event, self.layout.CENTER)
        self.equalizer_menu.set_parent_screen(self)
        self.equalizer_menu.set_bands(self.current_values)
        self.add_menu(self.equalizer_menu)
        
        self.equalizer_navigator = EqualizerNavigator(util, self.layout.BOTTOM, listeners, self.handle_presets)
        self.add_navigator(self.equalizer_navigator)

        self.link_borders(first_index=0, last_index=9)
        self.equalizer_navigator.buttons[0].set_selected(True)
        self.navigator_selected = True

    def handle_presets(self, state):
        """ Handle presets

        :param state: state object
        """
        self.current_values = self.util.preset_equalizer(state.name)
        self.equalizer_menu.set_bands(self.current_values)

    def refresh_equalizer(self):
        """ Refresh UI """

        self.current_values = self.util.get_equalizer()
        self.equalizer_menu.set_bands(self.current_values)

    def handle_slider_event(self, state):
        """ Handle slider event

        :param state: state object
        """
        if self.navigator_selected:
            for b in self.equalizer_navigator.buttons:
                b.set_selected(False)
                b.clean_draw_update()
            self.navigator_selected = False

        band = int(state.event_origin.name[-1])
        v = state.position
        self.current_values[band] = v
        self.config[CURRENT][EQUALIZER] = self.current_values.copy()       
        self.util.set_equalizer_band_value(band + 1, v)
        
        s = self.equalizer_menu.sliders[band]
        s.set_value(str(v))

    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        Screen.add_screen_observers(self, update_observer, redraw_observer)
        
        self.equalizer_menu.add_menu_observers(update_observer, redraw_observer)
        self.equalizer_navigator.add_observers(update_observer, redraw_observer)
        