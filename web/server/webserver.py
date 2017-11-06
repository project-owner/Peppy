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
from util.keys import WEB_SERVER, HTTP_PORT, KEY_AUDIO_FILES, KEY_PLAY_FILE, KEY_STATIONS, \
    KEY_GENRES, KEY_HOME, KEY_STREAM, KEY_AUDIOBOOKS, KEY_PLAY_SITE
from util.config import BROWSER_SITE
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
        self.prepare_site_news_handler(handler)
        self.prepare_site_abc_handler(handler)
        self.prepare_site_authors_handler(handler)
        self.prepare_author_books_handler(handler)
        self.prepare_site_genre_handler(handler)
        self.prepare_genre_books_handler(handler)
        self.prepare_site_player_handler(handler)
        self.prepare_book_track_screen_web_listeners(handler)
        
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
        
        handler.about_button_to_json = self.about_button_to_json        
        self.about_button_pressed = handler.update_about_button = rh.update_about_button
        
        handler.home_player_button_to_json = self.home_player_button_to_json        
        self.home_player_button_pressed = handler.update_home_player_button = rh.update_home_player_button
        
        handler.home_language_button_to_json = self.home_language_button_to_json        
        self.home_language_button_pressed = handler.update_home_language_button = rh.update_home_language_button
        
        handler.home_saver_button_to_json = self.home_saver_button_to_json        
        self.home_saver_button_pressed = handler.update_home_saver_button = rh.update_home_saver_button
        
        handler.home_back_button_to_json = self.home_back_button_to_json        
        self.home_back_button_pressed = handler.update_home_back_button = rh.update_home_back_button

    def prepare_language_screen_handler(self, handler):
        """ Add language screen specific handlers to provided handler 
        
        :param handler: request handler
        """
        rh = web.server.requesthandler
        
        handler.language_menu_to_json = self.language_menu_to_json        
        self.update_language_menu = handler.update_language_menu = rh.update_language_menu
        
        handler.language_home_button_to_json = self.language_home_button_to_json        
        self.language_home_button_pressed = handler.update_language_home_button = rh.update_language_home_button
         
        handler.language_player_button_to_json = self.language_player_button_to_json        
        self.language_player_button_pressed = handler.update_language_player_button = rh.update_language_player_button

    def prepare_saver_screen_handler(self, handler):
        """ Add screensaver screen specific handlers to provided handler 
        
        :param handler: request handler
        """
        rh = web.server.requesthandler
        
        handler.saver_screen_to_json = self.saver_screen_to_json        
        self.update_saver_screen = handler.update_saver_menu = rh.update_saver_screen
        
        handler.saver_home_button_to_json = self.saver_home_button_to_json        
        self.saver_home_button_pressed = handler.update_saver_home_button = rh.update_saver_home_button
           
        handler.saver_player_button_to_json = self.saver_player_button_to_json        
        self.saver_player_button_pressed = handler.update_saver_player_button = rh.update_saver_player_button

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
        
        handler.file_player_timer_stop_to_json = self.file_player_timer_stop_to_json
        self.file_player_timer_stop = handler.timer_stop = rh.timer_stop
        
        handler.file_player_timer_start_to_json = self.file_player_timer_start_to_json
        self.file_player_timer_start = handler.timer_start = rh.timer_start

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

    def prepare_site_player_handler(self, handler):
        """ Add file player screen handlers to provided handler 
        
        :param handler: request handler
        """
        rh = web.server.requesthandler
        
        handler.site_player_title_to_json = self.site_player_title_to_json        
        self.site_player_title_change = handler.update_site_player_title = rh.update_site_player_title
        
        handler.site_player_left_button_to_json = self.site_player_left_button_to_json        
        self.site_player_left_button_pressed = handler.update_site_player_left_button = rh.update_site_player_left_button

        handler.site_player_right_button_to_json = self.site_player_right_button_to_json        
        self.site_player_right_button_pressed = handler.update_site_player_right_button = rh.update_site_player_right_button
        
        handler.site_player_time_volume_button_to_json = self.site_player_time_volume_button_to_json        
        self.site_player_time_volume_button_pressed = handler.update_site_player_time_volume_button = rh.update_site_player_time_volume_button
        
        handler.site_player_file_button_to_json = self.site_player_file_button_to_json        
        self.site_player_file_button_pressed = handler.update_site_player_file_button = rh.update_site_player_file_button
        
        handler.site_player_home_button_to_json = self.site_player_home_button_to_json        
        self.site_player_home_button_pressed = handler.update_site_player_home_button = rh.update_site_player_home_button
        
        handler.site_player_shutdown_button_to_json = self.site_player_shutdown_button_to_json        
        self.site_player_shutdown_button_pressed = handler.update_site_player_shutdown_button = rh.update_site_player_shutdown_button
        
        handler.site_player_play_button_to_json = self.site_player_play_button_to_json        
        self.site_player_play_button_pressed = handler.update_site_player_play_button = rh.update_site_player_play_button
        
        handler.site_player_volume_to_json = self.site_player_volume_to_json
        self.site_player_volume_change = handler.update_site_player_volume = rh.update_site_player_volume
        
        handler.site_player_time_control_to_json = self.site_player_time_control_to_json
        self.site_player_time_control_change = handler.update_site_player_time_control = rh.update_site_player_time_control
        
        handler.site_player_timer_stop_to_json = self.site_player_timer_stop_to_json
        self.site_player_timer_stop = handler.site_timer_stop = rh.site_timer_stop
        
        handler.site_player_timer_start_to_json = self.site_player_timer_start_to_json
        self.site_player_timer_start = handler.site_timer_start = rh.site_timer_start

    def prepare_site_news_handler(self, handler):
        """ Add site news screen handlers to provided handler 
        
        :param handler: request handler
        """
        rh = web.server.requesthandler
        
        handler.site_news_left_button_to_json = self.site_news_left_button_to_json        
        self.site_news_left_button_pressed = handler.update_site_news_left_button = rh.update_site_news_left_button
        
        handler.site_news_right_button_to_json = self.site_news_right_button_to_json        
        self.site_news_right_button_pressed = handler.update_site_news_right_button = rh.update_site_news_right_button
        
        handler.site_news_home_button_to_json = self.site_news_home_button_to_json        
        self.site_news_home_button_pressed = handler.update_site_news_home_button = rh.update_site_news_home_button
        
        handler.site_news_abc_button_to_json = self.site_news_abc_button_to_json        
        self.site_news_abc_button_pressed = handler.update_site_news_abc_button = rh.update_site_news_abc_button
        
        handler.site_news_new_books_button_to_json = self.site_news_new_books_button_to_json        
        self.site_news_new_books_button_pressed = handler.update_site_news_new_books_button = rh.update_site_news_new_books_button
        
        handler.site_news_genre_button_to_json = self.site_news_genre_button_to_json        
        self.site_news_genre_button_pressed = handler.update_site_news_genre_button = rh.update_site_news_genre_button
        
        handler.site_news_player_button_to_json = self.site_news_player_button_to_json        
        self.site_news_player_button_pressed = handler.update_site_news_player_button = rh.update_site_news_player_button
        
        handler.site_news_back_button_to_json = self.site_news_back_button_to_json        
        self.site_news_back_button_pressed = handler.update_site_news_back_button = rh.update_site_news_back_button
        
        handler.site_news_book_menu_to_json = self.site_news_book_menu_to_json        
        self.site_news_update_book_menu = handler.update_site_news_book_menu = rh.update_site_news_book_menu

    def prepare_site_abc_handler(self, handler):
        """ Add site abc screen handlers to provided handler 
        
        :param handler: request handler
        """
        rh = web.server.requesthandler
        
        handler.site_abc_left_button_to_json = self.site_abc_left_button_to_json        
        self.site_abc_left_button_pressed = handler.update_site_abc_left_button = rh.update_site_abc_left_button
        
        handler.site_abc_right_button_to_json = self.site_abc_right_button_to_json        
        self.site_abc_right_button_pressed = handler.update_site_abc_right_button = rh.update_site_abc_right_button
        
        handler.site_abc_home_button_to_json = self.site_abc_home_button_to_json        
        self.site_abc_home_button_pressed = handler.update_site_abc_home_button = rh.update_site_abc_home_button
        
        handler.site_abc_abc_button_to_json = self.site_abc_abc_button_to_json        
        self.site_abc_abc_button_pressed = handler.update_site_abc_abc_button = rh.update_site_abc_abc_button
        
        handler.site_abc_new_books_button_to_json = self.site_abc_new_books_button_to_json        
        self.site_abc_new_books_button_pressed = handler.update_site_abc_new_books_button = rh.update_site_abc_new_books_button
        
        handler.site_abc_genre_button_to_json = self.site_abc_genre_button_to_json        
        self.site_abc_genre_button_pressed = handler.update_site_abc_genre_button = rh.update_site_abc_genre_button
        
        handler.site_abc_player_button_to_json = self.site_abc_player_button_to_json        
        self.site_abc_player_button_pressed = handler.update_site_abc_player_button = rh.update_site_abc_player_button
        
        handler.site_abc_back_button_to_json = self.site_abc_back_button_to_json        
        self.site_abc_back_button_pressed = handler.update_site_abc_back_button = rh.update_site_abc_back_button
        
        handler.site_abc_menu_to_json = self.site_abc_menu_to_json        
        self.site_abc_update_abc_menu = handler.update_site_abc_menu = rh.update_site_abc_menu

    def prepare_site_authors_handler(self, handler):
        """ Add site authors screen handlers to provided handler 
        
        :param handler: request handler
        """
        rh = web.server.requesthandler
        
        handler.site_authors_left_button_to_json = self.site_authors_left_button_to_json        
        self.site_authors_left_button_pressed = handler.update_site_authors_left_button = rh.update_site_authors_left_button
        
        handler.site_authors_right_button_to_json = self.site_authors_right_button_to_json        
        self.site_authors_right_button_pressed = handler.update_site_authors_right_button = rh.update_site_authors_right_button
        
        handler.site_authors_home_button_to_json = self.site_authors_home_button_to_json        
        self.site_authors_home_button_pressed = handler.update_site_authors_home_button = rh.update_site_authors_home_button
        
        handler.site_authors_abc_button_to_json = self.site_authors_abc_button_to_json        
        self.site_authors_abc_button_pressed = handler.update_site_authors_abc_button = rh.update_site_authors_abc_button
        
        handler.site_authors_new_books_button_to_json = self.site_authors_new_books_button_to_json        
        self.site_authors_new_books_button_pressed = handler.update_site_authors_new_books_button = rh.update_site_authors_new_books_button
        
        handler.site_authors_genre_button_to_json = self.site_authors_genre_button_to_json        
        self.site_authors_genre_button_pressed = handler.update_site_authors_genre_button = rh.update_site_authors_genre_button
        
        handler.site_authors_player_button_to_json = self.site_authors_player_button_to_json        
        self.site_authors_player_button_pressed = handler.update_site_authors_player_button = rh.update_site_authors_player_button
        
        handler.site_authors_back_button_to_json = self.site_authors_back_button_to_json        
        self.site_authors_back_button_pressed = handler.update_site_authors_back_button = rh.update_site_authors_back_button
        
        handler.site_authors_menu_to_json = self.site_authors_menu_to_json        
        self.site_authors_update_authors_menu = handler.update_site_authors_menu = rh.update_site_authors_menu

    def prepare_author_books_handler(self, handler):
        """ Add author books screen handlers to provided handler 
        
        :param handler: request handler
        """
        rh = web.server.requesthandler
        
        handler.author_books_left_button_to_json = self.author_books_left_button_to_json        
        self.author_books_left_button_pressed = handler.update_author_books_left_button = rh.update_author_books_left_button
        
        handler.author_books_right_button_to_json = self.author_books_right_button_to_json        
        self.author_books_right_button_pressed = handler.update_author_books_right_button = rh.update_author_books_right_button
        
        handler.author_books_home_button_to_json = self.author_books_home_button_to_json        
        self.author_books_home_button_pressed = handler.update_author_books_home_button = rh.update_author_books_home_button
        
        handler.author_books_abc_button_to_json = self.author_books_abc_button_to_json        
        self.author_books_abc_button_pressed = handler.update_author_books_abc_button = rh.update_author_books_abc_button
        
        handler.author_books_new_books_button_to_json = self.author_books_new_books_button_to_json        
        self.author_books_new_books_button_pressed = handler.update_author_books_new_books_button = rh.update_author_books_new_books_button
        
        handler.author_books_genre_button_to_json = self.author_books_genre_button_to_json        
        self.author_books_genre_button_pressed = handler.update_author_books_genre_button = rh.update_author_books_genre_button
        
        handler.author_books_player_button_to_json = self.author_books_player_button_to_json        
        self.author_books_player_button_pressed = handler.update_author_books_player_button = rh.update_author_books_player_button
        
        handler.author_books_back_button_to_json = self.author_books_back_button_to_json        
        self.author_books_back_button_pressed = handler.update_author_books_back_button = rh.update_author_books_back_button
        
        handler.author_books_book_menu_to_json = self.author_books_book_menu_to_json        
        self.author_books_update_book_menu = handler.update_author_books_book_menu = rh.update_author_books_book_menu

    def prepare_site_genre_handler(self, handler):
        """ Add site genres screen handlers to provided handler 
        
        :param handler: request handler
        """
        rh = web.server.requesthandler
        
        handler.site_genre_left_button_to_json = self.site_genre_left_button_to_json        
        self.site_genre_left_button_pressed = handler.update_site_genre_left_button = rh.update_site_genre_left_button
        
        handler.site_genre_right_button_to_json = self.site_genre_right_button_to_json        
        self.site_genre_right_button_pressed = handler.update_site_genre_right_button = rh.update_site_genre_right_button
        
        handler.site_genre_home_button_to_json = self.site_genre_home_button_to_json        
        self.site_genre_home_button_pressed = handler.update_site_genre_home_button = rh.update_site_genre_home_button
        
        handler.site_genre_abc_button_to_json = self.site_genre_abc_button_to_json        
        self.site_genre_abc_button_pressed = handler.update_site_genre_abc_button = rh.update_site_genre_abc_button
        
        handler.site_genre_new_books_button_to_json = self.site_genre_new_books_button_to_json        
        self.site_genre_new_books_button_pressed = handler.update_site_genre_new_books_button = rh.update_site_genre_new_books_button
        
        handler.site_genre_genre_button_to_json = self.site_genre_genre_button_to_json        
        self.site_genre_genre_button_pressed = handler.update_site_genre_genre_button = rh.update_site_genre_genre_button
        
        handler.site_genre_player_button_to_json = self.site_genre_player_button_to_json        
        self.site_genre_player_button_pressed = handler.update_site_genre_player_button = rh.update_site_genre_player_button
        
        handler.site_genre_back_button_to_json = self.site_genre_back_button_to_json        
        self.site_genre_back_button_pressed = handler.update_site_genre_back_button = rh.update_site_genre_back_button
        
        handler.site_genre_menu_to_json = self.site_genre_menu_to_json        
        self.site_genre_update_authors_menu = handler.update_site_genre_menu = rh.update_site_genre_menu

    def prepare_genre_books_handler(self, handler):
        """ Add genre books screen handlers to provided handler 
        
        :param handler: request handler
        """
        rh = web.server.requesthandler
        
        handler.genre_books_left_button_to_json = self.genre_books_left_button_to_json        
        self.genre_books_left_button_pressed = handler.update_genre_books_left_button = rh.update_genre_books_left_button
        
        handler.genre_books_right_button_to_json = self.genre_books_right_button_to_json        
        self.genre_books_right_button_pressed = handler.update_genre_books_right_button = rh.update_genre_books_right_button
        
        handler.genre_books_home_button_to_json = self.genre_books_home_button_to_json        
        self.genre_books_home_button_pressed = handler.update_genre_books_home_button = rh.update_genre_books_home_button
        
        handler.genre_books_abc_button_to_json = self.genre_books_abc_button_to_json        
        self.genre_books_abc_button_pressed = handler.update_genre_books_abc_button = rh.update_genre_books_abc_button
        
        handler.genre_books_new_books_button_to_json = self.genre_books_new_books_button_to_json        
        self.genre_books_new_books_button_pressed = handler.update_genre_books_new_books_button = rh.update_genre_books_new_books_button
        
        handler.genre_books_genre_button_to_json = self.genre_books_genre_button_to_json        
        self.genre_books_genre_button_pressed = handler.update_genre_books_genre_button = rh.update_genre_books_genre_button
        
        handler.genre_books_player_button_to_json = self.genre_books_player_button_to_json        
        self.genre_books_player_button_pressed = handler.update_genre_books_player_button = rh.update_genre_books_player_button
        
        handler.genre_books_back_button_to_json = self.genre_books_back_button_to_json        
        self.genre_books_back_button_pressed = handler.update_genre_books_back_button = rh.update_genre_books_back_button
        
        handler.genre_books_book_menu_to_json = self.genre_books_book_menu_to_json        
        self.genre_books_update_book_menu = handler.update_genre_books_book_menu = rh.update_genre_books_book_menu

    def prepare_book_track_screen_web_listeners(self, handler):
        """ Add books tracks screen handlers to provided handler 
        
        :param handler: request handler
        """
        rh = web.server.requesthandler
        
        handler.book_track_left_button_to_json = self.book_track_left_button_to_json        
        self.book_track_left_button_pressed = handler.update_book_track_left_button = rh.update_book_track_left_button
        
        handler.book_track_right_button_to_json = self.book_track_right_button_to_json        
        self.book_track_right_button_pressed = handler.update_book_track_right_button = rh.update_book_track_right_button
        
        handler.book_track_home_button_to_json = self.book_track_home_button_to_json        
        self.book_track_home_button_pressed = handler.update_book_track_home_button = rh.update_book_track_home_button
        
        handler.book_track_abc_button_to_json = self.book_track_abc_button_to_json        
        self.book_track_abc_button_pressed = handler.update_book_track_abc_button = rh.update_book_track_abc_button
        
        handler.book_track_new_books_button_to_json = self.book_track_new_books_button_to_json        
        self.book_track_new_books_button_pressed = handler.update_book_track_new_books_button = rh.update_book_track_new_books_button
        
        handler.book_track_genre_button_to_json = self.book_track_genre_button_to_json        
        self.book_track_genre_button_pressed = handler.update_book_track_genre_button = rh.update_book_track_genre_button
        
        handler.book_track_player_button_to_json = self.book_track_player_button_to_json        
        self.book_track_player_button_pressed = handler.update_book_track_player_button = rh.update_book_track_player_button
        
        handler.book_track_back_button_to_json = self.book_track_back_button_to_json        
        self.book_track_back_button_pressed = handler.update_book_track_back_button = rh.update_book_track_back_button
        
        handler.book_track_menu_to_json = self.book_track_menu_to_json        
        self.book_track_update_authors_menu = handler.update_book_track_menu = rh.update_book_track_menu

    def get_screen(self, key):
        """ Return Screen specified by key
        
        :param key: key
        :return: the screen
        """
        screen = None
        try:
            screen = self.peppy.screens[key]
        except:
            pass
        
        return screen

    def get_station_screen(self):
        """ Return Station Screen
        
        :return: the reference to the Station Screen
        """
        return self.get_screen(KEY_STATIONS)
    
    def get_stream_screen(self):
        """ Return Station Screen
        
        :return: the reference to the Station Screen
        """
        return self.get_screen(KEY_STREAM)
    
    def get_genre_screen(self):
        """ Return Genre Screen
        
        :return: the reference to the Genre Screen
        """
        return self.get_screen(KEY_GENRES)
    
    def get_home_screen(self):
        """ Return Home Screen
        
        :return: the reference to the Home Screen
        """
        return self.get_screen(KEY_HOME)
    
    def get_language_screen(self):
        """ Return Language Screen
        
        :return: the reference to the Language Screen
        """
        return self.get_screen("language")
    
    def get_saver_screen(self):
        """ Return Screensaver Screen
        
        :return: the reference to the Screensaver Screen
        """
        return self.get_screen("saver")
    
    def get_about_screen(self):
        """ Return About Screen
        
        :return: the reference to the About Screen
        """
        return self.get_screen("about")
    
    def get_file_player_screen(self):
        """ Return File Player Screen
        
        :return: the reference to the File Player Screen
        """
        return self.get_screen(KEY_PLAY_FILE)
    
    def get_file_browser_screen(self):
        """ Return File Browser Screen
        
        :return: the reference to the File Browser Screen
        """
        return self.get_screen(KEY_AUDIO_FILES)
    
    def get_site_news_screen(self):
        """ Return Site News Screen
        
        :return: the reference to the Site News Screen
        """
        return self.get_screen(self.config[KEY_AUDIOBOOKS][BROWSER_SITE] + ".new.books.screen")
    
    def get_site_abc_screen(self):
        """ Return Site Abc Screen
        
        :return: the reference to the Site Abc Screen
        """
        return self.get_screen("abc.screen")
    
    def get_site_authors_screen(self):
        """ Return Site Authors Screen
        
        :return: the reference to the Site Authors Screen
        """
        return self.get_screen(self.config[KEY_AUDIOBOOKS][BROWSER_SITE] + ".authors.screen")
    
    def get_author_books_screen(self):
        """ Return Author Books Screen
        
        :return: the reference to the Author Books Screen
        """
        return self.get_screen(self.config[KEY_AUDIOBOOKS][BROWSER_SITE] + ".author.books")
    
    def get_site_genre_screen(self):
        """ Return Site Genres Screen
        
        :return: the reference to the Site Genres Screen
        """
        return self.get_screen(self.config[KEY_AUDIOBOOKS][BROWSER_SITE] + ".genre.screen")

    def get_genre_books_screen(self):
        """ Return Genre Books Screen
        
        :return: the reference to the Genre Books Screen
        """
        return self.get_screen(self.config[KEY_AUDIOBOOKS][BROWSER_SITE] + ".genre.books")
    
    def get_site_player_screen(self):
        """ Return Site Player Screen
        
        :return: the reference to the Site Player Screen
        """
        return self.get_screen(KEY_PLAY_SITE)
    
    def get_book_track_screen(self):
        """ Return Book Tracks Screen
        
        :return: the reference to the Book Tracks Screen
        """
        return self.get_screen("book.track.screen")

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
        stations = self.get_station_screen()
        stream = self.get_stream_screen() 
               
        if stations and stations.visible:
            return self.json_factory.title_to_json(stations.screen_title)
        
        if stream and stream.visible:
            return self.json_factory.title_to_json(stream.screen_title)
        
        return None
    
    def file_player_title_to_json(self):
        """ Convert file player title object into JSON object
        
        :return: JSON object
        """
        if self.get_file_player_screen() == None or self.get_file_player_screen().visible == False:
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
    
    def file_player_timer_start_to_json(self):
        """ Convert start timer command into JSON object
        
        :return: JSON object
        """
        return self.json_factory.file_player_start_to_json() 
    
    def file_player_timer_stop_to_json(self):
        """ Convert stop timer command into JSON object
        
        :return: JSON object
        """
        return self.json_factory.file_player_stop_to_json()    
        
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
    
    # site player
    
    def site_player_title_to_json(self):
        """ Convert site player title into JSON object
        
        :return: JSON object
        """
        if self.get_site_player_screen() == None or self.get_site_player_screen().visible == False:
            return None
        else:
            return self.json_factory.file_player_title_to_json(self.get_site_player_screen().screen_title)
    
    def site_player_left_button_to_json(self):
        """ Convert site player left button into JSON object
        
        :return: JSON object
        """
        if self.get_site_player_screen().visible == False:
            return None
        else:
            return self.json_factory.container_to_json(self.get_site_player_screen().left_button)
    
    def site_player_right_button_to_json(self):
        """ Convert site player right button into JSON object
        
        :return: JSON object
        """
        if self.get_site_player_screen().visible == False:
            return None
        else:
            return self.json_factory.container_to_json(self.get_site_player_screen().right_button)
    
    def site_player_time_volume_button_to_json(self):
        """ Convert site time/volume button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_player_screen().time_volume_button)
    
    def site_player_file_button_to_json(self):
        """ Convert site player file button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_player_screen().file_button)
    
    def site_player_home_button_to_json(self):
        """ Convert site player home button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_player_screen().home_button)
    
    def site_player_shutdown_button_to_json(self):
        """ Convert site player shutdown button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_player_screen().shutdown_button)
    
    def site_player_play_button_to_json(self):
        """ Convert site player play button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_player_screen().play_button)
    
    def site_player_volume_to_json(self):
        """ Convert site player volume into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_player_screen().volume)
    
    def site_player_time_control_to_json(self):
        """ Convert site player time control into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_player_screen().time_control)
    
    def site_player_timer_start_to_json(self):
        """ Convert site player timer start into JSON object
        
        :return: JSON object
        """
        return self.json_factory.file_player_start_to_json() 
    
    def site_player_timer_stop_to_json(self):
        """ Convert site player timer stop into JSON object
        
        :return: JSON object
        """
        return self.json_factory.file_player_stop_to_json()    
            
    # news
    
    def site_news_left_button_to_json(self):
        """ Convert site news left button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_news_screen().navigator.left_button)
    
    def site_news_right_button_to_json(self):
        """ Convert site news right button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_news_screen().navigator.right_button)
    
    def site_news_home_button_to_json(self):
        """ Convert site news home button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_news_screen().navigator.home_button)
    
    def site_news_abc_button_to_json(self):
        """ Convert site news abc button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_news_screen().navigator.abc_button)
    
    def site_news_new_books_button_to_json(self):
        """ Convert site news new books button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_news_screen().navigator.new_books_button)
    
    def site_news_genre_button_to_json(self):
        """ Convert site news genre button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_news_screen().navigator.genre_button)
    
    def site_news_player_button_to_json(self):
        """ Convert site news player button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_news_screen().navigator.player_button)
    
    def site_news_back_button_to_json(self):
        """ Convert site news back button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_news_screen().navigator.back_button)
    
    def site_news_book_menu_to_json(self):
        """ Convert site news book menu into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_news_screen().book_menu)

    # abc
    
    def site_abc_left_button_to_json(self):
        """ Convert site abc left button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_abc_screen().navigator.left_button)
    
    def site_abc_right_button_to_json(self):
        """ Convert site abc right button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_abc_screen().navigator.right_button)
    
    def site_abc_home_button_to_json(self):
        """ Convert site abc home button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_abc_screen().navigator.home_button)
    
    def site_abc_abc_button_to_json(self):
        """ Convert site abc abc button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_abc_screen().navigator.abc_button)
    
    def site_abc_new_books_button_to_json(self):
        """ Convert site abc new books button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_abc_screen().navigator.new_books_button)
    
    def site_abc_genre_button_to_json(self):
        """ Convert site abc genre button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_abc_screen().navigator.genre_button)
    
    def site_abc_player_button_to_json(self):
        """ Convert site abc player button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_abc_screen().navigator.player_button)
    
    def site_abc_back_button_to_json(self):
        """ Convert site abc back button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_abc_screen().navigator.back_button)
 
    def site_abc_menu_to_json(self):
        """ Convert site abc menu into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_abc_screen().abc_menu)

    # authors
    
    def site_authors_left_button_to_json(self):
        """ Convert site authors left button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_authors_screen().navigator.left_button)
    
    def site_authors_right_button_to_json(self):
        """ Convert site authors right button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_authors_screen().navigator.right_button)
    
    def site_authors_home_button_to_json(self):
        """ Convert site authors home button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_authors_screen().navigator.home_button)
    
    def site_authors_abc_button_to_json(self):
        """ Convert site authors abc button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_authors_screen().navigator.abc_button)
    
    def site_authors_new_books_button_to_json(self):
        """ Convert site authors new books button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_authors_screen().navigator.new_books_button)
    
    def site_authors_genre_button_to_json(self):
        """ Convert site authors genre button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_authors_screen().navigator.genre_button)
    
    def site_authors_player_button_to_json(self):
        """ Convert site authors player button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_authors_screen().navigator.player_button)
    
    def site_authors_back_button_to_json(self):
        """ Convert site authors back button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_authors_screen().navigator.back_button)
 
    def site_authors_menu_to_json(self):
        """ Convert site authors menu into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_authors_screen().authors_menu)
    
    # author books
    
    def author_books_left_button_to_json(self):
        """ Convert author books left button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_author_books_screen().navigator.left_button)
    
    def author_books_right_button_to_json(self):
        """ Convert author books right button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_author_books_screen().navigator.right_button)
    
    def author_books_home_button_to_json(self):
        """ Convert author books home button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_author_books_screen().navigator.home_button)
    
    def author_books_abc_button_to_json(self):
        """ Convert author books abc button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_author_books_screen().navigator.abc_button)
    
    def author_books_new_books_button_to_json(self):
        """ Convert author books new books button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_author_books_screen().navigator.new_books_button)
    
    def author_books_genre_button_to_json(self):
        """ Convert author books genre button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_author_books_screen().navigator.genre_button)
    
    def author_books_player_button_to_json(self):
        """ Convert author books player button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_author_books_screen().navigator.player_button)
    
    def author_books_back_button_to_json(self):
        """ Convert author books back button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_author_books_screen().navigator.back_button)
    
    def author_books_book_menu_to_json(self):
        """ Convert author books menu into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_author_books_screen().book_menu)
    
    # genre
    
    def site_genre_left_button_to_json(self):
        """ Convert genre left button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_genre_screen().navigator.left_button)
    
    def site_genre_right_button_to_json(self):
        """ Convert genre right button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_genre_screen().navigator.right_button)
    
    def site_genre_home_button_to_json(self):
        """ Convert genre home button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_genre_screen().navigator.home_button)
    
    def site_genre_abc_button_to_json(self):
        """ Convert genre abc button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_genre_screen().navigator.abc_button)
    
    def site_genre_new_books_button_to_json(self):
        """ Convert genre new books button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_genre_screen().navigator.new_books_button)
    
    def site_genre_genre_button_to_json(self):
        """ Convert genre genre button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_genre_screen().navigator.genre_button)
    
    def site_genre_player_button_to_json(self):
        """ Convert genre player button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_genre_screen().navigator.player_button)
    
    def site_genre_back_button_to_json(self):
        """ Convert genre back button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_genre_screen().navigator.back_button)
 
    def site_genre_menu_to_json(self):
        """ Convert genre menu into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_site_genre_screen().genre_menu)
    
    # genre books
    
    def genre_books_left_button_to_json(self):
        """ Convert genre books left button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_genre_books_screen().navigator.left_button)
    
    def genre_books_right_button_to_json(self):
        """ Convert genre books right button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_genre_books_screen().navigator.right_button)
    
    def genre_books_home_button_to_json(self):
        """ Convert genre books home button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_genre_books_screen().navigator.home_button)
    
    def genre_books_abc_button_to_json(self):
        """ Convert genre books abc button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_genre_books_screen().navigator.abc_button)
    
    def genre_books_new_books_button_to_json(self):
        """ Convert genre books new books button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_genre_books_screen().navigator.new_books_button)
    
    def genre_books_genre_button_to_json(self):
        """ Convert genre books genre button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_genre_books_screen().navigator.genre_button)
    
    def genre_books_player_button_to_json(self):
        """ Convert genre books player button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_genre_books_screen().navigator.player_button)
    
    def genre_books_back_button_to_json(self):
        """ Convert genre books back button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_genre_books_screen().navigator.back_button)
    
    def genre_books_book_menu_to_json(self):
        """ Convert genre books book menu into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_genre_books_screen().book_menu)

    # book_track
    
    def book_track_left_button_to_json(self):
        """ Convert book tracks left button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_book_track_screen().navigator.left_button)
    
    def book_track_right_button_to_json(self):
        """ Convert book tracks right button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_book_track_screen().navigator.right_button)
    
    def book_track_home_button_to_json(self):
        """ Convert book tracks home button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_book_track_screen().navigator.home_button)
    
    def book_track_abc_button_to_json(self):
        """ Convert book tracks abc button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_book_track_screen().navigator.abc_button)
    
    def book_track_new_books_button_to_json(self):
        """ Convert book tracks new books button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_book_track_screen().navigator.new_books_button)
    
    def book_track_genre_button_to_json(self):
        """ Convert book tracks genre button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_book_track_screen().navigator.genre_button)
    
    def book_track_player_button_to_json(self):
        """ Convert book tracks player button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_book_track_screen().navigator.player_button)
    
    def book_track_back_button_to_json(self):
        """ Convert book tracks back button into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_book_track_screen().navigator.back_button)
 
    def book_track_menu_to_json(self):
        """ Convert book tracks menu into JSON object
        
        :return: JSON object
        """
        return self.json_factory.container_to_json(self.get_book_track_screen().track_menu)
        
    def volume_to_json(self):
        """ Convert volume object into JSON object
        
        :return: JSON object
        """
        stations = self.get_station_screen()
        stream = self.get_stream_screen() 
               
        if stations and stations.visible:
            return self.json_factory.container_to_json(stations.volume)
        
        if stream and stream.visible:
            return self.json_factory.container_to_json(stream.volume)
        
    def genre_button_to_json(self):
        """ Convert genre button into JSON object
        
        :return: JSON object
        """
        stations = self.get_station_screen()
        stream = self.get_stream_screen() 
               
        if stations and stations.visible:
            return self.json_factory.container_to_json(stations.genres_button)
        
        if stream and stream.visible:
            return self.json_factory.container_to_json(stream.genres_button)
    
    def home_button_to_json(self):
        """ Convert home button into JSON object
        
        :return: JSON object
        """
        stations = self.get_station_screen()
        stream = self.get_stream_screen()
               
        if stations and stations.visible:
            return self.json_factory.container_to_json(stations.home_button)
        
        if stream and stream.visible:
            return self.json_factory.container_to_json(stream.home_button)
        
    def about_button_to_json(self):
        """ Convert about button into JSON object
        
        :return: JSON object
        """
        home = self.get_home_screen() 
               
        if home and home.visible:
            return self.json_factory.container_to_json(home.home_navigation_menu.about_button)
    
    def home_player_button_to_json(self):
        """ Convert player button into JSON object
        
        :return: JSON object
        """
        home = self.get_home_screen() 
               
        if home and home.visible:
            return self.json_factory.container_to_json(home.home_navigation_menu.player_button)
        
    def home_language_button_to_json(self):
        """ Convert language button into JSON object
        
        :return: JSON object
        """
        home = self.get_home_screen() 
               
        if home and home.visible:
            return self.json_factory.container_to_json(home.home_navigation_menu.language_button)
        
    def home_saver_button_to_json(self):
        """ Convert saver button into JSON object
        
        :return: JSON object
        """
        home = self.get_home_screen() 
               
        if home and home.visible:
            return self.json_factory.container_to_json(home.home_navigation_menu.saver_button)
        
    def home_back_button_to_json(self):
        """ Convert back button into JSON object
        
        :return: JSON object
        """
        home = self.get_home_screen() 
               
        if home and home.visible:
            return self.json_factory.container_to_json(home.home_navigation_menu.back_button)
        
    def language_home_button_to_json(self):
        """ Convert home button into JSON object
        
        :return: JSON object
        """
        language = self.get_language_screen() 
                
        if language and language.visible:
            return self.json_factory.container_to_json(language.home_button)
         
    def language_player_button_to_json(self):
        """ Convert player button into JSON object
        
        :return: JSON object
        """
        language = self.get_language_screen() 
                
        if language and language.visible:
            return self.json_factory.container_to_json(language.player_button)
    
    def saver_home_button_to_json(self):
        """ Convert home button into JSON object
        
        :return: JSON object
        """
        saver = self.get_saver_screen()
                 
        if saver and saver.visible:
            return self.json_factory.container_to_json(saver.home_button)
         
    def saver_player_button_to_json(self):
        """ Convert player button into JSON object
        
        :return: JSON object
        """
        saver = self.get_saver_screen()
                 
        if saver and saver.visible:
            return self.json_factory.container_to_json(saver.player_button)
        
    def left_button_to_json(self):
        """ Convert left button into JSON object
        
        :return: JSON object
        """
        stations = self.get_station_screen()
        stream = self.get_stream_screen() 
               
        if stations and stations.visible:
            return self.json_factory.container_to_json(stations.left_button)
        
        if stream and stream.visible:
            return self.json_factory.container_to_json(stream.left_button)
        
    def page_down_button_to_json(self):
        """ Convert page down button into JSON object
        
        :return: JSON object
        """
        stations = self.get_station_screen()
        stream = self.get_stream_screen() 
               
        if stations and stations.visible:
            return self.json_factory.container_to_json(stations.page_down_button)
        
        if stream and stream.visible:
            return self.json_factory.container_to_json(stream.page_down_button)
    
    def right_button_to_json(self):
        """ Convert right button into JSON object
        
        :return: JSON object
        """
        stations = self.get_station_screen()
        stream = self.get_stream_screen() 
               
        if stations and stations.visible:
            return self.json_factory.container_to_json(stations.right_button)
        
        if stream and stream.visible:
            return self.json_factory.container_to_json(stream.right_button)
        
    def page_up_button_to_json(self):
        """ Convert page up button into JSON object
        
        :return: JSON object
        """
        stations = self.get_station_screen()
        stream = self.get_stream_screen() 
               
        if stations and stations.visible:
            return self.json_factory.container_to_json(stations.page_up_button)
        
        if stream and stream.visible:
            return self.json_factory.container_to_json(stream.page_up_button)
        
    def station_menu_to_json(self):
        """ Convert station menu into JSON object
        
        :return: JSON object
        """
        stations = self.get_station_screen()
        stream = self.get_stream_screen() 
               
        if stations and stations.visible:
            return self.json_factory.station_menu_to_json(stations.station_menu)
        
        if stream and stream.visible:
            return self.json_factory.station_menu_to_json(stream.station_menu)
        
    def play_button_to_json(self):
        """ Convert play button into JSON object
        
        :return: JSON object
        """
        stations = self.get_station_screen()
        stream = self.get_stream_screen() 
               
        if stations and stations.visible:
            return self.json_factory.container_to_json(stations.play_button)
        
        if stream and stream.visible:
            return self.json_factory.container_to_json(stream.play_button)
        
    def shutdown_button_to_json(self):
        """ Convert shutdown button into JSON object
        
        :return: JSON object
        """
        stations = self.get_station_screen()
        stream = self.get_stream_screen() 
               
        if stations and stations.visible:
            return self.json_factory.container_to_json(stations.shutdown_button)
        
        if stream and stream.visible:
            return self.json_factory.container_to_json(stream.shutdown_button)
    
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

    def add_menu_buttons_listeners(self, menu, press=True, release=True):
        for b in menu.buttons.values():
            if press: b.add_press_listener(self.create_screen)
            if release: b.add_release_listener(self.create_screen)

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
        self.add_menu_buttons_listeners(home.home_menu, release=False)
        home.home_menu.add_listener(self.create_screen)
        
        a = home.home_navigation_menu.about_button
        a.add_press_listener(self.about_button_pressed)
        a.add_release_listener(self.about_button_pressed)
        a.add_release_listener(self.create_screen)
        
        p = home.home_navigation_menu.player_button
        p.add_press_listener(self.home_player_button_pressed)
        p.add_release_listener(self.home_player_button_pressed)
        p.add_release_listener(self.create_screen)
        
        g = home.home_navigation_menu.language_button
        g.add_press_listener(self.home_language_button_pressed)
        g.add_release_listener(self.home_language_button_pressed)
        g.add_release_listener(self.create_screen)
        
        s = home.home_navigation_menu.saver_button
        s.add_press_listener(self.home_saver_button_pressed)
        s.add_release_listener(self.home_saver_button_pressed)
        s.add_release_listener(self.create_screen)
        
        b = home.home_navigation_menu.back_button
        b.add_press_listener(self.home_back_button_pressed)
        b.add_release_listener(self.home_back_button_pressed)
        b.add_release_listener(self.create_screen)
        
    def add_language_screen_web_listeners(self, language):
        """ Add web listeners to language screen components
        
        :param language: the language screen
        """
        self.add_menu_buttons_listeners(language.language_menu)
        language.language_menu.add_move_listener(self.update_language_menu)
        
        h = language.home_button
        h.add_press_listener(self.language_home_button_pressed)
        h.add_release_listener(self.language_home_button_pressed)
        h.add_release_listener(self.create_screen)
         
        p = language.player_button
        p.add_press_listener(self.language_player_button_pressed)
        p.add_release_listener(self.language_player_button_pressed)
        p.add_release_listener(self.create_screen)
        
    def add_saver_screen_web_listeners(self, saver):
        """ Add web listeners to screensaver screen components
        
        :param saver: the screensaver screen
        """
        self.add_menu_buttons_listeners(saver.saver_menu)
        saver.saver_menu.add_move_listener(self.update_saver_screen)
        
        self.add_menu_buttons_listeners(saver.delay_menu)
        saver.delay_menu.add_move_listener(self.update_saver_screen)
        
        h = saver.home_button        
        h.add_press_listener(self.create_screen)
        h.add_release_listener(self.create_screen)
        
        p = saver.player_button
        p.add_press_listener(self.create_screen)
        p.add_release_listener(self.create_screen)
        
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
        tc.web_seek_listener = self.file_player_time_control_change

        tc.add_stop_timer_listener(self.file_player_timer_stop)
        tc.add_start_timer_listener(self.file_player_timer_start)

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

    def add_site_player_web_listeners(self, site_player):
        """ Add web listeners to file player
        
        :param file_player: file player
        """
        site_player.screen_title.add_listener(self.site_player_title_change)
        site_player.add_play_listener(self.create_screen)
        site_player.add_loading_listener(self.create_screen)
        
        sb = site_player.shutdown_button
        sb.add_press_listener(self.site_player_shutdown_button_pressed)
        sb.add_release_listener(self.site_player_shutdown_button_pressed)
        sb.add_cancel_listener(self.site_player_shutdown_button_pressed)
        
        pb = site_player.play_button
        pb.add_press_listener(self.site_player_play_button_pressed)
        pb.add_release_listener(self.site_player_play_button_pressed)
        
        hb = site_player.home_button
        hb.add_press_listener(self.site_player_home_button_pressed)
        hb.add_release_listener(self.create_screen)
        
        vb = site_player.volume
        vb.add_slide_listener(self.site_player_volume_change)
        vb.add_knob_listener(self.site_player_volume_change)
        vb.add_press_listener(self.site_player_volume_change)
        vb.add_motion_listener(self.site_player_volume_change)
        
        lb = site_player.left_button
        lb.add_press_listener(self.site_player_left_button_pressed)
        lb.add_label_listener(self.site_player_left_button_pressed)
        
        rb = site_player.right_button
        rb.add_press_listener(self.site_player_right_button_pressed)
        rb.add_label_listener(self.site_player_right_button_pressed)
        
        tv = site_player.time_volume_button
        tv.add_press_listener(self.site_player_time_volume_button_pressed)
        tv.add_release_listener(self.create_screen)
        
        fb = site_player.file_button
        fb.add_press_listener(self.site_player_file_button_pressed)
        fb.add_release_listener(self.create_screen)
        
        tc = site_player.time_control
        tc.web_seek_listener = self.site_player_time_control_change

        tc.add_stop_timer_listener(self.site_player_timer_stop)
        tc.add_start_timer_listener(self.site_player_timer_start)


    def add_site_news_screen_web_listeners(self, site_news):
        """ Add web listeners to site news screen
        
        :param site_news: screen
        """
        n = site_news.navigator
        lb = n.left_button
        lb.add_release_listener(self.site_news_left_button_pressed)
        lb.add_press_listener(self.site_news_left_button_pressed)
        lb.add_release_listener(self.site_news_right_button_pressed)
        lb.add_release_listener(self.create_screen)
        
        rb = n.right_button
        rb.add_release_listener(self.site_news_right_button_pressed)
        rb.add_press_listener(self.site_news_right_button_pressed)
        rb.add_release_listener(self.site_news_left_button_pressed)
        rb.add_release_listener(self.create_screen)
        
        hb = n.home_button
        hb.add_press_listener(self.site_news_home_button_pressed)
        hb.add_release_listener(self.create_screen)
        
        if getattr(n, "abc_button", None):
            ab = n.abc_button
            ab.add_release_listener(self.site_news_abc_button_pressed)
            ab.add_press_listener(self.site_news_abc_button_pressed)
            ab.add_release_listener(self.create_screen)
            
        nb = n.new_books_button
        nb.add_release_listener(self.site_news_new_books_button_pressed)
        nb.add_press_listener(self.site_news_new_books_button_pressed)
        nb.add_release_listener(self.create_screen)
        
        if getattr(n, "genre_button", None):
            gb = n.genre_button
            gb.add_release_listener(self.site_news_genre_button_pressed)
            gb.add_press_listener(self.site_news_genre_button_pressed)
            gb.add_release_listener(self.create_screen)
            
        pb = n.player_button
        pb.add_release_listener(self.site_news_player_button_pressed)
        pb.add_press_listener(self.site_news_player_button_pressed)
        pb.add_release_listener(self.create_screen)
        
        bb = n.back_button
        bb.add_press_listener(self.site_news_back_button_pressed)
        bb.add_release_listener(self.create_screen)

        site_news.add_loading_listener(self.create_screen)
        site_news.book_menu.add_menu_loaded_listener(self.add_menu_buttons_listeners)

    def add_site_abc_screen_web_listeners(self, abc):
        """ Add web listeners to site abc screen
        
        :param abc: screen
        """
        n = abc.navigator
        
        lb = n.left_button
        lb.add_release_listener(self.site_abc_left_button_pressed)
        lb.add_press_listener(self.site_abc_left_button_pressed)
        lb.add_release_listener(self.site_abc_right_button_pressed)
        lb.add_release_listener(self.create_screen)
        
        rb = n.right_button
        rb.add_release_listener(self.site_abc_right_button_pressed)
        rb.add_press_listener(self.site_abc_right_button_pressed)
        rb.add_release_listener(self.site_abc_left_button_pressed)
        rb.add_release_listener(self.create_screen)
        
        hb = n.home_button
        hb.add_press_listener(self.site_abc_home_button_pressed)
        hb.add_release_listener(self.create_screen)
        
        if getattr(n, "abc_button", None):
            ab = n.abc_button
            ab.add_release_listener(self.site_abc_abc_button_pressed)
            ab.add_press_listener(self.site_abc_abc_button_pressed)
            ab.add_release_listener(self.create_screen)
            
        nb = n.new_books_button
        nb.add_release_listener(self.site_abc_new_books_button_pressed)
        nb.add_press_listener(self.site_abc_new_books_button_pressed)
        nb.add_release_listener(self.create_screen)
        
        if getattr(n, "genre_button", None):
            gb = n.genre_button
            gb.add_release_listener(self.site_abc_genre_button_pressed)
            gb.add_press_listener(self.site_abc_genre_button_pressed)
            gb.add_release_listener(self.create_screen)
            
        pb = n.player_button
        pb.add_release_listener(self.site_abc_player_button_pressed)
        pb.add_press_listener(self.site_abc_player_button_pressed)
        pb.add_release_listener(self.create_screen)
        
        bb = n.back_button
        bb.add_press_listener(self.site_abc_back_button_pressed)
        bb.add_release_listener(self.create_screen)
        
        for b in abc.abc_menu.buttons.values():
            b.add_press_listener(self.create_screen)
            b.add_release_listener(self.create_screen)
        
        abc.abc_menu.add_menu_loaded_listener(self.add_menu_buttons_listeners)

    def add_site_authors_screen_web_listeners(self, authors):
        """ Add web listeners to site authors screen
        
        :param authors: screen
        """
        n = authors.navigator
        
        lb = n.left_button
        lb.add_release_listener(self.site_authors_left_button_pressed)
        lb.add_press_listener(self.site_authors_left_button_pressed)
        lb.add_release_listener(self.site_authors_right_button_pressed)
        lb.add_release_listener(self.create_screen)
        
        rb = n.right_button
        rb.add_release_listener(self.site_authors_right_button_pressed)
        rb.add_press_listener(self.site_authors_right_button_pressed)
        rb.add_release_listener(self.site_authors_left_button_pressed)
        rb.add_release_listener(self.create_screen)
        
        hb = n.home_button
        hb.add_press_listener(self.site_authors_home_button_pressed)
        hb.add_release_listener(self.create_screen)
        
        if getattr(n, "abc_button", None):
            ab = n.abc_button
            ab.add_release_listener(self.site_authors_abc_button_pressed)
            ab.add_press_listener(self.site_authors_abc_button_pressed)
            ab.add_release_listener(self.create_screen)
            
        nb = n.new_books_button
        nb.add_release_listener(self.site_authors_new_books_button_pressed)
        nb.add_press_listener(self.site_authors_new_books_button_pressed)
        nb.add_release_listener(self.create_screen)
        
        if getattr(n, "genre_button", None):
            gb = n.genre_button
            gb.add_release_listener(self.site_authors_genre_button_pressed)
            gb.add_press_listener(self.site_authors_genre_button_pressed)
            gb.add_release_listener(self.create_screen)
            
        pb = n.player_button
        pb.add_release_listener(self.site_authors_player_button_pressed)
        pb.add_press_listener(self.site_authors_player_button_pressed)
        pb.add_release_listener(self.create_screen)
        
        bb = n.back_button
        bb.add_press_listener(self.site_authors_back_button_pressed)
        bb.add_release_listener(self.create_screen)
        
        self.add_menu_buttons_listeners(authors.authors_menu)
        authors.authors_menu.add_menu_loaded_listener(self.create_screen)
    
    def add_site_author_books_screen_web_listeners(self, author_books):
        """ Add web listeners to site author books screen
        
        :param author_books: screen
        """
        n = author_books.navigator
        
        lb = n.left_button
        lb.add_release_listener(self.author_books_left_button_pressed)
        lb.add_press_listener(self.author_books_left_button_pressed)
        lb.add_release_listener(self.author_books_right_button_pressed)
        lb.add_release_listener(self.create_screen)
        
        rb = n.right_button
        rb.add_release_listener(self.author_books_right_button_pressed)
        rb.add_press_listener(self.author_books_right_button_pressed)
        rb.add_release_listener(self.author_books_left_button_pressed)
        rb.add_release_listener(self.create_screen)
        
        hb = n.home_button
        hb.add_press_listener(self.author_books_home_button_pressed)
        hb.add_release_listener(self.create_screen)
        
        if getattr(n, "abc_button", None):
            ab = n.abc_button
            ab.add_release_listener(self.author_books_abc_button_pressed)
            ab.add_press_listener(self.author_books_abc_button_pressed)
            ab.add_release_listener(self.create_screen)
            
        nb = n.new_books_button
        nb.add_release_listener(self.author_books_new_books_button_pressed)
        nb.add_press_listener(self.author_books_new_books_button_pressed)
        nb.add_release_listener(self.create_screen)
        
        if getattr(n, "genre_button", None):
            gb = n.genre_button
            gb.add_release_listener(self.author_books_genre_button_pressed)
            gb.add_press_listener(self.author_books_genre_button_pressed)
            gb.add_release_listener(self.create_screen)
            
        pb = n.player_button
        pb.add_release_listener(self.author_books_player_button_pressed)
        pb.add_press_listener(self.author_books_player_button_pressed)
        pb.add_release_listener(self.create_screen)
        
        bb = n.back_button
        bb.add_press_listener(self.author_books_back_button_pressed)
        bb.add_release_listener(self.create_screen)

        author_books.add_loading_listener(self.create_screen)
        author_books.book_menu.add_menu_loaded_listener(self.add_menu_buttons_listeners)
    
    def add_site_genre_screen_web_listeners(self, genre):
        """ Add web listeners to site genres screen
        
        :param genre: screen
        """
        n = genre.navigator
        
        lb = n.left_button
        lb.add_release_listener(self.site_genre_left_button_pressed)
        lb.add_press_listener(self.site_genre_left_button_pressed)
        lb.add_release_listener(self.site_genre_right_button_pressed)
        lb.add_release_listener(self.create_screen)
        
        rb = n.right_button
        rb.add_release_listener(self.site_genre_right_button_pressed)
        rb.add_press_listener(self.site_genre_right_button_pressed)
        rb.add_release_listener(self.site_genre_left_button_pressed)
        rb.add_release_listener(self.create_screen)
        
        hb = n.home_button
        hb.add_press_listener(self.site_genre_home_button_pressed)
        hb.add_release_listener(self.create_screen)
        
        if getattr(n, "abc_button", None):
            ab = n.abc_button
            ab.add_release_listener(self.site_genre_abc_button_pressed)
            ab.add_press_listener(self.site_genre_abc_button_pressed)
            ab.add_release_listener(self.create_screen)
            
        nb = n.new_books_button
        nb.add_release_listener(self.site_genre_new_books_button_pressed)
        nb.add_press_listener(self.site_genre_new_books_button_pressed)
        nb.add_release_listener(self.create_screen)
        
        if getattr(n, "genre_button", None):
            gb = n.genre_button
            gb.add_release_listener(self.site_genre_genre_button_pressed)
            gb.add_press_listener(self.site_genre_genre_button_pressed)
            gb.add_release_listener(self.create_screen)
            
        pb = n.player_button
        pb.add_release_listener(self.site_genre_player_button_pressed)
        pb.add_press_listener(self.site_genre_player_button_pressed)
        pb.add_release_listener(self.create_screen)
        
        bb = n.back_button
        bb.add_press_listener(self.site_genre_back_button_pressed)
        bb.add_release_listener(self.create_screen)
        
        self.add_menu_buttons_listeners(genre.genre_menu)
    
    def add_genre_books_screen_web_listeners(self, genre_books):
        """ Add web listeners to site genre books screen
        
        :param genre_books: screen
        """
        n = genre_books.navigator
        
        lb = n.left_button
        lb.add_release_listener(self.genre_books_left_button_pressed)
        lb.add_press_listener(self.genre_books_left_button_pressed)
        lb.add_release_listener(self.genre_books_right_button_pressed)
        lb.add_release_listener(self.create_screen)
        
        rb = n.right_button
        rb.add_release_listener(self.genre_books_right_button_pressed)
        rb.add_press_listener(self.genre_books_right_button_pressed)
        rb.add_release_listener(self.genre_books_left_button_pressed)
        rb.add_release_listener(self.create_screen)
        
        hb = n.home_button
        hb.add_press_listener(self.genre_books_home_button_pressed)
        hb.add_release_listener(self.create_screen)
        
        if getattr(n, "abc_button", None):
            ab = n.abc_button
            ab.add_release_listener(self.genre_books_abc_button_pressed)
            ab.add_press_listener(self.genre_books_abc_button_pressed)
            ab.add_release_listener(self.create_screen)
            
        nb = n.new_books_button
        nb.add_release_listener(self.genre_books_new_books_button_pressed)
        nb.add_press_listener(self.genre_books_new_books_button_pressed)
        nb.add_release_listener(self.create_screen)
        
        if getattr(n, "genre_button", None):
            gb = n.genre_button
            gb.add_release_listener(self.genre_books_genre_button_pressed)
            gb.add_press_listener(self.genre_books_genre_button_pressed)
            gb.add_release_listener(self.create_screen)
            
        pb = n.player_button
        pb.add_release_listener(self.genre_books_player_button_pressed)
        pb.add_press_listener(self.genre_books_player_button_pressed)
        pb.add_release_listener(self.create_screen)
        
        bb = n.back_button
        bb.add_press_listener(self.genre_books_back_button_pressed)
        bb.add_release_listener(self.create_screen)

        genre_books.add_loading_listener(self.create_screen)
        genre_books.book_menu.add_menu_loaded_listener(self.add_menu_buttons_listeners)

    def add_book_track_screen_web_listeners(self, book_track):
        """ Add web listeners to book tracks screen
        
        :param book_track: screen
        """
        n = book_track.navigator
        lb = n.left_button
        lb.add_release_listener(self.book_track_left_button_pressed)
        lb.add_press_listener(self.book_track_left_button_pressed)
        lb.add_release_listener(self.book_track_right_button_pressed)
        lb.add_release_listener(self.create_screen)
        
        rb = n.right_button
        rb.add_release_listener(self.book_track_right_button_pressed)
        rb.add_press_listener(self.book_track_right_button_pressed)
        rb.add_release_listener(self.book_track_left_button_pressed)
        rb.add_release_listener(self.create_screen)
        
        hb = n.home_button
        hb.add_press_listener(self.book_track_home_button_pressed)
        hb.add_release_listener(self.create_screen)
        
        if getattr(n, "abc_button", None):
            ab = n.abc_button
            ab.add_release_listener(self.book_track_abc_button_pressed)
            ab.add_press_listener(self.book_track_abc_button_pressed)
            ab.add_release_listener(self.create_screen)
            
        nb = n.new_books_button
        nb.add_release_listener(self.book_track_new_books_button_pressed)
        nb.add_press_listener(self.book_track_new_books_button_pressed)
        nb.add_release_listener(self.create_screen)
        
        if getattr(n, "genre_button", None):
            gb = n.genre_button
            gb.add_release_listener(self.book_track_genre_button_pressed)
            gb.add_press_listener(self.book_track_genre_button_pressed)
            gb.add_release_listener(self.create_screen)
            
        pb = n.player_button
        pb.add_release_listener(self.book_track_player_button_pressed)
        pb.add_press_listener(self.book_track_player_button_pressed)
        pb.add_release_listener(self.create_screen)
        
        bb = n.back_button
        bb.add_press_listener(self.book_track_back_button_pressed)
        bb.add_release_listener(self.create_screen)
        
        self.add_menu_buttons_listeners(book_track.track_menu)

    def shutdown(self):
        """ Shutdown Web Server """
        
        self.web_server.socket.close()
        
        