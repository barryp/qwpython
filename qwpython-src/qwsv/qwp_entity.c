/*
 * Python version of the C edict_t structure
 */

#include "qwsvdef.h"

cvar_t	sv_aim = {"sv_aim", "2"};

static PyObject * entity_aim(PyObject *self, PyObject *args)
    {
	edict_t	*ent, *check, *bestent;
	vec3_t	start, dir, end, bestdir;
	int		i, j;
	trace_t	tr;
	float	dist, bestdist;
	float	speed;
	char	*noaim;

    if (!PyArg_ParseTuple(args, "f", &speed))
        return NULL;

	ent = ((qwp_entity_t *) self)->c_entity;

	VectorCopy (ent->v.origin, start);
	start[2] += 20;

    // noaim option
	i = NUM_FOR_EDICT(ent);
	if (i>0 && i<MAX_CLIENTS)
	    {
		noaim = Info_ValueForKey (svs.clients[i-1].userinfo, "noaim");
		if (atoi(noaim) > 0)
			return create_qwp_vector(pr_global_struct->v_forward);
	    }

    // try sending a trace straight
	VectorCopy (pr_global_struct->v_forward, dir);
	VectorMA (start, 2048, dir, end);
	tr = SV_Move (start, vec3_origin, vec3_origin, end, false, ent);
	if (tr.ent && tr.ent->v.takedamage == DAMAGE_AIM
	&& (!teamplay.value || ent->v.team <=0 || ent->v.team != tr.ent->v.team) )
		return create_qwp_vector(pr_global_struct->v_forward);


    // try all possible entities
	VectorCopy (dir, bestdir);
	bestdist = sv_aim.value;
	bestent = NULL;
	
	check = NEXT_EDICT(sv.edicts);
	for (i=1 ; i<sv.num_edicts ; i++, check = NEXT_EDICT(check) )
	    {
		if (check->v.takedamage != DAMAGE_AIM)
			continue;
		if (check == ent)
			continue;
		if (teamplay.value && ent->v.team > 0 && ent->v.team == check->v.team)
			continue;	// don't aim at teammate
		for (j=0 ; j<3 ; j++)
			end[j] = check->v.origin[j]
			+ 0.5*(check->v.mins[j] + check->v.maxs[j]);
		VectorSubtract (end, start, dir);
		VectorNormalize (dir);
		dist = DotProduct (dir, pr_global_struct->v_forward);
		if (dist < bestdist)
			continue;	// to far to turn
		tr = SV_Move (start, vec3_origin, vec3_origin, end, false, ent);
		if (tr.ent == check)
		    {	
            // can shoot at this one
			bestdist = dist;
			bestent = check;
		    }
	    }
	
	if (bestent)
	    {
		VectorSubtract (bestent->v.origin, ent->v.origin, dir);
		dist = DotProduct (dir, pr_global_struct->v_forward);
		VectorScale (pr_global_struct->v_forward, dist, end);
		end[2] = dir[2];
		VectorNormalize (end);
		return create_qwp_vector(end);
	    }

	return create_qwp_vector(bestdir);
    }


static PyObject * entity_centerprint(PyObject *self, PyObject *args)
    {   
	char		*s;
	int			entnum;
	
    if (!PyArg_ParseTuple(args, "s", &s))
        return NULL;

	entnum = NUM_FOR_EDICT(((qwp_entity_t *)self)->c_entity);
	
	if (entnum < 1 || entnum > MAX_CLIENTS)
		Con_Printf ("tried to sprint to a non-client\n");
    else
        {            
    	client_t	*cl;

	    cl = &svs.clients[entnum-1];
	    ClientReliableWrite_Begin (cl, svc_centerprint, 2 + strlen(s));
	    ClientReliableWrite_String (cl, s);
        }

    Py_INCREF(Py_None);
    return Py_None;
    }


static PyObject * entity_droptofloor(PyObject *self, PyObject *args)
    {
	edict_t		*ent;
	vec3_t		end;
	trace_t		trace;
    int result;
    
	ent = ((qwp_entity_t *) self)->c_entity;

	VectorCopy (ent->v.origin, end);
	end[2] -= 256;
	
	trace = SV_Move (ent->v.origin, ent->v.mins, ent->v.maxs, end, false, ent);

	if (trace.fraction == 1 || trace.allsolid)
        result = 0;
	else
	    {
		VectorCopy (trace.endpos, ent->v.origin);
		SV_LinkEdict (ent, false);
		ent->v.flags = (int)ent->v.flags | FL_ONGROUND;
		ent->v.groundentity = EDICT_TO_PROG(trace.ent);
        result = 1;
	    }

    return PyInt_FromLong(result);
    }

static PyObject * entity_infokey(PyObject *self, PyObject *args)
    {
	edict_t	*e;
	int		e1;
	char	*value;
	char	*key;
	static	char ov[256];

    if (!PyArg_ParseTuple(args, "s", &key))
        return NULL;

	e = ((qwp_entity_t *) self)->c_entity;
	e1 = NUM_FOR_EDICT(e);

    value = NULL;

	if (e1 == 0) 
        {
		if ((value = Info_ValueForKey (svs.info, key)) == NULL || !*value)
			value = Info_ValueForKey(localinfo, key);
	    } 
    else if (e1 <= MAX_CLIENTS) 
        {
		if (!strcmp(key, "ip"))
			value = strcpy(ov, NET_BaseAdrToString (svs.clients[e1-1].netchan.remote_address));
		else if (!strcmp(key, "ping")) 
            {
			int ping = SV_CalcPing (&svs.clients[e1-1]);
			sprintf(ov, "%d", ping);
			value = ov;
		    } 
        else
			value = Info_ValueForKey (svs.clients[e1-1].userinfo, key);
	    } 

    if (!value || (!(*value)))
        {
        Py_INCREF(Py_None);
        return Py_None;
        }

	return PyString_FromString(value);
    }


