# Copyright 2021-2022 Peppy Player peppy.player@gmail.com
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

from pygame import Rect
from ui.state import State
from ui.player.player import PlayerScreen
from util.keys import KEY_FAVORITES, kbd_keys, KEY_SELECT, KEY_GENRES, GENRE, KEY_RADIO_BROWSER, KEY_HOME
from util.favoritesutil import FavoritesUtil
from util.util import V_ALIGN_BOTTOM
from ui.button.button import Button
from util.config import CURRENT, MODE, RADIO, SCREEN_INFO, WIDTH, HEIGHT, LYRICS, LANGUAGE, CURRENT_STATIONS, \
    STATIONS, GENERATED_IMAGE, PLAYER_SETTINGS, VOLUME, BACKGROUND, BGR_TYPE, USE_ALBUM_ART
from util.imageutil import DEFAULT_CD_IMAGE

PERCENT_GENRE_IMAGE_AREA = 33.0

class RadioPlayerScreen(PlayerScreen):
    """ The Radio Player Screen """
    
    def __init__(self, util, listeners, voice_assistant=None, volume_control=None):
        """ Initializer
        
        :param util: utility object
        :param listeners: screen event listeners
        :param voice_assistant: the voice assistant
        :param volume_control: the volume control
        """
        self.util = util
        self.config = util.config
        self.bounding_box = util.screen_rect
        self.favorites_util = FavoritesUtil(self.util)
        self.image_util = util.image_util
        show_arrow_labels = True
        self.show_order = False
        self.show_info = True
        self.show_time_control = False
        self.listeners = listeners
        self.change_logo_listeners = []
        self.favorites_util.set_favorites_in_config()

        PlayerScreen.__init__(self, util, listeners, "station_screen_title", show_arrow_labels, self.show_order, self.show_info, \
            self.show_time_control, voice_assistant, volume_control)

        self.volume_visible = True
        self.set_custom_button()    
        self.set_center_button()
        self.favorites_util.mark_favorites({"b": self.center_button})
        self.add_component(self.info_popup)
        self.set_listeners(listeners)
        self.shutdown_button.release_listeners.insert(0, self.favorites_util.save_favorites)

        if self.center_button == None:
            self.custom_button.set_selected(True)
            self.current_button = self.custom_button
            self.custom_button.clean_draw_update()

    def set_custom_button(self):
        """ Set the custom buttom """

        self.genres = self.util.get_genres()
        self.genres[KEY_FAVORITES] = self.favorites_util.get_favorites_button_state(self.custom_button_layout)
        self.current_genre = self.util.get_current_genre()
        self.current_genre.bounding_box = self.custom_button_layout
        self.custom_button = self.get_custom_button(self.current_genre, self.listeners[KEY_GENRES])
        self.right_panel.add_component(self.custom_button)

    def stop(self):
        """ Stop playback """

        if self.center_button:
            self.center_button.components[1] = None
        self.set_title("")
        if hasattr(self, "stop_player"):
            self.stop_player()

    def set_center_button(self):
        """ Set the center button """

        if self.current_genre.name == KEY_FAVORITES:
            self.playlist = self.favorites_util.get_favorites_playlist()
        else:
            self.playlist = self.util.get_radio_player_playlist(self.current_genre.name)

        if self.playlist == None or len(self.playlist) == 0:
            self.clean_center_button()
            self.update_arrow_button_labels()
            self.set_title("")
            self.stop()
            return

        self.current_index = self.util.get_current_radio_station_index()

        if self.current_index >= len(self.playlist):
            self.current_index = len(self.playlist) - 1    
        
        self.current_state = self.playlist[self.current_index]
        self.current_state.bounding_box = self.layout.CENTER

        if not hasattr(self.current_state, "icon_base"):
            self.util.add_icon(self.current_state)
        
        if self.center_button == None:
            self.center_button = self.get_center_button(self.current_state)
            self.current_button = self.center_button
            self.add_component(self.center_button)
        else:
            button = self.get_center_button(self.current_state)
            self.center_button.state = button.state
            self.center_button.components = button.components
        
        self.center_button.selected = True
        self.center_button.add_release_listener(self.handle_favorite)
        self.center_button.add_release_listener(self.listeners[KEY_RADIO_BROWSER])
        
        self.center_button.clean_draw_update()
        img = self.center_button.components[1]
        self.logo_button_content = (img.image_filename, img.content, img.content_x, img.content_y)

        self.set_background()

        self.update_arrow_button_labels()
        self.set_title(self.current_state)
        self.link_borders()

    def update_center_button(self):
        """ Set album art background """

        super().update_center_button()
        self.set_background()

    def set_background(self):
        """ Set album art background """

        if self.config[BACKGROUND][BGR_TYPE] != USE_ALBUM_ART:
            return

        try:
            img = self.center_button.state.full_screen_image
        except:
            img = self.center_button.components[1].content

        if img == None:
            return

        i = self.image_util.get_album_art_bgr(img)
        if i != self.content:
            self.content = i
            self.clean_draw_update()

    def get_custom_button(self, genre_button_state, listener):
        """ Get the custom button

        :param genre_button_state: the genre button state
        :param listener: the button listener
        """
        self.util.add_icons(genre_button_state)
        bb = genre_button_state.bounding_box
        button = self.factory.get_genre_button(bb, genre_button_state, PERCENT_GENRE_IMAGE_AREA)
        button.add_release_listener(listener)
        return button

    def get_center_button(self, s):
        """ Create the center button

        :param s: button state

        :return: station logo button
        """
        bb = Rect(self.layout.CENTER.x + 1, self.layout.CENTER.y + 1, self.layout.CENTER.w - 2, self.layout.CENTER.h - 2)
        if not hasattr(s, "icon_base"):
            self.util.add_icon(s)

        state = State()
        state.icon_base = s.icon_base
        self.factory.set_state_scaled_icons(s, bb)
        state.index = s.index
        state.genre = s.genre
        state.scaled = getattr(s, "scaled", False)
        state.icon_base_scaled = s.icon_base_scaled
        state.name = "station." + s.name
        state.l_name = s.l_name
        state.url = s.url
        state.keyboard_key = kbd_keys[KEY_SELECT]
        state.bounding_box = bb
        state.img_x = bb.x
        state.img_y = bb.y
        state.auto_update = False
        state.show_bgr = True
        state.show_img = True
        state.logo_image_path = s.image_path
        state.image_align_v = V_ALIGN_BOTTOM
        state.comparator_item = self.current_state.comparator_item
        button = Button(self.util, state)

        img = button.components[1]
        self.logo_button_content = (img.image_filename, img.content, img.content_x, img.content_y)

        return button

    def add_change_logo_listener(self, listener):
        """ Add change logo listener
        
        :param listener: event listener
        """
        if listener not in self.change_logo_listeners:
            self.change_logo_listeners.append(listener)     

    def notify_change_logo_listeners(self, state):
        """ Notify change logo event listeners
        
        :param state: state object with new image in 'icon_base'
        """
        self.set_background()
        for listener in self.change_logo_listeners:
            listener(state)

    def change_genre(self, state=None):
        """ Change genre

        :para, state: the button state with new genre
        """
        self.genres = self.util.get_genres()
        self.genres[KEY_FAVORITES] = self.favorites_util.get_favorites_button_state(self.custom_button_layout)
        self.current_genre = self.genres[state.name]
        self.current_genre.bounding_box = self.custom_button_layout
        button = self.get_custom_button(self.current_genre, self.listeners[KEY_GENRES])
        self.custom_button.state = button.state
        self.custom_button.set_selected(True)
        self.set_center_button()

    def set_current(self, state=None):
        """ Set the current screen state

        :param state: the state object
        """
        if state == None:
            self.clean_center_button()
            self.update_arrow_button_labels()
            self.set_title("")
            self.stop_player()
            self.current_button = self.home_button
            self.home_button.clean_draw_update()
            return

        if not hasattr(state, "source"):
            return

        config_volume_level = int(self.config[PLAYER_SETTINGS][VOLUME])
        if self.volume.get_position() != config_volume_level:
            self.volume.set_position(config_volume_level)
            self.volume.update_position()

        src = getattr(state, "source", None)

        if src == KEY_HOME:
            if not hasattr(self, "current_button"): # after changing language
                self.home_button.set_selected(True)
                self.home_button.clean_draw_update()
                self.current_button = self.home_button
            if state.change_mode:
                self.start_playback()
        if src == GENRE:
            if state.comparator_item != self.current_genre.comparator_item:
                self.change_genre(state)
                if self.current_genre.name != KEY_FAVORITES:
                    self.favorites_util.mark_favorites({"b": self.center_button})
                self.play()
            self.center_button.set_selected(False)
        elif src == KEY_FAVORITES:
            current_language = self.config[CURRENT][LANGUAGE]
            key = STATIONS + "." + current_language
            self.config[key][CURRENT_STATIONS] = KEY_FAVORITES

            self.change_genre(state)
            self.center_button.set_selected(False)

            if self.favorites_util.get_current_favorites_station() != None:
                self.play()
        elif src == KEY_RADIO_BROWSER:
            if self.center_button and self.center_button.state.url != state.url:
                self.start_playback()

            favorites, _ = self.favorites_util.get_favorites_from_config()

            if self.center_button and len(self.center_button.components) == 4:
                if not self.favorites_util.is_favorite(favorites, self.center_button.state): # remove star icon if not favorite anymore
                    del self.center_button.components[3]
            elif self.center_button and len(self.center_button.components) == 3:
                if self.current_genre.name == KEY_FAVORITES:
                    if not self.favorites_util.is_favorite(favorites, self.center_button.state):
                        self.start_playback()
                else:
                    if self.favorites_util.is_favorite(favorites, self.center_button.state): # add star icon if favorite
                        self.favorites_util.mark_favorites({"b": self.center_button})

    def start_playback(self):
        """ Start playback """

        self.set_center_button()
        self.set_title(self.current_state)
        self.play()

    def set_current_item(self, index):
        """ Specific for each player. Sets config item """

        self.util.set_radio_station_index(index)
    
    def clean_center_button(self):
        """ Clean the center button """

        if self.center_button == None or self.center_button.components[1] == None:
            return
        self.center_button.components[1].content = None
        self.center_button.components[1].image_filename= None
        self.center_button.state.icon_base = None
        self.center_button.state.icon_base_scaled = None
        self.center_button.state.comparator_item = None
        if len(self.center_button.components) == 4:
            del self.center_button.components[3]
        if self.visible:
            self.center_button.clean_draw_update()    

    def show_logo(self):
        """ Show station logo image """
        
        self.center_button.components[1].image_filename = self.logo_button_content[0]
        self.center_button.components[1].content = self.logo_button_content[1]
        self.center_button.components[1].content_x = self.logo_button_content[2]
        self.center_button.components[1].content_y = self.logo_button_content[3]
        self.center_button.state.icon_base = (self.logo_button_content[0], self.logo_button_content[1])

        self.center_button.state.comparator_item = self.current_state.comparator_item

        if self.visible:
            self.center_button.clean_draw_update()

        self.notify_change_logo_listeners(self.center_button.state)
        self.redraw_observer()

    def show_album_art(self, status):
        """ Show album art from discogs.com
        
        :param status: object having artist & track names
        """
        self.current_album_image = None
        
        if self.config[CURRENT][MODE] != RADIO or status == None:
            return
        
        album = status['current_title']
        
        if len(album) < 10 or "jingle" in album.lower(): 
            self.show_logo()
            self.redraw_observer()         
            return
        
        r = Rect(0, 0, self.config[SCREEN_INFO][WIDTH], self.config[SCREEN_INFO][HEIGHT])
        full_screen_image = self.image_util.get_cd_album_art(album, r)
        
        bb = self.center_button.bounding_box
        scale_ratio = self.image_util.get_scale_ratio((bb.w, bb.h), full_screen_image[1])
        album_art = (full_screen_image[0], self.image_util.scale_image(full_screen_image, scale_ratio))
        
        if album_art and album_art[0] != None and album_art[0].endswith(DEFAULT_CD_IMAGE) or album_art[1] == None:
            self.show_logo()
            self.redraw_observer()
            return
        
        size = album_art[1].get_size()

        if self.center_button.components[1] == None:
            button = self.get_center_button(self.current_state)
            self.center_button.state = button.state
            self.center_button.components = button.components

        name = GENERATED_IMAGE + "album.art"
        self.center_button.components[1].image_filename = name
        self.center_button.components[1].content = album_art[1]
        self.center_button.components[1].content_x = int(bb.x + (bb.w - size[0]) / 2)
        self.center_button.components[1].content_y = int(bb.y + (bb.h - size[1]) / 2)
        album_art = (name, album_art[1])
        self.center_button.state.icon_base = self.center_button.state.icon_base_scaled = album_art
        self.center_button.state.comparator_item = self.current_state.comparator_item

        if full_screen_image:
            self.center_button.state.full_screen_image = full_screen_image[1]
        
        self.center_button.state.album = album
        if self.visible:    
            self.center_button.clean_draw_update()
        
        self.notify_change_logo_listeners(self.center_button.state)
        self.redraw_observer()

    def handle_info_popup_selection(self, state):
        """ Handle info menu selection

        :param state: button state
        """
        if state.name == LYRICS:
            a = None
            try:
                a = self.screen_title.text
            except:
                pass
            if a != None:
                s = State()
                s.album = a
                self.start_screensaver(state.name, s)
            else:
                self.start_screensaver(state.name)
        else:
            self.start_screensaver(state.name)
   
    def handle_favorite(self, state):
        """ Add/Remove station to/from the favorites
        
        :param state: button state
        """        
        if state == None or not getattr(state, "long_press", False):
            return
        
        favorites, lang_dict = self.favorites_util.get_favorites_from_config()
        
        if self.favorites_util.is_favorite(favorites, state):
            self.favorites_util.remove_favorite(favorites, state)
            if self.current_genre.name == KEY_FAVORITES:
                if len(self.playlist) > 0:
                    if state.index == 0:
                        self.current_index = 0
                    else:
                        self.current_index = state.index - 1
                    self.util.set_radio_station_index(self.current_index)
                    self.set_center_button()
                    self.play()
                else:
                    self.util.set_radio_station_index(None)
                    self.stop()
        else:
            if isinstance(state.icon_base, tuple):
                state.image_path = state.icon_base[0]
            self.favorites_util.add_favorite(favorites, state)
            if self.center_button and len(self.center_button.components) == 3:
                self.favorites_util.mark_favorites({"b": self.center_button})
