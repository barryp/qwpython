#
# Python code that somewhat mimics the QuakeC environment
#
import re, string, traceback
from string import join
from qwpython.qwsv import engine, Vector

class QCGlobals:
    def __init__(self):    
        self.centerprint3 = self.centerprint2
        self.centerprint4 = self.centerprint2
        self.centerprint5 = self.centerprint2
        self.centerprint6 = self.centerprint2
        self.centerprint7 = self.centerprint2

    def __getattr__(self, attr):
        return engine.get_qc_global(attr)

    def __setattr__(self, attr, value):
        try:
            engine.set_qc_global(attr, value)
        except AttributeError:
            self.__dict__[attr] = value                
                            
    def aim(self, ent, speed):
        return ent.aim(speed)   
            
    def centerprint(self, ent, str):
        ent.centerprint(str)    
            
    def centerprint2(self, ent, *strs):
        ent.centerprint(join(strs, ''))  
        
    def droptofloor(self):
        return engine.get_qc_global('self').droptofloor()
        
    def error(self, msg):
        engine.stdout.write(msg)
        
    def find(self, entstart, fieldname, match):
        while 1:
            entstart = entstart.next_entity()
            if not entstart:
                return engine.world
            if getattr(entstart, fieldname, None) == match:
                return entstart
        
    def findradius(self, origin, radius):
        ents = engine.findradius(origin, radius)
        if not ents:
            return None
        for i in range(len(ents)-1):
            ents[i].chain = ents[i+1]
        ents[-1].chain = None
        return ents[0]                   
            
    def infokey(self, ent, key):
        return ent.infokey(key)
    
    def length(self, v):
        return v.length()
                
    def logfrag(self, killer, killee):
        killer.logfrag(killee)
        
    def makestatic(self, ent):
        ent.makestatic()                
                    
    def makevectors(self, angles):
        (self.v_forward, self.v_up, self.v_right) = angles.to_vectors()                

    def nextent(self, ent):
        r = ent.next_entity()
        if r:
            return r
        else:
            return engine.world
                        
    def normalize(self, v):
        return v.normalize()
        
    def objerror(self, msg):
        print 'objerror [%s] %s' % (qc.self, msg)
        
    def precache_file(self, f):
        "precache_file is only used to copy files with qcc, it does nothing"
        pass   
        
    def remove(self, e):
        e.remove()        
            
    def setmodel(self, ent, m):
        ent.setmodel(m)
            
    def setorigin(self, ent, o):
        ent.origin = o
        ent.link()
            
    def setsize(self, ent, min, max):
        ent.mins = min
        ent.maxs = max
        ent.size = max - min
        ent.link()                
    
    def sound(self, e, chan, samp, vol, atten):
        e.sound(chan, samp, vol, atten)
                        
    def spawn(self):
        ent = engine.spawn()
        for f in game_entity_fields:  
            setattr(ent, f[0], f[1])
        return ent                              
                        
    def sprint(self, ent, level, str):
        ent.sprint(level, str)
        
    def stof(self, s):
        try:
            return float(s)
        except:
            return 0
                  
    def stuffcmd(self, ent, cmd):
        ent.stuffcmd(cmd)    
        
    def traceline(self, v1, v2, nomonsters, forent):
        engine.traceline(v1, v2, nomonsters, forent)

    def vectoangles(self, v):
        return v.to_angle()        
        
    def vectoyaw(self, v):
        return v.to_angle().yaw
        
    def WriteAngle(self, to, b):
        if to == 1:
            self.msg_entity.write_angle(b)
        else:
            engine.write_angle(to, b)
    
    def WriteByte(self, to, b):
        if to == 1:
            self.msg_entity.write_byte(b)
        else:
            engine.write_byte(to, b)
    
    def WriteChar(self, to, ch):
        if to == 1:
            self.msg_entity.write_char(ch)
        else:
            engine.write_char(to, ch)
    
    def WriteCoord(self, to, b):
        if to == 1:
            self.msg_entity.write_coord(b)
        else:
            engine.write_coord(to, b)
            
    def WriteEntity(self, to, b):
        if to == 1:
            self.msg_entity.write_entity(b)
        else:
            engine.write_entity(to, b)
    
    def WriteLong(self, to, b):
        if to == 1:
            self.msg_entity.write_long(b)
        else:
            engine.write_long(to, b)
    
    def WriteShort(self, to, s):
        if to == 1:
            self.msg_entity.write_short(s)
        else:
            engine.write_short(to, s)
    
    def WriteString(self, to, b):
        if to == 1:
            self.msg_entity.write_string(b)
        else:
            engine.write_string(to, b)

qc = QCGlobals()     


def _fix_value(s):
    """
    Try to convert a string value into an integer, float, or
    QWPython Vector.  Otherwise leave it as a string (but fix
    any occurances of "\n")
    """
    try:
        return int(s)
    except:
        pass
    try:
        return float(s)
    except:
        pass
    try:
        a = string.split(s)
        if len(a) == 3:
            a = map(float, a)
            return Vector(a[0], a[1], a[2])
    except:
        pass                
    return string.replace(s, '\\n', '\n')        
    
    
def parse_entity_string(s):
    """
    Parse an entity string supplied with a Quake map, and return
    a list.  Each entry in the list is a dictionary which holds 
    the keywords and values that describe one entity's initial 
    settings.  Each value will be either a Python int, float, 
    string, or QWPython Vector.
    """
    parengroups = re.findall('{([^}]+)}', s)  # Pick out stuff inside each {...} pair
    entities = []
    for p in parengroups:
        tokens =  re.findall('"([^"]*)"', p)  # Pick out each "..." string
        d = {}
        for i in range(0, len(tokens), 2):    
            d[tokens[i]] = _fix_value(tokens[i+1])
        entities.append(d)     
    return entities        
    

def config_entity(ent, data):
    try:
        for f in game_entity_fields:  
            setattr(ent, f[0], f[1])
                
        for k in data.keys():
            # emulate some hacks that were in the C code
            if k == 'angle':
                setattr(ent, 'angles', Vector(0, data[k], 0))
            elif k == 'light':
                setattr(ent, 'light_env', data[k])
            else:                    
                setattr(ent, k, data[k])
                
        qc.self = ent            
        spawn_func(data['classname'])
    except:
        ent.remove()    
        traceback.print_exc()  


def spawn_entities(s):
    """
    Parse the map's entstring, and for each entity not inhibited for
    deathmatch, create an engine entity, set its attributes, and
    run the spawn function for its class.  In case of trouble, 
    remove the engine entity.
    """
    ents = parse_entity_string(s)
    
    # the first gob of info is for the world (which already exists)
    config_entity(engine.world, ents[0])
    
    # the rest of the data is for new entities
    for e in ents[1:]:
        if e.get('spawnflags', 0) & 2048 != 0:  # flagged as non-deathmatch only
            continue  
        config_entity(engine.spawn(), e)            

