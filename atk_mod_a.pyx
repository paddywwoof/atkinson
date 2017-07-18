from __future__ import division
cimport numpy as cnp # to be clear this is different from 'import numpy'

cdef inline cnp.uint8_t adderror(cnp.uint8_t b, int e):
  return min(max(b + e, 0x00), 0xFF) 

cimport cython
@cython.boundscheck(False) # turn off bounds-checking for entire function
def atk(cnp.ndarray[cnp.uint8_t, ndim=2] pixels):
  cdef:
    int x, y, off, err
    int threshold = 127
    cnp.uint8_t old, new
    int h = pixels.shape[0]
    int w = pixels.shape[1]
  
  for y in range(h):
      for x in range(w):
          old = pixels[y, x]
          if old > threshold:
            new = 0xFF
          else:
            new = 0x00
          err = (old - new) >> 3; # divide by 8
          pixels[y, x] = new
          # now distribute the error...
          if (x+1) < w:            # x+1, y
              pixels[y, x + 1] = adderror(pixels[y, x + 1], err)
          if (x+2) < w:           # x+2, y
              pixels[y, x + 2] = adderror(pixels[y, x + 2], err)
          if x > 0 and (y+1) < h:   # x-1, y+1
              pixels[y + 1, x - 1] = adderror(pixels[y + 1, x - 1], err)
          if (y+1) < h:           # x, y+1
              pixels[y + 1, x] = adderror(pixels[y + 1, x], err)
          if (x+1) < w and (y+1) < h: # x+1, y+1
              pixels[y + 1, x + 1] = adderror(pixels[y + 1, x + 1], err)
          if (y+2) < h:            # x, y+2
              pixels[y + 2, x] = adderror(pixels[y + 2, x], err)
