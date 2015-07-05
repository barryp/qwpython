
#include "qwpython.h"



static void vector_destruct(qwp_vector_t *self)
    {
    }


static PyObject * vector_abs(qwp_vector_t *v)
    {
    vec3_t temp;

    if ((v->v[0] >= 0) && (v->v[1] >= 0) && (v->v[2] >= 0))
        {
        Py_INCREF(v);
        return (PyObject *) v;
        }

    temp[0] = (float) fabs(v->v[0]);
    temp[1] = (float) fabs(v->v[1]);
    temp[2] = (float) fabs(v->v[2]);

    return create_qwp_vector(temp);
    }


static PyObject * vector_add(qwp_vector_t *v, qwp_vector_t *w)
    {
    vec3_t temp;
    if (IS_SCALAR(w) || IS_SCALAR(v))
        {
        PyErr_SetString(PyExc_TypeError, "Can't add a vector to a scalar");
        return NULL;
        }

    VectorAdd(v->v, w->v, temp);
    return create_qwp_vector(temp);
    }


static PyObject *vector_angle_to_vectors(PyObject *self, PyObject *args)
    {
    vec3_t forward, right, up;
    PyObject *result;
    qwp_vector_t *v;

    v = (qwp_vector_t *) self;

    AngleVectors(v->v, forward, right, up);

    result = PyTuple_New(3);
    PyTuple_SET_ITEM(result, 0, create_qwp_vector(forward));
    PyTuple_SET_ITEM(result, 1, create_qwp_vector(right));
    PyTuple_SET_ITEM(result, 2, create_qwp_vector(up));

    return result;
    }


// Coerce a scalar into a pseudo-vector, so that we 
// can multiply and devide against it.
static int vector_coerce(PyObject **pv, PyObject **pw)
    {
    vec3_t temp;

    temp[0] = (float) PyFloat_AsDouble(*pw);
    temp[1] = 0;
    temp[2] = 0;

    if (PyErr_Occurred())
        {
        PyErr_Clear();
        return 1; // can't do it
        }
    else
        {
        *pw = create_qwp_vector(temp);
        ((qwp_vector_t *)(*pw))->flags = 8;
        Py_INCREF(*pv);
        return 0; // succeded
        }
    }


static int vector_compare(qwp_vector_t *v, qwp_vector_t *w)
    {
    vec_t diff;

    if (IS_SCALAR(w) || IS_SCALAR(v))
        return -1;

    if ((v->v[0] == w->v[0]) && (v->v[1] == w->v[1]) && (v->v[2] == w->v[2]))
        return 0;

    // vectors aren't identical, try ordering them by length
    diff = LengthSquared(v->v) - LengthSquared(w->v);

    if (diff < 0)
        return -1;
    if (diff > 0)
        return 1;

    // vectors are same length, resort to using pointers to differentiate them
    if (v < w)
        return -1;
    else
        return 1;
    }


static PyObject * vector_div(qwp_vector_t *v, qwp_vector_t *w)
    {
    if (IS_SCALAR(v))
        {
        PyErr_SetString(PyExc_TypeError, "can't divide a scalar by a vector");
        return NULL;
        }

    if (IS_SCALAR(w))
        {
        vec3_t temp;

        if (w->v[0] == 0)
            {
            PyErr_SetString(PyExc_ZeroDivisionError, "can't divide a vector by zero");
            return NULL;
            }

        temp[0] = v->v[0] / w->v[0];
        temp[1] = v->v[1] / w->v[0];
        temp[2] = v->v[2] / w->v[0];    

        return create_qwp_vector(temp);
        }

    return PyFloat_FromDouble(DotProduct(v->v, w->v));
    }


static PyObject * vector_length(PyObject *self, PyObject *args)
    {
    double length;
    qwp_vector_t *vec;

    vec = (qwp_vector_t *) self;
    length = sqrt((vec->v[0] * vec->v[0]) + (vec->v[1] * vec->v[1]) + (vec->v[2] * vec->v[2]));
    return PyFloat_FromDouble(length);
    }


static PyObject * vector_mul(qwp_vector_t *v, qwp_vector_t *w)
    {
    vec3_t temp;

    if (IS_SCALAR(w))
        VectorScale(v->v, w->v[0], temp);
    else if (IS_SCALAR(v))
        VectorScale(w->v, v->v[0], temp);
    else
        return PyFloat_FromDouble(DotProduct(v->v, w->v));

    return create_qwp_vector(temp);
    }


