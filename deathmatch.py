#!/usr/bin/env python
#
# Python-powered Deathmatch
#
# 2000-12-21  Barry Pederson
#

import sys
from qwpython.pakfile import PakLoader
from qwpython.qwsv import engine

#
# Let the engine know what the command-line args were
#
engine.argv = sys.argv


#
# Setup the QuakeWorld Server engine with a place to send output
# and an object that will load resources such as maps
#
engine.stdout = sys.stdout
engine.loader = PakLoader()
engine.loader.add_directory('../quake/id1')

#
# import the package which holds the game, which
# should start things running
#    
import py_dm

