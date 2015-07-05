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

/* 
Identify the engine - change the name if the API changes
enough to break backwards compatibility.  Otherwise just
bump the revision by 1 (unless the changes are so trivial
that they don't affect the Python code at all)
*/
#define ENGINE_NAME "qwpython v1"
#define ENGINE_REVISION 1

#include <sys/types.h>
#include <sys/timeb.h>
#ifdef _WIN32
    #include <winsock.h>
    #include <conio.h>
    #include <direct.h>
#else
	#include <sys/stat.h>
#endif    
#include <stdio.h> // for debugging resource loader only

#include "qwsvdef.h"
cvar_t	sys_nostdout = {"sys_nostdout","0"};
int engine_run = 1;
char error_text[2048] = "";

qwp_engine_t *qwp_engine;
static PyObject *module_dict;


/*
================
Sys_mkdir
================
*/
void Sys_mkdir (char *path)
{
#ifdef _WIN32
	_mkdir(path);
#else
	if (mkdir (path, 0777) != -1)
		return;
	if (errno != EEXIST)
		Sys_Error ("mkdir %s: %s",path, strerror(errno)); 
#endif
}


/*
================
Sys_Error
================
*/
void Sys_Error(char *error, ...)
	{
	va_list		argptr;

	va_start (argptr, error);
	vsprintf (error_text, error, argptr);
	va_end (argptr);

	printf("Sys_Error: %s\n", error_text);
	engine_run = 0;
	}


/*
================
Sys_DoubleTime
================
*/
double Sys_DoubleTime (void)
{
#ifdef _WIN32    
	double t;
    struct _timeb tstruct;
	static int	starttime;

	_ftime( &tstruct );
 
	if (!starttime)
		starttime = tstruct.time;
	t = (tstruct.time-starttime) + tstruct.millitm*0.001;
	
	return t;
#else	
	struct timeval tp;
	struct timezone tzp;
	static int		secbase;

	gettimeofday(&tp, &tzp);
	
	if (!secbase)
	{
		secbase = tp.tv_sec;
		return tp.tv_usec/1000000.0;
	}
	
	return (tp.tv_sec - secbase) + tp.tv_usec/1000000.0;	
#endif	
}


/*
================
Sys_ConsoleInput
================
*/
char *Sys_ConsoleInput(void)
	{
		return NULL;
	}
	

/*
================
Sys_Printf
================
*/
void Sys_Printf (char *fmt, ...)
	{
	PyObject *result;
	char		text[1024];
	va_list		argptr;
		
	va_start (argptr, fmt);
	vsprintf (text, fmt, argptr);
	va_end (argptr);

	result = PyObject_CallMethod(qwp_engine->out, "write", "s", text);
	if (!result)
		PyErr_Clear();
	else
		Py_DECREF(result);

	result = PyObject_CallMethod(qwp_engine->out, "flush", NULL);
	if (!result)
		PyErr_Clear();
	else
		Py_DECREF(result);
	}


/*
================
Sys_Quit
================
*/
void Sys_Quit (void)
{
//	exit (0);
	engine_run = 0;
}


/*
=============
Sys_Init

Quake calls this so the system can register variables before host_hunklevel
is marked
=============
*/
void Sys_Init (void)
{
	Cvar_RegisterVariable (&sys_nostdout);
}


/*
==================
main

==================
*/
char	*newargv[256];
quakeparms_t	parms;

static void engine_init(void)
	{
	int				t;

	parms.argc = com_argc;
	parms.argv = com_argv;

	parms.memsize = 16*1024*1024;

	if ((t = COM_CheckParm("-heapsize")) != 0 &&
		t + 1 < com_argc)
		parms.memsize = Q_atoi(com_argv[t + 1]) * 1024;

	if ((t = COM_CheckParm("-mem")) != 0 &&
		t + 1 < com_argc)
		parms.memsize = Q_atoi(com_argv[t + 1]) * 1024 * 1024;

	parms.membase = malloc(parms.memsize);

	if (!parms.membase)
		Sys_Error("Insufficient memory.\n");

	parms.basedir = ".";
	parms.cachedir = NULL;
    SV_Init(&parms);
    }


