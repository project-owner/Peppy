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

import json
import pygame
import logging

from ui.component import Component
from ui.container import Container
from util.keys import KEY_PLAY_FILE, KEY_STATIONS, KEY_PLAY_SITE
from util.config import USAGE, USE_BROWSER_STREAM_PLAYER, SCREEN_INFO, VOLUME, MUTE, PAUSE, \
    WIDTH, HEIGHT, STREAM_SERVER, STREAM_SERVER_PORT, COLORS, COLOR_WEB_BGR, PLAYER_SETTINGS, \
    AUDIO_FILES

class JsonFactory(object):
    """ Converts screen components into Json objects """
    
    def __init__(self, util, peppy):
        """ Initializer
        
        :param util: utility object contains config
        :param peppy: root object
        """
        self.util = util
        self.config = util.config
        self.peppy = peppy
    
    def screen_to_json(self, screen_name, screen):
        """ Convert screen object into Json object
        
        :param screen_name: the name of screen object
        :param screen: screen object
        """
        components = []
        s = {"type" : "screen"}
        s["name"] = "screen"
        s["bgr"] = self.color_to_hex(self.config[COLORS][COLOR_WEB_BGR])
        components.append(s)
        
        p = {"type" : "panel"}
        p["name"] = "panel"
        p["w"] = self.config[SCREEN_INFO][WIDTH]
        p["h"] = self.config[SCREEN_INFO][HEIGHT]
        if screen_name == "about":
            p["bgr"] = p["fgr"] = self.color_to_hex(self.config[COLORS][COLOR_WEB_BGR])
        else:
            p["bgr"] = p["fgr"] = self.color_to_hex((0, 0, 0))
        components.append(p)
        
        if screen_name == KEY_STATIONS or screen_name == KEY_PLAY_FILE or screen_name == AUDIO_FILES or screen_name == KEY_PLAY_SITE:
            components.extend(self.get_title_menu_screen_components(screen))
        else:            
            self.collect_components(components, screen)
        
        if self.config[USAGE][USE_BROWSER_STREAM_PLAYER]:
            components.append(self.get_stream_player_parameters())
        
        d = {"command" : "update_screen", "components" : components}
        e = json.dumps(d).encode(encoding="utf-8")
        return e

    def get_title_menu_screen_components(self, screen):
        """ Collects title and menu screen components
        
        :param screen: screen object
        
        :return: list of screen components
        """
        components = []
        tmp = []
        title = []
        menu = []        
        self.collect_components(tmp, screen)
        
        for i in tmp:
            if i:
                if "screen_title" in i["name"]:
                    title.append(i)
                elif "menu" in i["name"]:
                    menu.append(i)
                else:
                    components.append(i)
        
        components.append({"type" : "screen_title", "components" : title})        
        components.append({"type" : "screen_menu", "components" : menu})
        
        return components

    def title_to_json(self, title):
        """ Convert title object into Json object
        
        :param title: the title object
        
        :return: Json object
        """
        components = []
        ignore_visibility = False
        if self.peppy.current_screen == KEY_STATIONS:
            ignore_visibility = True
        self.collect_components(components, title, ignore_visibility)
        d = {"command" : "update_station_title", "components" : components}
        e = json.dumps(d).encode(encoding="utf-8")
        return e
    
    def file_player_title_to_json(self, title):
        """ Convert file player title to Json object
        
        :param title: title object
        
        :return: Json object
        """
        components = []
        ignore_visibility = False
        if self.peppy.current_screen == KEY_PLAY_FILE:
            ignore_visibility = True
        self.collect_components(components, title, ignore_visibility)
        d = {"command" : "update_file_player_title", "components" : components}
        e = json.dumps(d).encode(encoding="utf-8")
        return e

    def station_menu_to_json(self, menu):
        """ Convert station menu object into Json object
        
        :param menu: the station menu object
        
        :return: Json object
        """
        components = []
        self.collect_components(components, menu)
        d = {"command" : "update_station_menu", "components" : components}        
        e = json.dumps(d).encode(encoding="utf-8")
        return e
    
    def menu_to_json(self, menu):
        """ Convert menu object into Json object
        
        :param menu: menu object
        
        :return: Json object
        """
        components = []
        self.collect_components(components, menu)
        d = {"command" : "update_menu", "components" : components}        
        e = json.dumps(d).encode(encoding="utf-8")
        return e  

    def start_screensaver_to_json(self):
        """ Convert start screensaver event into Json object
        
        :return: Json object
        """
        d = {"command" : "start_screensaver"}        
        e = json.dumps(d).encode(encoding="utf-8")
        return e
    
    def stop_screensaver_to_json(self):
        """ Convert stop screensaver event into Json object
        
        :return: Json object
        """
        d = {"command" : "stop_screensaver"}        
        e = json.dumps(d).encode(encoding="utf-8")
        return e 

    def collect_components(self, components, container, ignore_visibility = False):
        """ Recursive method to collect container components
        
        :param components: component list where components will be collected
        :param container: container from which components will be collected
        :param ignore_visibility: True - collect invisible components, False - don't collect invisible components
        """
        if not ignore_visibility and not container.visible:
            return
        
        for item in container.components:
            if isinstance(item, Container):
                if ignore_visibility or item.visible:
                    self.collect_components(components, item)
            elif isinstance(item, Component):
                if ignore_visibility or item.visible:
                    j = self.component_to_json(item)
                    if j: components.append(j)

    def color_to_hex(self, color):
        """ Convert list of color numbers into its hex representation for web
        
        :param color: list of integre numbers
        
        :return: hex representation of the color defined by list of RGB values. Used for HTML
        """
        if not color:
            return None
        return "#%06x" % ((color[0] << 16) + (color[1] << 8) + color[2])

    def get_rectangle(self, component):
        """ Convert component into dictionary representing rectangle object
        
        :param component: the component
        
        :return: dictionary with rectangle attributes
        """
        c = {"type" : "rectangle"}
        c["name"] = component.name
        c["x"] = component.content_x
        c["y"] = component.content_y
        c["x"] = component.content.x
        c["y"] = component.content.y
        c["w"] = component.content.w + 1
        c["h"] = component.content.h + 1
        c["fgr"] = self.color_to_hex(component.fgr) 
        c["bgr"] = self.color_to_hex(component.bgr)
        return c
    
    def get_text(self, component):
        """ Convert text component into dictionary representing text object
        
        :param component: the component
        
        :return: dictionary with text attributes
        """
        c = {"type" : "text"}
        c["name"] = component.name
        c["label_type"] = getattr(component, "label_type", 0)
        c["x"] = component.content_x
        c["y"] = component.content_y
        c["text"] = component.text
        c["text_size"] = component.text_size
        text_color = getattr(component, "text_color_current", component.fgr)
        text_width = getattr(component, "text_width", None)
        if text_width:
            c["text_width"] = text_width
        c["text_color_current"] = self.color_to_hex(text_color)
        return c
    
    def get_image(self, component):
        """ Convert component into dictionary representing image object
        
        :param component: the component
        
        :return: dictionary with image attributes
        """
        c = {"type" : "image"}
        c["name"] = component.name
        img = component.content
        c["x"] = component.content_x
        c["y"] = component.content_y
        
        if isinstance(img, tuple):
            c["filename"] = img[0].replace('\\','/')
            img = img[1]                    
        else:
            if component.image_filename:
                c["filename"] = component.image_filename.replace('\\','/')
            else:
                return None
        
        c["w"] = img.get_width()
        c["h"] = img.get_height()
        
        if not c["filename"].startswith("http"):
            c["data"] = self.util.load_image(c["filename"], True)
        return c

    def component_to_json(self, component):
        """ Dispatcher method for converting components into Json dictionaries
        
        :param component: the component
        
        :return: dictionary with component specific attributes
        """
        if component.content:
            if component.text:
                return self.get_text(component)
            elif isinstance(component.content, pygame.Rect):
                return self.get_rectangle(component)
            else:
                return self.get_image(component)
    
    def container_to_json(self, cont):
        """ Convert container into Json objects
        
        :param cont: the container to convert
        
        :result: Json objects representing the components in the specified container
        """
        components = []
        
        if self.config[USAGE][USE_BROWSER_STREAM_PLAYER]:
            components.append(self.get_stream_player_parameters())
        
        self.collect_components(components, cont)
        d = {"command" : "update_element", "components" : components}
            
        e = json.dumps(d).encode(encoding="utf-8")
        
        logging.debug(e)
        return e
    
    def file_player_start_to_json(self):
        """ Start timer """
        
        d = {"command" : "start_timer"}
        e = json.dumps(d).encode(encoding="utf-8")        
        return e
    
    def file_player_stop_to_json(self):
        """ Stop timer """
        
        d = {"command" : "stop_timer"}
        e = json.dumps(d).encode(encoding="utf-8")        
        return e
    
    def get_stream_player_parameters(self):
        """ Add parameters for stream player
        
        :return: dictionary containing parameters
        """
        d = {"type" : "stream_player"}
        d["name"] =  "stream_player"
        d["port"] = self.config[STREAM_SERVER][STREAM_SERVER_PORT]
        d["volume"] = self.config[PLAYER_SETTINGS][VOLUME]
        d["mute"] = self.config[PLAYER_SETTINGS][MUTE]
        d["pause"] = self.config[PLAYER_SETTINGS][PAUSE]
        return d        
        
        