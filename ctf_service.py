#!/usr/bin/env python
"""
 Run a game of Pythonized Threewave CTF as an NT/Win2k service,
 assuming you have the Python win32all extensions loaded.

 Install with:  python ctf_service.py install
 Remove with :  python ctf_service.py remove
 
 Once that's done, you can manage it through the service control panel,
 or stop/start from the command line with something like:
 
   net start ctfpython
   net stop  ctfpython
 
 2001-04-15 Barry Pederson <bpederson@geocities.com>
"""
import os.path, sys
import win32serviceutil
from qwpython.pakfile import PakLoader
from qwpython.qwsv import engine

# Fix the current working directory -- this gets initialized incorrectly
# for some reason when run as an NT service.
# (lifted this from WebWare)
import os
try:
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
except:
    pass


class CTFService(win32serviceutil.ServiceFramework):
    _svc_name_ = "CTFPython"
    _svc_display_name_ = "Capture the Flag - QWPython"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)

        #
        # Let the engine know what the command-line args were
        #
        engine.argv = sys.argv + ['+gamedir', 'ctf']

        #
        # Setup the QuakeWorld Server engine with a place to send output
        # and an object that will load resources such as maps
        #
        engine.stdout = open('ctf_service.log', 'w')
        engine.loader = PakLoader()
        engine.loader.add_directory('../quake/id1')
        engine.loader.add_directory('../quake/ctf')  # Last added is first searched


    def SvcStop(self):
        #
        #self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        # (reporting the status hangs for some reason, commented out for now)
        try:
            engine.stop()
        except:
            import traceback
            traceback.print_exc(file=engine.stdout)
            engine.stdout.flush()

        
    def SvcDoRun(self):
        try:
            import py_ctf
        except:
            pass


if __name__=='__main__':
    win32serviceutil.HandleCommandLine(CTFService)