static PyObject * vector_neg(qwp_vector_t *v)
    {
    vec3_t temp;

    temp[0] = -(v->v[0]);
    temp[1] = -(v->v[1]);
    temp[2] = -(v->v[2]);

    return create_qwp_vector(temp);
    }


static int vector_nonzero(qwp_vector_t *v)
    {
    return (v->v[0] != 0) || (v->v[1] != 0) || (v->v[2] != 0);
    }


static PyObject * vector_normalize(PyObject *self, PyObject *args)
    {
    vec3_t temp;
    double length;
    qwp_vector_t *vec;

    vec = (qwp_vector_t *) self;
    length = sqrt((vec->v[0] * vec->v[0]) + (vec->v[1] * vec->v[1]) + (vec->v[2] * vec->v[2]));

    if (length == 0)
        {
        // the way things should be ...
        //PyErr_SetString(PyExc_ZeroDivisionError, "can't normalize a zero-length vector");
        //return NULL;
        
        // the way Quake actually works
        Py_INCREF(self);
        return self;
        }

    temp[0] = (float)(vec->v[0] / length);
    temp[1] = (float)(vec->v[1] / length);
    temp[2] = (float)(vec->v[2] / length);

    return create_qwp_vector(temp);
    }


static PyObject * vector_pos(qwp_vector_t *v)
    {
    Py_INCREF(v);
    return (PyObject *) v;
    }


// print is broken somehow, using repr instead works
//static int vector_print(qwp_vector_t *self, FILE *fp, int flags)
//    {
//	fprintf(fp, "(%.12g, %.12g, %.12g)", self->v[0], self->v[1], self->v[2]);
//	return 0;
//    }


// merge two vectors together, using the values from the first one, if the
// corresponding field in the second was a 'None' value when the second vector
// was created.
static PyObject * vector_remainder(qwp_vector_t *vec, qwp_vector_t *other)
    {
    vec3_t temp;

    if (PyErr_Occurred())
        printf("An error has already occurred\n");

    temp[0] = (other->flags & 4 ? vec->v[0] : other->v[0]);
    temp[1] = (other->flags & 2 ? vec->v[1] : other->v[1]);
    temp[2] = (other->flags & 1 ? vec->v[2] : other->v[2]);

    return create_qwp_vector(temp);
    }


static PyObject * vector_repr(qwp_vector_t *self)
    {
	char buf[128];
	sprintf(buf, "<%.17g, %.17g, %.17g>", self->v[0], self->v[1], self->v[2]);
	return PyString_FromString(buf);
    }


static PyObject * vector_sub(qwp_vector_t *v, qwp_vector_t *w)
    {
    vec3_t temp;

    if (IS_SCALAR(w))
        {
        PyErr_SetString(PyExc_TypeError, "Can't subtract a scalar from a vector");
        return NULL;
        }

    if (IS_SCALAR(v))
        {
        PyErr_SetString(PyExc_TypeError, "Can't subtract a vector from a scalar");
        return NULL;
        }
    
    VectorSubtract(v->v, w->v, temp);
    return create_qwp_vector(temp);
    }


static PyObject * vector_to_angle(PyObject *self, PyObject *args)
    {
    vec3_t temp;

	double	forward;
	int	yaw, pitch;
    qwp_vector_t *v;

    v = (qwp_vector_t *) self;
	
	if (v->v[1] == 0 && v->v[0] == 0)
    	{
		yaw = 0;
		if (v->v[2] > 0)
			pitch = 90;
		else
			pitch = 270;
	    }
	else
	    {
		yaw = (int) (atan2(v->v[1], v->v[0]) * 180 / M_PI);
		if (yaw < 0)
			yaw += 360;

		forward = sqrt (v->v[0]*v->v[0] + v->v[1]*v->v[1]);
		pitch = (int) (atan2(v->v[2], forward) * 180 / M_PI);
		if (pitch < 0)
			pitch += 360;
	    }

    temp[0] = (float) pitch;
    temp[1] = (float) yaw;
    temp[2] = 0;

    return create_qwp_vector(temp);
    }


static PyNumberMethods vector_as_number = 
    {
	(binaryfunc)vector_add, /*nb_add*/
	(binaryfunc)vector_sub, /*nb_subtract*/
	(binaryfunc)vector_mul, /*nb_multiply*/
	(binaryfunc)vector_div, /*nb_divide*/
	(binaryfunc)vector_remainder, //(binaryfunc)complex_remainder,	/*nb_remainder*/
	0, //(binaryfunc)complex_divmod,	/*nb_divmod*/
	0, //(ternaryfunc)complex_pow, /*nb_power*/
	(unaryfunc)vector_neg, /*nb_negative*/
	(unaryfunc)vector_pos, /*nb_positive*/
	(unaryfunc)vector_abs, /*nb_absolute*/
	(inquiry)vector_nonzero, /*nb_nonzero*/
	0,		/*nb_invert*/
	0,		/*nb_lshift*/
	0,		/*nb_rshift*/
	0,		/*nb_and*/
	0,		/*nb_xor*/
	0,		/*nb_or*/
	(coercion)vector_coerce, /*nb_coerce*/
    };


