#!/usr/bin/env python

import sys
from qwpython.pakfile import PakLoader
from qwpython.qwsv import engine

#
# Let the engine know what the command-line args were
#
engine.argv = sys.argv + ['+gamedir', 'ctf']


#
# Setup the QuakeWorld Server engine with a place to send output
# and an object that will load resources such as maps
#
engine.stdout = sys.stdout
engine.loader = PakLoader()
engine.loader.add_directory('ctf')
engine.loader.add_directory('id1')

#
# Import the game package to get things going.
#    
import py_ctf

