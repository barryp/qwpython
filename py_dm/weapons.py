###
### Generated by QuakeC -> Python translator
### Id: qc2python.py,v 1.4 2001/02/05 16:26:04 barryp Exp 
###
from qwpython.qwsv import engine, Vector
from qwpython.qcsupport import qc

import random
import defs
import combat
import subs
import player

# 
# 
#  called by worldspawn

def W_Precache(*qwp_extra):
    engine.precache_sound('weapons/r_exp3.wav') #  new rocket explosion
    engine.precache_sound('weapons/rocket1i.wav') #  spike gun
    engine.precache_sound('weapons/sgun1.wav')
    engine.precache_sound('weapons/guncock.wav') #  player shotgun
    engine.precache_sound('weapons/ric1.wav') #  ricochet (used in c code)
    engine.precache_sound('weapons/ric2.wav') #  ricochet (used in c code)
    engine.precache_sound('weapons/ric3.wav') #  ricochet (used in c code)
    engine.precache_sound('weapons/spike2.wav') #  super spikes
    engine.precache_sound('weapons/tink1.wav') #  spikes tink (used in c code)
    engine.precache_sound('weapons/grenade.wav') #  grenade launcher
    engine.precache_sound('weapons/bounce.wav') #  grenade bounce
    engine.precache_sound('weapons/shotgn2.wav') #  super shotgun
    

def crandom(*qwp_extra):
    return 2 * (random.random() - 0.5)
    
# 
# ================
# W_FireAxe
# ================
# 

def W_FireAxe(*qwp_extra):
    source = Vector(0, 0, 0)
    org = Vector(0, 0, 0)
    qc.makevectors(qc.self.v_angle)
    source = qc.self.origin + Vector(0, 0, 16)
    qc.traceline(source, source + qc.v_forward * 64, defs.FALSE, qc.self)
    if qc.trace_fraction == 1.0:
        return 
    org = qc.trace_endpos - qc.v_forward * 4
    if qc.trace_ent.takedamage:
        qc.trace_ent.axhitme = 1
        SpawnBlood(org, 20)
        if defs.deathmatch > 3:
            combat.T_Damage(qc.trace_ent, qc.self, qc.self, 75)
        else:
            combat.T_Damage(qc.trace_ent, qc.self, qc.self, 20)
        
    else:
        #  hit wall
        qc.self.sound(defs.CHAN_WEAPON, 'player/axhit2.wav', 1, defs.ATTN_NORM)
        qc.WriteByte(defs.MSG_MULTICAST, defs.SVC_TEMPENTITY)
        qc.WriteByte(defs.MSG_MULTICAST, defs.TE_GUNSHOT)
        qc.WriteByte(defs.MSG_MULTICAST, 3)
        qc.WriteCoord(defs.MSG_MULTICAST, org.x)
        qc.WriteCoord(defs.MSG_MULTICAST, org.y)
        qc.WriteCoord(defs.MSG_MULTICAST, org.z)
        engine.multicast(org, defs.MULTICAST_PVS)
        
    
# ============================================================================

def wall_velocity(*qwp_extra):
    vel = Vector(0, 0, 0)
    vel = qc.self.velocity.normalize()
    vel = qc.normalize(vel + qc.v_up * (random.random() - 0.5) + qc.v_right * (random.random() - 0.5))
    vel += 2 * qc.trace_plane_normal
    vel *= 200
    return vel
    
# 
# ================
# SpawnMeatSpray
# ================
# 

def SpawnMeatSpray(org, vel, *qwp_extra):
    missile = engine.world
    missile = qc.spawn()
    missile.owner = qc.self
    missile.movetype = defs.MOVETYPE_BOUNCE
    missile.solid = defs.SOLID_NOT
    qc.makevectors(qc.self.angles)
    missile.velocity = vel
    missile.velocity %= Vector(None, None, missile.velocity.z + 250 + 50 * random.random())
    missile.avelocity = Vector(3000, 1000, 2000)
    #  set missile duration
    missile.nextthink = qc.time + 1
    missile.think = subs.SUB_Remove
    missile.setmodel('progs/zom_gib.mdl')
    qc.setsize(missile, Vector(0, 0, 0), Vector(0, 0, 0))
    qc.setorigin(missile, org)
    
# 
# ================
# SpawnBlood
# ================
# 

def SpawnBlood(org, damage, *qwp_extra):
    qc.WriteByte(defs.MSG_MULTICAST, defs.SVC_TEMPENTITY)
    qc.WriteByte(defs.MSG_MULTICAST, defs.TE_BLOOD)
    qc.WriteByte(defs.MSG_MULTICAST, 1)
    qc.WriteCoord(defs.MSG_MULTICAST, org.x)
    qc.WriteCoord(defs.MSG_MULTICAST, org.y)
    qc.WriteCoord(defs.MSG_MULTICAST, org.z)
    engine.multicast(org, defs.MULTICAST_PVS)
    
# 
# ================
# spawn_touchblood
# ================
# 

def spawn_touchblood(damage, *qwp_extra):
    vel = Vector(0, 0, 0)
    vel = wall_velocity() * 0.2
    SpawnBlood(qc.self.origin + vel * 0.01, damage)
    
# 
# ==============================================================================
# 
# MULTI-DAMAGE
# 
# Collects multiple small damages into a single damage
# 
# ==============================================================================
# 
multi_ent = engine.world
multi_damage = 0
blood_org = Vector(0, 0, 0)
blood_count = 0
puff_org = Vector(0, 0, 0)
puff_count = 0

