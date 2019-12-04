from __future__ import division
from numba import njit

@njit
def  adderror(b, e):
  return min(max(b + e, 0x00), 0xFF) 

@njit(cache=True)
def atk(pixels):
  h = pixels.shape[0]
  w = pixels.shape[1]
  threshold = 127
  
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
