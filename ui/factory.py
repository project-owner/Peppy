# Copyright 2016-2018 Peppy Player peppy.player@gmail.com
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
from ui.button.button import Button
from ui.state import State
from ui.button.multistatebutton import MultiStateButton
from ui.button.togglebutton import ToggleButton
from ui.slider.slider import Slider
from ui.slider.timeslider import TimeSlider
from ui.slider.equalizerslider import EqualizerSlider
from ui.text.outputtext import OutputText
from ui.text.dynamictext import DynamicText
from ui.layout.buttonlayout import BOTTOM, CENTER, LEFT, RIGHT
from util.keys import kbd_keys, KEY_VOLUME_UP, KEY_VOLUME_DOWN, KEY_PLAY_PAUSE, KEY_MENU, \
    KEY_END, KEY_MUTE, KEY_SELECT, KEY_LEFT, KEY_RIGHT, KEY_PAGE_UP, KEY_PAGE_DOWN, KEY_SETUP, \
    TRACK_MENU, BOOK_MENU, HOME_NAVIGATOR
from util.util import IMAGE_SELECTED_SUFFIX, IMAGE_VOLUME, IMAGE_MUTE, V_ALIGN_CENTER, V_ALIGN_BOTTOM, \
    H_ALIGN_CENTER, IMAGE_TIME_KNOB, KEY_HOME, KEY_PLAYER 
from util.config import COLOR_DARK, COLOR_DARK_LIGHT, COLOR_MEDIUM, COLORS, COLOR_CONTRAST, COLOR_BRIGHT, \
    USAGE, USE_VOICE_ASSISTANT, COLOR_WEB_BGR, VOLUME, PLAYER_SETTINGS, MUTE, PAUSE, COLOR_MUTE
from util.fileutil import FOLDER_WITH_ICON
from websiteparser.siteparser import AUTHOR_URL, AUTHOR_NAME, AUTHOR_BOOKS
from websiteparser.audioknigi.constants import ABC_RU
from ui.button.multilinebutton import MultiLineButton
from ui.layout.gridlayout import GridLayout

