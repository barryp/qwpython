###
### Generated by QuakeC -> Python translator
### Id: qc2python.py,v 1.5 2001/02/05 21:15:44 barryp Exp 
###
### 2001-02-17 Cleaned up translation (barryp)
###
from qwpython.qwsv import engine, Vector
from qwpython.qcsupport import qc

import defs
import status

#  Identify the player you are pointed towards
#  By Suck (Nat Friedman)
#  This code falls under the GNU public license, and cannot be 
#  redistributed without my name attached.
#  hacked by Zoid for CTF4
#  This is called with the player who wants to know whose in front
#  of him as "self."  I call it with an impulse in weapons.qc 
#
def identify_player(disp, *qwp_extra):
    #  e is a temp entity; guy is our current best guess
    #  as to at whom the player is pointing
    guy = None
    #  The best "closeness" heuristic so far.
    closeness = -1
    
    #  Walk the list of players...
    e = qc.find(qc.world, 'classname', 'player')
    while e != qc.world:
        #  Get a vector pointing from the viewer to the current
        #  player under consideration
        diff = e.origin - qc.self.origin
        
        #  Normalize it since we only care where he's pointing,
        #  not how far away the guy is.
        diff = diff.normalize()
        
        #  Normalize self.angles so we can do a length-independent
        #  consideration
        point = qc.self.angles.normalize()
        
        #  Find the different between the current player's angle
        #  and the viewer's vision angle
        diff -= point
        
        #  The length is going to be our definition of closeness
        currclose = diff.length()
        
        qc.traceline(qc.self.origin, e.origin, defs.FALSE, qc.self)
        if qc.trace_ent == e:
            if (closeness == -1) or (currclose < closeness):
                closeness = currclose
                guy = e                           
        e = qc.find(e, 'classname', 'player')
        
    #  Now we display.
    if disp == 0:
        return guy
    if not guy:
        status.TeamPlayerUpdate(qc.self, "You're not looking at anyone!")
        return qc.world
        
    status.TeamPlayerUpdate2(qc.self, 'You are looking at ', guy.netname)
    return guy
    