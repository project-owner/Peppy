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

import struct
import logging

from hashlib import sha1
from base64 import b64encode

FRAME_FINAL_FRAGMENT = 0x80
FRAME_CONTINUATION = 0
FRAME_TEXT = 1
FRAME_MASK = 0x80
FRAME_BINARY = 2
CLOSE_CONNECTION = 8

class WebSocketProtocolHandler():
    """ This class handles server side of the WebSocket protocol """
    
    magic = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'

    def __init__(self, request):
        """ Initializer
        
        :param request: HTTP request
        """
        self.request = request
        self.closed = False

    def handshake(self):
        """ Implements WebSocket handshake functionality """
        key = self.request.headers['Sec-WebSocket-Key'].strip()
        accept_data = (key + self.magic).encode('latin-1', 'strict')
        digest = b64encode(sha1(accept_data).digest())
        d = {'Upgrade': 'websocket', 'Connection': 'Upgrade', 'Sec-WebSocket-Accept': str(digest.decode('latin-1'))}
        self.request.log_request(101)
        self.request.send_response_only(101)
        for k, v in d.items():
            self.request.send_header(k, v)
        self.request.end_headers()
        
    def read_next_message(self):
        """ Read next message from request """
        
        i = self.request.rfile
        
        header_byte_1 = struct.unpack('B', i.read(1))[0]
        header_byte_2 = struct.unpack('B', i.read(1))[0]
        
        fin = header_byte_1 & 0x80
        opcode = header_byte_1 & 0x0F 
        mask = header_byte_2 & 0x80
        length = header_byte_2 & 0x7F
        
        if fin != FRAME_FINAL_FRAGMENT:
            logging.warning("Multi-frame protocol not supported")
            return None
        
        if mask != FRAME_MASK:
            logging.warning("All frames sent from client to server should have mask bit set to 1")
            return None
        
        if length == 126:
            length = struct.unpack(">H", i.read(2))[0]
        elif length == 127:
            length = struct.unpack(">Q", i.read(8))[0]
            
        masks = list(iter(i.read(4)))
        a = bytearray()
        for byte in iter(i.read(length)):
            a.append(byte ^ masks[len(a) % 4])

        if opcode == FRAME_CONTINUATION:
            logging.warning("Frame continuation not supported")
            return None
        elif opcode == FRAME_TEXT:            
            return a.decode('utf-8')
        elif opcode == FRAME_BINARY:
            return bytes(a)
        elif opcode == CLOSE_CONNECTION:
            self.closed = True
            return None
        else:
            logging.warning("Not supported operation code")

    def read_message(self):
        """ Read the message from request """
        
        message = None
        while message is None and not self.closed:
            message = self.read_next_message()
        return message

    def send_message(self, message):
        """ Send the message to client
        
        :param message: the message to send
        """
        output = self.request.wfile
        output.write(struct.Struct(">B").pack(129))
            
        length = len(message)
        if length <= 125: 
            output.write(struct.Struct(">B").pack(length))
        elif length >= 126 and length <= 65535:
            output.write(struct.Struct(">B").pack(126))
            output.write(struct.pack(">H", length))
        else:
            output.write(struct.Struct(">B").pack(127))
            output.write(struct.pack(">Q", length))
        output.write(message)
