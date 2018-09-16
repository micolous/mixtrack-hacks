#!/usr/bin/env python3
# -*- mode: python; indent-tabs-mode: nil; tab-width: 4 -*-
"""
party_hard.py - Party Hard mode.
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
from random import randint

try:
    import mido
except ImportError:
    print("Please install mido and python-rtmidi:")
    print("  pip3 install mido python-rtmidi")
    exit(1)

state = [False] * 128
devices = mido.get_ioport_names()
numark_devname = None
print('MIDI devices:')
for device in devices:
    print('* ' + device)
    if device.startswith('Numark Mix Track'):
      print('  Mix Track found!')
      numark_devname = device

if numark_devname is None:
    print("Couldn't find a Mix Track, exiting.")
    exit(1)

with mido.open_output(device) as midi_out:
    print("Press ^C to end the party...")

    try:
        while True:
            x = randint(0, 127)
            state[x] = not state[x]
            msg = mido.Message('note_on',
                               note=x,
                               velocity=100 if state[x] else 0)
            midi_out.send(msg)
    except KeyboardInterrupt:
        pass

    for x in range(128):
        msg = mido.Message('note_off',
                           note=x,
                           velocity=0)
        midi_out.send(msg)

print("It's all fun and games until the cops show up.")