static PyObject * qw_run(PyObject *self, PyObject *args)
    {
	double			newtime, time, oldtime;
//	static	char	cwd[1024];
	struct timeval	timeout;
	fd_set			fdset;
//	int				t;

	SV_Init2();

// run one frame immediately for first heartbeat
	SV_Frame (0.1);		

//
// main loop
//
	oldtime = Sys_DoubleTime () - 0.1;
	while (engine_run)
		{
        PyObject *result;
        int rc;
		// select on the net socket and stdin
		// the only reason we have a timeout at all is so that if the last
		// connected client times out, the message would not otherwise
		// be printed until the next event.
		FD_ZERO(&fdset);
		FD_SET(net_socket, &fdset);
		
		// not sure why the Win32 and Unix versions of QWSV had
		// different timeouts, but I'll go along with what they had
		#ifdef _WIN32
		timeout.tv_sec = 0;
		timeout.tv_usec = 100;
		#else
		timeout.tv_sec = 1;
		timeout.tv_usec = 0;
		#endif

        Py_BEGIN_ALLOW_THREADS
		rc = select (net_socket+1, &fdset, NULL, NULL, &timeout);
        Py_END_ALLOW_THREADS
        if (rc == -1)
			continue;

    	// find time passed since last cycle
		newtime = Sys_DoubleTime ();
		time = newtime - oldtime;
		oldtime = newtime;
	
        // give Python a chance
        if (PyCallable_Check(qwp_engine->frame_handler))
            {
            result = PyObject_CallObject(qwp_engine->frame_handler, NULL);
            if (result)
                Py_DECREF(result);
            else
        		PyErr_Print();
            }

        SV_Frame (time);				
		}	

	SV_Shutdown();
	free(parms.membase);


	if (error_text[0])
		{
		PyErr_SetString(PyExc_RuntimeError, error_text);
		return NULL;
		}
	else
		{
		Py_INCREF(Py_None);
		return Py_None;
		}
	}



static PyObject * qw_stop(PyObject *self, PyObject *args)
	{
	engine_run = 0;
	Py_INCREF(Py_None);
	return Py_None;
	}


unsigned short COM_CRC_File(char *path)
    {
    PyObject *contents;
	unsigned short crc;
	byte *buf;
	Py_ssize_t len;

	contents = PyObject_CallMethod(qwp_engine->loader, "read", "s", path);
	if (!contents)
		{
		PyErr_Clear();
		return 0;
		}

	PyString_AsStringAndSize(contents, (char **) &buf, &len);
	crc = CRC_Block(buf, len);

    Py_DECREF(contents);
	return crc;
    }


/*
 Find out if a named resource exists
 */
int Sys_ResourceExists(char *path)
	{
	PyObject *result;
	int rval = 0;

	result = PyObject_CallMethod(qwp_engine->loader, "has_key", "s", path);
	if (!result)
		{
		PyErr_Clear();
		return 0;
		}
	
	rval = PyObject_IsTrue(result);
	Py_DECREF(result);
	return rval;
	}


/*
 Read a named resource, return as a Python string
 return NULL if not found
 */
PyObject * Sys_ReadResource(const char *path)
	{
	PyObject *result;

	result = PyObject_CallMethod(qwp_engine->loader, "read", "s", path);
	if (result)
		return result;
	else
		{
		PyErr_Clear();
		return NULL;
		}
	}


/*
============
COM_LoadFile

Filename are relative to the quake directory.
Always appends a 0 byte to the loaded data.
============
*/
byte	*loadbuf;
int		loadsize;

byte *COM_LoadFile (char *path, int usehunk)
	{
	PyObject *result;
	char *p;
	Py_ssize_t len;
	byte *buf;
	char base[32];

	result = Sys_ReadResource(path);
	if (!result)
		return NULL;

	PyString_AsStringAndSize(result, &p, &len);

	// extract the filename base name for hunk tag
	COM_FileBase (path, base);
	
	if (usehunk == 1)
		buf = Hunk_AllocName (len+1, base);
	else if (usehunk == 0)
		buf = Z_Malloc (len+1);
	else if (usehunk == 4)
		{
		if (len+1 > loadsize)
			buf = Hunk_TempAlloc (len+1);
		else
			buf = loadbuf;
		}
	else
		{
		Sys_Error("COM_LoadFile: bad usehunk");
		buf = NULL;
		}

	if (!buf)
		Sys_Error("COM_LoadFile: not enough space for %s", path);
	else
		{
		memcpy(buf, p, len);
		buf[len] = 0;
		}

	Py_DECREF(result);
	return buf;
	}


byte *COM_LoadHunkFile (char *path)
{
	return COM_LoadFile (path, 1);
}


// uses temp hunk if larger than bufsize
byte *COM_LoadStackFile (char *path, void *buffer, int bufsize)
{
	byte	*buf;
	
	loadbuf = (byte *)buffer;
	loadsize = bufsize;
	buf = COM_LoadFile (path, 4);
	
	return buf;
}


/******** QC Globals *********/