def ClearMultiDamage(*qwp_extra):
    global multi_ent
    global multi_damage
    global blood_count
    global puff_count
    multi_ent = qc.world
    multi_damage = 0
    blood_count = 0
    puff_count = 0
    

def ApplyMultiDamage(*qwp_extra):
    if not multi_ent:
        return 
    combat.T_Damage(multi_ent, qc.self, qc.self, multi_damage)
    

def AddMultiDamage(hit, damage, *qwp_extra):
    global multi_damage
    global multi_ent
    if not hit:
        return 
    if hit != multi_ent:
        ApplyMultiDamage()
        multi_damage = damage
        multi_ent = hit
        
    else:
        multi_damage += damage
    

def Multi_Finish(*qwp_extra):
    if puff_count:
        qc.WriteByte(defs.MSG_MULTICAST, defs.SVC_TEMPENTITY)
        qc.WriteByte(defs.MSG_MULTICAST, defs.TE_GUNSHOT)
        qc.WriteByte(defs.MSG_MULTICAST, puff_count)
        qc.WriteCoord(defs.MSG_MULTICAST, puff_org.x)
        qc.WriteCoord(defs.MSG_MULTICAST, puff_org.y)
        qc.WriteCoord(defs.MSG_MULTICAST, puff_org.z)
        engine.multicast(puff_org, defs.MULTICAST_PVS)
        
    if blood_count:
        qc.WriteByte(defs.MSG_MULTICAST, defs.SVC_TEMPENTITY)
        qc.WriteByte(defs.MSG_MULTICAST, defs.TE_BLOOD)
        qc.WriteByte(defs.MSG_MULTICAST, blood_count)
        qc.WriteCoord(defs.MSG_MULTICAST, blood_org.x)
        qc.WriteCoord(defs.MSG_MULTICAST, blood_org.y)
        qc.WriteCoord(defs.MSG_MULTICAST, blood_org.z)
        engine.multicast(puff_org, defs.MULTICAST_PVS)
        
    
# 
# ==============================================================================
# BULLETS
# ==============================================================================
# 
# 
# ================
# TraceAttack
# ================
# 

def TraceAttack(damage, dir, *qwp_extra):
    global blood_count
    global blood_org
    global puff_count
    vel = Vector(0, 0, 0)
    org = Vector(0, 0, 0)
    vel = qc.normalize(dir + qc.v_up * crandom() + qc.v_right * crandom())
    vel += 2 * qc.trace_plane_normal
    vel *= 200
    org = qc.trace_endpos - dir * 4
    if qc.trace_ent.takedamage:
        blood_count += 1
        blood_org = org
        AddMultiDamage(qc.trace_ent, damage)
        
    else:
        puff_count += 1
        
    
# 
# ================
# FireBullets
# 
# Used by shotgun, super shotgun, and enemy soldier firing
# Go to the trouble of combining multiple pellets into a single damage call.
# ================
# 

def FireBullets(shotcount, dir, spread, *qwp_extra):
    global puff_org
    direction = Vector(0, 0, 0)
    src = Vector(0, 0, 0)
    qc.makevectors(qc.self.v_angle)
    src = qc.self.origin + qc.v_forward * 10
    src %= Vector(None, None, qc.self.absmin.z + qc.self.size.z * 0.7)
    ClearMultiDamage()
    qc.traceline(src, src + dir * 2048, defs.FALSE, qc.self)
    puff_org = qc.trace_endpos - dir * 4
    while shotcount > 0:
        direction = dir + crandom() * spread.x * qc.v_right + crandom() * spread.y * qc.v_up
        qc.traceline(src, src + direction * 2048, defs.FALSE, qc.self)
        if qc.trace_fraction != 1.0:
            TraceAttack(4, direction)
        shotcount -= 1
        
    ApplyMultiDamage()
    Multi_Finish()
    
# 
# ================
# W_FireShotgun
# ================
# 

def W_FireShotgun(*qwp_extra):
    dir = Vector(0, 0, 0)
    qc.self.sound(defs.CHAN_WEAPON, 'weapons/guncock.wav', 1, defs.ATTN_NORM)
    qc.msg_entity = qc.self
    qc.WriteByte(defs.MSG_ONE, defs.SVC_SMALLKICK)
    if defs.deathmatch != 4:
        qc.self.currentammo = qc.self.ammo_shells = qc.self.ammo_shells - 1
    dir = qc.self.aim(100000)
    FireBullets(6, dir, Vector(0.04, 0.04, 0))
    
# 
# ================
# W_FireSuperShotgun
# ================
# 

def W_FireSuperShotgun(*qwp_extra):
    dir = Vector(0, 0, 0)
    if qc.self.currentammo == 1:
        W_FireShotgun()
        return 
        
    qc.self.sound(defs.CHAN_WEAPON, 'weapons/shotgn2.wav', 1, defs.ATTN_NORM)
    qc.msg_entity = qc.self
    qc.WriteByte(defs.MSG_ONE, defs.SVC_BIGKICK)
    if defs.deathmatch != 4:
        qc.self.currentammo = qc.self.ammo_shells = qc.self.ammo_shells - 2
    dir = qc.self.aim(100000)
    FireBullets(14, dir, Vector(0.14, 0.08, 0))
    
# 
# ==============================================================================
# 
# ROCKETS
# 
# ==============================================================================
# 

