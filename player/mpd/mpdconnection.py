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

import socket
import time
import logging

class MpdConnection(object):
    """ Handles TCP/IP communication with MPD process """
        
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
        self.encoding = encoding
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
            self.reader = self.socket.makefile(self.reader_flags)
            self.writer = self.socket.makefile(self.writer_flags)
            self.read_line()
        except:
            if self.socket: 
                self.disconnect()
                return False
        return True
    
    def disconnect(self):
        """ Disconnect from MPD """
        
        if self.reader: self.reader.close()
        if self.writer: self.writer.close()
        if self.socket: self.socket.close()
    
    def write(self, line):
        """ Send the message to MPD 
        :param line: message
        """        
        if self.writer == None: return
        self.writer.write(line + "\n")
        self.writer.flush()
        
    def read_line(self):
        """ Read one line message from MPD
        :return: message
        """
        if self.reader == None: return None
        line = self.reader.readline()
        if self.encoding:
            line = line.decode(self.encoding)
        line = line.rstrip()        
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
        
        while line != self.OK:
            index = line.find(": ")
            key = line[0:index]
            value = line[index + 1:]
            d[key.rstrip()] = value.rstrip()
            line = self.read_line()
        self.disconnect()
        return d
    
    def command(self, name):
        """ Send command to MPD process and read just one line output from MPD """
        
        self.connect()
        self.write(name)
        line = self.read_line()
        self.disconnect()
        return line