static PyObject * get_qc_global(PyObject *self, PyObject *args)
    {
    char *name;

    if (!PyArg_ParseTuple(args, "s", &name))
        return NULL;

    switch (name[0])
        {
        case 'c':
            if (!strcmp(name, "client_connect"))
                return get_function(pr_func_struct->ClientConnect);
            if (!strcmp(name, "client_disconnect"))
                return get_function(pr_func_struct->ClientDisconnect);
            if (!strcmp(name, "client_kill"))
                return get_function(pr_func_struct->ClientKill);
            break;
        case 'f':
            if (!strcmp(name, "force_retouch"))
                return get_py_number(pr_global_struct->force_retouch);
            if (!strcmp(name, "found_secrets"))
                return get_py_number(pr_global_struct->found_secrets);
            if (!strcmp(name, "frametime"))
                return get_py_number(pr_global_struct->frametime);
            break;
        case 'k':
            if (!strcmp(name, "killed_monsters"))
                return get_py_number(pr_global_struct->killed_monsters);
            break;
        case 'm':
            if (!strcmp(name, "mapname"))
                return get_string(pr_global_struct->mapname);
            if (!strcmp(name, "msg_entity"))
                return get_entity(pr_global_struct->msg_entity);
            break;
        case 'n':
            if (!strcmp(name, "newmis"))
                return get_entity(pr_global_struct->newmis);
            break;
        case 'o':
            if (!strcmp(name, "other"))
                return get_entity(pr_global_struct->other);
            break;
        case 'p':
            if (!strcmp(name, "parm1"))
                return get_py_number(pr_global_struct->parm1);
            if (!strcmp(name, "parm2"))
                return get_py_number(pr_global_struct->parm2);
            if (!strcmp(name, "parm3"))
                return get_py_number(pr_global_struct->parm3);
            if (!strcmp(name, "parm4"))
                return get_py_number(pr_global_struct->parm4);
            if (!strcmp(name, "parm5"))
                return get_py_number(pr_global_struct->parm5);
            if (!strcmp(name, "parm6"))
                return get_py_number(pr_global_struct->parm6);
            if (!strcmp(name, "parm7"))
                return get_py_number(pr_global_struct->parm7);
            if (!strcmp(name, "parm8"))
                return get_py_number(pr_global_struct->parm8);
            if (!strcmp(name, "parm9"))
                return get_py_number(pr_global_struct->parm9);
            if (!strcmp(name, "parm10"))
                return get_py_number(pr_global_struct->parm10);
            if (!strcmp(name, "parm11"))
                return get_py_number(pr_global_struct->parm11);
            if (!strcmp(name, "parm12"))
                return get_py_number(pr_global_struct->parm12);
            if (!strcmp(name, "parm13"))
                return get_py_number(pr_global_struct->parm13);
            if (!strcmp(name, "parm14"))
                return get_py_number(pr_global_struct->parm14);
            if (!strcmp(name, "parm15"))
                return get_py_number(pr_global_struct->parm15);
            if (!strcmp(name, "parm16"))
                return get_py_number(pr_global_struct->parm16);
            if (!strcmp(name, "player_postthink"))
                return get_function(pr_func_struct->PlayerPostThink);
            if (!strcmp(name, "player_prethink"))
                return get_function(pr_func_struct->PlayerPreThink);
            if (!strcmp(name, "put_client_in_server"))
                return get_function(pr_func_struct->PutClientInServer);
            break;
        case 's':
            if (!strcmp(name, "self"))
                return get_entity(pr_global_struct->self);
            if (!strcmp(name, "serverflags"))
                return PyInt_FromLong((long)(pr_global_struct->serverflags));
            if (!strcmp(name, "set_change_parms"))
                return get_function(pr_func_struct->SetChangeParms);
            if (!strcmp(name, "set_new_parms"))
                return get_function(pr_func_struct->SetNewParms);
            if (!strcmp(name, "start_frame"))
                return get_function(pr_func_struct->StartFrame);
            break;
        case 't':
            if (!strcmp(name, "time"))
                return get_py_number(pr_global_struct->time);
            if (!strcmp(name, "total_monsters"))
                return get_py_number(pr_global_struct->total_monsters);
            if (!strcmp(name, "total_secrets"))
                return get_py_number(pr_global_struct->total_secrets);
            if (!strcmp(name, "trace_allsolid"))
                return get_py_number(pr_global_struct->trace_allsolid);
            if (!strcmp(name, "trace_endpos"))
                return create_qwp_vector(pr_global_struct->trace_endpos);
            if (!strcmp(name, "trace_ent"))
                return get_entity(pr_global_struct->trace_ent);
            if (!strcmp(name, "trace_fraction"))
                return get_py_number(pr_global_struct->trace_fraction);
            if (!strcmp(name, "trace_inopen"))
                return get_py_number(pr_global_struct->trace_inopen);
            if (!strcmp(name, "trace_inwater"))
                return get_py_number(pr_global_struct->trace_inwater);
            if (!strcmp(name, "trace_plane_dist"))
                return get_py_number(pr_global_struct->trace_plane_dist);
            if (!strcmp(name, "trace_plane_normal"))
                return create_qwp_vector(pr_global_struct->trace_plane_normal);
            if (!strcmp(name, "trace_startsolid"))
                return get_py_number(pr_global_struct->trace_startsolid);
            break;
        case 'v':
            if (!strcmp(name, "v_forward"))
                return create_qwp_vector(pr_global_struct->v_forward);
            if (!strcmp(name, "v_right"))
                return create_qwp_vector(pr_global_struct->v_right);
            if (!strcmp(name, "v_up"))
                return create_qwp_vector(pr_global_struct->v_up);
            break;
        case 'w':
            if (!strcmp(name, "world"))
                return get_entity(pr_global_struct->world);
            break;
		default:
			break;
        }

    PyErr_Format(PyExc_AttributeError, "attribute: %s not found", name);
    return NULL;
    }


