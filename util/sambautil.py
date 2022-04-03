# Copyright 2022 Peppy Player peppy.player@gmail.com
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
import logging
import codecs

from subprocess import Popen
from configparser import ConfigParser
from util.keys import UTF8
from util.config import USAGE, USE_SAMBA

SMB_CONF_PATH = "/etc/samba/smb.conf"
TMP_CONF_FILE = os.path.join(os.getcwd(), "smb.conf")
DEFAULT_SECTIONS = ["global", "homes", "printers", "print$"]
NAME = "name"
PATH = "path"
OPTIONS = "options"
START_COMMAND = "sudo systemctl start smbd"
STOP_COMMAND = "sudo systemctl stop smbd"
MOVE_COMMAND = "sudo mv " + TMP_CONF_FILE + " " + SMB_CONF_PATH

class SambaUtil(object):
    """ Samba Utility class """
    
    def __init__(self, util):
        """ Initializer 
        
        :param util: utility object
        """
        self.config = util.config

    def start_sharing(self):
        """ Start sharing service """

        if not self.config[USAGE][USE_SAMBA] or not self.is_shareable():
            return

        try:
            Popen(START_COMMAND.split(), shell=False)
        except Exception as e:
            logging.debug(e)

    def stop_sharing(self):
        """ Stop sharing service """

        if not self.config[USAGE][USE_SAMBA] or not self.is_shareable():
            return

        try:
            Popen(STOP_COMMAND.split(), shell=False)
        except Exception as e:
            logging.debug(e)

    def is_shareable(self):
        """ Check if Samba config file is available and has content
        
        :return: True - shareable, False - not shareable
        """
        if not os.path.exists(SMB_CONF_PATH):
            return False

        shares = self.get_shares()
        if not shares:
            return False

        return True

    def get_shares(self):
        """ Get shares from the Samba config file
        
        :return: the list of shares
        """
        logging.debug("Get shares")
        config_file = ConfigParser()
        config_file.optionxform = str
        config_file.read(SMB_CONF_PATH, encoding=UTF8)

        sections = config_file.sections()
        shares = []
        if not sections:
            return []

        for section in sections:
            if section not in DEFAULT_SECTIONS:
                shares.append(section)

        if not shares:
            return []

        config_shares = []

        for share in shares:
            s = {NAME: share}
            options = ""
            for (k, v) in config_file.items(share):
                if k == PATH:
                    s[PATH] = v
                else:
                    options += k + " = " + str(v) + "\n"
            if options:
                s[OPTIONS] = options
            config_shares.append(s)

        logging.debug(f"""Found {len(config_shares)} shares""")

        return config_shares

    def save_shares(self, shares):
        """ Save shares in the Samba config file
        
        :param shares: the list of shares
        """
        dirty = False
        config_parser = ConfigParser()
        config_parser.optionxform = str
        config_parser.read(SMB_CONF_PATH, encoding=UTF8)
        sections = config_parser.sections()

        for section in sections:
            if section in DEFAULT_SECTIONS:
                continue
            else:
                config_parser.remove_section(section)
                dirty = True

        for share in shares:
            name = share[NAME]
            config_parser.add_section(name)
            for s in share.items():
                if s[0] == NAME:
                    continue
                elif s[0] == OPTIONS:
                    lines = s[1].splitlines()
                    for line in lines:
                        parts = line.split("=")
                        config_parser.set(name, parts[0].strip(), str(parts[1]).strip())
                else:
                    config_parser.set(name, s[0], str(s[1]))
            dirty = True
        
        if dirty:
            with codecs.open(TMP_CONF_FILE, 'w', UTF8) as file:
                config_parser.write(file)

            try:
                Popen(MOVE_COMMAND.split(), shell=False)
            except Exception as e:
                logging.debug(e)
