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

#include "Python.h"

typedef struct
    {	
    int	    self;
	int	    other;
	int	    world;
	float	time;
	float	frametime;
	int	    newmis;
	float	force_retouch;
	float	serverflags;
	float	total_secrets;
	float	total_monsters;
	float	found_secrets;
	float	killed_monsters;
	float	parm1;
	float	parm2;
	float	parm3;
	float	parm4;
	float	parm5;
	float	parm6;
	float	parm7;
	float	parm8;
	float	parm9;
	float	parm10;
	float	parm11;
	float	parm12;
	float	parm13;
	float	parm14;
	float	parm15;
	float	parm16;
	vec3_t	v_forward;
	vec3_t	v_up;
	vec3_t	v_right;
	float	trace_allsolid;
	float	trace_startsolid;
	float	trace_fraction;
	vec3_t	trace_endpos;
	vec3_t	trace_plane_normal;
	float	trace_plane_dist;
	int	    trace_ent;
	float	trace_inopen;
	float	trace_inwater;
	int	    msg_entity;

	PyObject *  mapname;
    } globalvars_t;


typedef struct
    {
	PyObject *	main;
	PyObject *	StartFrame;
	PyObject *	PlayerPreThink;
	PyObject *	PlayerPostThink;
	PyObject *	ClientKill;
	PyObject *	ClientConnect;
	PyObject *	PutClientInServer;
	PyObject *	ClientDisconnect;
	PyObject *	SetNewParms;
	PyObject *	SetChangeParms;
    } globalfuncs_t;
    

/* 
 Any changes to the PyObject *'s in this structure should
 be reflected in ED_ClearEdict
*/
typedef struct
    {
    vec3_t       absmax;
    vec3_t       absmin;
    int          aiment;
    float        ammo_cells;
    float        ammo_nails;
    float        ammo_rockets;
    float        ammo_shells;
    vec3_t       angles;
    float        armortype;
    float        armorvalue;
    vec3_t       avelocity;
    PyObject     *blocked;
    float        button0;
    float        button1;
    float        button2;
    int          chain;
    PyObject     *classname;
    float        colormap;
    float        currentammo;
    float        deadflag;
    int          dmg_inflictor;
    float        dmg_save;
    float        dmg_take;
    float        effects;
    int          enemy;
    float        fixangle;
    float        flags;
    float        frags;
    float        frame;
    int          goalentity;
	float		 gravity;
    int          groundentity;
    float        health;
    float        ideal_yaw;
    float        impulse;
    float        items;
    float        lastruntime;
    float        ltime;
    float        max_health;
    vec3_t       maxs;
	float		 maxspeed;
    PyObject     *message;
    vec3_t       mins;
    PyObject     *model;
    float        modelindex;
    vec3_t       movedir;
    float        movetype;
    PyObject     *netname;
    float        nextthink;
    PyObject     *noise;
    PyObject     *noise1;
    PyObject     *noise2;
    PyObject     *noise3;
    vec3_t       oldorigin;
    vec3_t       origin;
    int          owner;
    vec3_t       size;
    float        skin;
    float        solid;
    float        sounds;
    float        spawnflags;
    float        takedamage;
    PyObject     *target;
    PyObject     *targetname;
    float        team;
    float        teleport_time;
    PyObject     *think;
    PyObject     *touch;
    PyObject     *use;
    vec3_t       v_angle;
    vec3_t       velocity;
    vec3_t       view_ofs;
    float        waterlevel;
    float        watertype;
    float        weapon;
    float        weaponframe;
    PyObject     *weaponmodel;
    float        yaw_speed;
    } entvars_t;

/*
typedef struct
{
	float	modelindex;
	vec3_t	absmin;
	vec3_t	absmax;
	float	ltime;
	float	lastruntime;
	float	movetype;
	float	solid;
	vec3_t	origin;
	vec3_t	oldorigin;
	vec3_t	velocity;
	vec3_t	angles;
	vec3_t	avelocity;
	PyObject *classname;
	PyObject *model;
	float	frame;
	float	skin;
	float	effects;
	vec3_t	mins;
	vec3_t	maxs;
	vec3_t	size;
	PyObject *	touch;
	PyObject *	use;
	PyObject *	think;
	PyObject *	blocked;
	float	nextthink;
	int	groundentity;
	float	health;
	float	frags;
	float	weapon;
	PyObject *weaponmodel;
	float	weaponframe;
	float	currentammo;
	float	ammo_shells;
	float	ammo_nails;
	float	ammo_rockets;
	float	ammo_cells;
	float	items;
	float	takedamage;
	int	chain;
	float	deadflag;
	vec3_t	view_ofs;
	float	button0;
	float	button1;
	float	button2;
	float	impulse;
	float	fixangle;
	vec3_t	v_angle;
	PyObject *netname;
	int	enemy;
	float	flags;
	float	colormap;
	float	team;
	float	max_health;
	float	teleport_time;
	float	armortype;
	float	armorvalue;
	float	waterlevel;
	float	watertype;
	float	ideal_yaw;
	float	yaw_speed;
	int	aiment;
	int	goalentity;
	float	spawnflags;
	PyObject *target;
	PyObject *targetname;
	float	dmg_take;
	float	dmg_save;
	int	dmg_inflictor;
	int	owner;
	vec3_t	movedir;
	PyObject *message;
	float	sounds;
	PyObject *noise;
	PyObject *noise1;
	PyObject *noise2;
	PyObject *noise3;
} entvars_t;
*/
#define PROGHEADER_CRC 54730