int set_qc_global0(char *name, PyObject *value)
    {
    switch (name[0])
        {
        case 'c':
            if (!strcmp(name, "client_connect"))
                return set_function(&(pr_func_struct->ClientConnect), value);
            if (!strcmp(name, "client_disconnect"))
                return set_function(&(pr_func_struct->ClientDisconnect), value);
            if (!strcmp(name, "client_kill"))
                return set_function(&(pr_func_struct->ClientKill), value);
            break;
        case 'f':
            if (!strcmp(name, "force_retouch"))
                return set_float(&(pr_global_struct->force_retouch), value);
            if (!strcmp(name, "found_secrets"))
                return set_float(&(pr_global_struct->found_secrets), value);
            if (!strcmp(name, "frametime"))
                return set_float(&(pr_global_struct->frametime), value);
            break;
        case 'k':
            if (!strcmp(name, "killed_monsters"))
                return set_float(&(pr_global_struct->killed_monsters), value);
            break;
        case 'm':
            if (!strcmp(name, "mapname"))
                return set_string(&(pr_global_struct->mapname), value);
            if (!strcmp(name, "msg_entity"))
                return set_entity(&(pr_global_struct->msg_entity), value);
            break;
        case 'n':
            if (!strcmp(name, "newmis"))
                return set_entity(&(pr_global_struct->newmis), value);
            break;
        case 'o':
            if (!strcmp(name, "other"))
                return set_entity(&(pr_global_struct->other), value);            
            break;
        case 'p':
            if (!strcmp(name, "parm1"))
                return set_float(&(pr_global_struct->parm1), value);
            if (!strcmp(name, "parm2"))
                return set_float(&(pr_global_struct->parm2), value);
            if (!strcmp(name, "parm3"))
                return set_float(&(pr_global_struct->parm3), value);
            if (!strcmp(name, "parm4"))
                return set_float(&(pr_global_struct->parm4), value);
            if (!strcmp(name, "parm5"))
                return set_float(&(pr_global_struct->parm5), value);
            if (!strcmp(name, "parm6"))
                return set_float(&(pr_global_struct->parm6), value);
            if (!strcmp(name, "parm7"))
                return set_float(&(pr_global_struct->parm7), value);
            if (!strcmp(name, "parm8"))
                return set_float(&(pr_global_struct->parm8), value);
            if (!strcmp(name, "parm9"))
                return set_float(&(pr_global_struct->parm9), value);
            if (!strcmp(name, "parm10"))
                return set_float(&(pr_global_struct->parm10), value);
            if (!strcmp(name, "parm11"))
                return set_float(&(pr_global_struct->parm11), value);
            if (!strcmp(name, "parm12"))
                return set_float(&(pr_global_struct->parm12), value);
            if (!strcmp(name, "parm13"))
                return set_float(&(pr_global_struct->parm13), value);
            if (!strcmp(name, "parm14"))
                return set_float(&(pr_global_struct->parm14), value);
            if (!strcmp(name, "parm15"))
                return set_float(&(pr_global_struct->parm15), value);
            if (!strcmp(name, "parm16"))
                return set_float(&(pr_global_struct->parm16), value);
            if (!strcmp(name, "player_post_think"))
                return set_function(&(pr_func_struct->PlayerPostThink), value);
            if (!strcmp(name, "player_pre_think"))
                return set_function(&(pr_func_struct->PlayerPreThink), value);
            if (!strcmp(name, "put_client_in_server"))
                return set_function(&(pr_func_struct->PutClientInServer), value);
            break;
        case 's':
            if (!strcmp(name, "self"))
                return set_entity(&(pr_global_struct->self), value);
            if (!strcmp(name, "serverflags"))
                return set_float(&(pr_global_struct->serverflags), value);
            if (!strcmp(name, "set_change_parms"))
                return set_function(&(pr_func_struct->SetChangeParms), value);      
            if (!strcmp(name, "set_new_parms"))
                return set_function(&(pr_func_struct->SetNewParms), value);
            if (!strcmp(name, "start_frame"))
                return set_function(&(pr_func_struct->StartFrame), value);
            break;
        case 't':
            if (!strcmp(name, "time"))
                return set_float(&(pr_global_struct->time), value);
            if (!strcmp(name, "total_monsters"))
                return set_float(&(pr_global_struct->total_monsters), value);
            if (!strcmp(name, "total_secrets"))
                return set_float(&(pr_global_struct->total_secrets), value);
            if (!strcmp(name, "trace_allsolid"))
                return set_float(&(pr_global_struct->trace_allsolid), value);
            if (!strcmp(name, "trace_endpos"))
                return set_vector(&(pr_global_struct->trace_endpos), value);
            if (!strcmp(name, "trace_ent"))
                return set_entity(&(pr_global_struct->trace_ent), value);
            if (!strcmp(name, "trace_fraction"))
                return set_float(&(pr_global_struct->trace_fraction), value);
            if (!strcmp(name, "trace_inopen"))
                return set_float(&(pr_global_struct->trace_inopen), value);
            if (!strcmp(name, "trace_inwater"))
                return set_float(&(pr_global_struct->trace_inwater), value);
            if (!strcmp(name, "trace_plane_dist"))
                return set_float(&(pr_global_struct->trace_plane_dist), value);
            if (!strcmp(name, "trace_plane_normal"))
                return set_vector(&(pr_global_struct->trace_plane_normal), value);
            if (!strcmp(name, "trace_startsolid"))
                return set_float(&(pr_global_struct->trace_startsolid), value);
            break;
        case 'v':
            if (!strcmp(name, "v_forward"))
                return set_vector(&(pr_global_struct->v_forward), value);
            if (!strcmp(name, "v_right"))
                return set_vector(&(pr_global_struct->v_right), value);
            if (!strcmp(name, "v_up"))
                return set_vector(&(pr_global_struct->v_up), value);
            break;
        case 'w':
            if (!strcmp(name, "world"))
                return set_entity(&(pr_global_struct->world), value);
            break;
		default:
			break;
        }

    PyErr_Format(PyExc_AttributeError, "attribute: %s not found", name);
    return -1;
    }

