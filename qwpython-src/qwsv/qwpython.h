/*
 * Python stuff for QuakeWorld
 */

#ifndef _QWPYTHON_H_
#define _QWPYTHON_H_

#include "Python.h"
#include "mathlib.h"
typedef int	func_t;

/* Utility functions in qwp_entity.c */
PyObject *get_entity(int index);
PyObject *get_function(PyObject *f);
PyObject *get_string(PyObject *s);
PyObject *get_py_number(float f);

int set_entity(int *ip, PyObject *value);
int set_float(float *fp, PyObject *value);
int set_function(PyObject **fp, PyObject *value);
int set_string(PyObject **sp, PyObject *value);
int set_vector(vec3_t *vp, PyObject *value);


/* Engine Stuff */
int Sys_ResourceExists(char *path); 
PyObject * Sys_ReadResource(const char *path);

typedef struct
	{
	PyObject_HEAD
    PyObject *frame_handler;
	PyObject *loader;
    PyObject *argv;
	PyObject *out;
	PyObject *reset_game;
    PyObject *spawn_func;
    PyObject *world;
	} qwp_engine_t;

extern qwp_engine_t *qwp_engine;


/* Entity Stuff */
extern PyTypeObject QWP_Entity_Type;
#define qwp_entity_check(op) ((op)->ob_type == &QWP_Entity_Type)
typedef struct qwp_entity_s
	{
	PyObject_HEAD
    PyObject *dict;
    struct edict_s  *c_entity;
	} qwp_entity_t;

void init_qwp_entity_type(void);
PyObject * create_qwp_entity(struct edict_s *e);
void qwp_entity_clearall(void);


/* Vector Stuff */
extern PyTypeObject QWP_Vector_Type;
#define qwp_vector_check(op) ((op)->ob_type == &QWP_Vector_Type)
typedef struct qwp_vector_s
    {
    PyObject_HEAD
    vec3_t v;
    int flags; /* to track if a vector was constructed with None fields, or if a scalar has been coerced into being a pseudo-vector so we can do some math with it */
    } qwp_vector_t;

#define IS_SCALAR(v) (((v)->flags & 8) != 0)
void init_qwp_vector_type(void);
PyObject * create_qwp_vector(vec3_t source);
PyObject * qwp_vector_new(PyObject *self, PyObject *args);

#endif