def T_MissileTouch(*qwp_extra):
    damg = 0
    # 	if (deathmatch == 4)
    # 	{
    # 	if ( ((other.weapon == 32) || (other.weapon == 16)))
    # 		{	
    # 			if (random() < 0.1)
    # 			{
    # 				if (other != world)
    # 				{
    # 	//				bprint (PRINT_HIGH, "Got here\n");
    # 					other.deathtype = "blaze";
    # 					T_Damage (other, self, self.owner, 1000 );
    # 					T_RadiusDamage (self, self.owner, 1000, other);
    # 				}
    # 			}
    # 		}	
    # 	}
    if qc.other == qc.self.owner:
        return  #  don't explode on owner
    if qc.self.voided:
        return 
        
    qc.self.voided = 1
    if engine.pointcontents(qc.self.origin) == defs.CONTENT_SKY:
        qc.self.remove()
        return 
        
    damg = 100 + random.random() * 20
    if qc.other.health:
        qc.other.deathtype = 'rocket'
        combat.T_Damage(qc.other, qc.self, qc.self.owner, damg)
        
    #  don't do radius damage to the other, because all the damage
    #  was done in the impact
    combat.T_RadiusDamage(qc.self, qc.self.owner, 120, qc.other, 'rocket')
    #   sound (self, CHAN_WEAPON, "weapons/r_exp3.wav", 1, ATTN_NORM);
    qc.self.origin -= 8 * qc.self.velocity.normalize()
    qc.WriteByte(defs.MSG_MULTICAST, defs.SVC_TEMPENTITY)
    qc.WriteByte(defs.MSG_MULTICAST, defs.TE_EXPLOSION)
    qc.WriteCoord(defs.MSG_MULTICAST, qc.self.origin.x)
    qc.WriteCoord(defs.MSG_MULTICAST, qc.self.origin.y)
    qc.WriteCoord(defs.MSG_MULTICAST, qc.self.origin.z)
    engine.multicast(qc.self.origin, defs.MULTICAST_PHS)
    qc.self.remove()
    
# 
# ================
# W_FireRocket
# ================
# 

def W_FireRocket(*qwp_extra):
    if defs.deathmatch != 4:
        qc.self.currentammo = qc.self.ammo_rockets = qc.self.ammo_rockets - 1
    qc.self.sound(defs.CHAN_WEAPON, 'weapons/sgun1.wav', 1, defs.ATTN_NORM)
    qc.msg_entity = qc.self
    qc.WriteByte(defs.MSG_ONE, defs.SVC_SMALLKICK)
    qc.newmis = qc.spawn()
    qc.newmis.owner = qc.self
    qc.newmis.movetype = defs.MOVETYPE_FLYMISSILE
    qc.newmis.solid = defs.SOLID_BBOX
    #  set newmis speed     
    qc.makevectors(qc.self.v_angle)
    qc.newmis.velocity = qc.self.aim(1000)
    qc.newmis.velocity *= 1000
    qc.newmis.angles = qc.vectoangles(qc.newmis.velocity)
    qc.newmis.touch = T_MissileTouch
    qc.newmis.voided = 0
    #  set newmis duration
    qc.newmis.nextthink = qc.time + 5
    qc.newmis.think = subs.SUB_Remove
    qc.newmis.classname = 'rocket'
    qc.newmis.setmodel('progs/missile.mdl')
    qc.setsize(qc.newmis, Vector(0, 0, 0), Vector(0, 0, 0))
    qc.setorigin(qc.newmis, qc.self.origin + qc.v_forward * 8 + Vector(0, 0, 16))
    
# 
# ===============================================================================
# LIGHTNING
# ===============================================================================
# 

def LightningHit(from0, damage, *qwp_extra):
    qc.WriteByte(defs.MSG_MULTICAST, defs.SVC_TEMPENTITY)
    qc.WriteByte(defs.MSG_MULTICAST, defs.TE_LIGHTNINGBLOOD)
    qc.WriteCoord(defs.MSG_MULTICAST, qc.trace_endpos.x)
    qc.WriteCoord(defs.MSG_MULTICAST, qc.trace_endpos.y)
    qc.WriteCoord(defs.MSG_MULTICAST, qc.trace_endpos.z)
    engine.multicast(qc.trace_endpos, defs.MULTICAST_PVS)
    combat.T_Damage(qc.trace_ent, from0, from0, damage)
    
# 
# =================
# LightningDamage
# =================
# 

def LightningDamage(p1, p2, from0, damage, *qwp_extra):
    e1 = engine.world
    e2 = engine.world
    f = Vector(0, 0, 0)
    f = p2 - p1
    f.normalize()
    f %= Vector(0 - f.y, None, None)
    f %= Vector(None, f.x, None)
    f %= Vector(None, None, 0)
    f *= 16
    e1 = e2 = qc.world
    qc.traceline(p1, p2, defs.FALSE, qc.self)
    if qc.trace_ent.takedamage:
        LightningHit(from0, damage)
        if qc.self.classname == 'player':
            if qc.other.classname == 'player':
                qc.trace_ent.velocity %= Vector(None, None, qc.trace_ent.velocity.z + 400)
            
        
    e1 = qc.trace_ent
    qc.traceline(p1 + f, p2 + f, defs.FALSE, qc.self)
    if qc.trace_ent != e1 and qc.trace_ent.takedamage:
        LightningHit(from0, damage)
        
    e2 = qc.trace_ent
    qc.traceline(p1 - f, p2 - f, defs.FALSE, qc.self)
    if qc.trace_ent != e1 and qc.trace_ent != e2 and qc.trace_ent.takedamage:
        LightningHit(from0, damage)
        
    

