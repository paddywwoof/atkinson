# atkinson
*Experiments making shared libraries using ctypes and or numpy and or cython*

Following a questions on raspberry pi forum https://www.raspberrypi.org/forums/viewtopic.php?f=32&t=188181
I tried various ways of implementing the fairly simple functionality of the module here
https://github.com/migurski/atkinson

1. Using a simplified version of the migurski C code `atk_mod.c` compiled to a shared object using:
``` bash
gcc -shared -o atk.so -fPIC atk_mod.c
```
(NB or Win or OSX equivalents using alternative compilers, not tried) to produce the shared object `atk.so`
which can then be imported in python using `ctypes.CDLL` and passed the image array to work on either using:

1.a  `tobytes()` like this
``` python
import ctypes
from PIL import Image

PATH = '/home/patrick/raspberry_pi/atkinson/'
atklib = ctypes.CDLL(PATH + 'atk.so')
im = Image.open(PATH + 'lenna_l2.png')
img = im.tobytes()
atklib.atk(im.size[0], im.size[1], 
           ctypes.c_char_p(img))
Image.frombytes('L', im.size, img).save('lenna2_bw.png')
```
1.b or `fromarray()` with numpy like this
``` python
import ctypes
from PIL import Image
import numpy as np

PATH = '/home/patrick/raspberry_pi/atkinson/'
from atk_mod_a import atk as atk2
im = Image.open(PATH + 'lenna_l2.png')
img = np.array(im)
atklib.atk(img.shape[0], img.shape[1], 
           img.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte)))
Image.fromarray(img).save('lenna2_bw.png')
```

2. Using cython code `atk_mod_a.pyx` compiled to a python module (shared library) using the `setup.py` file run with:
``` bash
python3 setup.py build_ext --inplace
```
imported into python without resorting to ctypes
``` python
from PIL import Image
import numpy as np
import atk_mod_a
PATH = '/home/patrick/raspberry_pi/atkinson/'

img = np.array(Image.open(PATH + 'lenna_l2.png'))
atk_mod_a.atk(img)
Image.fromarray(img).save('lenna2_bw.png')

```
Although the cython file is much bigger it does run faster than the vanilla C version and keeps the option of using other
numpy (highly optimised) functionality inside the function if needed. (Note the decorator to remove bounds checking that might
need to be removed if the function was designed to do anything more complicated)
