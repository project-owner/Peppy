# Copyright 2016-2024 Peppy Player peppy.player@gmail.com
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

import time
import logging

from threading import Thread, RLock
from timeit import default_timer as timer
from ui.container import Container
from ui.slider.slider import Slider
from ui.layout.borderlayout import BorderLayout
from util.config import USAGE, USE_WEB, COLORS, COLOR_BRIGHT
from ui.state import State

class TimeSlider(Container):
    """ Time slider component """

    def __init__(self, util, name, bgr, slider_color, img_knob, img_knob_on, key_incr, key_decr, key_knob, bb, f, key_incr_alt=None, key_decr_alt=None):
        """ Initializer
        
        :param util: utility object
        :param name: slider name
        :param bgr: slider background color
        :param slider_color: slider center line color
        :param img_knob: knob image
        :param img_knob_on: knob image in on state
        :param key_incr: keyboard key associated with slider increment action
        :param key_decr: keyboard key associated with slider decrement action
        :param key_knob: keyboard key associated with single click on knob
        :param bb: slider bounding box
        :param key_incr_alt: alternative keyboard key associated with slider increment action
        :param key_decr_alt: alternative keyboard key associated with slider decrement action
        """
        Container.__init__(self, util, background=bgr, bounding_box=bb)
        self.content = None
        self.util = util
        self.config = util.config
        self.bgr = bgr
        
        self.lock = RLock()
        # don't increase the following number too much as it affects VU Meter screen-saver performance
        self.LOOP_CYCLES_PER_SECOND = 5 
        self.CYCLE_TIME = 1 / self.LOOP_CYCLES_PER_SECOND        
        self.active = True    

        layout = BorderLayout(bb)
        layout.set_percent_constraints(0.0, 0.0, 24.0, 24.0)
        
        current_time_name = name + "current"
        total_time_name = name + "total"
        current_time_layout = layout.LEFT
        total_time_layout = layout.RIGHT

        self.slider = Slider(util, name + "slider", bgr, slider_color, img_knob, img_knob_on, None, key_incr, key_decr, key_knob, layout.CENTER, False, key_incr_alt=key_incr_alt, key_decr_alt=key_decr_alt)
        self.slider.add_slide_listener(self.slider_action_handler)
        self.total_track_time = 0
        self.seek_time = 0     
        self.add_component(self.slider)
        
        height = 34
        font_size = int((current_time_layout.h * height)/100.0)
        c = self.config[COLORS][COLOR_BRIGHT]
        self.current = f.create_output_text(current_time_name, current_time_layout, bgr, c, font_size)
        self.total = f.create_output_text(total_time_name, total_time_layout, bgr, c, font_size)        
        self.add_component(self.current)
        self.add_component(self.total)

        self.seek_listeners = []
        self.start_timer_listeners = []
        self.stop_timer_listeners = []
        self.update_seek_listeners = True
        self.use_web = self.config[USAGE][USE_WEB]
        self.timer_started = False
        self.current_time = 0
        self.update_component = True
    
    def set_parent_screen(self, scr):
        """ Add parent screen

        :param scr: parent screen
        """
        self.slider.parent_screen = scr
        self.current.parent_screen = scr
        self.total.parent_screen = scr

    def start_timer(self):
        """ Start timer thread """

        logging.debug("start timer")
        self.timer_started = True
        self.thread = Thread(target = self.start_loop)
        self.thread.start()
        
    def stop_timer(self):  
        """ Stop timer thread """

        logging.debug("stop timer")
        self.timer_started = False
        
    def set_track_info(self, track_info):
        """ Set track time info
        
        :param track_info: track info
        """        
        if not isinstance(track_info, dict):
            return
        
        if not self.active:
            return

        t = "0"

        try:
            t = track_info["seek_time"]
        except:
            pass
        
        try:
            track_time = track_info["Time"]
            self.total_track_time = int(float(track_time))
            track_time = self.convert_seconds_to_label(track_time)
            self.total.set_text(track_time)
        except:
            pass
        
        try:
            if track_info["state"] != "pause":
                with self.lock:
                    self.seek_time = int(float(t))
                    self.stop_timer()
                    time.sleep(0.3)
                    self.start_timer()
                    self.update_seek_listeners = True
                    self.notify_start_timer_listeners()
        except:
            pass
    
    def stop_thread(self):
        """ Stop knob animation thread """
        
        with self.lock:
            logging.debug("stop thread")
            if self.timer_started:
                self.stop_timer()
                self.notify_stop_timer_listeners()
                logging.debug("timer stopped")
    
    def start_loop(self):
        """ Animation loop """
        
        count = 1
        while self.timer_started:
            start_update_time = timer()
            if count == 1:
                seek_time_label = self.convert_seconds_to_label(self.seek_time)
                self.current.set_text(seek_time_label, update=True)
                self.update_component = True
                step = self.total_track_time / 100
                if step > 0:
                    p = int(float(self.seek_time) / step)
                    if p > self.slider.get_position() or p == 0:
                        self.slider.set_position(p)
                        self.slider.update_position()
                        if self.use_web and self.update_seek_listeners and hasattr(self, "web_seek_listener"):
                            s = State()
                            s.event_origin = self
                            s.seek_time_label = seek_time_label
                            self.web_seek_listener(s)
                            self.update_seek_listeners = False                                
                    self.seek_time += 1
                    if int(self.seek_time) >= self.total_track_time + 1:
                        count = self.LOOP_CYCLES_PER_SECOND - 1
                        self.stop_timer()
            if count == self.LOOP_CYCLES_PER_SECOND:
                count = 1
            else:
                count += 1

            t = self.CYCLE_TIME - (timer() - start_update_time)
                                
            if t > 0:
                time.sleep(t)
            else:
                time.sleep(0.3)

    def set_current_time(self, current_time):
        """ Set current time

        :param current_time: the current time
        """
        self.current_time = current_time

    def convert_seconds_to_label(self, sec):
        """ Convert seconds to label in format HH:MM:SS
        
        :param sec: seconds
        """
        s = int(float(sec))
        hours = int(s / 3600)
        minutes = int(s / 60)
        seconds = int(s % 60)
        label = ''
        
        if hours != 0:
            label += str(hours).rjust(2, '0') + ":"
            minutes = int((s - hours * 3600) / 60)
            
        label += str(minutes).rjust(2, '0') + ":"
        label += str(seconds).rjust(2, '0')
        
        return label
    
    def slider_action_handler(self, evt):
        """ Slider action handler
        
        :param evt: event
        """
        if not self.timer_started:
            return
        
        step = self.total_track_time / 100
        self.seek_time = step * evt.position
        
        st = self.convert_seconds_to_label(self.seek_time)
        self.current.set_text(st)
        self.notify_seek_listeners(str(self.seek_time))
        
        if self.use_web and hasattr(self, "web_seek_listener"):
            s = State()
            s.event_origin = self
            s.seek_time_label = str(self.seek_time)
            self.web_seek_listener(s)
    
    def reset(self):
        self.stop_thread()
        t = 0
        self.seek_time = t
        self.set_track_info({"Time": t})
        self.slider.set_position(t)
        label = self.convert_seconds_to_label(t)
        self.current.set_text(label)
        self.slider.update_position() 
        
    def add_seek_listener(self, listener):
        """ Add seek track listener
        
        :param listener: the listener
        """
        if listener not in self.seek_listeners:
            self.seek_listeners.append(listener)
            
    def notify_seek_listeners(self, seek_time):
        """ Notify all seek track listeners
        
        :param seek_time: track time
        """ 
        for listener in self.seek_listeners:
            listener(seek_time)            
            
    def add_start_timer_listener(self, listener):
        """ Add start timer listener
        
        :param listener: the listener
        """
        if listener not in self.start_timer_listeners:
            self.start_timer_listeners.append(listener)
            
    def notify_start_timer_listeners(self):
        """ Notify all start timer listeners """ 
        
        for listener in self.start_timer_listeners:
            listener("")
            
    def add_stop_timer_listener(self, listener):
        """ Add stop timer listener
        
        :param listener: the listener
        """
        if listener not in self.stop_timer_listeners:
            self.stop_timer_listeners.append(listener)
            
    def notify_stop_timer_listeners(self):
        """ Notify all stop timer listeners """ 
        
        for listener in self.stop_timer_listeners:
            listener("")
            
    def pause(self):
        """ Stop animation thread """
        self.stop_thread()
    
    def resume(self): 
        """ Resumed in set_track_info """

        with self.lock:
            if not self.timer_started:
                self.start_timer()
                self.notify_start_timer_listeners()
