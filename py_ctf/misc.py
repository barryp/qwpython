###
### Generated by QuakeC -> Python translator
### Id: qc2python.py,v 1.5 2001/02/05 21:15:44 barryp Exp 
###
### 2001-02-17 Cleaned up translation (barryp)
###
from qwpython.qwsv import engine, Vector
from qwpython.qcsupport import qc

import defs
import random
import subs
import combat
import weapons

# QUAKED info_null (0 0.5 0) (-4 -4 -4) (4 4 4)
# Used as a positional target for spotlights, etc.
# 
def info_null(*qwp_extra):
    qc.self.remove()
  
    
# QUAKED info_notnull (0 0.5 0) (-4 -4 -4) (4 4 4)
# Used as a positional target for lightning.
# 
def info_notnull(*qwp_extra):
    pass
    
    
# ============================================================================
START_OFF = 1

def light_use(*qwp_extra):
    if qc.self.spawnflags & START_OFF:
        engine.lightstyle(qc.self.style, 'm')
        qc.self.spawnflags -= START_OFF        
    else:
        engine.lightstyle(qc.self.style, 'a')
        qc.self.spawnflags += START_OFF
        
    
# QUAKED light (0 1 0) (-8 -8 -8) (8 8 8) START_OFF
# Non-displayed light.
# Default light value is 300
# Default style is 0
# If targeted, it will toggle between on or off.
# 
def light(*qwp_extra):
    if not qc.self.targetname:
        #  inert light
        qc.self.remove()
        return         
    if qc.self.style >= 32:
        qc.self.use = light_use
        if qc.self.spawnflags & START_OFF:
            engine.lightstyle(qc.self.style, 'a')
        else:
            engine.lightstyle(qc.self.style, 'm')
        
    
# QUAKED light_fluoro (0 1 0) (-8 -8 -8) (8 8 8) START_OFF
# Non-displayed light.
# Default light value is 300
# Default style is 0
# If targeted, it will toggle between on or off.
# Makes steady fluorescent humming sound
# 
def light_fluoro(*qwp_extra):
    if qc.self.style >= 32:
        qc.self.use = light_use
        if qc.self.spawnflags & START_OFF:
            engine.lightstyle(qc.self.style, 'a')
        else:
            engine.lightstyle(qc.self.style, 'm')
        
    engine.precache_sound('ambience/fl_hum1.wav')
    engine.ambientsound(qc.self.origin, 'ambience/fl_hum1.wav', 0.5, defs.ATTN_STATIC)

    
# QUAKED light_fluorospark (0 1 0) (-8 -8 -8) (8 8 8)
# Non-displayed light.
# Default light value is 300
# Default style is 10
# Makes sparking, broken fluorescent sound
# 
def light_fluorospark(*qwp_extra):
    if not qc.self.style:
        qc.self.style = 10
    engine.precache_sound('ambience/buzz1.wav')
    engine.ambientsound(qc.self.origin, 'ambience/buzz1.wav', 0.5, defs.ATTN_STATIC)

    
# QUAKED light_globe (0 1 0) (-8 -8 -8) (8 8 8)
# Sphere globe light.
# Default light value is 300
# Default style is 0
# 
def light_globe(*qwp_extra):
    engine.precache_model('progs/s_light.spr')
    qc.self.setmodel('progs/s_light.spr')
    qc.self.makestatic()
    

def FireAmbient(*qwp_extra):
    engine.precache_sound('ambience/fire1.wav')
    #  attenuate fast
    engine.ambientsound(qc.self.origin, 'ambience/fire1.wav', 0.5, defs.ATTN_STATIC)

    
# QUAKED light_torch_small_walltorch (0 .5 0) (-10 -10 -20) (10 10 20)
# Short wall torch
# Default light value is 200
# Default style is 0
# 
def light_torch_small_walltorch(*qwp_extra):
    engine.precache_model('progs/flame.mdl')
    qc.self.setmodel('progs/flame.mdl')
    FireAmbient()
    qc.self.makestatic()

    