def W_FireLightning(*qwp_extra):
    org = Vector(0, 0, 0)
    cells = 0
    if qc.self.ammo_cells < 1:
        qc.self.weapon = W_BestWeapon()
        W_SetCurrentAmmo()
        return 
        
    #  explode if under water
    if qc.self.waterlevel > 1:
        if defs.deathmatch > 3:
            if random.random() <= 0.5:
                qc.self.deathtype = 'selfwater'
                combat.T_Damage(qc.self, qc.self, qc.self.owner, 4000)
                
            else:
                cells = qc.self.ammo_cells
                qc.self.ammo_cells = 0
                W_SetCurrentAmmo()
                combat.T_RadiusDamage(qc.self, qc.self, 35 * cells, qc.world, None)
                return 
                
            
        else:
            cells = qc.self.ammo_cells
            qc.self.ammo_cells = 0
            W_SetCurrentAmmo()
            combat.T_RadiusDamage(qc.self, qc.self, 35 * cells, qc.world, None)
            return 
            
        
    if qc.self.t_width < qc.time:
        qc.self.sound(defs.CHAN_WEAPON, 'weapons/lhit.wav', 1, defs.ATTN_NORM)
        qc.self.t_width = qc.time + 0.6
        
    qc.msg_entity = qc.self
    qc.WriteByte(defs.MSG_ONE, defs.SVC_SMALLKICK)
    if defs.deathmatch != 4:
        qc.self.currentammo = qc.self.ammo_cells = qc.self.ammo_cells - 1
    org = qc.self.origin + Vector(0, 0, 16)
    qc.traceline(org, org + qc.v_forward * 600, defs.TRUE, qc.self)
    qc.WriteByte(defs.MSG_MULTICAST, defs.SVC_TEMPENTITY)
    qc.WriteByte(defs.MSG_MULTICAST, defs.TE_LIGHTNING2)
    qc.WriteEntity(defs.MSG_MULTICAST, qc.self)
    qc.WriteCoord(defs.MSG_MULTICAST, org.x)
    qc.WriteCoord(defs.MSG_MULTICAST, org.y)
    qc.WriteCoord(defs.MSG_MULTICAST, org.z)
    qc.WriteCoord(defs.MSG_MULTICAST, qc.trace_endpos.x)
    qc.WriteCoord(defs.MSG_MULTICAST, qc.trace_endpos.y)
    qc.WriteCoord(defs.MSG_MULTICAST, qc.trace_endpos.z)
    engine.multicast(org, defs.MULTICAST_PHS)
    LightningDamage(qc.self.origin, qc.trace_endpos + qc.v_forward * 4, qc.self, 30)
    
# =============================================================================

def GrenadeExplode(*qwp_extra):
    if qc.self.voided:
        return 
        
    qc.self.voided = 1
    combat.T_RadiusDamage(qc.self, qc.self.owner, 120, qc.world, 'grenade')
    qc.WriteByte(defs.MSG_MULTICAST, defs.SVC_TEMPENTITY)
    qc.WriteByte(defs.MSG_MULTICAST, defs.TE_EXPLOSION)
    qc.WriteCoord(defs.MSG_MULTICAST, qc.self.origin.x)
    qc.WriteCoord(defs.MSG_MULTICAST, qc.self.origin.y)
    qc.WriteCoord(defs.MSG_MULTICAST, qc.self.origin.z)
    engine.multicast(qc.self.origin, defs.MULTICAST_PHS)
    qc.self.remove()
    

def GrenadeTouch(*qwp_extra):
    if qc.other == qc.self.owner:
        return  #  don't explode on owner
    if qc.other.takedamage == defs.DAMAGE_AIM:
        GrenadeExplode()
        return 
        
    qc.self.sound(defs.CHAN_WEAPON, 'weapons/bounce.wav', 1, defs.ATTN_NORM) #  bounce sound
    if qc.self.velocity == Vector(0, 0, 0):
        qc.self.avelocity = Vector(0, 0, 0)
    
# 
# ================
# W_FireGrenade
# ================
# 

def W_FireGrenade(*qwp_extra):
    if defs.deathmatch != 4:
        qc.self.currentammo = qc.self.ammo_rockets = qc.self.ammo_rockets - 1
    qc.self.sound(defs.CHAN_WEAPON, 'weapons/grenade.wav', 1, defs.ATTN_NORM)
    qc.msg_entity = qc.self
    qc.WriteByte(defs.MSG_ONE, defs.SVC_SMALLKICK)
    qc.newmis = qc.spawn()
    qc.newmis.voided = 0
    qc.newmis.owner = qc.self
    qc.newmis.movetype = defs.MOVETYPE_BOUNCE
    qc.newmis.solid = defs.SOLID_BBOX
    qc.newmis.classname = 'grenade'
    #  set newmis speed     
    qc.makevectors(qc.self.v_angle)
    if qc.self.v_angle.x:
        qc.newmis.velocity = qc.v_forward * 600 + qc.v_up * 200 + crandom() * qc.v_right * 10 + crandom() * qc.v_up * 10
    else:
        qc.newmis.velocity = qc.self.aim(10000)
        qc.newmis.velocity *= 600
        qc.newmis.velocity %= Vector(None, None, 200)
        
    qc.newmis.avelocity = Vector(300, 300, 300)
    qc.newmis.angles = qc.vectoangles(qc.newmis.velocity)
    qc.newmis.touch = GrenadeTouch
    #  set newmis duration
    if defs.deathmatch == 4:
        qc.newmis.nextthink = qc.time + 2.5
        qc.self.attack_finished = qc.time + 1.1
        # 		self.health = self.health - 1;
        combat.T_Damage(qc.self, qc.self, qc.self.owner, 10)
        
    else:
        qc.newmis.nextthink = qc.time + 2.5
    qc.newmis.think = GrenadeExplode
    qc.newmis.setmodel('progs/grenade.mdl')
    qc.setsize(qc.newmis, Vector(0, 0, 0), Vector(0, 0, 0))
    qc.setorigin(qc.newmis, qc.self.origin)
    