static PyObject * entity_link(PyObject *self, PyObject *args)
    {
    SV_LinkEdict(((qwp_entity_t *)self)->c_entity, false);

    Py_INCREF(Py_None);
    return Py_None;
    }


static PyObject * entity_logfrag(PyObject *self, PyObject *args)
    {
	qwp_entity_t	*ent2;
	int		e1, e2;
	char	*s;

    if (!PyArg_ParseTuple(args, "O!", &QWP_Entity_Type, &ent2))
        return NULL;

	e1 = NUM_FOR_EDICT(((qwp_entity_t *)self)->c_entity);
	e2 = NUM_FOR_EDICT(ent2->c_entity);
	
	if (e1 > 0 && e1 <= MAX_CLIENTS && e2 > 0 &&  e2 <= MAX_CLIENTS)
        {
    	s = va("\\%s\\%s\\\n",svs.clients[e1-1].name, svs.clients[e2-1].name);

    	SZ_Print(&svs.log[svs.logsequence&1], s);
    	if (sv_fraglogfile) 
            {
		    fprintf(sv_fraglogfile, s);
		    fflush(sv_fraglogfile);
	        }
        }

    Py_INCREF(Py_None);
    return Py_None;
    }
    

static PyObject * entity_makestatic(PyObject *self, PyObject *args)
    {
	edict_t	*ent;
	int		i;
	
	ent = ((qwp_entity_t *) self)->c_entity;

	MSG_WriteByte (&sv.signon,svc_spawnstatic);

	MSG_WriteByte (&sv.signon, SV_ModelIndex_Py(ent->v.model));

	MSG_WriteByte (&sv.signon, ent->v.frame);
	MSG_WriteByte (&sv.signon, ent->v.colormap);
	MSG_WriteByte (&sv.signon, ent->v.skin);
	for (i=0 ; i<3 ; i++)
	    {
		MSG_WriteCoord(&sv.signon, ent->v.origin[i]);
		MSG_WriteAngle(&sv.signon, ent->v.angles[i]);
	    }

    // throw the entity away now
	ED_Free(ent);

    Py_INCREF(Py_None);
    return Py_None;
    }


static PyObject * entity_next_entity(PyObject *self, PyObject *args)
    {
    int i;
    edict_t *ent;

    ent = ((qwp_entity_t *)self)->c_entity;
    if (!ent)
        {
        PyErr_SetString(PyExc_TypeError, "Entity has been removed from game");
        return NULL;
        }

    for (i = NUM_FOR_EDICT(ent) + 1; i < sv.num_edicts; i++)
        {
        edict_t *e2 = EDICT_NUM(i);

        if ((!(e2->free)) && e2->p_entity)
            {
            Py_INCREF(e2->p_entity);
            return (PyObject *) e2->p_entity;
            }
        }

    Py_INCREF(Py_None);
    return Py_None;
    }


static int entity_nonzero(qwp_entity_t *e)
    {
    return (NUM_FOR_EDICT(e->c_entity) > 0);
    }



static PyObject * entity_remove(PyObject *self, PyObject *args)
    {
    edict_t *ent;

	ent = ((qwp_entity_t *)self)->c_entity;

    // Sys_Printf("Removing %d, p_entity=%x c_entity=%x\n", NUM_FOR_EDICT(ent), ent->p_entity, ent->p_entity->c_entity);

    if (!ent)
        {
        PyErr_SetString(PyExc_TypeError, "Entity has already been removed from game");
        return NULL;
        }

    if (ent == sv.edicts)
        {
        PyErr_SetString(PyExc_TypeError, "Can't remove the world entity");
        return NULL;
        }

    ED_Free(ent);

    Py_INCREF(Py_None);
    return Py_None;
    }

/*
=================
setmodel(model)
Also sets size, mins, and maxs for inline bmodels
=================
*/
static PyObject * entity_setmodel(PyObject *self, PyObject *args)
    {
	edict_t	*e;
    PyObject *modelname;
	char	*m, **check;
	int		i;
	model_t	*mod;

    if (!PyArg_ParseTuple(args, "O", &modelname))
        return NULL;

	e = ((qwp_entity_t *)self)->c_entity;

    if (modelname == Py_None)
        {
        Py_XDECREF(e->v.model);
    	e->v.model = NULL;
    	e->v.modelindex = 0;
        Py_INCREF(Py_None);
        return Py_None;                    
        }

    if (!PyString_Check(modelname))
        {
        PyErr_SetString(PyExc_TypeError, "Expecting None or a string for the model name");
        return NULL;
        }
    
    if (!e)
        {
        PyErr_SetString(PyExc_TypeError, "Entity has been removed from game");
        return NULL;
        }

    // check to see if model was properly precached
    m = PyString_AsString(modelname);
	for (i=0, check = sv.model_precache ; *check ; i++, check++)
		if (!strcmp(*check, m))
			break;

	if (!*check)
        {
        PyErr_Format(PyExc_TypeError, "%s was not precached", m);
        return NULL;
        }

    Py_XDECREF(e->v.model);
	e->v.model = modelname;
    Py_INCREF(modelname);
	e->v.modelindex = i;

    // if it is an inline model, get the size information for it
	if (m[0] == '*')
	    {
		mod = Mod_ForName (m, true);
		VectorCopy (mod->mins, e->v.mins);
		VectorCopy (mod->maxs, e->v.maxs);
		VectorSubtract (mod->maxs, mod->mins, e->v.size);
		SV_LinkEdict (e, false);
	    }

    Py_INCREF(Py_None);
    return Py_None;
    }


