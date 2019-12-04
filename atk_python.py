from __future__ import division

def atk(pixels):
  h = pixels.size[0]
  w = pixels.size[1]
  threshold = 127
  
  for y in range(h):
      for x in range(w):
          old = pixels.getpixel((x, y))
          if old > threshold:
            new = 0xFF
          else:
            new = 0x00
          err = (old - new) >> 3; # divide by 8
          pixels.putpixel((x, y), new)
          # now distribute the error...
          if (x+1) < w:            # x+1, y
              pixels.putpixel((x + 1, y), min(max(pixels.getpixel((x + 1, y)) + err, 0x00), 0xFF))
          if (x+2) < w:           # x+2, y
              pixels.putpixel((x + 2, y), min(max(pixels.getpixel((x + 2, y)) + err, 0x00), 0xFF))
          if x > 0 and (y+1) < h:   # x-1, y+1
              pixels.putpixel((x - 1, y + 1), min(max(pixels.getpixel((x - 1, y + 1)) + err, 0x00), 0xFF))
          if (y+1) < h:           # x, y+1
              pixels.putpixel((x, y + 1), min(max(pixels.getpixel((x, y + 1)) + err, 0x00), 0xFF))
          if (x+1) < w and (y+1) < h: # x+1, y+1
              pixels.putpixel((x + 1, y + 1), min(max(pixels.getpixel((x + 1, y + 1)) + err, 0x00), 0xFF))
          if (y+2) < h:            # x, y+2
              pixels.putpixel((x, y + 2), min(max(pixels.getpixel((x, y + 2)) + err, 0x00), 0xFF))