# =============================================================================
# 
# ===============
# launch_spike
# 
# Used for both the player and the ogre
# ===============
# 

def launch_spike(org, dir, *qwp_extra):
    qc.newmis = qc.spawn()
    qc.newmis.voided = 0
    qc.newmis.owner = qc.self
    qc.newmis.movetype = defs.MOVETYPE_FLYMISSILE
    qc.newmis.solid = defs.SOLID_BBOX
    qc.newmis.angles = qc.vectoangles(dir)
    qc.newmis.touch = spike_touch
    qc.newmis.classname = 'spike'
    qc.newmis.think = subs.SUB_Remove
    qc.newmis.nextthink = qc.time + 6
    qc.newmis.setmodel('progs/spike.mdl')
    qc.setsize(qc.newmis, defs.VEC_ORIGIN, defs.VEC_ORIGIN)
    qc.setorigin(qc.newmis, org)
    qc.newmis.velocity = dir * 1000
    

def W_FireSuperSpikes(*qwp_extra):
    dir = Vector(0, 0, 0)
    old = engine.world
    qc.self.sound(defs.CHAN_WEAPON, 'weapons/spike2.wav', 1, defs.ATTN_NORM)
    qc.self.attack_finished = qc.time + 0.2
    if defs.deathmatch != 4:
        qc.self.currentammo = qc.self.ammo_nails = qc.self.ammo_nails - 2
    dir = qc.self.aim(1000)
    launch_spike(qc.self.origin + Vector(0, 0, 16), dir)
    qc.newmis.touch = superspike_touch
    qc.newmis.setmodel('progs/s_spike.mdl')
    qc.setsize(qc.newmis, defs.VEC_ORIGIN, defs.VEC_ORIGIN)
    qc.msg_entity = qc.self
    qc.WriteByte(defs.MSG_ONE, defs.SVC_SMALLKICK)
    

def W_FireSpikes(ox, *qwp_extra):
    dir = Vector(0, 0, 0)
    old = engine.world
    qc.makevectors(qc.self.v_angle)
    if qc.self.ammo_nails >= 2 and qc.self.weapon == defs.IT_SUPER_NAILGUN:
        W_FireSuperSpikes()
        return 
        
    if qc.self.ammo_nails < 1:
        qc.self.weapon = W_BestWeapon()
        W_SetCurrentAmmo()
        return 
        
    qc.self.sound(defs.CHAN_WEAPON, 'weapons/rocket1i.wav', 1, defs.ATTN_NORM)
    qc.self.attack_finished = qc.time + 0.2
    if defs.deathmatch != 4:
        qc.self.currentammo = qc.self.ammo_nails = qc.self.ammo_nails - 1
    dir = qc.self.aim(1000)
    launch_spike(qc.self.origin + Vector(0, 0, 16) + qc.v_right * ox, dir)
    qc.msg_entity = qc.self
    qc.WriteByte(defs.MSG_ONE, defs.SVC_SMALLKICK)
    

def spike_touch(*qwp_extra):
    rand = 0
    if qc.other == qc.self.owner:
        return 
    if qc.self.voided:
        return 
        
    qc.self.voided = 1
    if qc.other.solid == defs.SOLID_TRIGGER:
        return  #  trigger field, do nothing
    if engine.pointcontents(qc.self.origin) == defs.CONTENT_SKY:
        qc.self.remove()
        return 
        
    #  hit something that bleeds
    if qc.other.takedamage:
        spawn_touchblood(9)
        qc.other.deathtype = 'nail'
        combat.T_Damage(qc.other, qc.self, qc.self.owner, 9)
        
    else:
        qc.WriteByte(defs.MSG_MULTICAST, defs.SVC_TEMPENTITY)
        if qc.self.classname == 'wizspike':
            qc.WriteByte(defs.MSG_MULTICAST, defs.TE_WIZSPIKE)
        elif qc.self.classname == 'knightspike':
            qc.WriteByte(defs.MSG_MULTICAST, defs.TE_KNIGHTSPIKE)
        else:
            qc.WriteByte(defs.MSG_MULTICAST, defs.TE_SPIKE)
        qc.WriteCoord(defs.MSG_MULTICAST, qc.self.origin.x)
        qc.WriteCoord(defs.MSG_MULTICAST, qc.self.origin.y)
        qc.WriteCoord(defs.MSG_MULTICAST, qc.self.origin.z)
        engine.multicast(qc.self.origin, defs.MULTICAST_PHS)
        
    qc.self.remove()
    