static PyObject * entity_sound(PyObject *self, PyObject *args)
    {
	edict_t		*entity;
	int			channel;
	char		*sample;
	int 		volume;
	float attenuation;
		
    entity = ((qwp_entity_t *)self)->c_entity;
    if (!entity)
        {
        PyErr_SetString(PyExc_TypeError, "Entity has been removed from game");
        return NULL;
        }

    if (!PyArg_ParseTuple(args, "isif", &channel, &sample, &volume, &attenuation))
        return NULL;

	SV_StartSound(entity, channel, sample, volume * 255, attenuation);

    Py_INCREF(Py_None);
    return Py_None;
    }


/* single print to a specific client */
static PyObject * entity_sprint(PyObject *self, PyObject *args)
    {
	int			entnum;
	int			level;
	char		*s;

    if (!PyArg_ParseTuple(args, "is", &level, &s))
        return NULL;
    
	entnum = NUM_FOR_EDICT(((qwp_entity_t *)self)->c_entity);
	
	if (entnum < 1 || entnum > MAX_CLIENTS)
		Con_Printf ("tried to sprint to a non-client\n");
    else
        {
    	client_t	*client;

	    client = &svs.clients[entnum-1];	
	    SV_ClientPrintf (client, level, "%s", s);
        }

    Py_INCREF(Py_None);
    return Py_None;
    }


static PyObject * entity_stuffcmd(PyObject *self, PyObject *args)
    {
    edict_t *entity;
	int		entnum;
	char	*str;
	client_t	*cl;

    entity = ((qwp_entity_t *)self)->c_entity;
    if (!entity)
        {
        PyErr_SetString(PyExc_TypeError, "Entity has been removed from game");
        return NULL;
        }
    
	entnum = NUM_FOR_EDICT(entity);
	if (entnum < 1 || entnum > MAX_CLIENTS)
        {
        PyErr_SetString(PyExc_TypeError, "Entity is not a client");
        return NULL;
        }

    if (!PyArg_ParseTuple(args, "s", &str))
        return NULL;
	
	cl = &svs.clients[entnum-1];

	if (strcmp(str, "disconnect\n") == 0) 
		// so long and thanks for all the fish
		cl->drop = true;
    else
        {
	    ClientReliableWrite_Begin (cl, svc_stufftext, 2+strlen(str));
	    ClientReliableWrite_String (cl, str);
        }

    Py_INCREF(Py_None);
    return Py_None;
    }

static client_t * Write_GetClient(PyObject *self)
    {
	int		entnum;
	edict_t	*ent;

	ent = ((qwp_entity_t *)self)->c_entity;
	entnum = NUM_FOR_EDICT(ent);
	if (entnum < 1 || entnum > MAX_CLIENTS)
        {
        PyErr_SetString(PyExc_TypeError, "WriteDest: not a client");
        return NULL;
        }

	return &svs.clients[entnum-1];
    }


static PyObject * entity_write_angle(PyObject *self, PyObject *args)
    {
    float f;
	client_t *cl;
    
    cl = Write_GetClient(self);
    if (!cl || !PyArg_ParseTuple(args, "f", &f))
        return NULL;

    ClientReliableCheckBlock(cl, 1);
    ClientReliableWrite_Angle(cl, f);

    Py_INCREF(Py_None);
    return Py_None;
    }


static PyObject * entity_write_byte(PyObject *self, PyObject *args)
    {
    int x;
	client_t *cl;
    
    cl = Write_GetClient(self);
    if (!cl || !PyArg_ParseTuple(args, "i", &x))
        return NULL;

    ClientReliableCheckBlock(cl, 1);
    ClientReliableWrite_Byte(cl, x);

    Py_INCREF(Py_None);
    return Py_None;
    }


static PyObject * entity_write_char(PyObject *self, PyObject *args)
    {
    int x;
	client_t *cl;
    
    cl = Write_GetClient(self);
    if (!cl || !PyArg_ParseTuple(args, "i", &x))
        return NULL;

    ClientReliableCheckBlock(cl, 1);
    ClientReliableWrite_Char(cl, x);

    Py_INCREF(Py_None);
    return Py_None;
    }


static PyObject * entity_write_coord(PyObject *self, PyObject *args)
    {
    float f;
	client_t *cl;
    
    cl = Write_GetClient(self);
    if (!cl || !PyArg_ParseTuple(args, "f", &f))
        return NULL;

    ClientReliableCheckBlock(cl, 2);
    ClientReliableWrite_Coord(cl, f);

    Py_INCREF(Py_None);
    return Py_None;
    }


static PyObject * entity_write_entity(PyObject *self, PyObject *args)
    {
    qwp_entity_t *ent;
	client_t *cl;
    
    cl = Write_GetClient(self);
    if (!cl || !PyArg_ParseTuple(args, "O!", &QWP_Entity_Type, &ent))
        return NULL;

    ClientReliableCheckBlock(cl, 2);
    ClientReliableWrite_Short(cl, NUM_FOR_EDICT(((qwp_entity_t *)self)->c_entity));

    Py_INCREF(Py_None);
    return Py_None;
    }


static PyObject * entity_write_long(PyObject *self, PyObject *args)
    {
    int x;
	client_t *cl;
    
    cl = Write_GetClient(self);
    if (!cl || !PyArg_ParseTuple(args, "i", &x))
        return NULL;

    ClientReliableCheckBlock(cl, 4);
    ClientReliableWrite_Long(cl, x);

    Py_INCREF(Py_None);
    return Py_None;
    }


