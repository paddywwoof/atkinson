// this is a slightly condensed version of migurski - use an if rather than  lookup table for threshold
#include <string.h>
#include <stdio.h>

#ifndef adderror
    #define adderror( b, e ) ( ((b) < -(e)) ? 0x00 : ( ((0xFF - (b)) < (e)) ? 0xFF : (b + e) ) )
#endif

void atk(int w, int h, unsigned char pixels[])
{
  int x, y, off, err;
  int threshold = 127;
  unsigned char old, new;
  
  for(y = 0; y < h; y++)
  {
      for(x = 0; x < w; x++)
      {
          // offset in the string for a given (x, y) pixel
          off = (y * w) + x;
          // threshold and get the error
          old = pixels[off];
          if (old > threshold) {
            new = 0xFF;
          } else {
            new = 0x00;
          }
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
}