def superspike_touch(*qwp_extra):
    rand = 0
    if qc.other == qc.self.owner:
        return 
    if qc.self.voided:
        return 
        
    qc.self.voided = 1
    if qc.other.solid == defs.SOLID_TRIGGER:
        return  #  trigger field, do nothing
    if engine.pointcontents(qc.self.origin) == defs.CONTENT_SKY:
        qc.self.remove()
        return 
        
    #  hit something that bleeds
    if qc.other.takedamage:
        spawn_touchblood(18)
        qc.other.deathtype = 'supernail'
        combat.T_Damage(qc.other, qc.self, qc.self.owner, 18)
        
    else:
        qc.WriteByte(defs.MSG_MULTICAST, defs.SVC_TEMPENTITY)
        qc.WriteByte(defs.MSG_MULTICAST, defs.TE_SUPERSPIKE)
        qc.WriteCoord(defs.MSG_MULTICAST, qc.self.origin.x)
        qc.WriteCoord(defs.MSG_MULTICAST, qc.self.origin.y)
        qc.WriteCoord(defs.MSG_MULTICAST, qc.self.origin.z)
        engine.multicast(qc.self.origin, defs.MULTICAST_PHS)
        
    qc.self.remove()
    
# 
# ===============================================================================
# 
# PLAYER WEAPON USE
# 
# ===============================================================================
# 

def W_SetCurrentAmmo(*qwp_extra):
    player.player_run() #  get out of any weapon firing states
    qc.self.items -= qc.self.items & (defs.IT_SHELLS | defs.IT_NAILS | defs.IT_ROCKETS | defs.IT_CELLS)
    if qc.self.weapon == defs.IT_AXE:
        qc.self.currentammo = 0
        qc.self.weaponmodel = 'progs/v_axe.mdl'
        qc.self.weaponframe = 0
        
    elif qc.self.weapon == defs.IT_SHOTGUN:
        qc.self.currentammo = qc.self.ammo_shells
        qc.self.weaponmodel = 'progs/v_shot.mdl'
        qc.self.weaponframe = 0
        qc.self.items |= defs.IT_SHELLS
        
    elif qc.self.weapon == defs.IT_SUPER_SHOTGUN:
        qc.self.currentammo = qc.self.ammo_shells
        qc.self.weaponmodel = 'progs/v_shot2.mdl'
        qc.self.weaponframe = 0
        qc.self.items |= defs.IT_SHELLS
        
    elif qc.self.weapon == defs.IT_NAILGUN:
        qc.self.currentammo = qc.self.ammo_nails
        qc.self.weaponmodel = 'progs/v_nail.mdl'
        qc.self.weaponframe = 0
        qc.self.items |= defs.IT_NAILS
        
    elif qc.self.weapon == defs.IT_SUPER_NAILGUN:
        qc.self.currentammo = qc.self.ammo_nails
        qc.self.weaponmodel = 'progs/v_nail2.mdl'
        qc.self.weaponframe = 0
        qc.self.items |= defs.IT_NAILS
        
    elif qc.self.weapon == defs.IT_GRENADE_LAUNCHER:
        qc.self.currentammo = qc.self.ammo_rockets
        qc.self.weaponmodel = 'progs/v_rock.mdl'
        qc.self.weaponframe = 0
        qc.self.items |= defs.IT_ROCKETS
        
    elif qc.self.weapon == defs.IT_ROCKET_LAUNCHER:
        qc.self.currentammo = qc.self.ammo_rockets
        qc.self.weaponmodel = 'progs/v_rock2.mdl'
        qc.self.weaponframe = 0
        qc.self.items |= defs.IT_ROCKETS
        
    elif qc.self.weapon == defs.IT_LIGHTNING:
        qc.self.currentammo = qc.self.ammo_cells
        qc.self.weaponmodel = 'progs/v_light.mdl'
        qc.self.weaponframe = 0
        qc.self.items |= defs.IT_CELLS
        
    else:
        qc.self.currentammo = 0
        qc.self.weaponmodel = None
        qc.self.weaponframe = 0
        
    

def W_BestWeapon(*qwp_extra):
    it = 0
    it = qc.self.items
    if qc.self.waterlevel <= 1 and qc.self.ammo_cells >= 1 and (it & defs.IT_LIGHTNING):
        return defs.IT_LIGHTNING
    elif qc.self.ammo_nails >= 2 and (it & defs.IT_SUPER_NAILGUN):
        return defs.IT_SUPER_NAILGUN
    elif qc.self.ammo_shells >= 2 and (it & defs.IT_SUPER_SHOTGUN):
        return defs.IT_SUPER_SHOTGUN
    elif qc.self.ammo_nails >= 1 and (it & defs.IT_NAILGUN):
        return defs.IT_NAILGUN
    elif qc.self.ammo_shells >= 1 and (it & defs.IT_SHOTGUN):
        return defs.IT_SHOTGUN
    # 
    # 	if(self.ammo_rockets >= 1 && (it & IT_ROCKET_LAUNCHER) )
    # 		return IT_ROCKET_LAUNCHER;
    # 	else if(self.ammo_rockets >= 1 && (it & IT_GRENADE_LAUNCHER) )
    # 		return IT_GRENADE_LAUNCHER;
    # 
    # 
    return defs.IT_AXE
    

def W_CheckNoAmmo(*qwp_extra):
    if qc.self.currentammo > 0:
        return defs.TRUE
    if qc.self.weapon == defs.IT_AXE:
        return defs.TRUE
    qc.self.weapon = W_BestWeapon()
    W_SetCurrentAmmo()
    #  drop the weapon down
    return defs.FALSE
    
