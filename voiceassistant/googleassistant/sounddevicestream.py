# Copyright (C) 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Modified for Peppy Player

import logging

from sounddevice import RawInputStream
from threading import RLock

DEFAULT_AUDIO_SAMPLE_RATE = 16000 # sample rate in hertz.
DEFAULT_AUDIO_SAMPLE_WIDTH = 2 # size of a single sample in bytes.
DEFAULT_AUDIO_DEVICE_BLOCK_SIZE = 6400 # size in bytes of each read and write operation.
DEFAULT_AUDIO_DEVICE_FLUSH_SIZE = 25600 # size in bytes of silence data written during flush operation.
DEFAULT_DATA_TYPE = 'int16'

class SoundDeviceStream(object):
    """Audio stream based on an underlying sound device.
 
    It can be used as an audio source (read) and a audio sink (write).
    """
    def __init__(self):
        self.lock = RLock()
        self.audio_stream = None
        self.volume_percentage = 50
        self.sample_rate = DEFAULT_AUDIO_SAMPLE_RATE
        bs = int(DEFAULT_AUDIO_DEVICE_BLOCK_SIZE/2)
        try:
            self.audio_stream = RawInputStream(samplerate=DEFAULT_AUDIO_SAMPLE_RATE, dtype=DEFAULT_DATA_TYPE, channels=1, blocksize=bs)
        except Exception as e:
            logging.debug(str(e))

    def read(self, size):
        """Read bytes from the stream."""
        
        with self.lock:
            buf = self.audio_stream.read(size)
            return bytes(buf[0])
 
    def write(self, buf):
        """Write bytes to the stream."""
        self.audio_stream.write(buf)
        return len(buf)
 
    def flush(self):
        self.audio_stream.write(b'\x00' * DEFAULT_AUDIO_DEVICE_FLUSH_SIZE)
 
    def start(self):
        """Start the underlying stream."""
        
        if not self.audio_stream: return
        
        if self.audio_stream.active: return
        self.audio_stream.start()
 
    def stop(self):
        """Stop the underlying stream."""
        
        if not self.audio_stream: return
        
        if not self.audio_stream.active: return
        self.flush()
        self.audio_stream.stop()
 
    def close(self):
        """Close the underlying stream and audio interface."""
        if not self.audio_stream: return
        self.stop()
        self.audio_stream.close()
        self.audio_stream = None
