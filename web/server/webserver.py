# Copyright 2016-2017 Peppy Player peppy.player@gmail.com
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
from util.keys import WEB_SERVER, HTTP_PORT, KEY_AUDIO_FILES, KEY_PLAY_FILE, KEY_STATIONS, KEY_GENRES, KEY_HOME
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
        self.json_factory = JsonFactory(util, peppy)
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
        
        handler = self.prepare_request_handler()
        host = self.get_ip()
        port = self.config[WEB_SERVER][HTTP_PORT]
        self.web_server = HTTPServer((host, int(port)), handler)        
        logging.debug("Web Server Started at %s:%s", host, port)
        
        try:
            self.web_server.serve_forever()
        except:
            pass

    def prepare_request_handler(self):
        """ Create request handler
        
        :return: request handler
        """
        
        handler = RequestHandler
        
        handler.screen_to_json = self.screen_to_json        
        self.create_screen = handler.create_screen = web.server.requesthandler.create_screen
        
        self.prepare_stations_handler(handler)        
        self.prepare_genre_screen_handler(handler)
        self.prepare_home_screen_handler(handler)
        self.prepare_language_screen_handler(handler)
        self.prepare_saver_screen_handler(handler)
        self.prepare_about_screen_handler(handler)
        self.prepare_start_saver(handler)
        self.prepare_stop_saver(handler)
        self.prepare_file_player_handler(handler)
        self.prepare_file_browser_handler(handler)
        
        return handler

    def prepare_stations_handler(self, handler):
        """ Add station screen specific handlers to provided handler 
        
        :param handler: request handler
        """
        handler.title_to_json = self.title_to_json
        rh = web.server.requesthandler
                
        self.title_change = handler.update_title = rh.update_title
        
        handler.volume_to_json = self.volume_to_json        
        self.volume_change = handler.update_volume = rh.update_volume
        
        handler.genre_button_to_json = self.genre_button_to_json        
        self.genre_button_pressed = handler.update_genre_button = rh.update_genre_button
        
        handler.home_button_to_json = self.home_button_to_json        
        self.home_button_pressed = handler.update_home_button = rh.update_home_button
        
        handler.left_button_to_json = self.left_button_to_json        
        self.left_button_pressed = handler.update_left_button = rh.update_left_button
        
        handler.page_down_button_to_json = self.page_down_button_to_json        
        self.page_down_button_pressed = handler.update_page_down_button = rh.update_page_down_button
        
        handler.right_button_to_json = self.right_button_to_json        
        self.right_button_pressed = handler.update_right_button = rh.update_right_button
        
        handler.page_up_button_to_json = self.page_up_button_to_json        
        self.page_up_button_pressed = handler.update_page_up_button = rh.update_page_up_button
        
        handler.station_menu_to_json = self.station_menu_to_json        
        self.update_station_menu = handler.update_station_menu = rh.update_station_menu
        
        self.mode_listener = handler.mode_listener = rh.mode_listener
        
        handler.play_button_to_json = self.play_button_to_json        
        self.play_button_pressed = handler.update_play_button = rh.update_play_button
        
        handler.shutdown_button_to_json = self.shutdown_button_to_json        
        self.shutdown_button_pressed = handler.update_shutdown_button = rh.update_shutdown_button

    def prepare_genre_screen_handler(self, handler):
        """ Add genre screen specific handlers to provided handler 
        
        :param handler: request handler
        """
        rh = web.server.requesthandler
        handler.genre_menu_to_json = self.genre_menu_to_json        
        self.update_genre_menu = handler.update_genre_menu = rh.update_genre_menu

    def prepare_home_screen_handler(self, handler):
        """ Add home screen specific handlers to provided handler 
        
        :param handler: request handler
        """
        rh = web.server.requesthandler
        handler.home_menu_to_json = self.home_menu_to_json        
        self.update_home_menu = handler.update_home_menu = rh.update_home_menu

    def prepare_language_screen_handler(self, handler):
        """ Add language screen specific handlers to provided handler 
        
        :param handler: request handler
        """
        rh = web.server.requesthandler
        handler.language_menu_to_json = self.language_menu_to_json        
        self.update_language_menu = handler.update_language_menu = rh.update_language_menu

    def prepare_saver_screen_handler(self, handler):
        """ Add screensaver screen specific handlers to provided handler 
        
        :param handler: request handler
        """
        rh = web.server.requesthandler
        handler.saver_screen_to_json = self.saver_screen_to_json        
        self.update_saver_screen = handler.update_saver_menu = rh.update_saver_screen

    def prepare_about_screen_handler(self, handler):
        """ Add about screen specific handlers to provided handler 
        
        :param handler: request handler
        """
        rh = web.server.requesthandler
        handler.about_screen_to_json = self.about_screen_to_json        
        self.update_about_screen = handler.update_about_screen = rh.update_about_screen

    def prepare_start_saver(self, handler):
        """ Add start screensaver handlers to provided handler 
        
        :param handler: request handler
        """
        rh = web.server.requesthandler
        handler.start_screensaver_to_json = self.start_screensaver_to_json
        self.start_screensaver = handler.start_screensaver = rh.start_screensaver

    def prepare_stop_saver(self, handler):
        """ Add stop screensaver handlers to provided handler 
        
        :param handler: request handler
        """
        rh = web.server.requesthandler
        handler.stop_screensaver_to_json = self.stop_screensaver_to_json        
        self.stop_screensaver = handler.stop_screensaver = rh.stop_screensaver

    def prepare_file_player_handler(self, handler):
        """ Add file player screen handlers to provided handler 
        
        :param handler: request handler
        """
        rh = web.server.requesthandler
        handler.file_player_title_to_json = self.file_player_title_to_json        
        self.file_player_title_change = handler.update_file_player_title = rh.update_file_player_title
        
        handler.file_player_left_button_to_json = self.file_player_left_button_to_json        
        self.file_player_left_button_pressed = handler.update_file_player_left_button = rh.update_file_player_left_button

        handler.file_player_right_button_to_json = self.file_player_right_button_to_json        
        self.file_player_right_button_pressed = handler.update_file_player_right_button = rh.update_file_player_right_button
        
        handler.file_player_time_volume_button_to_json = self.file_player_time_volume_button_to_json        
        self.file_player_time_volume_button_pressed = handler.update_file_player_time_volume_button = rh.update_file_player_time_volume_button
        
        handler.file_player_file_button_to_json = self.file_player_file_button_to_json        
        self.file_player_file_button_pressed = handler.update_file_player_file_button = rh.update_file_player_file_button
        
        handler.file_player_home_button_to_json = self.file_player_home_button_to_json        
        self.file_player_home_button_pressed = handler.update_file_player_home_button = rh.update_file_player_home_button
        
        handler.file_player_shutdown_button_to_json = self.file_player_shutdown_button_to_json        
        self.file_player_shutdown_button_pressed = handler.update_file_player_shutdown_button = rh.update_file_player_shutdown_button
        
        handler.file_player_play_button_to_json = self.file_player_play_button_to_json        
        self.file_player_play_button_pressed = handler.update_file_player_play_button = rh.update_file_player_play_button
        
        handler.file_player_volume_to_json = self.file_player_volume_to_json
        self.file_player_volume_change = handler.update_file_player_volume = rh.update_file_player_volume
        
        handler.file_player_time_control_to_json = self.file_player_time_control_to_json
        self.file_player_time_control_change = handler.update_file_player_time_control = rh.update_file_player_time_control

    def prepare_file_browser_handler(self, handler):
        """ Add file browser screen handlers to provided handler 
        
        :param handler: request handler
        """
        rh = web.server.requesthandler
        handler.file_browser_left_button_to_json = self.file_browser_left_button_to_json        
        self.file_browser_left_button_pressed = handler.update_file_browser_left_button = rh.update_file_browser_left_button
        
        handler.file_browser_right_button_to_json = self.file_browser_right_button_to_json        
        self.file_browser_right_button_pressed = handler.update_file_browser_right_button = rh.update_file_browser_right_button

        handler.file_browser_home_button_to_json = self.file_browser_home_button_to_json        
        self.file_browser_home_button_pressed = handler.update_file_browser_home_button = rh.update_file_browser_home_button
        
        handler.file_browser_user_home_button_to_json = self.file_browser_user_home_button_to_json        
        self.file_browser_user_home_button_pressed = handler.update_file_browser_user_home_button = rh.update_file_browser_user_home_button

        handler.file_browser_root_button_to_json = self.file_browser_root_button_to_json        
        self.file_browser_root_button_pressed = handler.update_file_browser_root_button = rh.update_file_browser_root_button
        
        handler.file_browser_parent_button_to_json = self.file_browser_parent_button_to_json        
        self.file_browser_parent_button_pressed = handler.update_file_browser_parent_button = rh.update_file_browser_parent_button

        handler.file_browser_back_button_to_json = self.file_browser_back_button_to_json        
        self.file_browser_back_button_pressed = handler.update_file_browser_back_button = rh.update_file_browser_back_button

        handler.file_browser_file_menu_menu_to_json = self.file_browser_file_menu_to_json        
        self.file_browser_update_file_menu = handler.update_file_browser_file_menu = rh.update_file_browser_file_menu

    def get_station_screen(self):
        """ Return Station Screen
        
        :return: the reference to the Station Screen
        """
        return self.peppy.screens[KEY_STATIONS]
    
    def get_genre_screen(self):
        """ Return Genre Screen
        
        :return: the reference to the Genre Screen
        """
        return self.peppy.screens[KEY_GENRES]
    
    def get_home_screen(self):
        """ Return Home Screen
        
        :return: the reference to the Home Screen
        """
        return self.peppy.screens[KEY_HOME]
    
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
    
    def get_file_player_screen(self):
        """ Return File Player Screen
        
        :return: the reference to the File Player Screen
        """
        return self.peppy.screens[KEY_PLAY_FILE]
    
    def get_file_browser_screen(self):
        """ Return File Browser Screen
        
        :return: the reference to the File Browser Screen
        """
        return self.peppy.screens[KEY_AUDIO_FILES]

    def screen_to_json(self):
        """ Convert current screen to JSON objects
        
        :return: list of JSON objects representing current screen
        """
        if self.peppy.screensaver_dispatcher.saver_running:
            self.peppy.screensaver_dispatcher.cancel_screensaver()
            self.peppy.screensaver_dispatcher.restart_dispatcher_thread()     
        current_screen = self.peppy.current_screen
        screen = self.peppy.screens[current_screen]
        return self.json_factory.screen_to_json(current_screen, screen)    
    
    def title_to_json(self):
        """ Convert title object into JSON object
        
        :return: JSON object
        """
        if self.get_station_screen().visible == False:
            return None
        else:
            return self.json_factory.title_to_json(self.get_station_screen().screen_title)
    
    def file_player_title_to_json(self):
        """ Convert file player title object into JSON object
        
        :return: JSON object
        """
        if self.get_file_player_screen().visible == False:
            return None
        else:
            return self.json_factory.file_player_title_to_json(self.get_file_player_screen().screen_title)
    
    def file_player_left_button_to_json(self):
        """ Convert file player left button object into JSON object
        
        :return: JSON object
        """
        if self.get_file_player_screen().visible == False:
            return None
        else:
            return self.json_factory.container_to_json(self.get_file_player_screen().left_button)
    
    def file_player_right_button_to_json(self):
        """ Convert file player right button object into JSON object
        
        :return: JSON object
        """
        if self.get_file_player_screen().visible == False:
            return None
        else:
            return self.json_factory.container_to_json(self.get_file_player_screen().right_button)
    
    def file_player_time_volume_button_to_json(self):
        """ Convert file player time/volume button object into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_file_player_screen().time_volume_button)
    
    def file_player_file_button_to_json(self):
        """ Convert file player file button object into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_file_player_screen().file_button)
    
    def file_player_home_button_to_json(self):
        """ Convert file player home button object into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_file_player_screen().home_button)
    
    def file_player_shutdown_button_to_json(self):
        """ Convert file player shutdown button object into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_file_player_screen().shutdown_button)
    
    def file_player_play_button_to_json(self):
        """ Convert file player play button object into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_file_player_screen().play_button)
    
    def file_player_volume_to_json(self):
        """ Convert file player volume button object into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_file_player_screen().volume)
    
    def file_player_time_control_to_json(self):
        """ Convert file player time control object into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_file_player_screen().time_control)
        
    def file_browser_left_button_to_json(self):
        """ Convert file browser left button object into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_file_browser_screen().navigator.left_button)
    
    def file_browser_right_button_to_json(self):
        """ Convert file browser right button object into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_file_browser_screen().navigator.right_button)
    
    def file_browser_home_button_to_json(self):
        """ Convert file browser home button object into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_file_browser_screen().navigator.home_button)
    
    def file_browser_user_home_button_to_json(self):
        """ Convert file browser user home button object into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_file_browser_screen().navigator.user_home_button)
    
    def file_browser_root_button_to_json(self):
        """ Convert file browser root button object into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_file_browser_screen().navigator.root_button)
    
    def file_browser_parent_button_to_json(self):
        """ Convert file browser parent button object into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_file_browser_screen().navigator.parent_button)
    
    def file_browser_back_button_to_json(self):
        """ Convert file browser back button object into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_file_browser_screen().navigator.back_button)
    
    def file_browser_file_menu_to_json(self):
        """ Convert file browser menu object into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_file_browser_screen().file_menu)
        
    def volume_to_json(self):
        """ Convert volume object into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_station_screen().volume)
        
    def genre_button_to_json(self):
        """ Convert genre button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_station_screen().genres_button)
    
    def home_button_to_json(self):
        """ Convert home button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_station_screen().home_button)
        
    def left_button_to_json(self):
        """ Convert left button into JSON object
        
        :return: JSON object
        """
        if self.get_station_screen().visible == False:
            return None
        else:
            return self.json_factory.container_to_json(self.get_station_screen().left_button)
        
    def page_down_button_to_json(self):
        """ Convert page down button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_station_screen().page_down_button)
        
    def right_button_to_json(self):
        """ Convert right button into JSON object
        
        :return: JSON object
        """
        if self.get_station_screen().visible == False:
            return None
        else:
            return self.json_factory.container_to_json(self.get_station_screen().right_button)
        
    def page_up_button_to_json(self):
        """ Convert page up button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_station_screen().page_up_button)
        
    def station_menu_to_json(self):
        """ Convert station menu into JSON object
        
        :return: JSON object
        """
        return self.json_factory.station_menu_to_json(self.get_station_screen().station_menu)
        
    def play_button_to_json(self):
        """ Convert play button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_station_screen().play_button)
        
    def shutdown_button_to_json(self):
        """ Convert shutdown button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_station_screen().shutdown_button)
    
    def genre_menu_to_json(self):
        """ Convert genre menu into JSON object
        
        :return: JSON object
        """
        return self.json_factory.genre_menu_to_json(self.get_genre_screen().genre_menu)
        
    def home_menu_to_json(self):
        """ Convert home menu into JSON object
        
        :return: JSON object
        """
        return self.json_factory.home_menu_to_json(self.get_home_screen().home_menu)
    
    def language_menu_to_json(self):
        """ Convert language menu into JSON object
        
        :return: JSON object
        """
        return self.json_factory.language_menu_to_json(self.get_language_screen().language_menu)
        
    def saver_screen_to_json(self):
        """ Convert screensaver screen into JSON object
        
        :return: JSON object
        """
        return self.json_factory.saver_screen_to_json(self.get_saver_screen())
    
    def about_screen_to_json(self):
        """ Convert about screen into JSON object
        
        :return: JSON object
        """
        return self.json_factory.about_screen_to_json(self.get_about_screen())
    
    def start_screensaver_to_json(self):
        """ Convert start screensaver event into JSON object
        
        :return: JSON object
        """
        return self.json_factory.start_screensaver_to_json()
    
    def stop_screensaver_to_json(self):
        """ Convert stop screensaver event into JSON object
        
        :return: JSON object
        """
        return self.json_factory.stop_screensaver_to_json()

    def add_station_screen_web_listeners(self, stations):
        """ Add web listeners to station screen components
        
        :param stations: the stations screen
        """
        stations.screen_title.add_listener(self.title_change)
        
        vb = stations.volume
        vb.add_slide_listener(self.volume_change)
        vb.add_knob_listener(self.volume_change)
        vb.add_press_listener(self.volume_change)
        vb.add_motion_listener(self.volume_change)
        
        gb = stations.genres_button
        gb.add_press_listener(self.genre_button_pressed)
        gb.add_release_listener(self.create_screen)
        
        hb = stations.home_button
        hb.add_press_listener(self.home_button_pressed)
        hb.add_release_listener(self.create_screen)
        
        sm = stations.station_menu
        sm.add_menu_click_listener(self.update_station_menu)
        sm.add_menu_click_listener(self.left_button_pressed)
        sm.add_menu_click_listener(self.right_button_pressed)
        sm.add_menu_click_listener(self.page_down_button_pressed)
        sm.add_menu_click_listener(self.page_up_button_pressed)
        sm.add_mode_listener(self.mode_listener)
        
        lb = stations.left_button
        lb.add_press_listener(self.left_button_pressed)
        lb.add_release_listener(self.left_button_pressed)
        lb.add_release_listener(self.update_station_menu)
        lb.add_release_listener(self.right_button_pressed)
        
        db = stations.page_down_button
        db.add_press_listener(self.page_down_button_pressed)
        db.add_release_listener(self.page_down_button_pressed)
        db.add_release_listener(self.update_station_menu)
        db.add_release_listener(self.page_up_button_pressed)
        
        rb = stations.right_button
        rb.add_press_listener(self.right_button_pressed)
        rb.add_release_listener(self.right_button_pressed)
        rb.add_release_listener(self.update_station_menu)
        rb.add_release_listener(self.left_button_pressed)
        
        ub = stations.page_up_button
        ub.add_press_listener(self.page_up_button_pressed)
        ub.add_release_listener(self.page_up_button_pressed)
        ub.add_release_listener(self.update_station_menu)
        ub.add_release_listener(self.page_down_button_pressed)
        
        pb = stations.play_button
        pb.add_press_listener(self.play_button_pressed)
        pb.add_release_listener(self.play_button_pressed)
        
        sb = stations.shutdown_button
        sb.add_press_listener(self.shutdown_button_pressed)
        sb.add_release_listener(self.shutdown_button_pressed)
        sb.add_cancel_listener(self.shutdown_button_pressed)
        
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
        saver.home_button.add_release_listener(self.create_screen)
        
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
    
    def add_file_player_web_listeners(self, file_player):
        """ Add web listeners to file player
        
        :param file_player: file player
        """
        file_player.screen_title.add_listener(self.file_player_title_change)
        
        sb = file_player.shutdown_button
        sb.add_press_listener(self.file_player_shutdown_button_pressed)
        sb.add_release_listener(self.file_player_shutdown_button_pressed)
        sb.add_cancel_listener(self.file_player_shutdown_button_pressed)
        
        pb = file_player.play_button
        pb.add_press_listener(self.file_player_play_button_pressed)
        pb.add_release_listener(self.file_player_play_button_pressed)
        
        hb = file_player.home_button
        hb.add_press_listener(self.file_player_home_button_pressed)
        hb.add_release_listener(self.create_screen)
        
        vb = file_player.volume
        vb.add_slide_listener(self.file_player_volume_change)
        vb.add_knob_listener(self.file_player_volume_change)
        vb.add_press_listener(self.file_player_volume_change)
        vb.add_motion_listener(self.file_player_volume_change)
        
        lb = file_player.left_button
        lb.add_press_listener(self.file_player_left_button_pressed)
        lb.add_label_listener(self.file_player_left_button_pressed)
        
        rb = file_player.right_button
        rb.add_press_listener(self.file_player_right_button_pressed)
        rb.add_label_listener(self.file_player_right_button_pressed)
        
        tv = file_player.time_volume_button
        tv.add_press_listener(self.file_player_time_volume_button_pressed)
        tv.add_release_listener(self.create_screen)
        
        fb = file_player.file_button
        fb.add_press_listener(self.file_player_file_button_pressed)
        fb.add_release_listener(self.create_screen)
        
        tc = file_player.time_control
        tc.add_seek_listener(self.file_player_time_control_change)

    def add_file_browser_screen_web_listeners(self, file_browser):
        """ Add web listeners to file browser
        
        :param file_browser: file browser
        """
        lb = file_browser.navigator.left_button
        lb.add_release_listener(self.file_browser_left_button_pressed)
        lb.add_press_listener(self.file_browser_left_button_pressed)
        lb.add_release_listener(self.file_browser_right_button_pressed)
        lb.add_release_listener(self.create_screen)
        
        rb = file_browser.navigator.right_button
        rb.add_release_listener(self.file_browser_right_button_pressed)
        rb.add_press_listener(self.file_browser_right_button_pressed)
        rb.add_release_listener(self.file_browser_left_button_pressed)
        rb.add_release_listener(self.create_screen)
        
        hb = file_browser.navigator.home_button
        hb.add_press_listener(self.file_browser_home_button_pressed)
        hb.add_release_listener(self.create_screen)
        
        ub = file_browser.navigator.user_home_button
        ub.add_press_listener(self.file_browser_user_home_button_pressed)
        ub.add_release_listener(self.file_browser_user_home_button_pressed)
        ub.add_release_listener(self.create_screen)
        
        rb = file_browser.navigator.root_button
        rb.add_press_listener(self.file_browser_root_button_pressed)
        rb.add_release_listener(self.file_browser_root_button_pressed)
        rb.add_release_listener(self.create_screen)
        
        pb = file_browser.navigator.parent_button
        pb.add_press_listener(self.file_browser_parent_button_pressed)
        pb.add_release_listener(self.file_browser_parent_button_pressed)
        pb.add_release_listener(self.create_screen)
        
        bb = file_browser.navigator.back_button
        bb.add_press_listener(self.file_browser_back_button_pressed)
        bb.add_release_listener(self.create_screen)
        
        file_browser.file_menu.add_change_folder_listener(self.create_screen)
        file_browser.file_menu.add_play_file_listener(self.create_screen)
        file_browser.file_menu.add_menu_navigation_listeners(self.create_screen)

    def shutdown(self):
        """ Shutdown Web Server """
        
        self.web_server.socket.close()
        
        