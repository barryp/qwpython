/*
Copyright (C) 1996-1997 Id Software, Inc.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  

See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

*/
// sv_edict.c -- entity dictionary

#include "qwsvdef.h"
globalvars_t	*pr_global_struct;
globalfuncs_t   *pr_func_struct;

PyObject * SpectatorConnect;
PyObject * SpectatorThink;
PyObject * SpectatorDisconnect;


/*
=================
ED_ClearEdict

Sets everything to NULL, and create a new Python Entity if 
necessary, or clear the dict of an existing one.
=================
*/
void ED_ClearEdict (edict_t *e)
    {
    // free references to Python objects
    Py_XDECREF(e->v.blocked);
    Py_XDECREF(e->v.classname);
    Py_XDECREF(e->v.message);
    Py_XDECREF(e->v.model);
    Py_XDECREF(e->v.netname);
    Py_XDECREF(e->v.noise);
    Py_XDECREF(e->v.noise1);
    Py_XDECREF(e->v.noise2);
    Py_XDECREF(e->v.noise3);
    Py_XDECREF(e->v.target);
    Py_XDECREF(e->v.targetname);
    Py_XDECREF(e->v.think);
    Py_XDECREF(e->v.touch);
    Py_XDECREF(e->v.use);
    Py_XDECREF(e->v.weaponmodel);

	memset (&e->v, 0, sizeof(e->v));

    if (e->p_entity)
        PyDict_Clear(e->p_entity->dict);
    else
        create_qwp_entity(e);

	e->free = false;
    }

/*
=================
ED_Alloc

Either finds a free edict, or allocates a new one.
Try to avoid reusing an entity that was recently freed, because it
can cause the client to think the entity morphed into something else
instead of being removed and recreated, which can cause interpolated
angles and bad trails.
=================
*/
edict_t *ED_Alloc (void)
{
	int			i;
	edict_t		*e;

	for ( i=MAX_CLIENTS+1 ; i<sv.num_edicts ; i++)
	{
		e = EDICT_NUM(i);
		// the first couple seconds of server time can involve a lot of
		// freeing and allocating, so relax the replacement policy
		if (e->free && ( e->freetime < 2 || sv.time - e->freetime > 0.5 ) )
		{
			ED_ClearEdict (e);
			return e;
		}
	}
	
	if (i == MAX_EDICTS)
	{
		Con_Printf ("WARNING: ED_Alloc: no free edicts\n");
		i--;	// step on whatever is the last edict
		e = EDICT_NUM(i);
		//SV_UnlinkEdict(e);
        ED_Free(e);  // free instead of just unlink - to dispose of Python Entities
	}
	else
		sv.num_edicts++;
	e = EDICT_NUM(i);
	ED_ClearEdict (e);

	return e;
}

/*
=================
ED_Free

Marks the edict as free
FIXME: walk all entities and NULL out references to this entity
=================
*/
void ED_Free (edict_t *ed)
{
	SV_UnlinkEdict (ed);		// unlink from world bsp

	ed->free = true;
	Py_XDECREF(ed->v.model); ed->v.model = 0;
	ed->v.takedamage = 0;
	ed->v.modelindex = 0;
	ed->v.colormap = 0;
	ed->v.skin = 0;
	ed->v.frame = 0;
	VectorCopy (vec3_origin, ed->v.origin);
	VectorCopy (vec3_origin, ed->v.angles);
	ed->v.nextthink = -1;
	ed->v.solid = 0;
	
	ed->freetime = sv.time;
}

//===========================================================================

/*
=============
ED_Count

For debugging
=============
*/
void ED_Count (void)
{
	int		i;
	edict_t	*ent;
	int		active, models, solid, step;

	active = models = solid = step = 0;
	for (i=0 ; i<sv.num_edicts ; i++)
	{
		ent = EDICT_NUM(i);
		if (ent->free)
			continue;
		active++;
		if (ent->v.solid)
			solid++;
		if (ent->v.model)
			models++;
		if (ent->v.movetype == MOVETYPE_STEP)
			step++;
	}

	Con_Printf ("num_edicts:%3i\n", sv.num_edicts);
	Con_Printf ("active    :%3i\n", active);
	Con_Printf ("view      :%3i\n", models);
	Con_Printf ("touch     :%3i\n", solid);
	Con_Printf ("step      :%3i\n", step);

}

/*
===============
PR_Init
===============
*/
void PR_Init (void)
{
	Cmd_AddCommand ("edictcount", ED_Count);
}



edict_t *EDICT_NUM(int n)
    {
	if (n < 0 || n >= MAX_EDICTS)
		SV_Error ("EDICT_NUM: bad number %i", n);

	return sv.edicts + n;
    }


int NUM_FOR_EDICT(edict_t *e)
    {
	int		b;

    b = e - sv.edicts;
	
	if (b < 0 || b >= sv.num_edicts)
		SV_Error ("NUM_FOR_EDICT: bad pointer");
	return b;
    }


