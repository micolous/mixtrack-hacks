#!/usr/bin/env python3
"""
party_hard.py - Party Hard mode.
Copyright 2011, 2018 Michael Farrell <http://micolous.id.au/>

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
    import mido
except ImportError:
    print("Please install mido and python-rtmidi:")
    print("  pip3 install mido python-rtmidi")
    exit(1)

state = [False] * 128

with mido.open_output('Numark Mix Track') as midi_out:
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

