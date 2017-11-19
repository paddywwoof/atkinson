# atkinson
*Experiments making shared libraries using ctypes and or numpy and or cython*

Following a questions on raspberry pi forum https://www.raspberrypi.org/forums/viewtopic.php?f=32&t=188181
I tried various ways of implementing the fairly simple functionality of the module here
https://github.com/migurski/atkinson

Hopefully these notes can be used by others as a template for adding additional
C functionality to their python applications.

1. Using a simplified version of the migurski C code `atk_mod.c` compiled
to a shared object using:

``` bash
gcc -shared -o atk.so -fPIC atk_mod.c
```
  (NB or Win or OSX equivalents using alternative compilers, not tried) to 
  produce the shared object `atk.so` which can then be imported in python 
  using `ctypes.CDLL` and passed the image array to work on either using:

  1.a  `tobytes()` like this
    
``` python
import ctypes
from PIL import Image

atklib = ctypes.CDLL('/path/to/atk.so')
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

atklib = ctypes.CDLL('/path/to/atk.so')
im = Image.open('lenna_l2.png')
img = np.array(im)
atklib.atk(img.shape[0], img.shape[1], 
           img.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte)))
Image.fromarray(img).save('lenna2_bw.png')
```

2. Using cython code `atk_mod_a.pyx` compiled to a python module (shared 
library) using the `setup.py` file run with:

``` bash
python3 setup.py build_ext --inplace
```

  which creates the shared library in the same directory. Check the docs
  for how to build and install more generally, and what you need to do
  on Win or OSX systems.
  https://docs.python.org/3/extending/building.html#building
  This can be imported into python without resorting to ctypes

``` python
from PIL import Image
import numpy as np
import atk_mod_a

img = np.array(Image.open('lenna_l2.png'))
atk_mod_a.atk(img)
Image.fromarray(img).save('lenna2_bw.png')

```

3. Using the standard python module compilation system (*which is what I
originally set out to do*). This is all in the sub-directory `python_module/`. 
There were a few modifications to the original migurski code. The definition 
of the module and methods has changed see `python_module/atkmodule.c`
at the bottom `PyMethodDef`,`PyModuleDef`and `PyMODINIT_FUNC`. More
significantly I couldn't get it to work without importing the
pixels as part of a python object, specifically `PyBytesObject`
which holds the pixel as part of the struct `->ob_sval[]`. NB the revised
argument list to `PyArg_ParseTuple`: `iiS`. It was compiled
using the `setup.py` in the subdirectory with

``` bash
python3 setup.py build_ext --inplace
```

  imported into python without ctypes or numpy (i.e. 

``` python
from PIL import Image

import atk
im = Image.open('lenna_l2.png')

img = im.tobytes()
atk.atk(im.size[0], im.size[1], img)
Image.frombytes('L', im.size, img).save('lenna_bw.png')
```

4. Using Rust as in the sub-directory `rust`. The project was created using
`cargo new rust` in the top directory then Cargo.toml edited and src/lib.rs
relatively easily (for someone new to rust!) modified from the cython code.
A noticeable difference is the explicity casting between i32, u8 and usize.

``` bash
cargo build --release
```
Although the size pyx file is similar to C, the shared object file produced by 
cython is much bigger. However it does run slightly faster than the vanilla 
C version and using cython keeps the option of using other numpy (highly 
optimised) functionality inside the function if needed. (Note the decorator 
to remove bounds checking that might need to be removed if the function 
was designed to do anything more complicated).

The 'standard' python module using `atkmodule.c` is slightly more complicated
than the original in that it needs an additional pointer of `unsigned char*`
for accessing the char array of pixels. But the use of the `PyBytesObject`
is probably safer and reduces the likelyhood of segmentation faults etc.
... Though overwriting the bytes of the immutable bytes object might be
seen as slightly dodgy! This seems to run faster than the vanilla C version
but not quite as fast as the cython. Fastest of all is the rust library
which is interesting.

``` bash
1.593s for 10x 1a vanilla C version using ctypes, passing PIL.tobytes
1.589s for 10x 1b vanilla C version using ctypes, passing numpy array
1.362s for 10x 2 cython version using standard import passing numpy array
1.365s for 10x 3 standard python module import passing PIL.tobytes
1.299s for 10x 4a vanilla rust version using ctypes, passing PIL.tobytes
1.301s for 10x 4b vanilla rust version using ctypes, passing numpy array
``` 