# 
# ============
# W_Attack
# 
# An attack impulse can be triggered now
# ============
# 

def W_Attack(*qwp_extra):
    r = 0
    if not W_CheckNoAmmo():
        return 
    qc.makevectors(qc.self.v_angle) #  calculate forward angle for velocity
    qc.self.show_hostile = qc.time + 1 #  wake monsters up
    if qc.self.weapon == defs.IT_AXE:
        qc.self.attack_finished = qc.time + 0.5
        qc.self.sound(defs.CHAN_WEAPON, 'weapons/ax1.wav', 1, defs.ATTN_NORM)
        r = random.random()
        if r < 0.25:
            player.player_axe1()
        elif r < 0.5:
            player.player_axeb1()
        elif r < 0.75:
            player.player_axec1()
        else:
            player.player_axed1()
        
    elif qc.self.weapon == defs.IT_SHOTGUN:
        player.player_shot1()
        qc.self.attack_finished = qc.time + 0.5
        W_FireShotgun()
        
    elif qc.self.weapon == defs.IT_SUPER_SHOTGUN:
        player.player_shot1()
        qc.self.attack_finished = qc.time + 0.7
        W_FireSuperShotgun()
        
    elif qc.self.weapon == defs.IT_NAILGUN:
        player.player_nail1()
        
    elif qc.self.weapon == defs.IT_SUPER_NAILGUN:
        player.player_nail1()
        
    elif qc.self.weapon == defs.IT_GRENADE_LAUNCHER:
        player.player_rocket1()
        qc.self.attack_finished = qc.time + 0.6
        W_FireGrenade()
        
    elif qc.self.weapon == defs.IT_ROCKET_LAUNCHER:
        player.player_rocket1()
        qc.self.attack_finished = qc.time + 0.8
        W_FireRocket()
        
    elif qc.self.weapon == defs.IT_LIGHTNING:
        qc.self.attack_finished = qc.time + 0.1
        qc.self.sound(defs.CHAN_AUTO, 'weapons/lstart.wav', 1, defs.ATTN_NORM)
        player.player_light1()
        
    
# 
# ============
# W_ChangeWeapon
# 
# ============
# 

def W_ChangeWeapon(*qwp_extra):
    it = 0
    am = 0
    fl = 0
    it = qc.self.items
    am = 0
    if qc.self.impulse == 1:
        fl = defs.IT_AXE
        
    elif qc.self.impulse == 2:
        fl = defs.IT_SHOTGUN
        if qc.self.ammo_shells < 1:
            am = 1
        
    elif qc.self.impulse == 3:
        fl = defs.IT_SUPER_SHOTGUN
        if qc.self.ammo_shells < 2:
            am = 1
        
    elif qc.self.impulse == 4:
        fl = defs.IT_NAILGUN
        if qc.self.ammo_nails < 1:
            am = 1
        
    elif qc.self.impulse == 5:
        fl = defs.IT_SUPER_NAILGUN
        if qc.self.ammo_nails < 2:
            am = 1
        
    elif qc.self.impulse == 6:
        fl = defs.IT_GRENADE_LAUNCHER
        if qc.self.ammo_rockets < 1:
            am = 1
        
    elif qc.self.impulse == 7:
        fl = defs.IT_ROCKET_LAUNCHER
        if qc.self.ammo_rockets < 1:
            am = 1
        
    elif qc.self.impulse == 8:
        fl = defs.IT_LIGHTNING
        if qc.self.ammo_cells < 1:
            am = 1
        
    qc.self.impulse = 0
    if not (qc.self.items & fl):
        #  don't have the weapon or the ammo
        qc.self.sprint(defs.PRINT_HIGH, 'no weapon.\012')
        return 
        
    if am:
        #  don't have the ammo
        qc.self.sprint(defs.PRINT_HIGH, 'not enough ammo.\012')
        return 
        
    # 
    #  set weapon, set ammo
    # 
    qc.self.weapon = fl
    W_SetCurrentAmmo()
    
# 
# ============
# CheatCommand
# ============
# 

def CheatCommand(*qwp_extra):
    #       if (deathmatch || coop)
    return 
    qc.self.ammo_rockets = 100
    qc.self.ammo_nails = 200
    qc.self.ammo_shells = 100
    qc.self.items |= defs.IT_AXE | defs.IT_SHOTGUN | defs.IT_SUPER_SHOTGUN | defs.IT_NAILGUN | defs.IT_SUPER_NAILGUN | defs.IT_GRENADE_LAUNCHER | defs.IT_ROCKET_LAUNCHER | defs.IT_KEY1 | defs.IT_KEY2
    qc.self.ammo_cells = 200
    qc.self.items |= defs.IT_LIGHTNING
    qc.self.weapon = defs.IT_ROCKET_LAUNCHER
    qc.self.impulse = 0
    W_SetCurrentAmmo()
    
# 
# ============
# CycleWeaponCommand
# 
# Go to the next weapon with ammo
# ============
# 

