#!/usr/bin/env python
"""
etch-a-sketch.py - Emulates an Etch-A-Sketch(R) with the Numark Mixtrack DJ controller
Copyright 2011 Michael Farrell <http://micolous.id.au/>

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

from sys import exit
from colorsys import hsv_to_rgb

try:
	import pypm
except ImportError:
	print "Please install pyPortMidi >0.0.7 from https://bitbucket.org/aalex/pyportmidi/downloads"
	exit(1)

try:
	import pygame
except ImportError:
	print "Please install pygame from http://www.pygame.org/"
	exit(1)

# cursor position, colour
x = y = r = g = b = h = s = v = 0
rgb = True
# brush size
size = 1

SCREEN_SIZE = (1024, 600)
fullscreen = False

# open midi controller
pypm.Initialize()

# find the dj hero controller
in_controller_id = out_controller_id = None
for x in range(pypm.CountDevices()):
	interf,name,inp,outp,opened = pypm.GetDeviceInfo(x)
	if 'Numark Mix Track MIDI' in name:
		if inp:
			in_controller_id = x
		if outp:
			out_controller_id = x
		if in_controller_id != None and out_controller_id != None:
			break
			
if in_controller_id == None or out_controller_id == None:
	print "Couldn't find the Numark Mixtrack controller.  Is it plugged in?"
	exit(1)

# we have the controller id, lets open it
midi_in = pypm.Input(in_controller_id)
midi_out = pypm.Output(out_controller_id)
if rgb:
	midi_out.Write([[[0x90, 101, 100], pypm.Time()]])
	midi_out.Write([[[0x90, 102, 0], pypm.Time()]])	
else:
	midi_out.Write([[[0x90, 102, 100], pypm.Time()]])
	midi_out.Write([[[0x90, 101, 0], pypm.Time()]])

# init display
pygame.display.init()
fullscreen = (fullscreen and pygame.FULLSCREEN)
screen = pygame.display.set_mode(SCREEN_SIZE, fullscreen)
screen.fill((255,255,255))
pygame.display.flip()

running = True

while running:
	# handle midi input	
	if midi_in.Poll():
		data = midi_in.Read(1)
		if data[0][0][0] == 144 and data[0][0][2] == 127:
			# this is a button press event
			if data[0][0][1] == 101: # left cue (RGB mode)
				rgb = True
			elif data[0][0][1] == 102: # right cue (HSV mode)
				rgb = False

			# set LEDs			
			if rgb:
				midi_out.Write([[[0x90, 101, 100], pypm.Time()]])
				midi_out.Write([[[0x90, 102, 0], pypm.Time()]])	
			else:
				midi_out.Write([[[0x90, 102, 100], pypm.Time()]])
				midi_out.Write([[[0x90, 101, 0], pypm.Time()]])
		elif data[0][0][0] == 176:
			# this is a turntable event.
			if data[0][0][1] == 25: # left wheel (X)
				if data[0][0][2] < 64:
					x += data[0][0][2]
				elif data[0][0][2] >= 64:
					x -= 128 - data[0][0][2]
			elif data[0][0][1] == 24: # right wheel (Y)
				if data[0][0][2] < 64:
					y += data[0][0][2]
				elif data[0][0][2] >= 64:
					y -= 128 - data[0][0][2]
			elif data[0][0][1] == 8: # a gain (RED)
				if rgb:
					r = data[0][0][2] * 2
				else:
					h = data[0][0][2] / 127.
			elif data[0][0][1] == 23: # master gain (GREEN)
				if rgb:
					g = data[0][0][2] * 2
				else:
					s = data[0][0][2] / 127.
			elif data[0][0][1] == 9: # b gain (BLUE)
				if rgb:
					b = data[0][0][2] * 2
				else:
					v = data[0][0][2] / 127.
			elif data[0][0][1] == 10: # crossfade (size)
				size = data[0][0][2]
		
			# clamp x/y
			if x<-size: x=-size
			if y<-size: y=-size
			if x>SCREEN_SIZE[0]+size: x=SCREEN_SIZE[0]+size
			if y>SCREEN_SIZE[1]+size: y=SCREEN_SIZE[0]+size 
			
			print h, s, v
			# now blit the dot on the screen
			if rgb:
				colour = pygame.Color(r, g, b)
			else:
				# hsv colourspace
				colour = pygame.Color(*[int(i*255) for i in hsv_to_rgb(h, s, v)])
			pygame.draw.circle(screen, colour, (x, y), size)
			
			pygame.display.flip()
			pygame.event.pump()
			
	if pygame.event.peek():
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			if event.type == pygame.KEYDOWN:
				running = False

# clear leds
midi_out.Write([[[0x90, 102, 0], pypm.Time()]])
midi_out.Write([[[0x90, 101, 0], pypm.Time()]])