PyObject * set_qc_global(PyObject *self, PyObject *args)
    {
    char *name;
    PyObject *value;

    if (!PyArg_ParseTuple(args, "sO", &name, &value))
        return NULL;

    if (set_qc_global0(name, value))
        return NULL;
    else
        {
        Py_INCREF(Py_None);
        return Py_None;
        }
    }

/********* Engine ***************/


static PyObject * engine_ambientsound(PyObject *self, PyObject *args)
    {
	char		**check;
	char		*samp;
    qwp_vector_t *pos;
	float 		vol, attenuation;
	int			i, soundnum;

    if (!PyArg_ParseTuple(args, "O!sff", &QWP_Vector_Type, &pos, &samp, &vol, &attenuation))
        return NULL;
	
    // check to see if samp was properly precached
	for (soundnum=0, check = sv.sound_precache ; *check ; check++, soundnum++)
		if (!strcmp(*check,samp))
			break;
			
	if (!*check)
		Con_Printf("no precache: %s\n", samp);
    else
        {
        // add an svc_spawnambient command to the level signon packet

    	MSG_WriteByte (&sv.signon,svc_spawnstaticsound);
    	for (i=0 ; i<3 ; i++)
		    MSG_WriteCoord(&sv.signon, pos->v[i]);

	    MSG_WriteByte (&sv.signon, soundnum);
    
    	MSG_WriteByte (&sv.signon, vol*255);
    	MSG_WriteByte (&sv.signon, attenuation*64);
        }

    Py_INCREF(Py_None);
    return Py_None;
    }


static PyObject * engine_bprint(PyObject *self, PyObject *args)
    {
	char		*s;
	int			level;
	
    if (!PyArg_ParseTuple(args, "is", &level, &s))
        return NULL;

	SV_BroadcastPrintf(level, "%s", s);
    
    Py_INCREF(Py_None);
    return Py_None;
    }


static PyObject * engine_changelevel(PyObject *self, PyObject *args)
    {
	char	*s;
	static	int	last_spawncount;

    if (!PyArg_ParseTuple(args, "s", &s))
        return NULL;

    // make sure we don't issue two changelevels
	if (svs.spawncount != last_spawncount)
        {
	    last_spawncount = svs.spawncount;
	
    	Cbuf_AddText (va("map %s\n",s));
        }
    
    Py_INCREF(Py_None);
    return Py_None;
    }


static PyObject * engine_cvar(PyObject *self, PyObject *args)
    {
	char	*str;
	
    if (!PyArg_ParseTuple(args, "s", &str))
        return NULL;

    return get_py_number(Cvar_VariableValue(str));    
    }   


static PyObject * engine_cvar_set(PyObject *self, PyObject *args)
    {
	char	*var, *val;
	
    if (!PyArg_ParseTuple(args, "ss", &var, &val))
        return NULL;
	
	Cvar_Set(var, val);
    
    Py_INCREF(Py_None);
    return Py_None;
    }


static PyObject * engine_dprint(PyObject *self, PyObject *args)
    {
	char *s;
	
    if (!PyArg_ParseTuple(args, "s", &s))
        return NULL;

    Con_Printf("%s", s);
    
    Py_INCREF(Py_None);
    return Py_None;
    }


static PyObject * engine_findradius(PyObject *self, PyObject *args)
    {
    qwp_vector_t *v;
    PyObject *result;
	edict_t	*ent;
	float	rad;
	vec3_t	eorg;
	int		i, j;

    if (!PyArg_ParseTuple(args, "O!f", &QWP_Vector_Type, &v, &rad))
        return NULL;

    result = PyList_New(0);
    rad = rad * rad;
	ent = NEXT_EDICT(sv.edicts);
	for (i = 1; i < sv.num_edicts; i++)
    	{  
        ent = sv.edicts + i;
		if (ent->free)
			continue;
		if (ent->v.solid == SOLID_NOT)
			continue;
		for (j=0 ; j<3 ; j++)
			eorg[j] = v->v[j] - (ent->v.origin[j] + (ent->v.mins[j] + ent->v.maxs[j])*0.5);			
		if (LengthSquared(eorg) > rad)
			continue;
			
        PyList_Append(result, (PyObject *)(ent->p_entity));
	    }

    return result;
    }


