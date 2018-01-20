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
import threading
import math
import array

from voiceassistant.googleassistant.sounddevicestream import DEFAULT_AUDIO_SAMPLE_WIDTH

DEFAULT_AUDIO_ITER_SIZE = 3200

class ConversationStream(object):
    """Audio stream that supports half-duplex conversation.

    A conversation is the alternance of:
    - a recording operation
    - a playback operation

    Excepted usage:
      For each conversation:
      - start_recording()
      - read() or iter()
      - stop_recording()
      - start_playback()
      - write()
      - stop_playback()

      When conversations are finished:
      - close()
    """
    def __init__(self, source, sink):
        """ Initializer
        
        :param source: file-like stream object to read input audio bytes from.
        :param sink: file-like stream object to write output audio bytes to.
        """        
        self._source = source
        self._sink = sink
        self._iter_size = DEFAULT_AUDIO_ITER_SIZE
        self._sample_width = DEFAULT_AUDIO_SAMPLE_WIDTH
        self._stop_recording = threading.Event()
        self._start_playback = threading.Event()
        self._volume_percentage = 50

    def start_recording(self):
        """ Start recording from the audio source. """
        
        self._stop_recording.clear()        
        self._source.start()
        if self._sink:
            self._sink.start()

    def stop_recording(self):
        """ Stop recording from the audio source. """
        
        self._stop_recording.set()

    def start_playback(self):
        """ Start playback to the audio sink. """
        
        self._start_playback.set()

    def stop_playback(self):
        """ Stop playback from the audio sink. """
        
        self._start_playback.clear()
        self._source.stop()
        if self._sink:
            self._sink.stop()

    @property
    def volume_percentage(self):
        """ The current volume setting as an integer percentage (1-100). """
        
        return self._volume_percentage

    @volume_percentage.setter
    def volume_percentage(self, new_volume_percentage):
        """ Set volume 
        
        :param new_volume_percentage: new volume level
        """
        logging.info('Volume set to %s%%', new_volume_percentage)
        self._volume_percentage = new_volume_percentage

    def read(self, size):
        """ Read bytes from the source (if currently recording).

        Will returns an empty byte string, if stop_recording() was called.
        :param size: buffer size
        """
        if self._stop_recording.is_set():
            return b''
        return self._source.read(size)

    def write(self, buf):
        """ Write bytes to the sink (if currently playing).

        Will block until start_playback() is called.
        :param buf: buffer
        """
        self._start_playback.wait()
        buf = self.align_buf(buf, self._sample_width)
        buf = self.normalize_audio_buffer(buf, self.volume_percentage)
        if self._sink:
            return self._sink.write(buf)

    def close(self):
        """ Close source and sink. """
        
        self._source.close()
        if self._sink:
            self._sink.close()

    def __iter__(self):
        """ Returns a generator reading data from the stream. """
        
        return iter(lambda: self.read(self._iter_size), b'')

    @property
    def sample_rate(self):
        """ Sample rate property getter  """
        
        return self._source.sample_rate
    
    def align_buf(self, buf, sample_width):
        """ In case of buffer size not aligned to sample_width pad it with 0s
        
        :param buf: buffer
        :param sample_width: the width of sample
        """
        remainder = len(buf) % sample_width
        if remainder != 0:
            buf += b'\0' * (sample_width - remainder)
        return buf

    def normalize_audio_buffer(self, buf, volume_percentage, sample_width=2):
        """Adjusts the loudness of the audio data in the given buffer.
    
        Volume normalization is done by scaling the amplitude of the audio
        in the buffer by a scale factor of 2^(volume_percentage/100)-1.
        For example, 50% volume scales the amplitude by a factor of 0.414,
        and 75% volume scales the amplitude by a factor of 0.681.
        For now we only sample_width 2.
    
        :param buf: byte string containing audio data to normalize.
        :param volume_percentage: volume setting as an integer percentage (1-100).
        :param sample_width: size of a single sample in bytes.
        """
        if sample_width != 2:
            raise Exception('unsupported sample width:', sample_width)
        scale = math.pow(2, 1.0*volume_percentage/100)-1
        # Construct array from bytes based on sample_width, multiply by scale
        # and convert it back to bytes
        arr = array.array('h', buf)
        for idx in range(0, len(arr)):
            arr[idx] = int(arr[idx]*scale)
        buf = arr.tostring()
        return buf