def CycleWeaponCommand(*qwp_extra):
    it = 0
    am = 0
    it = qc.self.items
    qc.self.impulse = 0
    while 1:
        am = 0
        if qc.self.weapon == defs.IT_LIGHTNING:
            qc.self.weapon = defs.IT_AXE
            
        elif qc.self.weapon == defs.IT_AXE:
            qc.self.weapon = defs.IT_SHOTGUN
            if qc.self.ammo_shells < 1:
                am = 1
            
        elif qc.self.weapon == defs.IT_SHOTGUN:
            qc.self.weapon = defs.IT_SUPER_SHOTGUN
            if qc.self.ammo_shells < 2:
                am = 1
            
        elif qc.self.weapon == defs.IT_SUPER_SHOTGUN:
            qc.self.weapon = defs.IT_NAILGUN
            if qc.self.ammo_nails < 1:
                am = 1
            
        elif qc.self.weapon == defs.IT_NAILGUN:
            qc.self.weapon = defs.IT_SUPER_NAILGUN
            if qc.self.ammo_nails < 2:
                am = 1
            
        elif qc.self.weapon == defs.IT_SUPER_NAILGUN:
            qc.self.weapon = defs.IT_GRENADE_LAUNCHER
            if qc.self.ammo_rockets < 1:
                am = 1
            
        elif qc.self.weapon == defs.IT_GRENADE_LAUNCHER:
            qc.self.weapon = defs.IT_ROCKET_LAUNCHER
            if qc.self.ammo_rockets < 1:
                am = 1
            
        elif qc.self.weapon == defs.IT_ROCKET_LAUNCHER:
            qc.self.weapon = defs.IT_LIGHTNING
            if qc.self.ammo_cells < 1:
                am = 1
            
        if (qc.self.items & qc.self.weapon) and am == 0:
            W_SetCurrentAmmo()
            return 
            
        
    
# 
# ============
# CycleWeaponReverseCommand
# 
# Go to the prev weapon with ammo
# ============
# 

def CycleWeaponReverseCommand(*qwp_extra):
    it = 0
    am = 0
    it = qc.self.items
    qc.self.impulse = 0
    while 1:
        am = 0
        if qc.self.weapon == defs.IT_LIGHTNING:
            qc.self.weapon = defs.IT_ROCKET_LAUNCHER
            if qc.self.ammo_rockets < 1:
                am = 1
            
        elif qc.self.weapon == defs.IT_ROCKET_LAUNCHER:
            qc.self.weapon = defs.IT_GRENADE_LAUNCHER
            if qc.self.ammo_rockets < 1:
                am = 1
            
        elif qc.self.weapon == defs.IT_GRENADE_LAUNCHER:
            qc.self.weapon = defs.IT_SUPER_NAILGUN
            if qc.self.ammo_nails < 2:
                am = 1
            
        elif qc.self.weapon == defs.IT_SUPER_NAILGUN:
            qc.self.weapon = defs.IT_NAILGUN
            if qc.self.ammo_nails < 1:
                am = 1
            
        elif qc.self.weapon == defs.IT_NAILGUN:
            qc.self.weapon = defs.IT_SUPER_SHOTGUN
            if qc.self.ammo_shells < 2:
                am = 1
            
        elif qc.self.weapon == defs.IT_SUPER_SHOTGUN:
            qc.self.weapon = defs.IT_SHOTGUN
            if qc.self.ammo_shells < 1:
                am = 1
            
        elif qc.self.weapon == defs.IT_SHOTGUN:
            qc.self.weapon = defs.IT_AXE
            
        elif qc.self.weapon == defs.IT_AXE:
            qc.self.weapon = defs.IT_LIGHTNING
            if qc.self.ammo_cells < 1:
                am = 1
            
        if (it & qc.self.weapon) and am == 0:
            W_SetCurrentAmmo()
            return 
            
        
    
# 
# ============
# ServerflagsCommand
# 
# Just for development
# ============
# 

def ServerflagsCommand(*qwp_extra):
    qc.serverflags = qc.serverflags * 2 + 1
    
# 
# ============
# ImpulseCommands
# 
# ============
# 

def ImpulseCommands(*qwp_extra):
    if qc.self.impulse >= 1 and qc.self.impulse <= 8:
        W_ChangeWeapon()
    if qc.self.impulse == 9:
        CheatCommand()
    if qc.self.impulse == 10:
        CycleWeaponCommand()
    if qc.self.impulse == 11:
        ServerflagsCommand()
    if qc.self.impulse == 12:
        CycleWeaponReverseCommand()
    qc.self.impulse = 0
    
# 
# ============
# W_WeaponFrame
# 
# Called every frame so impulse events can be handled as well as possible
# ============
# 

def W_WeaponFrame(*qwp_extra):
    if qc.time < qc.self.attack_finished:
        return 
    ImpulseCommands()
    #  check for attack
    if qc.self.button0:
        SuperDamageSound()
        W_Attack()
        
    
# 
# ========
# SuperDamageSound
# 
# Plays sound if needed
# ========
# 

def SuperDamageSound(*qwp_extra):
    if qc.self.super_damage_finished > qc.time:
        if qc.self.super_sound < qc.time:
            qc.self.super_sound = qc.time + 1
            qc.self.sound(defs.CHAN_BODY, 'items/damage3.wav', 1, defs.ATTN_NORM)
            
        
    return 
    


def qwp_reset_weapons(*qwp_extra):
    global multi_ent
    global multi_damage
    global blood_org
    global blood_count
    global puff_org
    global puff_count
    multi_ent = engine.world
    multi_damage = 0
    blood_org = Vector(0, 0, 0)
    blood_count = 0
    puff_org = Vector(0, 0, 0)
    puff_count = 0
