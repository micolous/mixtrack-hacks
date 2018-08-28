#!/usr/bin/env python3
"""
etch-a-sketch.py - Emulates an Etch-A-Sketch(R) with the Numark Mixtrack DJ controller
Copyright 2011, 2018 Michael Farrell <http://micolous.id.au/>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from sys import exit
from colorsys import hsv_to_rgb
from threading import Lock

try:
    import mido
except ImportError:
    print("Please install mido and python-rtmidi:")
    print("  pip3 install mido python-rtmidi")
    exit(1)

try:
	import pygame
except ImportError:
	print("Please install pygame from http://www.pygame.org/")
	exit(1)

fullscreen = False

class EtchController:
    def __init__(self, turtle):
        self.turtle = turtle
        self.midi_in = mido.open_input('Numark Mix Track', callback=self.midi_callback)
        self.midi_out = mido.open_output('Numark Mix Track')
        self.rgb = True
        self.size = 1
        self._update_rgb_indicator()
    
    def midi_callback(self, msg):
        #print('got message:', msg)
        if msg.type == 'note_on':
            # Button press / release event
            if msg.velocity == 127:
                # Press
                if msg.note == 101: # Left Cue (RGB mode)
                    self.rgb = True
                    self._update_rgb_indicator()
                elif msg.note == 102: # Right Cue (HSV mode)
                    self.rgb = False
                    self._update_rgb_indicator()
                elif msg.note == 105: # Back (clear screen)
                    self.turtle.clear()
                else:
                    print(msg)
            elif msg.velocity == 0:
                # Release
                pass
        
        elif msg.type == 'control_change':
            # Slider / turntable event
            if msg.control == 25: # left turntable
                if msg.value < 64:
                    self.turtle.move(x=+msg.value)
                else:
                    self.turtle.move(x=-(128-msg.value))

            elif msg.control == 24: # right turntable
                if msg.value < 64:
                    self.turtle.move(y=+msg.value)
                else:
                    self.turtle.move(y=-(128-msg.value))
            
            elif msg.control == 8: # a gain (RED / HUE)
                if self.rgb:
                    self.turtle.colour(red=msg.value*2)
                else: # hsv
                    self.turtle.colour(hue=msg.value/127.)
            elif msg.control == 23: # master gain (GREEN / SATURATION)
                if self.rgb:
                    self.turtle.colour(green=msg.value*2)
                else: # hsv
                    self.turtle.colour(saturation=msg.value/127.)
            elif msg.control == 9: # b gain (BLUE / VALUE)
                if self.rgb:
                    self.turtle.colour(blue=msg.value*2)
                else: # hsv
                    self.turtle.colour(value=msg.value/127.)
            
            elif msg.control == 10: # Crossfade (SIZE)
                self.turtle.size(msg.value)

    def _update_rgb_indicator(self):
        if self.rgb:
            self._send_light(101, True)
            self._send_light(102, False)
        else:
            self._send_light(101, False)
            self._send_light(102, True)
        self.turtle.colour_mode(self.rgb)
        print("Colour mode: " + ("rgb" if self.rgb else "hsv"))

    def _send_light(self, light_id, on=True):
        msg = mido.Message('note_on', note=light_id, velocity=100 if on else 0)
        self.midi_out.send(msg)

    def close(self):
        self.midi_out.close()
        self.midi_in.close()
        self.midi_in = self.midi_out = None

class Turtle:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = self.width // 2
        self.y = self.height // 2
        # Pen colour
        self.r = self.g = self.b = self.h = self.s = self.v = 0
        self.pen_size = 1
        self.rgb = True
        self.pen_colour = None
        self.update_rect = None
        self._update_colour()

        pygame.display.init()
        self.screen = pygame.display.set_mode((self.width, self.height), True)
        self.screen_size = pygame.Rect(0, 0, self.width, self.height)
        pygame.display.set_caption('etch-a-sketch')
        self.canvas = pygame.Surface((self.width, self.height))
        self.canvas.fill((255, 255, 255))
        self.update_rect = self.screen_size
        #self.canvas_lock = Lock()

        pygame.display.flip()

    def move(self, x=0, y=0):
        # Move the turtle by x, y
        self.x += x
        self.y += y
        self._clamp_position()
        self.draw()
        
    def _clamp_position(self):
        if self.x < -self.pen_size:
            self.x = -self.pen_size
        if self.y < -self.pen_size:
            self.y = -self.pen_size
        if self.x >= self.width + self.pen_size:
            self.x = self.width + self.pen_size
        if self.y >= self.height + self.pen_size:
            self.y = self.height + self.pen_size

    def colour(self, **kwargs):
        if 'red' in kwargs:
            self.r = kwargs['red']
        if 'green' in kwargs:
            self.g = kwargs['green']
        if 'blue' in kwargs:
            self.b = kwargs['blue']
        if 'hue' in kwargs:
            self.h = kwargs['hue']
        if 'saturation' in kwargs:
            self.s = kwargs['saturation']
        if 'value' in kwargs:
            self.v = kwargs['value']
        self._update_colour()
        self.draw()
    
    def colour_mode(self, rgb):
        self.rgb = rgb
        self.draw()

    def size(self, size):
        self.pen_size = size
        self.draw()

    def clear(self):
        # clear with fill colour
        self.canvas.fill(self.pen_colour)
        self.update_rect = self.screen_size

    def _update_colour(self):
        if self.rgb:
            self.pen_colour = pygame.Color(self.r, self.g, self.b)
        else:
            self.pen_colour = pygame.Color(*[int(i*255) for i in hsv_to_rgb(
                                           self.h, self.s, self.v)])

    def draw(self):
        #self.canvas_lock.acquire()
        try:
            pygame.draw.circle(self.canvas,
                               self.pen_colour,
                               (self.x, self.y),
                               self.pen_size)
            area_rect = pygame.Rect(
                self.x - self.pen_size,
                self.y - self.pen_size,
                self.pen_size * 2,
                self.pen_size * 2)
            area_rect.clip(self.screen_size)
            
            if self.update_rect is None:
                self.update_rect = area_rect
            else:
                self.update_rect.union_ip(area_rect)
        finally: pass
            #self.canvas_lock.release()
    
    def pump(self):
        running = True
        if self.update_rect:
            r, self.update_rect = self.update_rect, None
            p = self.canvas.subsurface(r)
            self.screen.blit(p, r)

            pygame.display.update(r)

        pygame.event.pump()

        if pygame.event.peek():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    running = False 

        return running


# Screen resolution
turtle = Turtle(1680, 1050)
controller = EtchController(turtle)
running = True

while running:
    running = turtle.pump()