class Factory(object):
    """ UI Factory class """
    
    def __init__(self, util):
        """ Initializer
        
        :param util: utility object
        """
        self.util = util
        self.config = util.config        
    
    def set_state_icons(self, state, selected=True):
        """ Load and set button icons
        
        :param state: the state object on which icons will be set
        """
        resizable = getattr(state, "resizable", True)
        state.icon_base = self.util.load_mono_svg_icon(state.name, self.util.COLOR_MAIN, state.bounding_box, state.image_size_percent)
        if selected:
            state.icon_selected = self.util.load_mono_svg_icon(state.name, self.util.COLOR_ON, state.bounding_box, state.image_size_percent)
            
    def set_state_scaled_icons(self, state, constr):
        """ Load and set scaled button icons
        
        :param state: the state object on which icons will be set
        :param constr: constraints used for scaling images
        """
        icon_base = getattr(state, "icon_base", None)
        icon_selected = getattr(state, "icon_selected", None)
        
        if icon_base:
            state.icon_base_scaled = self.util.scale_image(state.icon_base, (constr.width, constr.height))
        if icon_selected:
            state.icon_selected_scaled = self.util.scale_image(state.icon_selected, (constr.width, constr.height))
        state.scaled = True
    
    def create_image_button(self, name, action=None, keyboard_key=None, lirc_code=None, bounding_box=None, 
                            bgr=(0, 0, 0), x_margin_percent=None, resizable=True, image_size_percent=100, source=None, selected=True):
        """ Create image button
         
        :param name: button name
        :param action: action listener
        :param keyboard_key: keyboard key assigned to the button
        :param lirc_code: LIRC code assigned to the button
        :param bounding_box: button bounding box
        :param bgr: button background color
        :param x_margin_percent: X margin for the button
        :param resizable: flag defining if button can be resized, True - resizable, False - non-resizable
        """
        state = State()
        state.name = name
        state.bounding_box = bounding_box
        state.bgr = bgr
        state.keyboard_key = keyboard_key
        state.lirc_code = lirc_code
        state.img_x = None
        state.img_y = None
        state.auto_update = True
        state.show_bgr = True
        state.show_img = True
        state.image_align_v = V_ALIGN_CENTER
        state.x_margin_percent = x_margin_percent
        state.resizable = resizable
        state.source = source
        state.image_size_percent = image_size_percent / 100.0
        self.set_state_icons(state, selected)
        button = Button(self.util, state)
        if action:
            button.add_release_listener(action)
        return button
    
    def create_toggle_button(self, name, keyboard_key=None, lirc_code=None, bounding_box=None, image_size_percent=100):
        """ Create toggle button (e.g. Shutdown button)
        
        :param name: button name
        :param keyboard_key: keyboard key assigned to the button
        :param lirc_code: LIRC code assigned to the button
        :param bounding_box: button bounding box
        """
        state = State()
        state.name = name
        state.keyboard_key = keyboard_key
        state.lirc_code = lirc_code
        state.bgr = (0, 0, 0)
        state.bounding_box = bounding_box
        state.img_x = None
        state.img_y = None
        state.auto_update = True
        state.image_align_v = V_ALIGN_CENTER
        state.show_bgr = True
        state.show_img = True
        state.image_size_percent = image_size_percent
        self.set_state_icons(state)
        button = ToggleButton(self.util, state)
        return button

    def create_timer_button(self, name, keyboard_key=None, lirc_code=None, bounding_box=None, image_size_percent=100, bgr=(0, 0, 0), label=None):
        """ Create timer button
        
        :param name: button name
        :param keyboard_key: keyboard key assigned to the button
        :param lirc_code: LIRC code assigned to the button
        :param bounding_box: button bounding box
        :param image_size_percent: button icon size in percent
        :param bgr: button background color
        :param label: button label
        """
        state = State()
        state.name = name
        state.keyboard_key = keyboard_key
        state.lirc_code = lirc_code
        state.bgr = bgr
        state.bounding_box = bounding_box
        state.img_x = None
        state.img_y = None
        state.auto_update = True
        state.image_align_v = V_ALIGN_CENTER
        state.show_bgr = True
        state.show_img = True
        state.image_size_percent = image_size_percent
        self.set_state_icons(state)
        button = Button(self.util, state)
        return button
        
    def create_multi_state_button(self, states):
        """ Create multi-state button (e.g. Play/Pause button)
        
        :param states: button states
        
        :return: multi-state button
        """
        actions = dict()
        for state in states:
            name = state.name
            actions[name] = [state.action]
            self.set_state_icons(state)
        button = MultiStateButton(self.util, states)
        button.add_listeners(actions)     
        return button
    
    def create_volume_control(self, bb):
        """ Create volume control
        
        :param bb: bounding box
        
        :return: volume control slider
        """
        scale_factor = 0.7
        
        img_knob = self.util.load_mono_svg_icon(IMAGE_VOLUME, self.util.COLOR_MAIN, bb, scale_factor)
        img_knob_on = self.util.load_mono_svg_icon(IMAGE_VOLUME, self.util.COLOR_ON, bb, scale_factor)
        img_mute = self.util.load_mono_svg_icon(IMAGE_VOLUME, self.util.COLOR_MUTE, bb, scale_factor)
        
        d = {}
        d["name"] = VOLUME
        d['bgr'] = self.config[COLORS][COLOR_DARK_LIGHT]
        d['slider_color'] = self.config[COLORS][COLOR_MEDIUM]
        d['img_knob'] = img_knob
        d['img_knob_on'] = img_knob_on
        d['img_selected'] = img_mute
        d['key_incr'] = kbd_keys[KEY_VOLUME_UP]
        d['key_decr'] = kbd_keys[KEY_VOLUME_DOWN]
        d['key_knob'] = kbd_keys[KEY_MUTE]
        d['bb'] = bb
        d['util'] = self.util
        d['knob_selected'] = self.config[PLAYER_SETTINGS][MUTE]
        
        slider = Slider(**d)        
        volume_level = int(self.config[PLAYER_SETTINGS][VOLUME])
        slider.set_position(volume_level)
        slider.update_position()
                
        return slider
    
    def create_time_control(self, bb):
        """ Create time control
        
        :param bb: bounding box
        
        :return: volume control slider
        """
        scale_factor = 0.7        
        img_knob = self.util.load_mono_svg_icon(IMAGE_TIME_KNOB, self.util.COLOR_MAIN, bb, scale_factor)
        img_knob_on = self.util.load_mono_svg_icon(IMAGE_TIME_KNOB, self.util.COLOR_ON, bb, scale_factor)
        d = {}
        d["name"] = "track.time."
        d['bgr'] = self.config[COLORS][COLOR_DARK_LIGHT]
        d['slider_color'] = self.config[COLORS][COLOR_MEDIUM]
        d['img_knob'] = img_knob
        d['img_knob_on'] = img_knob_on
        d['key_incr'] = kbd_keys[KEY_VOLUME_UP]
        d['key_decr'] = kbd_keys[KEY_VOLUME_DOWN]
        d['key_knob'] = kbd_keys[KEY_MUTE]
        d['bb'] = bb
        d['util'] = self.util         
        return TimeSlider(**d)
    
    def create_equalizer_slider(self, id, bb, name, listener, label):
        """ Create equalizer slider
        
        :param id: slider ID
        :param bb: bounding box
        :param name: slider name
        :param listener: slider listener
        :param label: slider label        
        
        :return: equalizer slider
        """
        scale_factor = 0.56        
        img_knob = self.util.load_mono_svg_icon(IMAGE_VOLUME, self.util.COLOR_MAIN, bb, scale_factor)
        img_knob_on = self.util.load_mono_svg_icon(IMAGE_VOLUME, self.util.COLOR_ON, bb, scale_factor)        
        d = {}
        d["id"] = id
        d["name"] = name
        d['bgr'] = self.config[COLORS][COLOR_DARK_LIGHT]
        d['slider_color'] = (0, 0, 0)
        d['img_knob'] = img_knob
        d['img_knob_on'] = img_knob_on
        d['key_incr'] = kbd_keys[KEY_VOLUME_DOWN]
        d['key_decr'] = kbd_keys[KEY_VOLUME_UP]
        d['key_knob'] = kbd_keys[KEY_MUTE]
        d['bb'] = bb
        d['util'] = self.util
        d['listener'] = listener
        d["label"] = label
        slider = EqualizerSlider(**d)        
                
        return slider
    
    def create_output_text(self, name, bb, bgr, fgr, font_size, halign=H_ALIGN_CENTER, valign=V_ALIGN_CENTER, shift_x=0, shift_y=0, full_width=False):
        """ Create static output text component
        
        :param name: component name
        :param bb: bounding box
        :param bgr: background color
        :param fgr: text color
        :param font_size: font size
        :param halign: horizontal alignment
        :param valign: vertical alignment
        :param shift_x: X axis shift
        :param shift_y: Y axis shift
        :param full_width: True - use the whole bounding box width, False - use reduced width
        
        :return: static output text control
        """
        d = {}
        d["name"] = name
        d["bgr"] = bgr
        d["fgr"] = fgr
        d["bb"] = bb
        d["halign"] = halign
        d["valign"] = valign
        d["shift_x"] = shift_x
        d["shift_y"] = shift_y 
        d["font_size"] = font_size
        d["full_width"] = full_width
        d["font"] = self.util.get_font(font_size)
        d["util"] = self.util
        
        outputText = OutputText(**d) 
        return outputText
    
    def create_dynamic_text(self, name, bb, bgr, fgr, font_size, halign=H_ALIGN_CENTER, valign=V_ALIGN_CENTER, shift_x=0, shift_y=0):
        """ Create dynamic text component which supports animation
        
        :param name: component name
        :param bb: bounding box
        :param bgr: background color
        :param fgr: text color
        :param font_size: font size
        :param halign: horizontal alignment
        :param valign: vertical alignment
        :param shift_x: X axis shift
        :param shift_y: Y axis shift
        
        :return: dynamic output text control
        """
        d = {}
        d["name"] = name
        d["bgr"] = bgr
        d["fgr"] = fgr
        d["bb"] = bb
        d["halign"] = halign
        d["valign"] = valign
        d["shift_x"] = shift_x
        d["shift_y"] = shift_y 
        d["font_size"] = font_size
        d["util"] = self.util
        
        dynamicText = DynamicText(**d) 
        return dynamicText
    
    def create_menu_button(self, s, constr, action, scale, label_area_percent=30, label_text_height=44, show_img=True, show_label=True, bgr=None, source=None, font_size=None):
        """ Create Menu button
        
        :param s: button state
        :param constr: scaling constraints
        :param action: button event listener
        :param scale: True - scale image and label, False - don't scale image and label
        
        :return: menu button
        """          
        s.bounding_box = constr
        s.img_x = None
        s.img_y = None
        s.auto_update = True
        s.show_bgr = True
        s.show_img = show_img and getattr(s, "show_img", True)
        s.show_label = show_label
        s.image_location = CENTER
        s.label_location = BOTTOM
        s.label_area_percent = label_area_percent
        s.label_text_height = label_text_height
        s.text_color_normal = self.config[COLORS][COLOR_BRIGHT]
        s.text_color_selected = self.config[COLORS][COLOR_CONTRAST]
        s.text_color_disabled = self.config[COLORS][COLOR_MEDIUM]
        s.text_color_current = s.text_color_normal
        if font_size:
            s.fixed_height = int(font_size * 0.8) 
        s.scale = scale
        s.source = source 
        if bgr:
            s.bgr = bgr
        else:
            s.bgr = self.config[COLORS][COLOR_DARK]
        button = Button(self.util, s)
        button.add_release_listener(action)
        if not getattr(s, "enabled", True):
            button.set_enabled(False)
        elif getattr(s, "icon_base", False) and not getattr(s, "scaled", False):
            button.components[1].content = s.icon_base
        button.scaled = scale        
        return button
    
    def create_station_menu_button(self, s, constr, action, scale):
        """ Create Station Menu button
        
        :param s: button state
        :param constr: scaling constraints
        :param action: button event listener
        :param scale: True - scale images, False - don't scale images
        
        :return: station menu button
        """
        if scale:
            self.set_state_scaled_icons(s, constr)
        s.scaled = scale            
        button = self.create_station_button(s, constr, action)
        button.bgr = (0, 0, 0)
        return button
    
    def create_station_button(self, s, bb, action=None):
        """ Create station button
        
        :param s: button state
        :param bb: bounding box
        :param action: event listener
        
        :return: station logo button
        """
        state = State()
        state.icon_base = s.icon_base
        state.index_in_page = s.index_in_page
        state.index = s.index
        state.genre = s.genre
        state.scaled = getattr(s, "scaled", False)
        state.icon_base_scaled = s.icon_base_scaled
        state.name = "station_menu." + s.name
        state.l_name = s.l_name
        state.url = s.url
        state.keyboard_key = kbd_keys[KEY_SELECT]
        state.bounding_box = bb
        state.img_x = bb.x
        state.img_y = bb.y
        state.auto_update = False
        state.show_bgr = True
        state.show_img = True
        state.image_align_v = V_ALIGN_BOTTOM
        button = Button(self.util, state)
        button.add_release_listener(action)
        return button        
    
    def create_genre_menu_button(self, s, constr, action, scale):
        """ Create Genre Menu button
        
        :param s: button state
        :param constr: scaling constraints
        :param action: button event listener
        :param scale: True - scale images, False - don't scale images
        
        :return: genre menu button
        """
        return self.create_menu_button(s, constr, action, scale, 30, 75)
    
    def create_book_genre_menu_button(self, s, constr, action, show_img=True, show_label=True):
        """ Create Genre Menu button
        
        :param s: button state
        :param constr: bounding box
        :param action: button event listener
        :param show_img: True - show image, False - don't show image
        :param show_label: True - show label, False - don't show label
        
        :return: genre menu button
        """
        s.bounding_box = constr
        s.img_x = None
        s.img_y = None
        s.auto_update = True
        s.show_bgr = True
        s.show_img = show_img
        s.show_label = show_label
        s.text_color_normal = self.config[COLORS][COLOR_BRIGHT]
        s.text_color_selected = self.config[COLORS][COLOR_CONTRAST]
        s.text_color_disabled = self.config[COLORS][COLOR_MEDIUM]
        s.text_color_current = s.text_color_normal
        s.label_text_height = 35
        button = Button(self.util, s)
        button.bgr = self.config[COLORS][COLOR_DARK]
        button.add_release_listener(action)
        return button

    def create_book_author_menu_button(self, s, constr, action, show_img=True, show_label=True):
        """ Create Author Menu button
        
        :param s: button state
        :param constr: bounding box
        :param action: button event listener
        :param show_img: True - show image, False - don't show image
        :param show_label: True - show label, False - don't show label
        
        :return: genre menu button
        """
        s.bounding_box = constr
        s.img_x = None
        s.img_y = None
        s.auto_update = True
        s.show_bgr = True
        s.show_img = show_img
        s.show_label = show_label
        s.text_color_normal = self.config[COLORS][COLOR_BRIGHT]
        s.text_color_selected = self.config[COLORS][COLOR_CONTRAST]
        s.text_color_disabled = self.config[COLORS][COLOR_MEDIUM]
        s.text_color_current = s.text_color_normal
        s.label_text_height = 35
        button = Button(self.util, s)
        button.bgr = self.config[COLORS][COLOR_DARK]
        button.add_release_listener(action)
        return button
   
    def create_book_author_items(self, authors):
        """ Create dictionary with author books
        
        :param authors: list of author books
        
        :return: dictionary with author books
        """
        items = {}
        for i, g in enumerate(authors):
            state = State()
            state.name = g[AUTHOR_NAME]
            state.url = g[AUTHOR_URL] + "/"
            state.l_name = state.name + " (" + g[AUTHOR_BOOKS] + ")"
            state.bgr = self.config[COLORS][COLOR_DARK]
            state.img_x = None
            state.img_y = None
            state.auto_update = True
            state.show_bgr = True
            state.show_img = False
            state.show_label = True
            state.comparator_item = state.name
            state.index = i
            items[state.name] = state
        return items
   
    def create_book_genre_items(self, genres, base_url):
        """ Create dictionary with genres
        
        :param genres: list of genres
        :param base_url: base url
        
        :return: dictionary with genres
        """
        items = {}
        for i, g in enumerate(genres):
            state = State()
            state.name = g[0]
            state.genre = base_url + g[1]
            state.l_name = state.name
            state.bgr = self.config[COLORS][COLOR_DARK]
            state.img_x = None
            state.img_y = None
            state.auto_update = True
            state.show_bgr = True
            state.show_img = False
            state.show_label = True
            state.comparator_item = state.name
            state.index = i
            items[state.name] = state
        return items

    def create_saver_menu_button(self, s, constr, action, scale):
        """ Create Screensaver Menu button
        
        :param s: button state
        :param constr: scaling constraints
        :param action: button event listener
        :param scale: True - scale images, False - don't scale images
        
        :return: screensaver menu button
        """
        return self.create_menu_button(s, constr, action, scale, 36, 60)
    
    def create_saver_delay_menu_button(self, s, constr, action, scale):
        """ Create Screensaver Delay Menu button
        
        :param s: button state
        :param constr: scaling constraints
        :param action: button event listener
        :param scale: True - scale images, False - don't scale images
        
        :return: screensaver delay menu button
        """        
        return self.create_menu_button(s, constr, action, scale, 100, 38, False)

    def create_home_menu_button(self, s, constr, action, scale, font_size):
        """ Create Home Menu button
        
        :param s: button state
        :param constr: scaling constraints
        :param action: button event listener
        :param scale: True - scale images, False - don't scale images
        
        :return: home menu button
        """
        return self.create_menu_button(s, constr, action, scale, 30, 54, font_size=font_size)
    
    def create_home_navigator_button(self, s, constr, action, scale):
        """ Create Home Navigator button
        
        :param s: button state
        :param constr: scaling constraints
        :param action: button event listener
        :param scale: True - scale images, False - don't scale images
        
        :return: home navigator button
        """
        return self.create_menu_button(s, constr, action, scale, show_label=False, bgr=self.config[COLORS][COLOR_DARK_LIGHT], source=HOME_NAVIGATOR)
    
    def create_book_menu_button(self, s, constr, action, show_img=True, show_label=True, menu_button_layout=None):
        """ Create Menu button
        
        :param s: button state
        :param constr: scaling constraints
        :param action: button event listener
        :param scale: True - scale images, False - don't scale images
        
        :return: menu button
        """       
        s.bounding_box = constr
        s.img_x = None
        s.img_y = None
        s.auto_update = True
        s.show_bgr = True
        s.show_img = show_img
        s.show_label = show_label
        s.text_color_normal = self.config[COLORS][COLOR_DARK]
        s.text_color_selected = self.config[COLORS][COLOR_WEB_BGR]
        s.text_color_disabled = self.config[COLORS][COLOR_MEDIUM]
        s.text_color_current = s.text_color_normal
        s.bgr_selected = self.config[COLORS][COLOR_BRIGHT]
        menu_button_layout.create_layout(constr)
        s.layout = menu_button_layout        
        s.source = BOOK_MENU
        button = MultiLineButton(self.util, s)
        button.bgr = self.config[COLORS][COLOR_DARK]
        button.add_release_listener(action)
        if not getattr(s, "enabled", True):
            button.set_enabled(False)
        elif getattr(s, "icon_base", False) and not getattr(s, "scaled", False):
            button.components[1].content = s.icon_base

        if self.config[USAGE][USE_VOICE_ASSISTANT]:
            s.voice_commands = [s.name.lower().strip(), s.l_name.lower().strip()]

        return button

    def create_track_menu_button(self, s, constr, action, show_img=True, show_label=True):
        """ Create Menu button
        
        :param s: button state
        :param constr: scaling constraints
        :param action: button event listener
        :param scale: True - scale images, False - don't scale images
        
        :return: menu button
        """       
        
        s.bounding_box = constr
        s.img_x = None
        s.img_y = None
        s.auto_update = True
        s.show_bgr = True
        s.show_img = show_img
        s.show_label = show_label
        s.source = TRACK_MENU
        if s.name in ABC_RU:
            s.text_color_normal = self.config[COLORS][COLOR_BRIGHT]
        else:
            s.text_color_normal = (255, 255, 255)
        s.text_color_selected = self.config[COLORS][COLOR_CONTRAST]
        s.text_color_disabled = self.config[COLORS][COLOR_MEDIUM]
        s.text_color_current = s.text_color_normal
        
        button = Button(self.util, s)
        button.bgr = self.config[COLORS][COLOR_DARK]
        button.add_release_listener(action)

        return button

    def create_language_menu_button(self, s, constr, action, scale):
        """ Create Language Menu button
        
        :param s: button state
        :param constr: scaling constraints
        :param action: button event listener
        :param scale: True - scale images, False - don't scale images
        
        :return: language menu button
        """
        return self.create_menu_button(s, constr, action, scale, 30, 54)
    
    def create_button(self, img_name, kbd_key, bb, action=None, bgr=(0, 0, 0), image_size_percent=1, source=None):
        """ Create image button
        
        :param img_name: image filename
        :param kbd_key: keyboard key
        :param bb: bounding box
        :param action: action
        :param bgr: background color
        :param image_size_percent: percent of image area in tottal button area
        :return: image button
        """
        d = {}
        d["name"] = img_name
        d["bounding_box"] = bb
        d["action"] = action
        d["keyboard_key"] = kbd_keys[kbd_key]
        d["bgr"] = bgr
        d["image_size_percent"] = image_size_percent
        d["source"] = source
        return self.create_image_button(**d)
    
    def create_play_pause_button(self, bb, action):
        """ Create Play/Pause button
        
        :param bb: bounding box
        :param action: event listener
        
        :return: play/pause button
        """
        states = []
        
        pause_state = State()
        pause_state.name = "pause"
        pause_state.bounding_box = bb
        pause_state.bgr = (0, 0, 0)
        pause_state.keyboard_key = kbd_keys[KEY_PLAY_PAUSE]
        pause_state.action = action
        pause_state.img_x = None
        pause_state.img_y = None
        pause_state.auto_update = True
        pause_state.image_align_v = V_ALIGN_CENTER
        pause_state.show_bgr = True
        pause_state.show_img = True
        pause_state.image_size_percent = 0.36
        
        play_state = State()
        play_state.name = "play"
        play_state.bounding_box = bb
        play_state.bgr = (0, 0, 0)
        play_state.keyboard_key = kbd_keys[KEY_PLAY_PAUSE]
        play_state.action = action
        play_state.img_x = None
        play_state.img_y = None
        play_state.auto_update = True
        play_state.image_align_v = V_ALIGN_CENTER
        play_state.show_bgr = True
        play_state.show_img = True
        play_state.image_size_percent = 0.36
        
        if self.config[PLAYER_SETTINGS][PAUSE]:
            states.append(play_state)
            states.append(pause_state) 
        else:
            states.append(pause_state)
            states.append(play_state)        
        
        return self.create_multi_state_button(states)
    
    def create_time_volume_button(self, bb, action):
        """ Create Time/Volume two states button
        
        :param bb: bounding box
        :param action: event listener
        
        :return: Time/Volume button
        """
        states = []
        
        volume_state = State()
        volume_state.name = "speaker"
        volume_state.bounding_box = bb
        volume_state.bgr = (0, 0, 0)
        volume_state.keyboard_key = kbd_keys[KEY_SETUP]
        volume_state.action = action
        volume_state.img_x = None
        volume_state.img_y = None
        volume_state.auto_update = True
        volume_state.image_align_v = V_ALIGN_CENTER
        volume_state.show_bgr = True
        volume_state.show_img = True
        volume_state.image_size_percent = 0.36
        states.append(volume_state)
        
        time_state = State()
        time_state.name = "time"
        time_state.bounding_box = bb
        time_state.bgr = (0, 0, 0)
        time_state.keyboard_key = kbd_keys[KEY_SETUP]
        time_state.action = action
        time_state.img_x = None
        time_state.img_y = None
        time_state.auto_update = True
        time_state.image_align_v = V_ALIGN_CENTER
        time_state.show_bgr = True
        time_state.show_img = True
        time_state.image_size_percent = 0.36
        states.append(time_state)        
        
        return self.create_multi_state_button(states)
    
    def create_genre_button(self, bb, state, image_area):
        """ Create Genre button
        
        :param bb: bounding box
        :param state: button state        
        :return: genre button
        """
        s = State()
        s.__dict__ = state.__dict__
        s.bgr = (0, 0, 0)
        s.bounding_box = bb        
        s.keyboard_key = kbd_keys[KEY_MENU]
        s.img_x = None
        s.img_y = None
        s.auto_update = True
        s.image_align_v = V_ALIGN_CENTER
        s.show_bgr = True
        s.show_img = True
        s.show_label = False
        self.scale_genre_button_image(s, image_area)        
        
        return Button(self.util, s)
    
    def scale_genre_button_image(self, s, image_area):
        """ Scale genre button image
        
        :param s: button state object
        :param image_area: image bounding box
        """
        img_w = int((s.bounding_box.w / 100) * image_area)
        img_h = int((s.bounding_box.h / 100) * image_area)
        scale_ratio = self.util.get_scale_ratio((img_w, img_h), s.icon_base[1])
        constr = Rect(0, 0, scale_ratio[0], scale_ratio[1])
        self.set_state_scaled_icons(s, constr)
    
    def create_stream_button(self, bb):
        """ Create Stream button
        
        :param bb: bounding box
        :return: genre button
        """
        state = State()
        state.name = "stream"        
        state.icon_base = self.util.load_mono_svg_icon(state.name, self.util.COLOR_OFF, bb, 0.4)
        
        state.icon_selected = state.icon_base
        state.bgr = (0, 0, 0)
        state.bounding_box = bb
        state.img_x = None
        state.img_y = None
        state.auto_update = True
        state.image_align_v = V_ALIGN_CENTER
        state.show_bgr = True
        state.show_img = True
        state.show_label = False
        return Button(self.util, state)
    
    def create_arrow_button(self, bb, name, key, location, label_text, image_area, image_size):
        """ Create Arrow button (e.g. Left, Next Page etc.)
        
        :param bb: bounding box
        :param name: button name
        :param key: keyboard key associated with button
        :param location: image location inside of bounding box
        :param label_text: button label text
        :param image_area: percentage of height occupied by button image        
        :return: arrow button
        """
        s = State()
        s.name = name
        s.bounding_box = bb
        s.keyboard_key = key
        s.bgr = self.config[COLORS][COLOR_DARK_LIGHT]
        s.show_bgr = True
        s.show_img = True
        s.show_label = True
        s.image_location = location
        s.label_location = CENTER        
        s.label_text_height = 40
        s.l_name = label_text
        s.auto_update = True
        s.image_size_percent = image_area / 100
        s.text_color_normal = self.config[COLORS][COLOR_BRIGHT]
        s.text_color_selected = self.config[COLORS][COLOR_CONTRAST]
        s.text_color_disabled = self.config[COLORS][COLOR_MEDIUM]
        s.text_color_current = s.text_color_normal
        self.set_state_icons(s)
        if image_size != 100:
            self.resize_image(s, image_size)
        b = Button(self.util, s)
        return b
    
    def resize_image(self, state, image_size_percent):
        """ Resize image
        
        :param state: state object which includes image to resize
        :param image_size_percent: image size percent
        """
        bb = state.bounding_box
        w = bb.w * image_size_percent / 100
        k = w / state.icon_base[1].get_size()[0]
        h = state.icon_base[1].get_size()[1] * k
        constr = Rect(0, 0, w, h)
        self.set_state_scaled_icons(state, constr)
    
    def create_right_button(self, bb, label_text, image_area, image_size):
        """ Create Right button
        
        :param bb: bounding box
        :param label_text: button label text
        
        :return: right arrow button
        """
        return self.create_arrow_button(bb, KEY_RIGHT, kbd_keys[KEY_RIGHT], RIGHT, label_text, image_area, image_size)
    
    def create_left_button(self, bb, label_text, image_area, image_size):
        """ Create Left button
        
        :param bb: bounding box
        :param label_text: button label text
        
        :return: left arrow button
        """
        return self.create_arrow_button(bb, KEY_LEFT, kbd_keys[KEY_LEFT], LEFT, label_text, image_area, image_size)
    
    def create_page_up_button(self, bb, label_text, image_area, image_size):
        """ Create Page Up button
        
        :param bb: bounding box
        :param label_text: button label text
        
        :return: page up button
        """
        return self.create_arrow_button(bb, KEY_PAGE_UP, kbd_keys[KEY_PAGE_UP], RIGHT, label_text, image_area, image_size)
    
    def create_page_down_button(self, bb, label_text, image_area, image_size):
        """ Create Page Down button
        
        :param bb: bounding box
        :param label_text: button label text
        
        :return: page down button
        """
        return self.create_arrow_button(bb, KEY_PAGE_DOWN, kbd_keys[KEY_PAGE_DOWN], LEFT, label_text, image_area, image_size)
    
    def create_shutdown_button(self, bb):
        """ Create Shutdown button
        
        :param bb: bounding box
        
        :return: shutdown button
        """
        d = {}
        d["name"] = "shutdown"
        d["bounding_box"] = bb
        d["keyboard_key"] = kbd_keys[KEY_END]
        d["image_size_percent"] = 0.36
        return self.create_toggle_button(**d)
    
    def create_file_menu_button(self, s, constr, action, scale):
        """ Create File Menu button
        
        :param s: button state
        :param constr: scaling constraints
        :param action: button event listener
        :param scale: True - scale images, False - don't scale images 
               
        :return: file menu button
        """
        scale = False
        if s.file_type == FOLDER_WITH_ICON:
            scale = True
        return self.create_menu_button(s, constr, action, scale, label_text_height=80)
    
    def create_file_button(self, bb, action=None):
        """ Create default audio file button
        
        :param bb: bounding box
        :param action: button event listener
        
        :return: default audio file button
        """
        state = State()

        state.icon_base = self.util.get_audio_file_icon("", bb)
        state.scaled = False
        state.name = "cd"
        state.keyboard_key = kbd_keys[KEY_SELECT]
        state.bounding_box = bb
        state.img_x = bb.x
        state.img_y = bb.y
        state.auto_update = False
        state.show_bgr = False
        state.show_img = True
        state.image_align_v = V_ALIGN_CENTER
        button = Button(self.util, state)
        button.add_release_listener(action)
        return button

    def create_home_player_buttons(self, container, layout, listeners):
        """ Create home and player buttons
        
        :param container: destination of the buttons
        :param layout: bounding box
        :param listeners: buttons listeners
        
        :return: tuple with home and player buttons
        """
        nav_layout = GridLayout(layout)
        nav_layout.set_pixel_constraints(1, 2, 1, 0)        
        nav_layout.current_constraints = 0
        d = self.config[COLORS][COLOR_DARK_LIGHT]
        
        constr = nav_layout.get_next_constraints()
        home_button = self.create_button(KEY_HOME, KEY_HOME, constr, listeners[KEY_HOME], d, image_size_percent=60)
        container.add_component(home_button)
        
        constr = nav_layout.get_next_constraints()
        player_button = self.create_button(KEY_PLAYER, KEY_PLAY_PAUSE, constr, listeners[KEY_PLAYER], d, image_size_percent=60)
        container.add_component(player_button)
        
        return (home_button, player_button)
    
    def create_cyrillic_menu_button(self, s, constr, action, show_img=True, show_label=True):
        """ Create Cyrillic Menu button
        
        :param s: button state
        :param constr: scaling constraints
        :param action: button event listener
        :param show_img: True - show image, False - don't show image
        :param show_label: True - show label, False - don't show label
        
        :return: menu button
        """       
        
        s.bounding_box = constr
        s.img_x = None
        s.img_y = None
        s.auto_update = True
        s.show_bgr = True
        s.show_img = show_img
        s.show_label = show_label
        if s.name in ABC_RU:
            s.text_color_normal = self.config[COLORS][COLOR_BRIGHT]
            s.label_text_height = 50
        else:
            s.text_color_normal = (255, 255, 255)
            s.label_text_height = 45
        s.text_color_selected = self.config[COLORS][COLOR_CONTRAST]
        s.text_color_disabled = self.config[COLORS][COLOR_MEDIUM]
        s.text_color_current = s.text_color_normal
        
        button = Button(self.util, s)
        button.bgr = self.config[COLORS][COLOR_DARK]
        button.add_release_listener(action)

        return button
    
    def create_cd_drive_menu_button(self, s, constr, action, scale):
        """ Create CD drive button
        
        :param s: button state
        :param constr: scaling constraints
        :param action: button event listener
        :param scale: True - scale images, False - don't scale images 
               
        :return: file menu button
        """
        return self.create_menu_button(s, constr, action, scale, label_text_height=30)
    
    def create_cd_track_menu_button(self, s, constr, action, scale):
        """ Create File Menu button
        
        :param s: button state
        :param constr: scaling constraints
        :param action: button event listener
        :param scale: True - scale images, False - don't scale images 
               
        :return: file menu button
        """
        return self.create_menu_button(s, constr, action, False, label_text_height=80)
