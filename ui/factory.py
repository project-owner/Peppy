# Copyright 2016 Peppy Player peppy.player@gmail.com
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

from ui.button.button import Button
from ui.state import State
from ui.button.multistatebutton import MultiStateButton
from ui.button.togglebutton import ToggleButton
from ui.slider.slider import Slider
from ui.text.outputtext import OutputText
from ui.text.dynamictext import DynamicText
from ui.layout.buttonlayout import BOTTOM, CENTER, LEFT, RIGHT
from util.keys import kbd_keys, KEY_VOLUME_UP, KEY_VOLUME_DOWN, KEY_HOME, KEY_PLAY_PAUSE, KEY_MENU, \
    KEY_END, KEY_MUTE, KEY_SELECT, KEY_LEFT, KEY_RIGHT, KEY_PAGE_UP, KEY_PAGE_DOWN 
from util.util import IMAGE_SELECTED_SUFFIX, IMAGE_VOLUME, IMAGE_MUTE, V_ALIGN_CENTER, V_ALIGN_BOTTOM, H_ALIGN_CENTER 
from util.config import COLOR_DARK, COLOR_MEDIUM, COLORS, COLOR_CONTRAST, COLOR_BRIGHT

class Factory(object):
    """ UI Factory class """
    
    def __init__(self, util):
        """ Initializer
        
        :param util: utility object
        """
        self.util = util
        self.config = util.config
    
    def set_state_icons(self, state):
        """ Load and set button icons
        
        :param state: the state object on which icons will be set
        """
        resizable = getattr(state, "resizable", True)
        state.icon_base = self.util.load_icon(state.name, resizable)
        state.icon_selected = self.util.load_icon(state.name + IMAGE_SELECTED_SUFFIX, resizable)
        
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
    
    def create_image_button(self, name, action=None, keyboard_key=None, lirc_code=None, bounding_box=None, bgr=(0, 0, 0), x_margin_percent=None, resizable=True):
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
        self.set_state_icons(state)
        button = Button(self.util, state)
        if action:
            button.add_release_listener(action)
        return button
    
    def create_toggle_button(self, name, keyboard_key=None, lirc_code=None, bounding_box=None):
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
        self.set_state_icons(state)
        button = ToggleButton(self.util, state)
        return button
        
    def create_multi_state_button(self, states):
        """ Create multi-state button (e.g. Play/Pause button)
        
        :param states: button states
        
        :return: multi-state button
        """
        actions = dict()
        for state in states:
            name = state.name
            actions[name] = state.action
            self.set_state_icons(state)
        button = MultiStateButton(self.util, states)
        button.add_listeners(actions)     
        return button
    
    def create_volume_control(self, bb):
        """ Create volume control
        
        :param bb: bounding box
        
        :return: colume control slider
        """
        img_knob = self.util.load_icon(IMAGE_VOLUME)
        img_knob_on = self.util.load_icon(IMAGE_VOLUME + IMAGE_SELECTED_SUFFIX)
        img_mute = self.util.load_icon(IMAGE_MUTE)
        d = {}
        d["name"] = "volume"
        d['bgr'] = self.config[COLORS][COLOR_DARK]
        d['slider_color'] = self.config[COLORS][COLOR_MEDIUM]
        d['img_knob'] = img_knob
        d['img_knob_on'] = img_knob_on
        d['img_selected'] = img_mute
        d['key_incr'] = kbd_keys[KEY_VOLUME_UP]
        d['key_decr'] = kbd_keys[KEY_VOLUME_DOWN]
        d['key_knob'] = kbd_keys[KEY_MUTE]
        d['bb'] = bb
        d['util'] = self.util         
        return Slider(**d)
    
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
    
    def create_menu_button(self, s, constr, action, scale, label_area_percent, label_text_height, show_img=True):
        """ Create Menu button
        
        :param s: button state
        :param constr: scaling constraints
        :param action: button event listener
        :param scale: True - scale images, False - don't scale images
        
        :return: menu button
        """  
        
        if scale:
            self.set_state_scaled_icons(s, constr)
        s.bounding_box = constr
        s.img_x = None
        s.img_y = None
        s.auto_update = True
        s.show_bgr = True
        s.show_img = show_img
        s.show_label = True
        s.image_location = CENTER
        s.label_location = BOTTOM
        s.label_area_percent = label_area_percent
        s.label_text_height = label_text_height
        s.text_color_normal = self.config[COLORS][COLOR_BRIGHT]
        s.text_color_selected = self.config[COLORS][COLOR_CONTRAST]
        s.text_color_disabled = self.config[COLORS][COLOR_MEDIUM]
        s.text_color_current = s.text_color_normal
        button = Button(self.util, s)
        button.bgr = self.config[COLORS][COLOR_DARK]
        button.add_release_listener(action)         
        if getattr(s, "icon_base", False):
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
        return self.create_menu_button(s, constr, action, scale, 30, 60)
    
    def create_saver_menu_button(self, s, constr, action, scale):
        """ Create Screensaver Menu button
        
        :param s: button state
        :param constr: scaling constraints
        :param action: button event listener
        :param scale: True - scale images, False - don't scale images
        
        :return: screensaver menu button
        """
        return self.create_menu_button(s, constr, action, scale, 40, 40)
    
    def create_saver_delay_menu_button(self, s, constr, action, scale):
        """ Create Screensaver Delay Menu button
        
        :param s: button state
        :param constr: scaling constraints
        :param action: button event listener
        :param scale: True - scale images, False - don't scale images
        
        :return: screensaver delay menu button
        """        
        return self.create_menu_button(s, constr, action, scale, 100, 18, False)

    def create_home_menu_button(self, s, constr, action, scale):
        """ Create Home Menu button
        
        :param s: button state
        :param constr: scaling constraints
        :param action: button event listener
        :param scale: True - scale images, False - don't scale images
        
        :return: home menu button
        """
        return self.create_menu_button(s, constr, action, scale, 40, 30)

    def create_language_menu_button(self, s, constr, action, scale):
        """ Create Language Menu button
        
        :param s: button state
        :param constr: scaling constraints
        :param action: button event listener
        :param scale: True - scale images, False - don't scale images
        
        :return: language menu button
        """
        return self.create_menu_button(s, constr, action, scale, 40, 30)
    
    def create_home_button(self, bb, action=None):
        """ Create Home button
        
        :param bb: bounding box
        :param action: event listener
        
        :return: home button
        """
        d = {}
        d["name"] = KEY_HOME
        d["bounding_box"] = bb
        d["action"] = action
        d["keyboard_key"] = kbd_keys[KEY_HOME] 
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
        states.append(pause_state)
        
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
        states.append(play_state)        
        
        return self.create_multi_state_button(states)
    
    def create_genre_button(self, bb, state):
        """ Create Genre button
        
        :param bb: bounding box
        :param state: button state
        
        :return: genre button
        """
        state.bgr = (0, 0, 0)
        state.bounding_box = bb
        state.keyboard_key = kbd_keys[KEY_MENU]
        state.img_x = None
        state.img_y = None
        state.auto_update = True
        state.image_align_v = V_ALIGN_CENTER
        state.show_bgr = True
        state.show_img = True
        state.show_label = False
        return Button(self.util, state)
    
    def create_arrow_button(self, bb, name, key, location, label_text, image_area=40):
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
        s.bgr = self.config[COLORS][COLOR_DARK]
        s.show_bgr = True
        s.show_img = True
        s.show_label = True
        s.image_location = location
        s.label_location = CENTER
        s.image_area_percent = image_area
        s.label_text_height = 44
        s.l_name = label_text
        s.auto_update = True
        s.text_color_normal = self.config[COLORS][COLOR_BRIGHT]
        s.text_color_selected = self.config[COLORS][COLOR_CONTRAST]
        s.text_color_disabled = self.config[COLORS][COLOR_MEDIUM]
        s.text_color_current = s.text_color_normal
        self.set_state_icons(s)
        b = Button(self.util, s)
        return b
    
    def create_right_button(self, bb, label_text):
        """ Create Right button
        
        :param bb: bounding box
        :param label_text: button label text
        
        :return: right arrow button
        """
        return self.create_arrow_button(bb, KEY_RIGHT, kbd_keys[KEY_RIGHT], RIGHT, label_text)
    
    def create_left_button(self, bb, label_text):
        """ Create Left button
        
        :param bb: bounding box
        :param label_text: button label text
        
        :return: left arrow button
        """
        return self.create_arrow_button(bb, KEY_LEFT, kbd_keys[KEY_LEFT], LEFT, label_text)
    
    def create_page_up_button(self, bb, label_text):
        """ Create Page Up button
        
        :param bb: bounding box
        :param label_text: button label text
        
        :return: page up button
        """
        return self.create_arrow_button(bb, KEY_PAGE_UP, kbd_keys[KEY_PAGE_UP], RIGHT, label_text, 45)
    
    def create_page_down_button(self, bb, label_text):
        """ Create Page Down button
        
        :param bb: bounding box
        :param label_text: button label text
        
        :return: page down button
        """
        return self.create_arrow_button(bb, KEY_PAGE_DOWN, kbd_keys[KEY_PAGE_DOWN], LEFT, label_text, 45)
    
    def create_shutdown_button(self, bb):
        """ Create Shutdown button
        
        :param bb: bounding box
        
        :return: shutdown button
        """
        d = {}
        d["name"] = "shutdown"
        d["bounding_box"] = bb
        d["keyboard_key"] = kbd_keys[KEY_END]
        return self.create_toggle_button(**d)
   
        