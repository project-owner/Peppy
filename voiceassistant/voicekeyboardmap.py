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

import pygame

# Maps voice commands to keyboard keys
VOICE_KEYBOARD_MAP = {
    "VA_SHUTDOWN" : pygame.K_END,
    "VA_HOME" : pygame.K_HOME,
    "VA_GO_HOME" : pygame.K_HOME,            
    "VA_ABOUT" : pygame.K_HOME,
    "VA_GO_ABOUT" : pygame.K_HOME,            
    "VA_PAUSE" : pygame.K_SPACE,
    "VA_PLAY" : pygame.K_SPACE,
    "VA_OK" : pygame.K_RETURN,
    "VA_ENTER" : pygame.K_RETURN,
    "VA_SELECT" : pygame.K_RETURN,
    "VA_LEFT" : pygame.K_LEFT,
    "VA_GO_LEFT" : pygame.K_LEFT,
    "VA_PREVIOUS" : pygame.K_LEFT,
    "VA_RIGHT" : pygame.K_RIGHT,
    "VA_GO_RIGHT" : pygame.K_RIGHT,
    "VA_NEXT" : pygame.K_RIGHT,
    "VA_UP" : pygame.K_UP,
    "VA_GO_UP" : pygame.K_UP,
    "VA_DOWN" : pygame.K_DOWN,
    "VA_GO_DOWN" : pygame.K_DOWN,
    "VA_NEXT_PAGE" : pygame.K_PAGEUP,
    "VA_PREVIOUS_PAGE" : pygame.K_PAGEDOWN,
    "VA_MUTE" : pygame.K_x,
    "VA_BACK" : pygame.K_ESCAPE,
    "VA_GO_BACK" : pygame.K_ESCAPE,
    "VA_VOLUME" : pygame.K_s,
    "VA_VOLUME_UP" : pygame.K_KP_PLUS,
    "VA_VOLUME_DOWN" : pygame.K_KP_MINUS,
    "VA_TIME_UP" : pygame.K_KP_PLUS,
    "VA_TIME_DOWN" : pygame.K_KP_MINUS,
    "VA_TIME" : pygame.K_s,            
    "VA_ABC" : pygame.K_s,
    "VA_ALPHABET" : pygame.K_s,            
    "VA_SEARCH_BY_AUTHOR" : pygame.K_s,                        
    "VA_ROOT" : pygame.K_r,
    "VA_MUSIC" : pygame.K_m,
    "VA_USER_HOME" : pygame.K_m,            
    "VA_NEW_BOOKS" : pygame.K_m,            
    "VA_LANGUAGE" : pygame.K_m,
    "VA_GO_LANGUAGE" : pygame.K_m,
    "VA_CHANGE_LANGUAGE" : pygame.K_m,                         
    "VA_SEARCH_BY_GENRE" : pygame.K_r,                       
    "VA_GENRE" : pygame.K_m,                       
    "VA_PARENT" : pygame.K_p,
    "VA_0" : pygame.K_0,
    "VA_1" : pygame.K_1,
    "VA_2" : pygame.K_2,
    "VA_3" : pygame.K_3,
    "VA_4" : pygame.K_4,
    "VA_5" : pygame.K_5,
    "VA_6" : pygame.K_6,
    "VA_7" : pygame.K_7,
    "VA_8" : pygame.K_8,
    "VA_9" : pygame.K_9,
    "VA_PLAYER" : pygame.K_SPACE,
    "VA_GO_PLAYER" : pygame.K_SPACE,
    "VA_SCREENSAVER" : pygame.K_s,
    "VA_SAVER" : pygame.K_s}        