# QUAKED light_flame_large_yellow (0 1 0) (-10 -10 -12) (12 12 18)
# Large yellow flame ball
# 
def light_flame_large_yellow(*qwp_extra):
    engine.precache_model('progs/flame2.mdl')
    qc.self.setmodel('progs/flame2.mdl')
    qc.self.frame = 1
    FireAmbient()
    qc.self.makestatic()

    
# QUAKED light_flame_small_yellow (0 1 0) (-8 -8 -8) (8 8 8) START_OFF
# Small yellow flame ball
# 
def light_flame_small_yellow(*qwp_extra):
    engine.precache_model('progs/flame2.mdl')
    qc.self.setmodel('progs/flame2.mdl')
    FireAmbient()
    qc.self.makestatic()

    
# QUAKED light_flame_small_white (0 1 0) (-10 -10 -40) (10 10 40) START_OFF
# Small white flame ball
# 
def light_flame_small_white(*qwp_extra):
    engine.precache_model('progs/flame2.mdl')
    qc.self.setmodel('progs/flame2.mdl')
    FireAmbient()
    qc.self.makestatic()

    
# ============================================================================
# QUAKED misc_fireball (0 .5 .8) (-8 -8 -8) (8 8 8)
# Lava Balls
# 
def misc_fireball(*qwp_extra):
    engine.precache_model('progs/lavaball.mdl')
    qc.self.classname = 'fireball'
    qc.self.nextthink = qc.time + (random.random() * 5)
    qc.self.think = fire_fly
    if not qc.self.speed:
        qc.self.speed == 1000
    

def fire_fly(*qwp_extra):
    fireball = qc.spawn()
    fireball.solid = defs.SOLID_TRIGGER
    fireball.movetype = defs.MOVETYPE_TOSS
    fireball.velocity = Vector((random.random() * 100) - 50, (random.random() * 100) - 50, qc.self.speed + (random.random() * 200))
    fireball.classname = 'fireball'
    fireball.setmodel('progs/lavaball.mdl')
    qc.setsize(fireball, Vector(0, 0, 0), Vector(0, 0, 0))
    qc.setorigin(fireball, qc.self.origin)
    fireball.nextthink = qc.time + 5
    fireball.think = subs.SUB_Remove
    fireball.touch = fire_touch
    qc.self.nextthink = qc.time + (random.random() * 5) + 3
    qc.self.think = fire_fly
    

def fire_touch(*qwp_extra):
    combat.T_Damage(qc.other, qc.self, qc.self, 20)
    qc.self.remove()

    
# ============================================================================

def barrel_explode(*qwp_extra):
    qc.self.takedamage = defs.DAMAGE_NO
    qc.self.classname = 'explo_box'
    #  did say self.owner
    combat.T_RadiusDamage(qc.self, qc.self, 160, qc.world)
    qc.WriteByte(defs.MSG_BROADCAST, defs.SVC_TEMPENTITY)
    qc.WriteByte(defs.MSG_BROADCAST, defs.TE_EXPLOSION)
    qc.WriteCoord(defs.MSG_BROADCAST, qc.self.origin.x)
    qc.WriteCoord(defs.MSG_BROADCAST, qc.self.origin.y)
    qc.WriteCoord(defs.MSG_BROADCAST, qc.self.origin.z + 32)
    qc.self.remove()
    

# QUAKED misc_explobox (0 .5 .8) (0 0 0) (32 32 64)
# TESTING THING
# 
def misc_explobox(*qwp_extra):
    qc.self.solid = defs.SOLID_BBOX
    qc.self.movetype = defs.MOVETYPE_NONE
    engine.precache_model('maps/b_explob.bsp')
    qc.self.setmodel('maps/b_explob.bsp')
    qc.setsize(qc.self, Vector(0, 0, 0), Vector(32, 32, 64))
    engine.precache_sound('weapons/r_exp3.wav')
    qc.self.health = 20
    qc.self.th_die = barrel_explode
    qc.self.takedamage = defs.DAMAGE_AIM
    qc.self.origin %= Vector(None, None, qc.self.origin.z + 2)
    oldz = qc.self.origin.z
    qc.droptofloor()
    if oldz - qc.self.origin.z > 250:
        engine.dprint('item fell out of level at ')
        engine.dprint(str(qc.self.origin))
        engine.dprint('\012')
        qc.self.remove()
        
    