static PyObject * entity_write_short(PyObject *self, PyObject *args)
    {
    int x;
	client_t *cl;
    
    cl = Write_GetClient(self);
    if (!cl || !PyArg_ParseTuple(args, "i", &x))
        return NULL;

    ClientReliableCheckBlock(cl, 2);
    ClientReliableWrite_Short(cl, x);

    Py_INCREF(Py_None);
    return Py_None;
    }


static PyObject * entity_write_string(PyObject *self, PyObject *args)
    {
    char *s;
	client_t *cl;
    
    cl = Write_GetClient(self);
    if (!cl || !PyArg_ParseTuple(args, "s", &s))
        return NULL;

    ClientReliableCheckBlock(cl, strlen(s) + 1);
    ClientReliableWrite_String(cl, s);

    Py_INCREF(Py_None);
    return Py_None;
    }


/************************************/

static PyNumberMethods entity_as_number = 
    {
	0, /*nb_add*/
	0, /*nb_subtract*/
	0, /*nb_multiply*/
	0, /*nb_divide*/
	0, /*nb_remainder*/
	0, /*nb_divmod*/
	0, /*nb_power*/
	0, /*nb_negative*/
	0, /*nb_positive*/
	0, /*nb_absolute*/
	(inquiry)entity_nonzero, /*nb_nonzero*/
    };


static struct PyMethodDef entity_methods[] =
	{
        {"aim", entity_aim, 1},
        {"centerprint", entity_centerprint, 1},
        {"droptofloor", entity_droptofloor, 1},
        {"infokey", entity_infokey, 1},
        {"link", entity_link, 1},
        {"logfrag", entity_logfrag, 1},
        {"makestatic", entity_makestatic, 1},
        {"next_entity", entity_next_entity, 1},
        {"remove", entity_remove, 1},
        {"setmodel", entity_setmodel, 1},
        {"sound", entity_sound, 1},
        {"sprint", entity_sprint, 1},
        {"stuffcmd", entity_stuffcmd, 1},
        {"write_angle", entity_write_angle, 1},
        {"write_byte", entity_write_byte, 1},
        {"write_char", entity_write_char, 1},
        {"write_coord", entity_write_coord, 1},
        {"write_entity", entity_write_entity, 1},
        {"write_long", entity_write_long, 1},
        {"write_short", entity_write_short, 1},
        {"write_string", entity_write_string, 1},
		{NULL, NULL}
	};


static void entity_destruct(qwp_entity_t *self)
    {
    // edict_t *ent = self->c_entity;
    // Sys_Printf("Destructing %d, p_entity=%x c_entity=%x\n", NUM_FOR_EDICT(ent), ent->p_entity, ent->p_entity->c_entity);

    self->c_entity = NULL;
    if (self->dict)
        {
        Py_DECREF(self->dict);
        self->dict = NULL;
        }
    }


PyObject *get_entity(int index)
    {
    edict_t *ent;
    PyObject *result;

    ent = PROG_TO_EDICT(index);
    result = (PyObject *)(ent->p_entity);

    if (!result)
        {
        Sys_Printf("C Entity %d (%d) Missing p_entity %d\n", NUM_FOR_EDICT(ent), ent, ent->p_entity);
        PyErr_SetString(PyExc_TypeError, "C entity missing Python entity!");

        return NULL;
        }

    Py_INCREF(result);
    return result;
    }

PyObject *get_function(PyObject *f)
    {
    if (!f)
        f = Py_None;
    Py_INCREF(f);
    return f;
    }


PyObject *get_py_number(float f)
    {
    if (((int)f) == f)
        return PyInt_FromLong((int)f);
    else
        return PyFloat_FromDouble(f);        
    }

PyObject *get_string(PyObject *s)
    {
    if (!s)
        s = Py_None;

    Py_INCREF(s);
    return s;
    }