static PyObject * engine_lightstyle(PyObject *self, PyObject *args)
    {
	int		style;
	char	*val;
    char    *val2;
	client_t	*client;
	int			j;
	
    if (!PyArg_ParseTuple(args, "is", &style, &val))
        return NULL;

    // change the string in sv
    val2 = Hunk_Alloc(strlen(val)+1);
    strcpy(val2, val);
	sv.lightstyles[style] = val2;
	
    // send message to all clients on this server
	if (sv.state == ss_active)
        {
    	for (j=0, client = svs.clients ; j<MAX_CLIENTS ; j++, client++)
            {
		    if ( client->state == cs_spawned )
    	    	{
			    ClientReliableWrite_Begin (client, svc_lightstyle, strlen(val2)+3);
			    ClientReliableWrite_Char (client, style);
			    ClientReliableWrite_String (client, val2);
		        }
            }
        }

    Py_INCREF(Py_None);
    return Py_None; 
    }


static PyObject * engine_multicast(PyObject *self, PyObject *args)
    {
	qwp_vector_t *v;
	int		to;

    if (!PyArg_ParseTuple(args, "O!i", &QWP_Vector_Type, &v, &to))
        return NULL;
    
	SV_Multicast (v->v, to);

    Py_INCREF(Py_None);
    return Py_None;
    }


static PyObject * engine_pointcontents(PyObject *self, PyObject *args)
    {
    qwp_vector_t *v;

    if (!PyArg_ParseTuple(args, "O!", &QWP_Vector_Type, &v))
        return NULL;

	return get_py_number(SV_PointContents(v->v));	    
    }


static PyObject *engine_precache(PyObject *self, PyObject *args, char **cache, int max_cache)
    {
	char	*s;
	int		i;
	
	if (sv.state != ss_loading)
        {
        PyErr_SetString(PyExc_RuntimeError, "Precache can only be done in spawn functions");
	    return NULL;
        }

    if (!PyArg_ParseTuple(args, "s", &s))
        return NULL;
    
//	G_INT(OFS_RETURN) = G_INT(OFS_PARM0);
//	PR_CheckEmptyString(s);
	
	for (i = 0; i < max_cache; i++)
	    {
		if (!cache[i])
		    {
			cache[i] = Hunk_Alloc(strlen(s)+1);
            strcpy(cache[i], s);
            Py_INCREF(Py_None);
	        return Py_None;
		    }
		if (!strcmp(cache[i], s))
            {
            Py_INCREF(Py_None);
	        return Py_None;
            }
	    }

    PyErr_SetString(PyExc_RuntimeError, "precache overflow");
	return NULL;
    }


static PyObject *engine_precache_model(PyObject *self, PyObject *args)
    {
    return engine_precache(self, args, sv.model_precache, MAX_MODELS);
    }

static PyObject *engine_precache_sound(PyObject *self, PyObject *args)
    {
    return engine_precache(self, args, sv.sound_precache, MAX_SOUNDS);
    }



static PyObject *engine_spawn(PyObject *self, PyObject *args)
    {
    edict_t *ent;

    ent = ED_Alloc();

    //Sys_Printf("Created %d, p_entity=%x c_entity=%x\n", NUM_FOR_EDICT(ent), ent->p_entity, ent->p_entity->c_entity);
    Py_INCREF(ent->p_entity);

    return (PyObject *)(ent->p_entity);
    }


static PyObject * engine_traceline(PyObject *self, PyObject *args)
    {
    qwp_vector_t *v1;
    qwp_vector_t *v2;
	int		nomonsters;
    qwp_entity_t *pent;
    edict_t *ent;
	trace_t	trace;

    if (!PyArg_ParseTuple(args, "O!O!iO", &QWP_Vector_Type, &v1, &QWP_Vector_Type, &v2, &nomonsters, &pent))
        return NULL;

    if ((PyObject *)pent == Py_None)
        ent = sv.edicts;
    else if (qwp_entity_check(pent))
        ent = pent->c_entity;
    else
        {
        PyErr_SetString(PyExc_TypeError, "passent must be None or an Entity");
        return NULL;
        }

	trace = SV_Move(v1->v, vec3_origin, vec3_origin, v2->v, nomonsters, ent);

	pr_global_struct->trace_allsolid = trace.allsolid;
	pr_global_struct->trace_startsolid = trace.startsolid;
	pr_global_struct->trace_fraction = trace.fraction;
	pr_global_struct->trace_inwater = trace.inwater;
	pr_global_struct->trace_inopen = trace.inopen;
	VectorCopy (trace.endpos, pr_global_struct->trace_endpos);
	VectorCopy (trace.plane.normal, pr_global_struct->trace_plane_normal);
	pr_global_struct->trace_plane_dist =  trace.plane.dist;	
	if (trace.ent)
		pr_global_struct->trace_ent = EDICT_TO_PROG(trace.ent);
	else
		pr_global_struct->trace_ent = EDICT_TO_PROG(sv.edicts);

    
    Py_INCREF(Py_None);
	return Py_None;
    }

