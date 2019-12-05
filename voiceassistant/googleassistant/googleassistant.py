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

import google.auth.transport.grpc
import google.auth.transport.requests
import google.oauth2.credentials
import json
import logging

from threading import Thread
from voiceassistant.googleassistant.conversationstream import ConversationStream
from voiceassistant.googleassistant.sounddevicestream import SoundDeviceStream
from google.rpc import code_pb2
from google.assistant.embedded.v1alpha2 import embedded_assistant_pb2, embedded_assistant_pb2_grpc
from ui.state import State
from util.keys import USER_EVENT_TYPE

ASSISTANT_API_ENDPOINT = 'embeddedassistant.googleapis.com'
END_OF_UTTERANCE = embedded_assistant_pb2.AssistResponse.END_OF_UTTERANCE
DIALOG_FOLLOW_ON = embedded_assistant_pb2.DialogStateOut.DIALOG_FOLLOW_ON
CLOSE_MICROPHONE = embedded_assistant_pb2.DialogStateOut.CLOSE_MICROPHONE
TIMEOUT = 6 # seconds

class GoogleAssistant(object):
    """ Implementation of Voice Assistant based on Google Assistant """
    
    def __init__(self, credentials, language_code, commands, device_model_id, device_id):
        """ Initializer
        
        :param credentials: credentials filename. Should be defined in file config.txt
        :param language_code: language code e.g. en-US
        :param commands: dictionary of commands for the language
        :param device_model_id: model ID of the registered device
        :param device_id: ID or the registered device
        """
        self.language_code = language_code
        self.commands = commands.values()
        self.device_model_id = device_model_id
        self.device_id = device_id
        
        try:
            with open(credentials, 'r') as f:
                c = google.oauth2.credentials.Credentials(token=None, **json.load(f))
                http_request = google.auth.transport.requests.Request()
                c.refresh(http_request)
                self.channel = google.auth.transport.grpc.secure_authorized_channel(c, http_request, ASSISTANT_API_ENDPOINT)
        except Exception as e:
            logging.debug("Cannot connect to Google API")
            raise e
        
        try:
            audio_source = SoundDeviceStream()
            audio_sink = None
            self.conversation_stream = ConversationStream(audio_source, audio_sink)
        except Exception as e:
            raise e
        
        self.conversation_state = None
        self.assistant = embedded_assistant_pb2_grpc.EmbeddedAssistantStub(self.channel)
        self.GRPC_DEADLINE = TIMEOUT
        self.text_listeners = []
        self.start_conversation_listeners = []
        self.stop_conversation_listeners = []
        self.run_assistant = False
    
    def change_language(self, language, commands):
        """ Change assistant language
        
        :param language: new language
        """
        self.language_code = language
        self.commands = commands.values()
    
    def is_running(self):
        """ Check if assistant is running
        
        :return: True - assistant is running, False - assistant is not running
        """
        return self.run_assistant
        
    def start(self):
        """ Start assistant thread """
        
        if self.run_assistant:
            return
        
        self.run_assistant = True
        t = Thread(target = self.start_assistant_thread)
        t.start()
        
    def start_assistant_thread(self):
        """ Implementation of the assistant thread """
        
        logging.debug("start")
        while self.run_assistant:
            logging.debug("running")
            self.notify_start_conversation_listeners()
            try:
                self.assist()
            except Exception as e:
                logging.error(str(e))
        logging.debug("stopped loop")
        
    def stop(self):
        """ Stop assistant thread """
        
        if not self.run_assistant:
            return
                
        t = Thread(target = self.stop_assistant_thread)
        t.start()
    
    def stop_assistant_thread(self):
        """ Implementation of the stop assistant thread """
        
        logging.debug("stopping...")
        self.notify_stop_conversation_listeners()
        self.conversation_stream.stop_recording()
        self.run_assistant = False            
        logging.debug("stopped conversation")
            
    def assist(self):
        """ Send a voice request to the Assistant """
        
        self.conversation_stream.start_recording()
        def iter_assist_requests():
            for c in self.gen_assist_requests():
                yield c
        
        for resp in self.assistant.Assist(iter_assist_requests(), self.GRPC_DEADLINE):
            if resp.event_type == END_OF_UTTERANCE:
                logging.info('End of audio request detected')
                self.conversation_stream.stop_recording()
            if resp.speech_results:
                received = ""
                for r in resp.speech_results:
                    received = r.transcript.lower().strip()

                if received in self.commands:
                    self.notify_text_listeners(received)
                    break
                                
        self.conversation_stream.stop_playback()

    def gen_assist_requests(self):
        """ Yields: AssistRequest messages to send to the API. """

        dialog_state_in = embedded_assistant_pb2.DialogStateIn(language_code=self.language_code, conversation_state=b'')        
        
        if self.conversation_state:
            logging.debug('Sending conversation state.')
            dialog_state_in.conversation_state = self.conversation_state
        
        config = embedded_assistant_pb2.AssistConfig(        
            audio_in_config=embedded_assistant_pb2.AudioInConfig(
                encoding='LINEAR16',
                sample_rate_hertz=self.conversation_stream.sample_rate,
            ),
            audio_out_config=embedded_assistant_pb2.AudioOutConfig(
                encoding='LINEAR16',
                sample_rate_hertz=self.conversation_stream.sample_rate,
                volume_percentage=self.conversation_stream.volume_percentage,
            ),
            dialog_state_in = dialog_state_in, device_config = embedded_assistant_pb2.DeviceConfig(device_id=self.device_id, device_model_id=self.device_model_id)
        )
        # The first AssistRequest must contain the AssistConfig and no audio data.
        yield embedded_assistant_pb2.AssistRequest(config=config)
        for data in self.conversation_stream:
            # Subsequent requests need audio data, but not config.
            yield embedded_assistant_pb2.AssistRequest(audio_in=data)

    def add_text_listener(self, listener):
        """ Add recognized text listener
        
        :param listener: text listener
        """
        if listener not in self.text_listeners:
            self.text_listeners.append(listener)
            
    def notify_text_listeners(self, text):
        """ Notify recognized text listeners
        
        :param text: recognized text
        """
        for listener in self.text_listeners:
            listener(text)
            
    def add_start_conversation_listener(self, listener):
        """ Add start conversation listener
        
        :param listener: text listener
        """
        if listener not in self.start_conversation_listeners:
            self.start_conversation_listeners.append(listener)
            
    def notify_start_conversation_listeners(self):
        """ Notify start conversation listeners """

        if not self.run_assistant:
            return

        for listener in self.start_conversation_listeners:
            s = State()
            s.type = USER_EVENT_TYPE
            listener(s)
            
    def add_stop_conversation_listener(self, listener):
        """ Add stop conversation listener
        
        :param listener: text listener
        """
        if listener not in self.stop_conversation_listeners:
            self.stop_conversation_listeners.append(listener)
            
    def notify_stop_conversation_listeners(self):
        """ Notify stop conversation listeners """
        
        for listener in self.stop_conversation_listeners:
            listener()
