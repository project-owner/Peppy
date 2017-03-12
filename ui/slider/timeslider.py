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

import time
from threading import Thread, RLock
from ui.component import Component
from ui.container import Container
from ui.slider.slider import Slider
from ui.layout.borderlayout import BorderLayout
from util.keys import COLORS, COLOR_BRIGHT, LINUX_PLATFORM, CURRENT
from util.config import CURRENT_FILE

class TimeSlider(Container):
    """ Time slider component """

    def __init__(self, util, name, bgr, slider_color, img_knob, img_knob_on, key_incr, key_decr, key_knob, bb):
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
        """
        Container.__init__(self, util, background=bgr, bounding_box=bb)
        self.util = util
        self.config = util.config

        self.lock = RLock()
        WINDOWS_CYCLE = 0.164
        LINUX_CYCLE = 0.164
        self.CYCLE = WINDOWS_CYCLE
        if self.config[LINUX_PLATFORM]:
            self.CYCLE = LINUX_CYCLE
        
        comp = Component(self.util, bb)
        comp.name = name + "bgr"
        comp.bgr = bgr
        self.add_component(comp)
        
        layout = BorderLayout(bb)
        layout.set_percent_constraints(0.0, 0.0, 20.0, 20.0)
        
        self.slider = Slider(util, name + "slider", bgr, slider_color, img_knob, img_knob_on, None, key_incr, key_decr, key_knob, layout.CENTER)
        self.slider.add_slide_listener(self.slider_action_handler)
        self.add_component(self.slider)
        
        self.current_time_layer = 3
        self.total_time_layer = 2
        self.current_time_name = name + "current"
        self.total_time_name = name + "total"
        self.current_time_layout = layout.LEFT
        self.total_time_layout = layout.RIGHT
        
        self.total_track_time = 0
        
        self.seek_listeners = []
        self.timer_started = False
        self.seek_time = 0
        
    def set_track_time(self, name, time, bb, layer_num):
        """ Set track time
        
        :param name: button state
        :param time: track time
        :param bb: bounding box
        :param layer_num: layer number
        """
        font_size = int((bb.h * 45)/100.0)
        font = self.util.get_font(font_size)
        size = font.size(time)
        label = font.render(time, 1, self.config[COLORS][COLOR_BRIGHT])
        c = Component(self.util, label)
        c.bgr = (255, 0, 0)
        c.name = name
        c.text = time
        c.text_size = font_size
        c.text_color_current = self.config[COLORS][COLOR_BRIGHT]
        c.content_x = bb.x + (bb.width - size[0])/2
        c.content_y = bb.y + (bb.height - size[1])/2
                
        if len(self.components) <= layer_num:
            self.components.append(c)
        else:
            self.components[layer_num] = c
        
        if self.visible:    
            self.draw()
            self.update()
            
    def set_track_info(self, track_info):
        """ Set track time info
        
        :param track_info: track info
        """
        
        if not isinstance(track_info, dict):
            return

        seek_time = "0"

        try:
            seek_time = track_info["seek_time"]            
        except:
            pass
        
        try:
            track_time = track_info["Time"]
            self.total_track_time = int(float(track_time))
            track_time = self.convert_seconds_to_label(track_time)
            self.set_track_time(self.total_time_name, track_time, self.total_time_layout, self.total_time_layer)            
        except:
            pass
        
        try:
            if track_info["state"] != "pause":                
                self.start_thread(seek_time)
        except:
            pass
    
    def start_thread(self, seek_time):
        """ Start knob animation thread
        
        :param seek_time: track time
        """
        self.stop_thread()
        with self.lock:
            t = Thread(target=self.start_loop, args=[seek_time])
            t.start()
    
    def stop_thread(self):
        """ Stop knob animation thread """
        
        with self.lock:
            if self.timer_started:
                self.timer_started = False
                time.sleep(0.3)
    
    def start_loop(self, seek_time):
        """ Animation loop
        
        :param seek_time: track time
        """
        count = 0
        self.seek_time = int(float(seek_time))
        self.timer_started = True
        while self.timer_started:
            if count == 0:
                seek_time_label = self.convert_seconds_to_label(self.seek_time)
                self.set_track_time(self.current_time_name, seek_time_label, self.current_time_layout, self.current_time_layer)
                step = self.total_track_time / 100
                if step > 0:
                    p = int(float(self.seek_time) / step)
                    if p > self.slider.get_position() or p == 0:
                        self.slider.set_position(p)
                        self.slider.update_position()
                    self.seek_time += 1
                    if self.seek_time > self.total_track_time:
                        self.timer_started = False
            
            if count == 10:
                count = 0
            else:
                count += 2
              
            time.sleep(self.CYCLE)
            
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
        
        if not self.config[CURRENT][CURRENT_FILE]:
            return
        
        step = self.total_track_time / 100
        p = step * evt
        seek_time = self.convert_seconds_to_label(p)
        self.set_track_time(self.current_time_name, seek_time, self.current_time_layout, self.current_time_layer)
        self.notify_seek_listeners(str(p))
    
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
            
    def pause(self):
        """ Stop animation thread """
        self.stop_thread()
                
    def resume(self): 
        """ Resumed in set_track_info """
        pass
            
    