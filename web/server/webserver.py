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

import threading
from util.keys import WEB_SERVER, HTTP_PORT
from web.server.jsonfactory import JsonFactory
from http.server import HTTPServer
from web.server.requesthandler import RequestHandler
import web.server.requesthandler
import logging
import socket

class WebServer(object):
    """ Starts simple HTTPServer in a separate thread """
    
    def __init__(self, util, peppy):
        """ Initializer
        
        :param util: utility object contains configuration settings
        :param peppy: the reference to the root object
        """
        self.config = util.config
        self.peppy = peppy
        self.jason_factory = JsonFactory(util, peppy)
        self.web_server_thread = threading.Thread(target=self.start)
        self.web_server_thread.start()
    
    def get_ip(self):
        """ Returns current IP address """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 0))
            ip = s.getsockname()[0]
        except:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip
        
    def start(self):
        """ Prepares request handler and starts web server """
        
        host = self.get_ip()

        port = self.config[WEB_SERVER][HTTP_PORT]
        handler = RequestHandler
        
        handler.screen_to_json = self.screen_to_json        
        self.create_screen = handler.create_screen = web.server.requesthandler.create_screen
        
        handler.title_to_json = self.title_to_json        
        self.title_change = handler.update_title = web.server.requesthandler.update_title
        
        handler.volume_to_json = self.volume_to_json        
        self.volume_change = handler.update_volume = web.server.requesthandler.update_volume
        
        handler.genre_button_to_json = self.genre_button_to_json        
        self.genre_button_pressed = handler.update_genre_button = web.server.requesthandler.update_genre_button
        
        handler.home_button_to_json = self.home_button_to_json        
        self.home_button_pressed = handler.update_home_button = web.server.requesthandler.update_home_button
        
        handler.left_button_to_json = self.left_button_to_json        
        self.left_button_pressed = handler.update_left_button = web.server.requesthandler.update_left_button
        
        handler.page_down_button_to_json = self.page_down_button_to_json        
        self.page_down_button_pressed = handler.update_page_down_button = web.server.requesthandler.update_page_down_button
        
        handler.right_button_to_json = self.right_button_to_json        
        self.right_button_pressed = handler.update_right_button = web.server.requesthandler.update_right_button
        
        handler.page_up_button_to_json = self.page_up_button_to_json        
        self.page_up_button_pressed = handler.update_page_up_button = web.server.requesthandler.update_page_up_button
        
        handler.station_menu_to_json = self.station_menu_to_json        
        self.update_station_menu = handler.update_station_menu = web.server.requesthandler.update_station_menu
        
        handler.genre_menu_to_json = self.genre_menu_to_json        
        self.update_genre_menu = handler.update_genre_menu = web.server.requesthandler.update_genre_menu
        
        handler.home_menu_to_json = self.home_menu_to_json        
        self.update_home_menu = handler.update_home_menu = web.server.requesthandler.update_home_menu
        
        handler.language_menu_to_json = self.language_menu_to_json        
        self.update_language_menu = handler.update_language_menu = web.server.requesthandler.update_language_menu
        
        handler.saver_screen_to_json = self.saver_screen_to_json        
        self.update_saver_screen = handler.update_saver_menu = web.server.requesthandler.update_saver_screen
        
        handler.about_screen_to_json = self.about_screen_to_json        
        self.update_about_screen = handler.update_about_screen = web.server.requesthandler.update_about_screen
        
        self.mode_listener = handler.mode_listener = web.server.requesthandler.mode_listener
        
        handler.play_button_to_json = self.play_button_to_json        
        self.play_button_pressed = handler.update_play_button = web.server.requesthandler.update_play_button
        
        handler.shutdown_button_to_json = self.shutdown_button_to_json        
        self.shutdown_button_pressed = handler.update_shutdown_button = web.server.requesthandler.update_shutdown_button
        
        handler.start_screensaver_to_json = self.start_screensaver_to_json
        handler.stop_screensaver_to_json = self.stop_screensaver_to_json
        self.start_screensaver = handler.start_screensaver = web.server.requesthandler.start_screensaver
        self.stop_screensaver = handler.stop_screensaver = web.server.requesthandler.stop_screensaver
        
        self.web_server = HTTPServer((host, int(port)), handler)        
        logging.debug("Web Server Started at %s:%s", host, port)
        
        try:
            self.web_server.serve_forever()
        except:
            pass

    def get_station_screen(self):
        """ Return Station Screen
        
        :return: the reference to the Station Screen
        """
        return self.peppy.screens["stations"]
    
    def get_genre_screen(self):
        """ Return Genre Screen
        
        :return: the reference to the Genre Screen
        """
        return self.peppy.screens["genres"]
    
    def get_home_screen(self):
        """ Return Home Screen
        
        :return: the reference to the Home Screen
        """
        return self.peppy.screens["home"]
    
    def get_language_screen(self):
        """ Return Language Screen
        
        :return: the reference to the Language Screen
        """
        return self.peppy.screens["language"]
    
    def get_saver_screen(self):
        """ Return Screensaver Screen
        
        :return: the reference to the Screensaver Screen
        """
        return self.peppy.screens["saver"]
    
    def get_about_screen(self):
        """ Return About Screen
        
        :return: the reference to the About Screen
        """
        return self.peppy.screens["about"]

    def screen_to_json(self):
        """ Convert current screen to JSON objects
        
        :return: list of JSON objects representing current screen
        """
        if self.peppy.screensaver_dispatcher.saver_running:
            self.peppy.screensaver_dispatcher.cancel_screensaver()
            self.peppy.screensaver_dispatcher.restart_dispatcher_thread()     
        current_screen = self.peppy.current_screen
        screen = self.peppy.screens[current_screen]        
        return self.jason_factory.screen_to_json(current_screen, screen)    
    
    def title_to_json(self):
        """ Convert title object into JSON object
        
        :return: JSON object
        """
        return self.jason_factory.title_to_json(self.get_station_screen().screen_title)
        
    def volume_to_json(self):
        """ Convert volume object into JSON object
        
        :return: JSON object
        """
        return self.jason_factory.container_to_json(self.get_station_screen().volume)
        
    def genre_button_to_json(self):
        """ Convert genre button into JSON object
        
        :return: JSON object
        """
        return self.jason_factory.container_to_json(self.get_station_screen().genres_button)
    
    def home_button_to_json(self):
        """ Convert home button into JSON object
        
        :return: JSON object
        """
        return self.jason_factory.container_to_json(self.get_station_screen().home_button)
        
    def left_button_to_json(self):
        """ Convert left button into JSON object
        
        :return: JSON object
        """
        return self.jason_factory.container_to_json(self.get_station_screen().left_button)
        
    def page_down_button_to_json(self):
        """ Convert page down button into JSON object
        
        :return: JSON object
        """
        return self.jason_factory.container_to_json(self.get_station_screen().page_down_button)
        
    def right_button_to_json(self):
        """ Convert right button into JSON object
        
        :return: JSON object
        """
        return self.jason_factory.container_to_json(self.get_station_screen().right_button)
        
    def page_up_button_to_json(self):
        """ Convert page up button into JSON object
        
        :return: JSON object
        """
        return self.jason_factory.container_to_json(self.get_station_screen().page_up_button)
        
    def station_menu_to_json(self):
        """ Convert station menu into JSON object
        
        :return: JSON object
        """
        return self.jason_factory.station_menu_to_json(self.get_station_screen().station_menu)
        
    def play_button_to_json(self):
        """ Convert play button into JSON object
        
        :return: JSON object
        """
        return self.jason_factory.container_to_json(self.get_station_screen().play_button)
        
    def shutdown_button_to_json(self):
        """ Convert shutdown button into JSON object
        
        :return: JSON object
        """
        return self.jason_factory.container_to_json(self.get_station_screen().shutdown_button)
    
    def genre_menu_to_json(self):
        """ Convert genre menu into JSON object
        
        :return: JSON object
        """
        return self.jason_factory.genre_menu_to_json(self.get_genre_screen().genre_menu)
        
    def home_menu_to_json(self):
        """ Convert home menu into JSON object
        
        :return: JSON object
        """
        return self.jason_factory.home_menu_to_json(self.get_home_screen().home_menu)
    
    def language_menu_to_json(self):
        """ Convert language menu into JSON object
        
        :return: JSON object
        """
        return self.jason_factory.language_menu_to_json(self.get_language_screen().language_menu)
        
    def saver_screen_to_json(self):
        """ Convert screensaver screen into JSON object
        
        :return: JSON object
        """
        return self.jason_factory.saver_screen_to_json(self.get_saver_screen())
    
    def about_screen_to_json(self):
        """ Convert about screen into JSON object
        
        :return: JSON object
        """
        return self.jason_factory.about_screen_to_json(self.get_about_screen())
    
    def start_screensaver_to_json(self):
        """ Convert start screensaver event into JSON object
        
        :return: JSON object
        """
        return self.jason_factory.start_screensaver_to_json()
    
    def stop_screensaver_to_json(self):
        """ Convert stop screensaver event into JSON object
        
        :return: JSON object
        """
        return self.jason_factory.stop_screensaver_to_json()

    def add_station_screen_web_listeners(self, stations):
        """ Add web listeners to station screen components
        
        :param stations: the stations screen
        """
        stations.screen_title.add_listener(self.title_change)
            
        stations.volume.add_slide_listener(self.volume_change)
        stations.volume.add_knob_listener(self.volume_change)
        stations.volume.add_press_listener(self.volume_change)
        stations.volume.add_motion_listener(self.volume_change)
            
        stations.genres_button.add_press_listener(self.genre_button_pressed)
        stations.genres_button.add_release_listener(self.create_screen)
            
        stations.home_button.add_press_listener(self.home_button_pressed)
        stations.home_button.add_release_listener(self.create_screen)
            
        stations.station_menu.add_menu_click_listener(self.update_station_menu)
        stations.station_menu.add_menu_click_listener(self.left_button_pressed)
        stations.station_menu.add_menu_click_listener(self.right_button_pressed)
        stations.station_menu.add_menu_click_listener(self.page_down_button_pressed)
        stations.station_menu.add_menu_click_listener(self.page_up_button_pressed)
        stations.station_menu.add_mode_listener(self.mode_listener)
            
        stations.left_button.add_press_listener(self.left_button_pressed)
        stations.left_button.add_release_listener(self.left_button_pressed)
        stations.left_button.add_release_listener(self.update_station_menu)
        stations.left_button.add_release_listener(self.right_button_pressed)
            
        stations.page_down_button.add_press_listener(self.page_down_button_pressed)
        stations.page_down_button.add_release_listener(self.page_down_button_pressed)
        stations.page_down_button.add_release_listener(self.update_station_menu)
        stations.page_down_button.add_release_listener(self.page_up_button_pressed)
            
        stations.right_button.add_press_listener(self.right_button_pressed)
        stations.right_button.add_release_listener(self.right_button_pressed)
        stations.right_button.add_release_listener(self.update_station_menu)
        stations.right_button.add_release_listener(self.left_button_pressed)
            
        stations.page_up_button.add_press_listener(self.page_up_button_pressed)
        stations.page_up_button.add_release_listener(self.page_up_button_pressed)
        stations.page_up_button.add_release_listener(self.update_station_menu)
        stations.page_up_button.add_release_listener(self.page_down_button_pressed)
            
        stations.play_button.add_press_listener(self.play_button_pressed)
        stations.play_button.add_release_listener(self.play_button_pressed)
            
        stations.shutdown_button.add_press_listener(self.shutdown_button_pressed)
        stations.shutdown_button.add_release_listener(self.shutdown_button_pressed)
        stations.shutdown_button.add_cancel_listener(self.shutdown_button_pressed)
        
    def add_genre_screen_web_listeners(self, genres):
        """ Add web listeners to genre screen components
        
        :param genres: the genres screen
        """
        genres.genre_menu.add_listener(self.create_screen)
        genres.genre_menu.add_move_listener(self.update_genre_menu)
    
    def add_home_screen_web_listeners(self, home):
        """ Add web listeners to home screen components
        
        :param home: the home screen
        """
        home.home_menu.add_listener(self.create_screen)
        home.home_menu.add_move_listener(self.update_home_menu)
        
    def add_language_screen_web_listeners(self, language):
        """ Add web listeners to language screen components
        
        :param language: the language screen
        """
        language.language_menu.add_listener(self.create_screen)
        language.language_menu.add_move_listener(self.update_language_menu)
        
    def add_saver_screen_web_listeners(self, saver):
        """ Add web listeners to screensaver screen components
        
        :param saver: the screensaver screen
        """
        saver.saver_menu.add_listener(self.create_screen)
        saver.delay_menu.add_listener(self.create_screen)
        saver.saver_menu.add_move_listener(self.update_saver_screen)
        saver.delay_menu.add_move_listener(self.update_saver_screen)
        
    def add_about_screen_web_listeners(self, about):
        """ Add web listeners to about screen
        
        :param about: the about screen
        """
        about.add_listener(self.create_screen)
        
    def add_screensaver_web_listener(self, screensaver_dispatcher):
        """ Add web listeners to screensaver start and stop events
        
        :param screensaver_dispatcher: the screensaver dispatcher
        """
        screensaver_dispatcher.add_start_listener(self.start_screensaver)
        screensaver_dispatcher.add_stop_listener(self.stop_screensaver)
    
    def shutdown(self):
        """ Shutdown Web Server """
        
        self.web_server.socket.close()
        
        