# QUAKED misc_explobox2 (0 .5 .8) (0 0 0) (32 32 64)
# Smaller exploding box, REGISTERED ONLY
# 
def misc_explobox2(*qwp_extra):
    qc.self.solid = defs.SOLID_BBOX
    qc.self.movetype = defs.MOVETYPE_NONE
    engine.precache_model('maps/b_exbox2.bsp')
    qc.self.setmodel('maps/b_exbox2.bsp')
    qc.setsize(qc.self, Vector(0, 0, 0), Vector(32, 32, 32))
    engine.precache_sound('weapons/r_exp3.wav')
    qc.self.health = 20
    qc.self.th_die = barrel_explode
    qc.self.takedamage = defs.DAMAGE_AIM
    qc.self.origin %= Vector(None, None, qc.self.origin.z + 2)
    oldz = qc.self.origin.z
    qc.droptofloor()
    if oldz - qc.self.origin.z > 250:
        engine.dprint('item fell out of level at ')
        engine.dprint(str(qc.self.origin))
        engine.dprint('\012')
        qc.self.remove()
        
    
# ============================================================================
SPAWNFLAG_SUPERSPIKE = 1
SPAWNFLAG_LASER = 2

def Laser_Touch(*qwp_extra):
    if qc.other == qc.self.owner:
        return  #  don't explode on owner
    if engine.pointcontents(qc.self.origin) == defs.CONTENT_SKY:
        qc.self.remove()
        return 
        
    qc.self.sound(defs.CHAN_WEAPON, 'enforcer/enfstop.wav', 1, defs.ATTN_STATIC)
    org = qc.self.origin - 8 * qc.self.velocity.normalize()
    if qc.other.health:
        weapons.SpawnBlood(org, 15)
        combat.T_Damage(qc.other, qc.self, qc.self.owner, 15)        
    else:
        qc.WriteByte(defs.MSG_BROADCAST, defs.SVC_TEMPENTITY)
        qc.WriteByte(defs.MSG_BROADCAST, defs.TE_GUNSHOT)
        qc.WriteCoord(defs.MSG_BROADCAST, org.x)
        qc.WriteCoord(defs.MSG_BROADCAST, org.y)
        qc.WriteCoord(defs.MSG_BROADCAST, org.z)
        
    qc.self.remove()
    

def LaunchLaser(org, vec, *qwp_extra):
    if qc.self.classname == 'monster_enforcer':
        qc.self.sound(defs.CHAN_WEAPON, 'enforcer/enfire.wav', 1, defs.ATTN_NORM)
    vec = vec.normalize()
    qc.newmis = qc.spawn()
    qc.newmis.owner = qc.self
    qc.newmis.movetype = defs.MOVETYPE_FLY
    qc.newmis.solid = defs.SOLID_BBOX
    qc.newmis.effects = defs.EF_DIMLIGHT
    qc.newmis.classname = 'missile'
    qc.newmis.setmodel('progs/laser.mdl')
    qc.setsize(qc.newmis, Vector(0, 0, 0), Vector(0, 0, 0))
    qc.setorigin(qc.newmis, org)
    qc.newmis.velocity = vec * 600
    qc.newmis.angles = qc.vectoangles(qc.newmis.velocity)
    qc.newmis.nextthink = qc.time + 5
    qc.newmis.think = subs.SUB_Remove
    qc.newmis.touch = Laser_Touch
    

def spikeshooter_use(*qwp_extra):
    if qc.self.spawnflags & SPAWNFLAG_LASER:
        return 
        qc.self.sound(defs.CHAN_VOICE, 'enforcer/enfire.wav', 1, defs.ATTN_NORM)
        LaunchLaser(qc.self.origin, qc.self.movedir)        
    else:
        qc.self.sound(defs.CHAN_VOICE, 'weapons/spike2.wav', 1, defs.ATTN_NORM)
        weapons.launch_spike(qc.self.origin, qc.self.movedir)
        qc.newmis.velocity = qc.self.movedir * 500
        if qc.self.spawnflags & SPAWNFLAG_SUPERSPIKE:
            qc.newmis.touch = weapons.superspike_touch
            

