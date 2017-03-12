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

import socket
import time
import logging

class MpdConnection(object):
    """ Handles TCP/IP communication with MPD server """
        
    def __init__(self, host, port, reader_flags='rb', writer_flags='w', encoding='utf-8'):
        """ Initializer
        
        :param host: host where MPD process is running
        :param port: port at which MPD process is listening
        :param reader_flags: flags used for creating reader
        :param writer_flags: flags used for creating writer
        :param encoding: encoding used to encode/decode messages
        """
        self.host = host
        self.port = port
        self.reader_flags = reader_flags
        self.writer_flags = writer_flags
        self.character_encoding = encoding
        self.OK = "OK"
        self.socket = None
        self.reader = None
        self.writer = None

    def connect(self):
        """ Connect to MPD process' socket. It's making 3 attempts maximum with 2 seconds delay. """  
              
        attempts = 3
        delay = 2
        attempt = 0
         
        while attempt < attempts:
            success = self.try_to_connect()
            if not success:
                logging.error("Cannot connect to MPD server. Attempt {}".format(attempt))
                attempt = attempt + 1
                time.sleep(delay)
            else:
                attempt = attempts
    
    def try_to_connect(self):
        """ Connect to MPD socket """
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self.socket.connect((self.host, self.port))
            self.reader = self.socket.makefile(self.reader_flags, encoding=self.character_encoding)
            self.writer = self.socket.makefile(self.writer_flags, encoding=self.character_encoding)
            self.read_line()
        except:
            if self.socket: 
                self.disconnect()
                return False
        return True
    
    def disconnect(self):
        """ Disconnect from MPD """
        try:
            if self.reader: self.reader.close()
            if self.writer: self.writer.close()
            if self.socket: self.socket.close()
        except:
            pass
    
    def write(self, line):
        """ Send the message to MPD
        
        :param line: message
        """        
        if self.writer == None: return
        try:
            self.writer.write(line + "\n")
            self.writer.flush()
        except:
            pass
        
    def read_line(self):
        """ Read one line message from MPD
        
        :return: message
        """
        line = None
        if self.reader == None: return line
        
        try:
            line = self.reader.readline()
            if self.encoding:
                line = line.decode(self.encoding)
            line = line.rstrip()
        except:
            pass
                
        return line

    def read_dictionary(self, cmd):
        """ Send command to MPD and read the output messages until it's terminated by OK
        
        :param cmd: command for MPD
        :return: dictionary representing MPD process output for the specified input command
        """
        d = {}        
        self.connect()
        self.write(cmd)
        
        line = self.read_line()
        
        if not line:
            return d
        
        line = line.decode(self.character_encoding).rstrip()
        
        while line and line != self.OK:
            index = line.find(": ")
            key = line[0:index]
            if key.endswith(":file"):
                key = key[0 : key.strip().find(":file")]
            value = line[index + 1:]
            d[key.rstrip()] = value.rstrip().strip()
            line = self.read_line().decode(self.character_encoding).rstrip()
        self.disconnect()
        
        return d
    
    def command(self, name):
        """ Send command to MPD process and read just one line output from MPD """
        
        self.connect()
        self.write(name)
        line = self.read_line()
        self.disconnect()
        return line