static PyObject * entity_getattr(qwp_entity_t *self, char *name)
	{
	PyObject *result = NULL;

    if (!self->c_entity)
        {
        PyErr_SetString(PyExc_TypeError, "Entity has been removed from game");
        return NULL;
        }

    switch (name[0])
        {
        case 'a':
            if (!strcmp(name, "absmax"))
                return create_qwp_vector(self->c_entity->v.absmax);
            if (!strcmp(name, "absmin"))
                return create_qwp_vector(self->c_entity->v.absmin);
            if (!strcmp(name, "aiment"))
                return get_entity(self->c_entity->v.aiment);
            if (!strcmp(name, "ammo_cells"))
                return get_py_number(self->c_entity->v.ammo_cells);
            if (!strcmp(name, "ammo_nails"))
                return get_py_number(self->c_entity->v.ammo_nails);
            if (!strcmp(name, "ammo_rockets"))
                return get_py_number(self->c_entity->v.ammo_rockets);
            if (!strcmp(name, "ammo_shells"))
                return get_py_number(self->c_entity->v.ammo_shells);
            if (!strcmp(name, "angles"))
                return create_qwp_vector(self->c_entity->v.angles);
            if (!strcmp(name, "armortype"))
                return get_py_number(self->c_entity->v.armortype);
            if (!strcmp(name, "armorvalue"))
                return get_py_number(self->c_entity->v.armorvalue);
            if (!strcmp(name, "avelocity"))
                return create_qwp_vector(self->c_entity->v.avelocity);
            break;
        case 'b':
            if (!strcmp(name, "blocked"))
                return get_function(self->c_entity->v.blocked);
            if (!strcmp(name, "button0"))
                return get_py_number(self->c_entity->v.button0);
            if (!strcmp(name, "button1"))
                return get_py_number(self->c_entity->v.button1);
            if (!strcmp(name, "button2"))
                return get_py_number(self->c_entity->v.button2);
            break;
        case 'c':
            // Python will handle "chain"
            if (!strcmp(name, "classname"))
                return get_string(self->c_entity->v.classname);
            if (!strcmp(name, "colormap"))
                return get_py_number(self->c_entity->v.colormap);
            if (!strcmp(name, "currentammo"))
                return get_py_number(self->c_entity->v.currentammo);
            break;
        case 'd':
            if (!strcmp(name, "deadflag"))
                return get_py_number(self->c_entity->v.deadflag);
            if (!strcmp(name, "dmg_inflictor"))
                return get_entity(self->c_entity->v.dmg_inflictor);
            if (!strcmp(name, "dmg_save"))
                return get_py_number(self->c_entity->v.dmg_save);
            if (!strcmp(name, "dmg_take"))
                return get_py_number(self->c_entity->v.dmg_take);
            break;
        case 'e':
            if (!strcmp(name, "effects"))
                return PyInt_FromLong((long)(self->c_entity->v.effects));
            if (!strcmp(name, "enemy"))
                return get_entity(self->c_entity->v.enemy);
            break;
        case 'f':
            if (!strcmp(name, "fixangle"))
                return get_py_number(self->c_entity->v.fixangle);
            if (!strcmp(name, "flags"))
                return PyInt_FromLong((long)(self->c_entity->v.flags));
            if (!strcmp(name, "frags"))
                return get_py_number(self->c_entity->v.frags);
            if (!strcmp(name, "frame"))
                return get_py_number(self->c_entity->v.frame);
            break;
        case 'g':
            if (!strcmp(name, "goalentity"))
                return get_entity(self->c_entity->v.goalentity);
            if (!strcmp(name, "gravity"))
                return get_py_number(self->c_entity->v.gravity);
            if (!strcmp(name, "groundentity"))
                return get_entity(self->c_entity->v.groundentity);
            break;
        case 'h':            
            if (!strcmp(name, "health"))
                return get_py_number(self->c_entity->v.health);
            break;
        case 'i':
            if (!strcmp(name, "ideal_yaw"))
                return get_py_number(self->c_entity->v.ideal_yaw);
            if (!strcmp(name, "items"))
                return PyInt_FromLong((long)(self->c_entity->v.items));
            if (!strcmp(name, "impulse"))
                return get_py_number(self->c_entity->v.impulse);
            break;
        case 'l':
            if (!strcmp(name, "lastruntime"))
                return get_py_number(self->c_entity->v.lastruntime);
            if (!strcmp(name, "ltime"))
                return get_py_number(self->c_entity->v.ltime);
            break;
        case 'm':
            if (!strcmp(name, "max_health"))
                return get_py_number(self->c_entity->v.max_health);
            if (!strcmp(name, "maxs"))
                return create_qwp_vector(self->c_entity->v.maxs);
            if (!strcmp(name, "maxspeed"))
                return get_py_number(self->c_entity->v.maxspeed);
            if (!strcmp(name, "message"))
                return get_string(self->c_entity->v.message);
            if (!strcmp(name, "mins"))
                return create_qwp_vector(self->c_entity->v.mins);
            if (!strcmp(name, "model"))
                return get_string(self->c_entity->v.model);
            if (!strcmp(name, "modelindex"))
                return get_py_number(self->c_entity->v.modelindex);
            if (!strcmp(name, "movedir"))
                return create_qwp_vector(self->c_entity->v.movedir);
            if (!strcmp(name, "movetype"))
                return get_py_number(self->c_entity->v.movetype);
            break;
        case 'n':
            if (!strcmp(name, "netname"))
                return get_string(self->c_entity->v.netname);
            if (!strcmp(name, "nextthink"))
                return get_py_number(self->c_entity->v.nextthink);
            if (!strcmp(name, "noise"))
                return get_string(self->c_entity->v.noise);
            if (!strcmp(name, "noise1"))
                return get_string(self->c_entity->v.noise1);
            if (!strcmp(name, "noise2"))
                return get_string(self->c_entity->v.noise2);
            if (!strcmp(name, "noise3"))
                return get_string(self->c_entity->v.noise3);
            break;
        case 'o':
            if (!strcmp(name, "oldorigin"))
                return create_qwp_vector(self->c_entity->v.oldorigin);
            if (!strcmp(name, "origin"))
                return create_qwp_vector(self->c_entity->v.origin);
            if (!strcmp(name, "owner"))
                return get_entity(self->c_entity->v.owner);
            break;
        case 'q':
            if (!strcmp(name, "qwp_entnum"))
                return PyInt_FromLong(NUM_FOR_EDICT(self->c_entity));
            break;
        case 's':
            if (!strcmp(name, "size"))
                return create_qwp_vector(self->c_entity->v.size);
            if (!strcmp(name, "skin"))
                return get_py_number(self->c_entity->v.skin);
            if (!strcmp(name, "solid"))
                return get_py_number(self->c_entity->v.solid);
            if (!strcmp(name, "sounds"))
                return get_py_number(self->c_entity->v.sounds);
            if (!strcmp(name, "spawnflags"))
                return PyInt_FromLong((long)(self->c_entity->v.spawnflags));
            break;
        case 't':
            if (!strcmp(name, "takedamage"))
                return get_py_number(self->c_entity->v.takedamage);
            if (!strcmp(name, "target"))
                return get_string(self->c_entity->v.target);
            if (!strcmp(name, "targetname"))
                return get_string(self->c_entity->v.targetname);
            if (!strcmp(name, "team"))
                return get_py_number(self->c_entity->v.team);
            if (!strcmp(name, "teleport_time"))
                return get_py_number(self->c_entity->v.teleport_time);
            if (!strcmp(name, "think"))
                return get_function(self->c_entity->v.think);
            if (!strcmp(name, "touch"))
                return get_function(self->c_entity->v.touch);
            break;
        case 'u':
            if (!strcmp(name, "use"))
                return get_function(self->c_entity->v.use);
            break;
        case 'v':
            if (!strcmp(name, "v_angle"))
                return create_qwp_vector(self->c_entity->v.v_angle);
            if (!strcmp(name, "velocity"))
                return create_qwp_vector(self->c_entity->v.velocity);
            if (!strcmp(name, "view_ofs"))
                return create_qwp_vector(self->c_entity->v.view_ofs);
            break;
        case 'w':
            if (!strcmp(name, "waterlevel"))
                return get_py_number(self->c_entity->v.waterlevel);
            if (!strcmp(name, "watertype"))
                return get_py_number(self->c_entity->v.watertype);
            if (!strcmp(name, "weapon"))
                return PyInt_FromLong((long)(self->c_entity->v.weapon));
            if (!strcmp(name, "weaponframe"))
                return get_py_number(self->c_entity->v.weaponframe);
            if (!strcmp(name, "weaponmodel"))
                return get_string(self->c_entity->v.weaponmodel);
            break;
        case 'y':
            if (!strcmp(name, "yaw_speed"))
                return get_py_number(self->c_entity->v.yaw_speed);
            break;
        }


//	if (strcmp(name, "__members__") == 0)
//		return Py_BuildValue("[s,s,s,s]", "frame_handler", "loader", "stdout", "world");

    result = Py_FindMethod(entity_methods, (PyObject *)self, name);
    if (result)
        return result;
    
    PyErr_Clear();
    result = PyDict_GetItemString(self->dict, name);
    if (result)
        Py_INCREF(result);
    else
        PyErr_SetString(PyExc_AttributeError, name);
        //result = PyInt_FromLong(0);
    return result;
	}