def shooter_think(*qwp_extra):
    spikeshooter_use()
    qc.self.nextthink = qc.time + qc.self.wait
    qc.newmis.velocity = qc.self.movedir * 500

    
# QUAKED trap_spikeshooter (0 .5 .8) (-8 -8 -8) (8 8 8) superspike laser
# When triggered, fires a spike in the direction set in QuakeEd.
# Laser is only for REGISTERED.
# 
def trap_spikeshooter(*qwp_extra):
    subs.SetMovedir()
    qc.self.use = spikeshooter_use
    if qc.self.spawnflags & SPAWNFLAG_LASER:
        engine.precache_model('progs/laser.mdl')
        engine.precache_sound('enforcer/enfire.wav')
        engine.precache_sound('enforcer/enfstop.wav')        
    else:
        engine.precache_sound('weapons/spike2.wav')

    
# QUAKED trap_shooter (0 .5 .8) (-8 -8 -8) (8 8 8) superspike laser
# Continuously fires spikes.
# "wait" time between spike (1.0 default)
# "nextthink" delay before firing first spike, so multiple shooters can be stagered.
# 
def trap_shooter(*qwp_extra):
    trap_spikeshooter()
    if qc.self.wait == 0:
        qc.self.wait = 1
    qc.self.nextthink += qc.self.wait + qc.self.ltime
    qc.self.think = shooter_think

    
# 
# QUAKED air_bubbles (0 .5 .8) (-8 -8 -8) (8 8 8)
# 
# testing air bubbles
# 
def air_bubbles(*qwp_extra):
    qc.self.remove()
    

def make_bubbles(*qwp_extra):
    bubble = qc.spawn()
    bubble.setmodel('progs/s_bubble.spr')
    qc.setorigin(bubble, qc.self.origin)
    bubble.movetype = defs.MOVETYPE_NOCLIP
    bubble.solid = defs.SOLID_NOT
    bubble.velocity = Vector(0, 0, 15)
    bubble.nextthink = qc.time + 0.5
    bubble.think = bubble_bob
    bubble.touch = bubble_remove
    bubble.classname = 'bubble'
    bubble.frame = 0
    bubble.cnt = 0
    qc.setsize(bubble, Vector(-8, -8, -8), Vector(8, 8, 8))
    qc.self.nextthink = qc.time + random.random() + 0.5
    qc.self.think = make_bubbles
    

def bubble_split(*qwp_extra):
    bubble = qc.spawn()
    bubble.setmodel('progs/s_bubble.spr')
    qc.setorigin(bubble, qc.self.origin)
    bubble.movetype = defs.MOVETYPE_NOCLIP
    bubble.solid = defs.SOLID_NOT
    bubble.velocity = qc.self.velocity
    bubble.nextthink = qc.time + 0.5
    bubble.think = bubble_bob
    bubble.touch = bubble_remove
    bubble.classname = 'bubble'
    bubble.frame = 1
    bubble.cnt = 10
    qc.setsize(bubble, Vector(-8, -8, -8), Vector(8, 8, 8))
    qc.self.frame = 1
    qc.self.cnt = 10
    if qc.self.waterlevel != 3:
        qc.self.remove()
    

def bubble_remove(*qwp_extra):
    if qc.other.classname == qc.self.classname:
        # 		dprint ("bump");
        return         
    qc.self.remove()
    

def bubble_bob(*qwp_extra):
    qc.self.cnt += 1
    if qc.self.cnt == 4:
        bubble_split()
    if qc.self.cnt == 20:
        qc.self.remove()
    rnd1 = qc.self.velocity.x + ((random.random() * 20) - 10)
    rnd2 = qc.self.velocity.y + ((random.random() * 20) - 10)
    rnd3 = qc.self.velocity.z + ((random.random() * 10) + 10)
    if rnd1 > 10:
        rnd1 = 5
    if rnd1 < -10:
        rnd1 = -5
    if rnd2 > 10:
        rnd2 = 5
    if rnd2 < -10:
        rnd2 = -5
    if rnd3 < 10:
        rnd3 = 15
    if rnd3 > 30:
        rnd3 = 25
    qc.self.velocity = Vector(rnd1, rnd2, rnd3)
    qc.self.nextthink = qc.time + 0.5
    qc.self.think = bubble_bob

    