#define	MSG_BROADCAST	0		// unreliable to all
#define	MSG_ONE			1		// reliable to one (msg_entity)
#define	MSG_ALL			2		// reliable to all
#define	MSG_INIT		3		// write to the init string
#define	MSG_MULTICAST	4		// for multicast()

static sizebuf_t *WriteDest(int dest)
    {
	switch (dest)
	    {
	    case MSG_BROADCAST:
    		return &sv.datagram;
			
	    case MSG_ALL:
    		return &sv.reliable_datagram;
	
    	case MSG_INIT:
		    if (sv.state != ss_loading)
                {
    			PyErr_SetString(PyExc_TypeError, "MSG_INIT can only be written in spawn functions");
                return NULL;
                }
		    return &sv.signon;

	    case MSG_MULTICAST:
    		return &sv.multicast;
		default:
			break;
        }

	PyErr_SetString(PyExc_TypeError, "Bad destination");	
	return NULL;
    }


static PyObject * engine_write_angle(PyObject *self, PyObject *args)
    {
    sizebuf_t *dest;
    int to;
    float f;

    if (!PyArg_ParseTuple(args, "if", &to, &f) || !(dest = WriteDest(to)))
        return NULL;

	MSG_WriteAngle(dest, f);

    Py_INCREF(Py_None);
    return Py_None;
    }


static PyObject * engine_write_byte(PyObject *self, PyObject *args)
    {
    sizebuf_t *dest;
    int to;
    int i;

    if (!PyArg_ParseTuple(args, "ii", &to, &i) || !(dest = WriteDest(to)))
        return NULL;

	MSG_WriteByte(dest, i);

    Py_INCREF(Py_None);
    return Py_None;
    }


static PyObject * engine_write_char(PyObject *self, PyObject *args)
    {
    sizebuf_t *dest;
    int to;
    int i;

    if (!PyArg_ParseTuple(args, "ii", &to, &i) || !(dest = WriteDest(to)))
        return NULL;

	MSG_WriteChar(dest, i);

    Py_INCREF(Py_None);
    return Py_None;
    }


static PyObject * engine_write_coord(PyObject *self, PyObject *args)
    {
    sizebuf_t *dest;
    int to;
    float f;

    if (!PyArg_ParseTuple(args, "if", &to, &f) || !(dest = WriteDest(to)))
        return NULL;

	MSG_WriteCoord(dest, f);

    Py_INCREF(Py_None);
    return Py_None;
    }


static PyObject * engine_write_entity(PyObject *self, PyObject *args)
    {
    sizebuf_t *dest;
    int to;
    qwp_entity_t *ent;

    if (!PyArg_ParseTuple(args, "iO!", &to, &QWP_Entity_Type, &ent) || !(dest = WriteDest(to)))
        return NULL;

	MSG_WriteShort(dest, NUM_FOR_EDICT(ent->c_entity));

    Py_INCREF(Py_None);
    return Py_None;
    }


static PyObject * engine_write_long(PyObject *self, PyObject *args)
    {
    sizebuf_t *dest;
    int to;
    int i;

    if (!PyArg_ParseTuple(args, "ii", &to, &i) || !(dest = WriteDest(to)))
        return NULL;

	MSG_WriteLong(dest, i);

    Py_INCREF(Py_None);
    return Py_None;
    }


static PyObject * engine_write_short(PyObject *self, PyObject *args)
    {
    sizebuf_t *dest;
    int to;
    int i;

    if (!PyArg_ParseTuple(args, "ii", &to, &i) || !(dest = WriteDest(to)))
        return NULL;

	MSG_WriteShort(dest, i);

    Py_INCREF(Py_None);
    return Py_None;
    }


static PyObject * engine_write_string(PyObject *self, PyObject *args)
    {
    sizebuf_t *dest;
    int to;
    char *s;

    if (!PyArg_ParseTuple(args, "is", &to, &s) || !(dest = WriteDest(to)))
        return NULL;

	MSG_WriteString(dest, s);

    Py_INCREF(Py_None);
    return Py_None;
    }



static struct PyMethodDef engine_methods[] =
	{
        {"ambientsound", engine_ambientsound, 1},
        {"bprint", engine_bprint, 1},
        {"changelevel", engine_changelevel, 1},
        {"cvar", engine_cvar, 1},
        {"cvar_set", engine_cvar_set, 1},
        {"dprint", engine_dprint, 1},
        {"findradius", engine_findradius, 1},
		{"get_qc_global", get_qc_global, 1},
        {"lightstyle", engine_lightstyle, 1},
        {"multicast", engine_multicast, 1},
        {"pointcontents", engine_pointcontents, 1},
        {"precache_model", engine_precache_model, 1},
        {"precache_sound", engine_precache_sound, 1},
		{"run", qw_run, 1},
		{"set_qc_global", set_qc_global, 1},
        {"spawn", engine_spawn, 1},
		{"stop", qw_stop, 1},
		{"traceline", engine_traceline, 1},
        {"write_angle", engine_write_angle, 1},
        {"write_byte", engine_write_byte, 1},
        {"write_char", engine_write_char, 1},
        {"write_coord", engine_write_coord, 1},
        {"write_entity", engine_write_entity, 1},
        {"write_long", engine_write_long, 1},
        {"write_short", engine_write_short, 1},
        {"write_string", engine_write_string, 1},
		{NULL, NULL}
	};


