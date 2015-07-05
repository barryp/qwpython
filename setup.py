#!/usr/bin/env python
#
# Python Distutils Setup file, should work on both Win32 and Unix platforms
#    (running under Win32 requires you have VisualC++ installed)
#
# This script compiles the QWPython extension module and installs it 
# in the appropriate place in your Python installation.  Run it from the
# command line with:
#
#    python setup.py install
#
# 2000-12-21 Barry Pederson <bpederson@geocities.com>  
#

import sys
from distutils.core import setup, Extension

cfiles = [
    'qwpython-src/qwsv/cmd.c',
    'qwpython-src/qwsv/common.c',
    'qwpython-src/qwsv/crc.c',
    'qwpython-src/qwsv/cvar.c',
    'qwpython-src/qwsv/mathlib.c',
    'qwpython-src/qwsv/md4.c',
    'qwpython-src/qwsv/model.c',
    'qwpython-src/qwsv/net_chan.c',
    'qwpython-src/qwsv/pmove.c',
    'qwpython-src/qwsv/pmovetst.c',
    'qwpython-src/qwsv/pr_edict.c',
    'qwpython-src/qwsv/qwp_entity.c',
    'qwpython-src/qwsv/qwp_vector.c',
    'qwpython-src/qwsv/sv_ccmds.c',
    'qwpython-src/qwsv/sv_ents.c',
    'qwpython-src/qwsv/sv_init.c',
    'qwpython-src/qwsv/sv_main.c',
    'qwpython-src/qwsv/sv_move.c',
    'qwpython-src/qwsv/sv_nchan.c',
    'qwpython-src/qwsv/sv_phys.c',
    'qwpython-src/qwsv/sv_send.c',
    'qwpython-src/qwsv/sv_user.c',
    'qwpython-src/qwsv/sys_python.c',
    'qwpython-src/qwsv/world.c',
    'qwpython-src/qwsv/zone.c']    

#
# Slightly different network code and libraries 
# for the different platforms
#
if sys.platform == 'win32':
    cfiles.append('qwpython-src/qwsv/net_wins.c')
    libs= ['wsock32', 'winmm']
else:
    cfiles.append('qwpython-src/qwsv/net_udp.c')
    libs = None   
    
#
# Have distutils do the actual work
#    
setup(name = "qwpython", 
      version = "1.0",
      author = "Barry Pederson",
      author_email = "bpederson@geocities.com",
      url = "http://qwpython.sourceforge.net",
      description = "Python-powered QuakeWorld dedicated server",
      license = "GPL",
      package_dir = {'': 'qwpython-src'},
      packages = ['qwpython'],
      ext_modules = 
        [
        Extension("qwpython.qwsv", cfiles, define_macros=[('SERVERONLY', '1')], libraries=libs)
        ]
     )
    
##### That's all folks ###########    