int set_entity(int *ip, PyObject *value)
    {
    if (!value)
        {
        PyErr_SetString(PyExc_TypeError, "non-deletable attribute");
        return -1;
        }

    if (value == Py_None)
        {
        (*ip) = 0;
        return 0;
        }

    if (qwp_entity_check(value))
        {
        qwp_entity_t *ent;

        ent = (qwp_entity_t *) value;
        *ip = EDICT_TO_PROG(ent->c_entity);
        return 0;
        }

    return -1;
    }


int set_float(float *fp, PyObject *value)
    {
    float f;

    if (!value)
        {
        PyErr_SetString(PyExc_TypeError, "non-deletable attribute");
        return -1;
        }
    
    f = (float) PyFloat_AsDouble(value);
    if (PyErr_Occurred())
        return -1;

    *fp = f;
    return 0;
    }

int set_function(PyObject **fp, PyObject *value)
    {
    if (!value)
        {
        PyErr_SetString(PyExc_TypeError, "non-deletable attribute");
        return -1;
        }

    if ((value == Py_None) || PyCallable_Check(value))
        {
        Py_XDECREF(*fp);
        Py_INCREF(value);
        *fp = value;
        return 0;
        }

    PyErr_SetString(PyExc_TypeError, "must supply a callable object");
    return -1;
    }


int set_string(PyObject **sp, PyObject *value)
    {
    PyObject *sv;

    if (!value)
        {
        PyErr_SetString(PyExc_TypeError, "non-deletable attribute");
        return -1;
        }

    if ((value == Py_None) || PyString_Check(value))
        {
        Py_XDECREF(*sp);
        Py_INCREF(value);
        (*sp) = value;
        return 0;
        }

    sv = PyObject_Str(value);
    if (sv)
        {
        Py_XDECREF(*sp);
        *sp = sv;
        return 0;
        }

    PyErr_SetString(PyExc_TypeError, "must supply a string, or something convertable to a string");
    return -1;
    }


int set_vector(vec3_t *vp, PyObject *value)
    {
    if (!value)
        {
        PyErr_SetString(PyExc_TypeError, "non-deletable attribute");
        return -1;
        }

    if (qwp_vector_check(value))
        {
        qwp_vector_t *v = (qwp_vector_t *) value;
        (*vp)[0] = v->v[0];
        (*vp)[1] = v->v[1];
        (*vp)[2] = v->v[2];
        return 0;
        }

    PyErr_SetString(PyExc_TypeError, "Must supply a QWPython Vector");
    return -1;
    }


