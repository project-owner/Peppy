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

from threading import RLock
from player.client.commandthread import CommandThread

class MpdConnection(object):
    """ Handles TCP/IP communication with MPD server """
    
    lock = RLock()
        
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
        self.IDLE_COMMAND_TIMEOUT = 3600.0
        self.COMMAND_TIMEOUT = 5.0 # command thread timeout in seconds

    def connect(self):
        """ Connect to MPD process' socket. It's making 3 attempts maximum with 2 seconds delay. """ 
         
        with self.lock:      
            attempts = 3
            delay = 2
            attempt = 0
             
            while attempt < attempts:
                success = self.try_to_connect()
                if not success:
                    logging.error("Host: " + self.host + " Port: " + str(self.port))
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
            self.socket.settimeout(self.IDLE_COMMAND_TIMEOUT)
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
        
        with self.lock:
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
        with self.lock:        
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
        with self.lock:
            line = None
            if self.reader == None: return line
            
            try:
                line = self.reader.readline()
                if line and not isinstance(line, str):
                    line = line.decode(self.character_encoding)
                line = line.rstrip()
            except:
                pass
    
            return line

    def get_multiline_result(self, cmd):
        """ Send command to MPD and read the output messages until it's terminated by OK
         
        :param cmd: command for MPD
        :return: list of lines returned after command
        """  
        with self.lock:
            r = []        
            self.connect()
            self.write(cmd)
            line = self.read_line()
            if not line:
                return r
            while line and line != self.OK:
                r.append(line)
                line = self.read_line()
            self.disconnect()            
            return r

    def read_dictionary(self, cmd):
        """ Call multiline result method and parse the list of returned lines
         
        :param cmd: command for MPD
        :return: dictionary representing MPD process output for the specified input command
        """        
        ct = CommandThread(target=self.get_multiline_result, args=[cmd])
        ct.start()
        r = ct.join(self.COMMAND_TIMEOUT)
        
        d = {}
        if r == None:
            return d
        
        with self.lock:
            for line in r:
                index = line.find(": ")
                key = line[0:index]
                if key.endswith(":file"):
                    key = key[0 : key.strip().find(":file")]
                value = line[index + 1:]
                d[key.rstrip()] = value.rstrip().strip()
        return d        

    def command_method(self, name):
        """ Send command to mpd process and read one line output.
        
        Connects and disconnects to/from mpd server to avoid mpd client
        connection timeout - default 60 seconds (property connection_timeout
        in mpd.conf)
        
        :param name: command name
        :return: command result
        """        
        with self.lock:
            self.connect()
            self.write(name)
            logging.debug("command: " + name)
            line = self.read_line()
            self.disconnect()
            logging.debug("return: " + str(line))
            return line
    
    def command(self, name):
        """ Start new command thread
        
        :param name: command name
        """
#         ct = CommandThread(target=self.command_method, args=[name])
#         ct.start()
#         r = ct.join(self.COMMAND_TIMEOUT)
        self.command_method(name)        
        return ""
    