static struct PyMethodDef vector_methods[] =
	{
        {"length", vector_length, 1},
        {"normalize", vector_normalize, 1},
        {"to_angle", vector_to_angle, 1},
        {"to_vectors", vector_angle_to_vectors, 1},
		{NULL, NULL}
	};


static PyObject * vector_getattr(qwp_vector_t *self, char *name)
	{
    if (!strcmp(name, "x") || !strcmp(name, "pitch"))
        return PyFloat_FromDouble(self->v[0]);

    if (!strcmp(name, "y") || !strcmp(name, "yaw"))
        return PyFloat_FromDouble(self->v[1]);

    if (!strcmp(name, "z") || !strcmp(name, "roll"))
        return PyFloat_FromDouble(self->v[2]);

	if (strcmp(name, "__members__") == 0)
		return Py_BuildValue("[s,s,s,s,s,s]", "x", "y", "z", "pitch", "yaw", "roll");

    return Py_FindMethod(vector_methods, (PyObject *)self, name);
	}


PyTypeObject QWP_Vector_Type = 
	{
	PyObject_HEAD_INIT(NULL) // work around MSVC problem, use NULL here, set in the initqw() function
							 // otherwise you get an "initializer not constant" error
	0,			                    /*ob_size*/
	"QWPython Vector",	            /*tp_name*/
	sizeof(qwp_vector_t),	        /*tp_size*/
	0,			                    /*tp_itemsize*/
	(destructor)vector_destruct,    /*tp_dealloc*/
    0,                              /*tp_print*/
	(getattrfunc)vector_getattr,    /*tp_getattr*/
	0,                              /*tp_setattr*/
	(cmpfunc)vector_compare,        /*tp_compare*/
	(reprfunc)vector_repr,          /*tp_repr*/
    &vector_as_number,
	};


void init_qwp_vector_type(void)
    {
	QWP_Vector_Type.ob_type = &PyType_Type;  // Fix for MSVC problem
    }


PyObject * create_qwp_vector(vec3_t source)
    {
    qwp_vector_t * result;

	result = PyObject_NEW(qwp_vector_t, &QWP_Vector_Type);

    result->v[0] = source[0];
    result->v[1] = source[1];
    result->v[2] = source[2];
    result->flags = 0;

    return (PyObject *) result;
    }

PyObject * qwp_vector_new(PyObject *self, PyObject *args)
    {
    vec3_t temp;
    int none_flag;
    PyObject *x;
    PyObject *y;
    PyObject *z;
    PyObject *result;

    // handle common case 
    if (PyArg_ParseTuple(args, "fff", &(temp[0]), &(temp[1]), &(temp[2])))
        return create_qwp_vector(temp);

    // now things get funky, one or more of the args wasn't a number, or
    // there were not 3 args
    PyErr_Clear();
    if (!PyArg_ParseTuple(args, "OOO", &x, &y, &z))
        return NULL;  // not 3 args of any type

    // ok, there are 3 args, make sure each is either None or a number
    if (((x != Py_None) && !PyNumber_Check(x))
    ||  ((y != Py_None) && !PyNumber_Check(y))
    ||  ((z != Py_None) && !PyNumber_Check(z)))
        {
        PyErr_SetString(PyExc_TypeError, "Expecting 3 values, either of number type, or None");
        return NULL;
        }

    // Create a pseudo-vector, with flags 
    // showing which of the x,y or z values was missing.
    none_flag = 0;

    if (x == Py_None)
        {
        none_flag |= 4;
        temp[0] = 0;
        }
    else
        temp[0] = (float)PyFloat_AsDouble(x);

    if (y == Py_None)
        {
        none_flag |= 2;
        temp[1] = 0;
        }
    else
        temp[1] = (float)PyFloat_AsDouble(y);

    if (z == Py_None)
        {
        none_flag |= 1;
        temp[2] = 0;
        }
    else
        temp[2] = (float)PyFloat_AsDouble(z);

    result = create_qwp_vector(temp);
    ((qwp_vector_t *)result)->flags = none_flag;

    return result;
    }