static PyObject * engine_getattr(qwp_engine_t *self, char *name)
	{
	PyObject *result = NULL;

    if (strcmp(name, "argv") == 0)
        result = self->argv;
	else if (strcmp(name, "loader") == 0)
		result = self->loader;
	else if (strcmp(name, "reset_game") == 0)
		result = self->reset_game;
	else if (strcmp(name, "spawn_func") == 0)
		result = self->spawn_func;
	else if (strcmp(name, "stdout") == 0)
		result = self->out;
    else if (strcmp(name, "version") == 0)
        return Py_BuildValue("{s:s, s:i}", "name", ENGINE_NAME, "revision", ENGINE_REVISION); 		
    else if (strcmp(name, "world") == 0)
        result = self->world;

	if (result)
		{
		Py_INCREF(result);
		return result;
		}

	if (strcmp(name, "__members__") == 0)
		return Py_BuildValue("[s,s,s,s,s]", "argv", "loader", "reset_game",  "spawn_func", "stdout", "version", "world");

	return Py_FindMethod(engine_methods, (PyObject *)self, name);
	}


static int engine_setattr(qwp_engine_t *self, char *name, PyObject *value)
	{
	PyObject **target = NULL;

    if (!value)
        {
        PyErr_SetString(PyExc_TypeError, "attributes are not deletable");
        return -1;
        }
    
    if (strcmp(name, "argv") == 0)
        target = &(self->argv);
    else if (strcmp(name, "frame_handler") == 0)
        target = &(self->frame_handler);
	else if (strcmp(name, "loader") == 0)
		target = &(self->loader);
	else if (strcmp(name, "reset_game") == 0)
		target = &(self->reset_game);
	else if (strcmp(name, "stdout") == 0)
		target = &(self->out);
	else if (strcmp(name, "spawn_func") == 0)
		target = &(self->spawn_func);

	if (target)
		{
		Py_DECREF(*target);
		*target = value;
		Py_INCREF(value);
		return 0;
		}

	PyErr_SetString(PyExc_AttributeError, name);
	return -1;
	}


static PyTypeObject Engine_Type = 
	{
	PyObject_HEAD_INIT(NULL) // work around MSVC problem, use NULL here, set in the initqw() function
							 // otherwise you get an "initializer not constant" error
	0,			/*ob_size*/
	"engine",		/*tp_name*/
	sizeof(qwp_engine_t),	/*tp_size*/
	0,			/*tp_itemsize*/
	0, //(destructor)module_dealloc, /*tp_dealloc*/
	0,			/*tp_print*/
	(getattrfunc)engine_getattr, /*tp_getattr*/
	(setattrfunc)engine_setattr, /*tp_setattr*/
	0,			/*tp_compare*/
	0, //(reprfunc)module_repr, /*tp_repr*/
	};


static void init_qwp_engine(void)
	{
	Engine_Type.ob_type = &PyType_Type;  // Fix for MSVC problem
	qwp_engine = PyObject_NEW(qwp_engine_t, &Engine_Type);

    qwp_engine->frame_handler = Py_None;
    Py_INCREF(Py_None);

	qwp_engine->loader = Py_None;
	Py_INCREF(Py_None);

	qwp_engine->out = Py_None;
	Py_INCREF(Py_None);
	
	qwp_engine->reset_game = Py_None;
	Py_INCREF(Py_None);

    qwp_engine->spawn_func = Py_None;
    Py_INCREF(Py_None);

    qwp_engine->argv = Py_None;
    Py_INCREF(Py_None);

    qwp_engine->world = create_qwp_entity(NULL);
	}


/********* qwsv Module ***************/

static struct PyMethodDef qwsv_methods[] =
	{
        {"Vector", qwp_vector_new, 1},
		{NULL, NULL}
	};


void initqwsv(void)
	{
	PyObject *m;

	m = Py_InitModule("qwsv", qwsv_methods);
	module_dict = PyModule_GetDict(m);
	Py_INCREF(module_dict);

    init_qwp_engine();
    init_qwp_entity_type();
    init_qwp_vector_type();

	PyDict_SetItemString(module_dict, "engine", (PyObject *)qwp_engine);

	if (PyErr_Occurred())
		Py_FatalError("Can't initialize module qwsv");

    engine_init();
	}


void PR_ExecuteProgram(PyObject *func)
    {
    PyObject *result = PyObject_CallFunction(func, NULL);
    if (result)
        Py_DECREF(result);
    else
        PyErr_Print();
    }


void qwp_global_clearall(void)
    {
    Py_XDECREF(pr_global_struct->mapname);
    memset(pr_global_struct, 0, sizeof(pr_global_struct));
    }

