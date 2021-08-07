# Copyright 2016-2021 Peppy Player peppy.player@gmail.com
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

import pygame
import random

from ui.component import Component
from ui.container import Container
from util.keys import KEY_PLAY_FILE, KEY_STATIONS
from util.config import USAGE, USE_BROWSER_STREAM_PLAYER, SCREEN_INFO, VOLUME, MUTE, PAUSE, \
    WIDTH, HEIGHT, STREAM_SERVER, STREAM_SERVER_PORT, COLORS, PLAYER_SETTINGS, \
    GENERATED_IMAGE, BGR_TYPE_IMAGE, BACKGROUND, WEB_BGR_NAMES, BACKGROUND_DEFINITIONS, \
    BGR_FILENAME, OVERLAY_COLOR, WEB_BGR_BLUR_RADIUS, OVERLAY_OPACITY, COLOR_WEB_BGR, WEB_SCREEN_COLOR

class JsonFactory(object):
    """ Converts screen components into Json objects """
    
    def __init__(self, util, peppy):
        """ Initializer
        
        :param util: utility object contains config
        :param peppy: root object
        """
        self.util = util
        self.config = util.config
        self.image_util = util.image_util
        self.peppy = peppy
    
    def screen_to_json(self, screen_name, screen, command=True):
        """ Convert screen object into Json object
        
        :param screen_name: the name of screen object
        :param screen: screen object
        :param command: True - add command to output, False - don't add command
        """
        components = []
        s = {"type" : "screen"}
        s["name"] = "screen"
        s["bgr"] = self.image_util.color_to_hex(self.config[BACKGROUND][WEB_SCREEN_COLOR])
        self.set_web_bgr(screen, s)
        components.append(s)
        
        p = {"type" : "panel"}
        p["name"] = "panel"
        p["w"] = self.config[SCREEN_INFO][WIDTH]
        p["h"] = self.config[SCREEN_INFO][HEIGHT]
        p["bgr_type"] = getattr(screen, "bgr_type", "color")

        c = self.config[BACKGROUND][WEB_SCREEN_COLOR]
        if c and c[3] == 0:
            p["bgr_type"] = "color"

        if p["bgr_type"] == BGR_TYPE_IMAGE:
            p["bgr"] = self.get_image(screen)
        else:
            p["bgr"] = p["fgr"] = self.image_util.color_to_hex(self.config[BACKGROUND][WEB_SCREEN_COLOR])

        components.append(p)
        
        if getattr(screen, "animated_title", False):
            components.extend(self.get_title_menu_screen_components(screen))
        else:            
            self.collect_components(components, screen)
        
        if self.config[USAGE][USE_BROWSER_STREAM_PLAYER]:
            components.append(self.get_stream_player_parameters())
        
        if command:
            return {"command" : "update_screen", "components" : components}
        else:
            return {"components" : components}

    def set_web_bgr(self, screen, state):
        """ Prepare web background

        :param screen: screen object
        :param state: state dictionary
        """
        key = None
        web_bgr = self.config[BACKGROUND][WEB_BGR_NAMES]
        
        if web_bgr and len(web_bgr[0]) != 0:
            key = web_bgr[random.randrange(0, len(web_bgr))]                
        else:
            key = getattr(screen, "bgr_key", None)

        if key == None:
            c = self.config[COLORS][COLOR_WEB_BGR]
            state["bgr"] = self.image_util.color_to_hex(c)
            return

        definitions = self.config[BACKGROUND_DEFINITIONS] 
        definition = definitions[key]
        filename = "backgrounds/" + definition[BGR_FILENAME]
        state["original_image_filename"] = filename
        state["bgr_base_color"] = self.image_util.color_to_hex(definition[OVERLAY_COLOR])
        state["bgr_blur"] = definition[WEB_BGR_BLUR_RADIUS]
        state["bgr_opacity"] = definition[OVERLAY_OPACITY] / 255

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
                elif "menu" in i["name"] or i["name"].endswith(".fav"):
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
        return {"command" : "update_station_title", "components" : components}
    
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
        return {"command" : "update_file_player_title", "components" : components}

    def station_menu_to_json(self, menu):
        """ Convert station menu object into Json object
        
        :param menu: the station menu object
        
        :return: Json object
        """
        components = []
        self.collect_components(components, menu)
        return {"command" : "update_station_menu", "components" : components}        
    
    def menu_to_json(self, menu):
        """ Convert menu object into Json object
        
        :param menu: menu object
        
        :return: Json object
        """
        components = []
        self.collect_components(components, menu)
        return {"command" : "update_menu", "components" : components}        

    def start_screensaver_to_json(self):
        """ Convert start screensaver event into Json object
        
        :return: Json object
        """
        return {"command" : "start_screensaver"}        
    
    def stop_screensaver_to_json(self):
        """ Convert stop screensaver event into Json object
        
        :return: Json object
        """
        return {"command" : "stop_screensaver"}        

    def collect_components(self, components, container, ignore_visibility = False):
        """ Recursive method to collect container components
        
        :param components: component list where components will be collected
        :param container: container from which components will be collected
        :param ignore_visibility: True - collect invisible components, False - don't collect invisible components
        """
        if (not ignore_visibility and not container.visible) or container.is_empty():
            return
        
        for item in container.components:
            if isinstance(item, Container):
                if ignore_visibility or item.visible:
                    self.collect_components(components, item)
            elif isinstance(item, Component):
                if ignore_visibility or item.visible:
                    j = self.component_to_json(item)
                    if j: components.append(j)

    def get_rectangle(self, component):
        """ Convert component into dictionary representing rectangle object
        
        :param component: the component
        
        :return: dictionary with rectangle attributes
        """
        c = {"type" : "rectangle"}
        c["name"] = component.name
        c["x"] = component.content.x
        c["y"] = component.content.y
        c["w"] = component.content.w
        c["h"] = component.content.h
        c["t"] = component.border_thickness
        c["fgr"] = self.image_util.color_to_hex(component.fgr) 
        c["bgr"] = self.image_util.color_to_hex(component.bgr)
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
        c["text_color_current"] = self.image_util.color_to_hex(text_color)
        c["pause"] = self.config[PLAYER_SETTINGS][PAUSE]

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
            if img[0] and img[1]:
                c["filename"] = img[0].replace('\\','/')
                img = img[1]
            else:
                return None
        else:
            if component.image_filename:
                c["filename"] = component.image_filename.replace('\\','/')
            else:
                return None
                
        c["w"] = img.get_width()
        c["h"] = img.get_height()

        if c["filename"].startswith(GENERATED_IMAGE):
            c["data"] = self.image_util.get_base64_surface(img)
            return c
        
        if not c["filename"].startswith("http"):
            c["data"] = self.image_util.load_image(c["filename"], True)
        
        if "_" in c["filename"] and not c["filename"].startswith("http"):
            c["filename"] = c["filename"][0 : c["filename"].find("_")]

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
        
        return d
    
    def file_player_start_to_json(self):
        """ Start timer """
        
        d = {"command" : "start_timer"}
        return d
    
    def file_player_stop_to_json(self):
        """ Stop timer """
        
        d = {"command" : "stop_timer"}
        return d
    
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
        