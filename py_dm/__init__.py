#
# QWPython Game translated from QuakeC Source
#
import sys
from qwpython.qwsv import engine, Vector
import qwpython.qcsupport
from qwpython.qcsupport import qc

# Stop on CTRL-C
import signal
signal.signal(signal.SIGINT, engine.stop)

#
# Modules translated from QuakeC
#
from buttons import *
from client import *
from combat import *
from defs import *
from doors import *
from items import *
from misc import *
from plats import *
from player import *
from server import *
from spectate import *
from subs import *
from triggers import *
from weapons import *
from world import *

#
# Reset the globals that appear in the game, and
# spawn the entities specified by the map
#    
def qwp_reset():
    qwp_reset_client()
    qwp_reset_defs()
    qwp_reset_doors()
    qwp_reset_items()
    qwp_reset_misc()
    qwp_reset_plats()
    qwp_reset_triggers()
    qwp_reset_weapons()
    qwp_reset_world()
 
#
# Let the engine know who to call when it's time to reset and spawn
#    
engine.reset_game = qwp_reset
engine.spawn_func = qwpython.qcsupport.spawn_entities

#
# Entity fields defined for this game
#
qwpython.qcsupport.game_entity_fields = (
    ('aflag', 0),
    ('air_finished', 0),
    ('attack_finished', 0),
    ('attack_state', 0),
    ('axhitme', 0),
    ('bubble_count', 0),
    ('cnt', 0),
    ('count', 0),
    ('deathtype', None),
    ('delay', 0),
    ('dest', Vector(0, 0, 0)),
    ('dest1', Vector(0, 0, 0)),
    ('dest2', Vector(0, 0, 0)),
    ('distance', 0),
    ('dmg', 0),
    ('dmgtime', 0),
    ('finalangle', Vector(0, 0, 0)),
    ('finaldest', Vector(0, 0, 0)),
    ('fly_sound', 0),
    ('healamount', 0),
    ('healtype', 0),
    ('height', 0),
    ('hit.z', 0),
    ('invincible_finished', 0),
    ('invincible_sound', 0),
    ('invincible_time', 0),
    ('invisible_finished', 0),
    ('invisible_sound', 0),
    ('invisible_time', 0),
    ('jump_flag', 0),
    ('killtarget', None),
    ('lefty', 0),
    ('light_lev', 0),
    ('lip', 0),
    ('mangle', Vector(0, 0, 0)),
    ('map', None),
    ('mdl', None),
    ('movetarget', engine.world),
    ('noise4', None),
    ('oldenemy', engine.world),
    ('pain_finished', 0),
    ('pausetime', 0),
    ('pos1', Vector(0, 0, 0)),
    ('pos2', Vector(0, 0, 0)),
    ('rad_time', 0),
    ('radsuit_finished', 0),
    ('search_time', 0),
    ('show_hostile', 0),
    ('speed', 0),
    ('state', 0),
    ('style', 0),
    ('super_damage_finished', 0),
    ('super_sound', 0),
    ('super_time', 0),
    ('swim_flag', 0),
    ('t_length', 0),
    ('t_width', 0),
    ('th_die', None),
    ('th_melee', None),
    ('th_missile', None),
    ('th_pain', None),
    ('th_run', None),
    ('th_stand', None),
    ('th_walk', None),
    ('think1', None),
    ('trigger_field', engine.world),
    ('voided', 0),
    ('volume', 0),
    ('wad', None),
    ('wait', 0),
    ('waitmax', 0),
    ('waitmin', 0),
    ('walkframe', 0),
    ('worldtype', 0)
)
    
def spawn_entity(ent_class):
    sys.modules[__name__].__dict__[ent_class]()

def wrap_client_connect():
    for f in qwpython.qcsupport.game_entity_fields:  
        setattr(qc.self, f[0], f[1])
    ClientConnect()
    
def wrap_put_client_in_server():
    for f in qwpython.qcsupport.game_entity_fields: 
        if not hasattr(qc.self, f[0]): 
            setattr(qc.self, f[0], f[1])
    PutClientInServer()
    
#
# Hook up the Engine to various Python functions that it will need to call
#    
qwpython.qcsupport.spawn_func    = spawn_entity
qc.start_frame          = StartFrame
qc.player_pre_think     = PlayerPreThink
qc.player_post_think    = PlayerPostThink
qc.client_kill          = ClientKill
qc.client_connect       = wrap_client_connect
qc.put_client_in_server = wrap_put_client_in_server
qc.client_disconnect    = ClientDisconnect
qc.set_new_parms        = SetNewParms
qc.set_change_parms     = SetChangeParms

#
# Run the game
#
engine.run()
