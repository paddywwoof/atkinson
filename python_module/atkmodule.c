// original source https://github.com/migurski/atkinson
#include <Python.h>
#include <string.h>
#include <stdio.h>

// adds the error so that it doesn't overflow an unsigned char
#ifndef adderror
    #define adderror( b, e ) ( ((b) < -(e)) ? 0x00 : ( ((0xFF - (b)) < (e)) ? 0xFF : (b + e) ) )
#endif

/* atk.atk()
 *   Given image dimensions and a raw string of grayscale pixels, dithers the "image"
 */
static PyObject *atk(PyObject *self, PyObject *args)
{
    int i, x, y, w, h, off, err;
    unsigned char *pixels, threshold[256];
    unsigned char old, new;
    PyBytesObject *byte_object;
    
    if(!PyArg_ParseTuple(args, "iiS", &w, &h, &byte_object))
    {
        /* fail unless I got two ints and a single bytes object as input */
        return NULL;
    }
    // access the pixel values using the *pixels pointer. We need unsigned
    pixels = byte_object->ob_sval; // char behaviour (will give compile warning)
    
    if(w * h != Py_SIZE(byte_object)) // not intuitive location for size
    {
        // fail if the given dimensions don't seem to match the passed image
        return NULL;
    }
    // set up a basic threshold table to save some if/else later on
    for(i = 0; i < 128; i++) {
        threshold[i] = 0x00;
    }
    for(i = 128; i < 256; i++) {
        threshold[i] = 0xFF;
    }
    for(y = 0; y < h; y++)
    {
        for(x = 0; x < w; x++)
        {
            // offset in the string for a given (x, y) pixel
            off = (y * w) + x;
            
            // threshold and get the error
            old = pixels[off];
            new = threshold[ pixels[off] ];
            err = (old - new) >> 3; // divide by 8

            // update the image
            pixels[off] = new;
            
            // now distribute the error...
            if(x+1 < w) { // x+1, y
                pixels[off + 1] = adderror(pixels[off + 1], err);
            }
            if(x+2 < w) { // x+2, y
                pixels[off + 2] = adderror(pixels[off + 2], err);
            }
            if(x > 0 && y+1 < h) { // x-1, y+1
                pixels[off + w - 1] = adderror(pixels[off + w - 1], err);
            }
            if(y+1 < h) { // x, y+1
                pixels[off + w] = adderror(pixels[off + w], err);
            }
            if(x+1 < w && y+1 < h) { // x+1, y+1
                pixels[off + w + 1] = adderror(pixels[off + w + 1], err);
            }
            if(y+2 < h) { // x, y+2
                pixels[off + 2 * w] = adderror(pixels[off + 2 * w], err);
            }
        }
    }
    byte_object->ob_shash = -1; // writing into immutable object so least we can do is set to unhashed
    return Py_BuildValue("S", pixels);
}

/* map between python function name and C function pointer */
static PyMethodDef AtkMethods[] = {
    {"atk", atk, METH_VARARGS, "Dither an image"},
    {NULL, NULL, 0, NULL}
};

/* There is quite a difference between python 2 and 3 for the actual 
 * module init function. Py3 uses a different function that needs a
 * whole PyModuleDef struct passing to it*/
#if PY_MAJOR_VERSION >= 3 
  static struct PyModuleDef atkmodule = {
     PyModuleDef_HEAD_INIT,
     "atk",    /* name of module */
     NULL,     /* module documentation, may be NULL */
     -1,       /* size of per-interpreter state of the module,
                  or -1 if the module keeps state in global variables. */
     AtkMethods
  };

  /* bootstrap function, called automatically when you 'import atk' */
  PyMODINIT_FUNC PyInit_atk(void) {
      return PyModule_Create(&atkmodule);
  }
#else
  PyMODINIT_FUNC initatk(void) {
      (void)Py_InitModule("atk", AtkMethods);
  }
#endif