static int entity_setattr(qwp_entity_t *self, char *name, PyObject *value)
	{
    if (!self->c_entity)
        {
        PyErr_SetString(PyExc_TypeError, "Entity has been removed from game");
        return -1;
        }

    switch (name[0])
        {
        case 'a':
            if (!strcmp(name, "absmax"))
                return set_vector(&(self->c_entity->v.absmax), value);
            if (!strcmp(name, "absmin"))
                return set_vector(&(self->c_entity->v.absmin), value);
            if (!strcmp(name, "aiment"))
                return set_entity(&(self->c_entity->v.aiment), value);
            if (!strcmp(name, "ammo_cells"))
                return set_float(&(self->c_entity->v.ammo_cells), value);
            if (!strcmp(name, "ammo_nails"))
                return set_float(&(self->c_entity->v.ammo_nails), value);
            if (!strcmp(name, "ammo_rockets"))
                return set_float(&(self->c_entity->v.ammo_rockets), value);
            if (!strcmp(name, "ammo_shells"))
                return set_float(&(self->c_entity->v.ammo_shells), value);
            if (!strcmp(name, "angles"))
                return set_vector(&(self->c_entity->v.angles), value);
            if (!strcmp(name, "armortype"))
                return set_float(&(self->c_entity->v.armortype), value);
            if (!strcmp(name, "armorvalue"))
                return set_float(&(self->c_entity->v.armorvalue), value);
            if (!strcmp(name, "avelocity"))
                return set_vector(&(self->c_entity->v.avelocity), value);
            break;
        case 'b':
            if (!strcmp(name, "blocked"))
                return set_function(&(self->c_entity->v.blocked), value);
            if (!strcmp(name, "button0"))
                return set_float(&(self->c_entity->v.button0), value);
            if (!strcmp(name, "button1"))
                return set_float(&(self->c_entity->v.button1), value);
            if (!strcmp(name, "button2"))
                return set_float(&(self->c_entity->v.button2), value);
            break;
        case 'c':
            // Python will handle "chain"
            if (!strcmp(name, "classname"))
                return set_string(&(self->c_entity->v.classname), value);
            if (!strcmp(name, "colormap"))
                return set_float(&(self->c_entity->v.colormap), value);
            if (!strcmp(name, "currentammo"))
                return set_float(&(self->c_entity->v.currentammo), value);
            break;
        case 'd':
            if (!strcmp(name, "deadflag"))
                return set_float(&(self->c_entity->v.deadflag), value);
            if (!strcmp(name, "dmg_inflictor"))
                return set_entity(&(self->c_entity->v.dmg_inflictor), value);
            if (!strcmp(name, "dmg_save"))
                return set_float(&(self->c_entity->v.dmg_save), value);
            if (!strcmp(name, "dmg_take"))
                return set_float(&(self->c_entity->v.dmg_take), value);
            break;
        case 'e':
            if (!strcmp(name, "effects"))
                return set_float(&(self->c_entity->v.effects), value);
            if (!strcmp(name, "enemy"))
                return set_entity(&(self->c_entity->v.enemy), value);
            break;
        case 'f':
            if (!strcmp(name, "fixangle"))
                return set_float(&(self->c_entity->v.fixangle), value);
            if (!strcmp(name, "flags"))
                return set_float(&(self->c_entity->v.flags), value);
            if (!strcmp(name, "frags"))
                return set_float(&(self->c_entity->v.frags), value);
            if (!strcmp(name, "frame"))
                return set_float(&(self->c_entity->v.frame), value);
            break;
        case 'g':
            if (!strcmp(name, "goalentity"))
                return set_entity(&(self->c_entity->v.goalentity), value);
            if (!strcmp(name, "gravity"))
                return set_float(&(self->c_entity->v.gravity), value);
            if (!strcmp(name, "groundentity"))
                return set_entity(&(self->c_entity->v.groundentity), value);
            break;
        case 'h':            
            if (!strcmp(name, "health"))
                return set_float(&(self->c_entity->v.health), value);
            break;
        case 'i':
            if (!strcmp(name, "ideal_yaw"))
                return set_float(&(self->c_entity->v.ideal_yaw), value);
            if (!strcmp(name, "items"))
                return set_float(&(self->c_entity->v.items), value);
            if (!strcmp(name, "impulse"))
                return set_float(&(self->c_entity->v.impulse), value);
            break;
        case 'l':
            if (!strcmp(name, "lastruntime"))
                return set_float(&(self->c_entity->v.lastruntime), value);
            if (!strcmp(name, "ltime"))
                return set_float(&(self->c_entity->v.ltime), value);
            break;
        case 'm':
            if (!strcmp(name, "max_health"))
                return set_float(&(self->c_entity->v.max_health), value);
            if (!strcmp(name, "maxs"))
                return set_vector(&(self->c_entity->v.maxs), value);
            if (!strcmp(name, "maxspeed"))
                return set_float(&(self->c_entity->v.maxspeed), value);
            if (!strcmp(name, "message"))
                return set_string(&(self->c_entity->v.message), value);
            if (!strcmp(name, "mins"))
                return set_vector(&(self->c_entity->v.mins), value);
            if (!strcmp(name, "model"))
                return set_string(&(self->c_entity->v.model), value);
            if (!strcmp(name, "modelindex"))
                return set_float(&(self->c_entity->v.modelindex), value);
            if (!strcmp(name, "movedir"))
                return set_vector(&(self->c_entity->v.movedir), value);
            if (!strcmp(name, "movetype"))
                return set_float(&(self->c_entity->v.movetype), value);
            break;
        case 'n':
            if (!strcmp(name, "netname"))
                return set_string(&(self->c_entity->v.netname), value);
            if (!strcmp(name, "nextthink"))
                return set_float(&(self->c_entity->v.nextthink), value);
            if (!strcmp(name, "noise"))
                return set_string(&(self->c_entity->v.noise), value);
            if (!strcmp(name, "noise1"))
                return set_string(&(self->c_entity->v.noise1), value);
            if (!strcmp(name, "noise2"))
                return set_string(&(self->c_entity->v.noise2), value);
            if (!strcmp(name, "noise3"))
                return set_string(&(self->c_entity->v.noise3), value);
            break;
        case 'o':
            if (!strcmp(name, "oldorigin"))
                return set_vector(&(self->c_entity->v.oldorigin), value);
            if (!strcmp(name, "origin"))
                return set_vector(&(self->c_entity->v.origin), value);
            if (!strcmp(name, "owner"))
                return set_entity(&(self->c_entity->v.owner), value);
            break;
        case 's':
            if (!strcmp(name, "size"))
                return set_vector(&(self->c_entity->v.size), value);
            if (!strcmp(name, "skin"))
                return set_float(&(self->c_entity->v.skin), value);
            if (!strcmp(name, "solid"))
                return set_float(&(self->c_entity->v.solid), value);
            if (!strcmp(name, "sounds"))
                return set_float(&(self->c_entity->v.sounds), value);
            if (!strcmp(name, "spawnflags"))
                return set_float(&(self->c_entity->v.spawnflags), value);
            break;
        case 't':
            if (!strcmp(name, "takedamage"))
                return set_float(&(self->c_entity->v.takedamage), value);
            if (!strcmp(name, "target"))
                return set_string(&(self->c_entity->v.target), value);
            if (!strcmp(name, "targetname"))
                return set_string(&(self->c_entity->v.targetname), value);
            if (!strcmp(name, "team"))
                return set_float(&(self->c_entity->v.team), value);
            if (!strcmp(name, "teleport_time"))
                return set_float(&(self->c_entity->v.teleport_time), value);
            if (!strcmp(name, "think"))
                return set_function(&(self->c_entity->v.think), value);
            if (!strcmp(name, "touch"))
                return set_function(&(self->c_entity->v.touch), value);
            break;
        case 'u':
            if (!strcmp(name, "use"))
                return set_function(&(self->c_entity->v.use), value);
            break;
        case 'v':
            if (!strcmp(name, "v_angle"))
                return set_vector(&(self->c_entity->v.v_angle), value);
            if (!strcmp(name, "velocity"))
                return set_vector(&(self->c_entity->v.velocity), value);
            if (!strcmp(name, "view_ofs"))
                return set_vector(&(self->c_entity->v.view_ofs), value);
            break;
        case 'w':
            if (!strcmp(name, "waterlevel"))
                return set_float(&(self->c_entity->v.waterlevel), value);
            if (!strcmp(name, "watertype"))
                return set_float(&(self->c_entity->v.watertype), value);
            if (!strcmp(name, "weapon"))
                return set_float(&(self->c_entity->v.weapon), value);
            if (!strcmp(name, "weaponframe"))
                return set_float(&(self->c_entity->v.weaponframe), value);
            if (!strcmp(name, "weaponmodel"))
                return set_string(&(self->c_entity->v.weaponmodel), value);
            break;
        case 'y':
            if (!strcmp(name, "yaw_speed"))
                return set_float(&(self->c_entity->v.yaw_speed), value);
            break;
        }

    if (value)
        return PyDict_SetItemString(self->dict, name, value);

    // no value, must be trying to delete
    if (PyDict_DelItemString(self->dict, name) < 0)
        {
        PyErr_SetString(PyExc_AttributeError, "delete non-existing attribute");
        return -1;
        }

	return 0;
	}




