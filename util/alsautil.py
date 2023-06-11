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
import sys
import codecs
import logging
import shutil
import subprocess

from datetime import datetime
from os.path import expanduser

UTF8 = "utf8"
TOKEN_1 = "card "
TOKEN_2 = "plughw:"

class AlsaUtil(object):
    """ ALSA utility class """

    def __init__(self):
        """ Initializer """

        self.home = expanduser("~")
        config_filename = ".asoundrc"
        self.ALSA_CONFIG_FILE = os.path.join(self.home, config_filename)

    def get_alsa_cards(self):
        """ Get ALSA cards

        :return: list of tuples where first element is card ID, second ID and description
        """
        card_lines = []
        cards = []
        default_card = self.get_default_card()

        if "win" in sys.platform:
            command = "type " + os.path.join(self.home, "aplay.txt")
            use_shell = True
        else:
            command = "aplay -l"
            use_shell = False

        try:
            n = subprocess.check_output(command.split(), shell=use_shell)
            content = n.decode("utf8")
            lines = content.split("\n")
            card_lines = [n for n in lines if n.startswith("card ")]
        except Exception as e:
            logging.debug(e)
            return cards

        for i, card in enumerate(card_lines):
            tokens = card.split(",")
            index_id_desc = tokens[0]
            tokens = index_id_desc.split(":")
            id_desc = tokens[1].strip()
            id = id_desc.split(" ")

            try:
                n = int(default_card)
                digit = True
            except:
                digit = False

            if digit:
                if i == int(default_card):
                    current = True
                else:
                    current = False
            else:
                if id[0] == default_card:
                    current = True
                else:
                    current = False

            cards.append((id[0], id_desc.strip(), current))

        return cards

    def get_default_card(self):
        """ Get default ALSA card

        :return: default card index or ID
        """
        default_card = ""

        with codecs.open(self.ALSA_CONFIG_FILE, "r", UTF8) as file:
            lines = file.read().split(os.linesep)
            for line in lines:
                if TOKEN_1 in line:
                    start = line.index(TOKEN_1)
                    default_card = line[start + len(TOKEN_1):]
                    break

        return default_card

    def set_default_card(self, card_id):
        """ Backup the current .asoundrc file and create the new one with specified card ID

        :param card_id: new card ID
        """
        new_config = ""
        final_config = ""

        try:
            ts = datetime.now().strftime(".%m.%d.%Y.%H.%M.%S")
            new_filename = self.ALSA_CONFIG_FILE + ts
            shutil.copy(self.ALSA_CONFIG_FILE, new_filename)
        except Exception as e:
            logging.debug(e)
            return

        with codecs.open(self.ALSA_CONFIG_FILE, "r", UTF8) as file:
            alsa_config_file = file.read()
            if TOKEN_1 in alsa_config_file:
                start = alsa_config_file.index(TOKEN_1)
                end_of_line = alsa_config_file.find(os.linesep, start)
                new_config = alsa_config_file[0:start + len(TOKEN_1)] + card_id + alsa_config_file[end_of_line:]
            if TOKEN_2 in new_config:
                token_start = new_config.index(TOKEN_2)
                comma_start = new_config.find(",", token_start)
                final_config = new_config[0:token_start + len(TOKEN_2)] + card_id + new_config[comma_start:] 

        if final_config:
            with codecs.open(self.ALSA_CONFIG_FILE, "w", UTF8) as file:
                file.write(final_config)

    def get_mixer_name(self):
        """ Get the ALSA default mixer name

        :return: default mixer name
        """
        mixer_line = ""
        mixer_name = ""

        if "win" in sys.platform:
            command = "type " + os.path.join(self.home, "amixer.txt")
            use_shell = True
        else:
            command = "amixer"
            use_shell = False

        try:
            n = subprocess.check_output(command.split(), shell=use_shell)
            content = n.decode("utf8")
            lines = content.split("\n")
            mixer_line = lines[0]
        except Exception as e:
            logging.debug(e)
            return ""

        if not mixer_line:
            return ""

        tokens = mixer_line.split("'")

        if tokens and len(tokens) > 1 and tokens[1]:
            mixer_name = tokens[1]

        return mixer_name
