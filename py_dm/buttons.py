###
### Generated by QuakeC -> Python translator
### Id: qc2python.py,v 1.4 2001/02/05 16:26:04 barryp Exp 
###
from qwpython.qwsv import engine, Vector
from qwpython.qcsupport import qc

import defs
import subs
import math

#  button and multiple button

def button_wait(*qwp_extra):
    qc.self.state = defs.STATE_TOP
    qc.self.nextthink = qc.self.ltime + qc.self.wait
    qc.self.think = button_return
    defs.activator = qc.self.enemy
    subs.SUB_UseTargets()
    qc.self.frame = 1 #  use alternate textures
    

def button_done(*qwp_extra):
    qc.self.state = defs.STATE_BOTTOM
    

def button_return(*qwp_extra):
    qc.self.state = defs.STATE_DOWN
    subs.SUB_CalcMove(qc.self.pos1, qc.self.speed, button_done)
    qc.self.frame = 0 #  use normal textures
    if qc.self.health:
        qc.self.takedamage = defs.DAMAGE_YES #  can be shot again
    

def button_blocked(*qwp_extra):
    pass

def button_fire(*qwp_extra):
    if qc.self.state == defs.STATE_UP or qc.self.state == defs.STATE_TOP:
        return 
    qc.self.sound(defs.CHAN_VOICE, qc.self.noise, 1, defs.ATTN_NORM)
    qc.self.state = defs.STATE_UP
    subs.SUB_CalcMove(qc.self.pos2, qc.self.speed, button_wait)
    

def button_use(*qwp_extra):
    qc.self.enemy = defs.activator
    button_fire()
    

def button_touch(*qwp_extra):
    if qc.other.classname != 'player':
        return 
    qc.self.enemy = qc.other
    button_fire()
    

def button_killed(*qwp_extra):
    qc.self.enemy = defs.damage_attacker
    qc.self.health = qc.self.max_health
    qc.self.takedamage = defs.DAMAGE_NO #  wil be reset upon return
    button_fire()
    
# QUAKED func_button (0 .5 .8) ?
# When a button is touched, it moves some distance in the direction of it's angle, triggers all of it's targets, waits some time, then returns to it's original position where it can be triggered again.
# 
# "angle"		determines the opening direction
# "target"	all entities with a matching targetname will be used
# "speed"		override the default 40 speed
# "wait"		override the default 1 second wait (-1 = never return)
# "lip"		override the default 4 pixel lip remaining at end of move
# "health"	if set, the button must be killed instead of touched
# "sounds"
# 0) steam metal
# 1) wooden clunk
# 2) metallic click
# 3) in-out
# 

def func_button(*qwp_extra):
    gtemp = 0
    ftemp = 0
    if qc.self.sounds == 0:
        engine.precache_sound('buttons/airbut1.wav')
        qc.self.noise = 'buttons/airbut1.wav'
        
    if qc.self.sounds == 1:
        engine.precache_sound('buttons/switch21.wav')
        qc.self.noise = 'buttons/switch21.wav'
        
    if qc.self.sounds == 2:
        engine.precache_sound('buttons/switch02.wav')
        qc.self.noise = 'buttons/switch02.wav'
        
    if qc.self.sounds == 3:
        engine.precache_sound('buttons/switch04.wav')
        qc.self.noise = 'buttons/switch04.wav'
        
    subs.SetMovedir()
    qc.self.movetype = defs.MOVETYPE_PUSH
    qc.self.solid = defs.SOLID_BSP
    qc.self.setmodel(qc.self.model)
    qc.self.blocked = button_blocked
    qc.self.use = button_use
    if qc.self.health:
        qc.self.max_health = qc.self.health
        qc.self.th_die = button_killed
        qc.self.takedamage = defs.DAMAGE_YES
        
    else:
        qc.self.touch = button_touch
    if not qc.self.speed:
        qc.self.speed = 40
    if not qc.self.wait:
        qc.self.wait = 1
    if not qc.self.lip:
        qc.self.lip = 4
    qc.self.state = defs.STATE_BOTTOM
    qc.self.pos1 = qc.self.origin
    qc.self.pos2 = qc.self.pos1 + qc.self.movedir * (math.fabs(qc.self.movedir * qc.self.size) - qc.self.lip)
    