PyTypeObject QWP_Entity_Type = 
	{
	PyObject_HEAD_INIT(NULL) // work around MSVC problem, use NULL here, set in the initqw() function
							 // otherwise you get an "initializer not constant" error
	0,			                    /*ob_size*/
	"QWPython Entity",		        /*tp_name*/
	sizeof(qwp_entity_t),	        /*tp_size*/
	0,			                    /*tp_itemsize*/
	(destructor)entity_destruct,    /*tp_dealloc*/
    0,                              /*tp_print*/
	(getattrfunc)entity_getattr,    /*tp_getattr*/
	(setattrfunc)entity_setattr,    /*tp_setattr*/
	0,			                    /*tp_compare*/
	0,                              /*tp_repr*/
    &entity_as_number,
	};


void init_qwp_entity_type(void)
    {
	QWP_Entity_Type.ob_type = &PyType_Type;  // Fix for MSVC problem
    }


/*
 * Create a Python entity that corresponds to a given C edict_t
 */
PyObject * create_qwp_entity(struct edict_s *ent)
    {
    qwp_entity_t * result;

	result = PyObject_NEW(qwp_entity_t, &QWP_Entity_Type);
    result->c_entity = ent;
    result->dict = PyDict_New();

    if (ent)
        {
        // the only time ent should be NULL is when we're creating
        // the world entity, which occurs before the C edict_t's
        // are available.  The SpawnServer() code will be responsible
        // for attaching the Python world entity to the C world edict_t
        if (ent->p_entity)
            {
            ent->p_entity->c_entity = NULL;
            Py_DECREF(ent->p_entity);
            }

        ent->p_entity = result;
        }

    return (PyObject *) result;
    }


/*
 * Called before a level starts, to clear out Python entities
 * from the previous level
 */
void qwp_entity_clearall(void)
    {
    int i;

    if (!sv.edicts)
        return;

    if (sv.edicts->p_entity->dict)
        PyDict_Clear(sv.edicts->p_entity->dict);
    else
        sv.edicts->p_entity->dict = PyDict_New();

    for (i = 1; i < MAX_EDICTS; i++)
        {
        ED_ClearEdict(sv.edicts + i);
        if (sv.edicts[i].p_entity)
            {
            sv.edicts[i].p_entity->c_entity = NULL;
            Py_DECREF(sv.edicts[i].p_entity->dict);
            sv.edicts[i].p_entity->dict = NULL;
            Py_DECREF(sv.edicts[i].p_entity);
            sv.edicts[i].p_entity = NULL;
            }
        }
    }