# ~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>
# ~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~<~>~
# QUAKED viewthing (0 .5 .8) (-8 -8 -8) (8 8 8)
# 
# Just for the debugging level.  Don't use
# 
def viewthing(*qwp_extra):
    qc.self.movetype = defs.MOVETYPE_NONE
    qc.self.solid = defs.SOLID_NOT
    engine.precache_model('progs/player.mdl')
    qc.self.setmodel('progs/player.mdl')
    
# 
# ==============================================================================
# 
# SIMPLE BMODELS
# 
# ==============================================================================
# 

def func_wall_use(*qwp_extra):
    #  change to alternate textures
    qc.self.frame = 1 - qc.self.frame

    
# QUAKED func_wall (0 .5 .8) ?
# This is just a solid wall if not inhibitted
# 
def func_wall(*qwp_extra):
    if defs.gamestart and qc.self.model == '*47':
        return  #  remove deathmatch only wall on start map
    qc.self.angles = Vector(0, 0, 0)
    qc.self.movetype = defs.MOVETYPE_PUSH #  so it doesn't get pushed by anything
    qc.self.solid = defs.SOLID_BSP
    qc.self.use = func_wall_use
    qc.self.setmodel(qc.self.model)

    
# QUAKED func_illusionary (0 .5 .8) ?
# A simple entity that looks solid but lets you walk through it.
# 
def func_illusionary(*qwp_extra):
    qc.self.angles = Vector(0, 0, 0)
    qc.self.movetype = defs.MOVETYPE_NONE
    qc.self.solid = defs.SOLID_NOT
    qc.self.setmodel(qc.self.model)
    qc.self.makestatic()
    

# QUAKED func_episodegate (0 .5 .8) ? E1 E2 E3 E4
# This bmodel will appear if the episode has allready been completed, so players can't reenter it.
# 
def func_episodegate(*qwp_extra):
    if not (qc.serverflags & qc.self.spawnflags):
        return  #  can still enter episode
    qc.self.angles = Vector(0, 0, 0)
    qc.self.movetype = defs.MOVETYPE_PUSH #  so it doesn't get pushed by anything
    qc.self.solid = defs.SOLID_BSP
    qc.self.use = func_wall_use
    qc.self.setmodel(qc.self.model)
    

# QUAKED func_bossgate (0 .5 .8) ?
# This bmodel appears unless players have all of the episode sigils.
# 
def func_bossgate(*qwp_extra):
    if (qc.serverflags & 15) == 15 or defs.gamestart:
        return  #  all episodes completed
    qc.self.angles = Vector(0, 0, 0)
    qc.self.movetype = defs.MOVETYPE_PUSH #  so it doesn't get pushed by anything
    qc.self.solid = defs.SOLID_BSP
    qc.self.use = func_wall_use
    qc.self.setmodel(qc.self.model)

    
# ============================================================================
# QUAKED ambient_suck_wind (0.3 0.1 0.6) (-10 -10 -8) (10 10 8)
# 
def ambient_suck_wind(*qwp_extra):
    engine.precache_sound('ambience/suck1.wav')
    engine.ambientsound(qc.self.origin, 'ambience/suck1.wav', 1, defs.ATTN_STATIC)

    
# QUAKED ambient_drone (0.3 0.1 0.6) (-10 -10 -8) (10 10 8)
# 
def ambient_drone(*qwp_extra):
    engine.precache_sound('ambience/drone6.wav')
    engine.ambientsound(qc.self.origin, 'ambience/drone6.wav', 0.5, defs.ATTN_STATIC)

    
# QUAKED ambient_flouro_buzz (0.3 0.1 0.6) (-10 -10 -8) (10 10 8)
# 
def ambient_flouro_buzz(*qwp_extra):
    engine.precache_sound('ambience/buzz1.wav')
    engine.ambientsound(qc.self.origin, 'ambience/buzz1.wav', 1, defs.ATTN_STATIC)

    
