# Copyright 2023 Peppy Player peppy.player@gmail.com
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

import os
import codecs

from configparser import ConfigParser
from util.keys import UTF8

VOICE_ASSISTANT_FOLDER = "voiceassistant"
CONFIG_FILENAME = "voice-assistant-config.txt"
VOICE_ASSISTANT = "voice.assistant"
VOICE_ASSISTANT_TYPE = "type"
VOICE_ASSISTANT_TRANSLATE_NAMES = "translate.names"

class VoiceAssistantUtil(object):
    """ Voice Assistant utility class """

    def __init__(self):
        self.path = os.path.join(os.getcwd(), VOICE_ASSISTANT_FOLDER, CONFIG_FILENAME)
    
    def load_config(self):
        """ Load voice assistant configuration file
        
        :return: configuration dictionary
        """
        config_parser = ConfigParser()
        config_parser.read(self.path, encoding=UTF8)

        config = {VOICE_ASSISTANT_TYPE: config_parser.get(VOICE_ASSISTANT, VOICE_ASSISTANT_TYPE)}
        config[VOICE_ASSISTANT_TRANSLATE_NAMES] = config_parser.getboolean(VOICE_ASSISTANT, VOICE_ASSISTANT_TRANSLATE_NAMES)

        return config
    
    def save_config(self, config):
        """ Save configuration
        
        :param config: new configuration
        """
        config_parser = ConfigParser()
        config_parser.optionxform = str
        config_parser.read(self.path, encoding=UTF8)
        config_parser.set(VOICE_ASSISTANT, VOICE_ASSISTANT_TRANSLATE_NAMES, str(config[VOICE_ASSISTANT_TRANSLATE_NAMES]))

        with codecs.open(self.path, 'w', UTF8) as file:
            config_parser.write(file)
