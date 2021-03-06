#! /usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Wang Yong
# 
# Author:     Wang Yong <lazycat.manatee@gmail.com>
# Maintainer: Wang Yong <lazycat.manatee@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PyQt5.QtCore import QObject, pyqtSignal
from Xlib import X
from threading import Timer
from xutils import record_event, get_keyname, check_valid_event, get_event_data, delete_selection
import commands
from config import setting_config

press_ctrl = False
press_shift = False

class RecordEvent(QObject):
    
    press_ctrl = pyqtSignal()    
    release_ctrl = pyqtSignal()    
    
    press_esc = pyqtSignal()

    left_button_press = pyqtSignal(int, int, int)
    right_button_press = pyqtSignal(int, int, int)    
    wheel_press = pyqtSignal()
    
    cursor_stop = pyqtSignal()
    
    translate_selection = pyqtSignal(int, int, str)
    
    def __init__(self, view):
        QObject.__init__(self)

        self.stop_timer = None
        self.stop_delay = 0.05
        
        self.press_ctrl_timer = None
        self.press_ctrl_delay = 0.3
        
        self.view = view
        
        # Delete selection first.
        delete_selection()
        
    def record_callback(self, reply):
        global press_ctrl
        global press_shift
        
        check_valid_event(reply)
     
        data = reply.data
        while len(data):
            event, data = get_event_data(data)
            
            if event.type == X.KeyPress:
                keyname = get_keyname(event)
                
                if keyname not in ["Control_L", "Control_R"]:
                    self.try_stop_timer(self.press_ctrl_timer)
        
                if keyname in ["Control_L", "Control_R"]:
                    press_ctrl = True
                    
                    if not setting_config.get_trayicon_config("pause"):
                        if not self.view.isVisible() or not self.view.in_translate_area():
                            self.press_ctrl_timer = Timer(self.press_ctrl_delay, self.emit_press_ctrl)
                            self.press_ctrl_timer.start()
                elif keyname in ["Shift_L", "Shift_R"]:
                    press_shift = True
                elif keyname in ["Escape"]:
                    self.press_esc.emit()
            elif event.type == X.KeyRelease:
                keyname = get_keyname(event)
                if keyname in ["Control_L", "Control_R"]:
                    press_ctrl = False
                    self.release_ctrl.emit()
                elif keyname in ["Shift_L", "Shift_R"]:
                    press_shift = False
            elif event.type == X.ButtonPress:
                if event.detail == 1:
                    self.left_button_press.emit(event.root_x, event.root_y, event.time)
                elif event.detail == 3:
                    self.right_button_press.emit(event.root_x, event.root_y, event.time)
                elif event.detail == 5:
                    self.wheel_press.emit()
            elif event.type == X.ButtonRelease:
                if not self.view.isVisible() or not self.view.in_translate_area():
                    if not setting_config.get_trayicon_config("pause"):
                        if not setting_config.get_trayicon_config("key_trigger_select") or press_shift:
                            selection_content = commands.getoutput("xsel -p -o")
                            delete_selection()
                            
                            if len(selection_content) > 1 and not selection_content.isspace():
                                self.translate_selection.emit(event.root_x, event.root_y, selection_content)
                # Delete clipboard selection if user selection in visible area to avoid next time to translate those selection content.
                elif self.view.isVisible() and self.view.in_translate_area():
                    delete_selection()
            elif event.type == X.MotionNotify:
                self.try_stop_timer(self.stop_timer)
            
                if not setting_config.get_trayicon_config("pause"):
                    self.stop_timer = Timer(self.stop_delay, lambda : self.emit_cursor_stop(event.root_x, event.root_y))
                    self.stop_timer.start()
                    
    def try_stop_timer(self, timer):
        if timer and timer.is_alive():
            timer.cancel()
                
    def emit_press_ctrl(self):
        self.press_ctrl.emit()
        
    def emit_cursor_stop(self, mouse_x, mouse_y):
        if (not setting_config.get_trayicon_config("key_trigger_ocr") or press_ctrl) and (not self.view.isVisible() or not self.view.in_translate_area()):
            self.cursor_stop.emit()
                
    def filter_event(self):
        record_event(self.record_callback)
