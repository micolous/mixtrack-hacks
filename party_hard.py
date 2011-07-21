#!/usr/bin/env python
"""
party_hard.py - Party Hard mode.
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
from random import randint

try:
	import pypm
except ImportError:
	print "Please install pyPortMidi >0.0.7 from https://bitbucket.org/aalex/pyportmidi/downloads"
	exit(1)


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

state = [False] * 128

print "Press ^C to end the party..."

try:
	while True:
		x = randint(0, 127)
		state[x] = not state[x]		
		midi_out.Write([[[0x90, x, (state[x] and 100) or 0], pypm.Time()]])
except KeyboardInterrupt:
	pass

for x in range(128):
	midi_out.Write([[[0x90, x, 0], pypm.Time()]])

print "It's all fun and games until the cops show up."