# QUAKED ambient_drip (0.3 0.1 0.6) (-10 -10 -8) (10 10 8)
# 
def ambient_drip(*qwp_extra):
    engine.precache_sound('ambience/drip1.wav')
    engine.ambientsound(qc.self.origin, 'ambience/drip1.wav', 0.5, defs.ATTN_STATIC)

    
# QUAKED ambient_comp_hum (0.3 0.1 0.6) (-10 -10 -8) (10 10 8)
# 
def ambient_comp_hum(*qwp_extra):
    engine.precache_sound('ambience/comp1.wav')
    engine.ambientsound(qc.self.origin, 'ambience/comp1.wav', 1, defs.ATTN_STATIC)

    
# QUAKED ambient_thunder (0.3 0.1 0.6) (-10 -10 -8) (10 10 8)
# 
def ambient_thunder(*qwp_extra):
    engine.precache_sound('ambience/thunder1.wav')
    engine.ambientsound(qc.self.origin, 'ambience/thunder1.wav', 0.5, defs.ATTN_STATIC)

    
# QUAKED ambient_light_buzz (0.3 0.1 0.6) (-10 -10 -8) (10 10 8)
# 
def ambient_light_buzz(*qwp_extra):
    engine.precache_sound('ambience/fl_hum1.wav')
    engine.ambientsound(qc.self.origin, 'ambience/fl_hum1.wav', 0.5, defs.ATTN_STATIC)

    
# QUAKED ambient_swamp1 (0.3 0.1 0.6) (-10 -10 -8) (10 10 8)
# 
def ambient_swamp1(*qwp_extra):
    engine.precache_sound('ambience/swamp1.wav')
    engine.ambientsound(qc.self.origin, 'ambience/swamp1.wav', 0.5, defs.ATTN_STATIC)

    
# QUAKED ambient_swamp2 (0.3 0.1 0.6) (-10 -10 -8) (10 10 8)
# 
def ambient_swamp2(*qwp_extra):
    engine.precache_sound('ambience/swamp2.wav')
    engine.ambientsound(qc.self.origin, 'ambience/swamp2.wav', 0.5, defs.ATTN_STATIC)
    
# ============================================================================

def noise_think(*qwp_extra):
    qc.self.nextthink = qc.time + 0.5
    qc.self.sound(1, 'enforcer/enfire.wav', 1, defs.ATTN_NORM)
    qc.self.sound(2, 'enforcer/enfstop.wav', 1, defs.ATTN_NORM)
    qc.self.sound(3, 'enforcer/sight1.wav', 1, defs.ATTN_NORM)
    qc.self.sound(4, 'enforcer/sight2.wav', 1, defs.ATTN_NORM)
    qc.self.sound(5, 'enforcer/sight3.wav', 1, defs.ATTN_NORM)
    qc.self.sound(6, 'enforcer/sight4.wav', 1, defs.ATTN_NORM)
    qc.self.sound(7, 'enforcer/pain1.wav', 1, defs.ATTN_NORM)

    
# QUAKED misc_noisemaker (1 0.5 0) (-10 -10 -10) (10 10 10)
# 
# For optimzation testing, starts a lot of sounds.
# 
def misc_noisemaker(*qwp_extra):
    engine.precache_sound('enforcer/enfire.wav')
    engine.precache_sound('enforcer/enfstop.wav')
    engine.precache_sound('enforcer/sight1.wav')
    engine.precache_sound('enforcer/sight2.wav')
    engine.precache_sound('enforcer/sight3.wav')
    engine.precache_sound('enforcer/sight4.wav')
    engine.precache_sound('enforcer/pain1.wav')
    engine.precache_sound('enforcer/pain2.wav')
    engine.precache_sound('enforcer/death1.wav')
    engine.precache_sound('enforcer/idle1.wav')
    qc.self.nextthink = qc.time + 0.1 + random.random()
    qc.self.think = noise_think
    

def qwp_reset_misc(*qwp_extra):
    global START_OFF
    global SPAWNFLAG_SUPERSPIKE
    global SPAWNFLAG_LASER
    
    START_OFF = 1
    SPAWNFLAG_SUPERSPIKE = 1
    SPAWNFLAG_LASER = 2
