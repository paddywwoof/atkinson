# atkinson
*Experiments making shared libraries using ctypes and or numpy and or cython*

Following a questions on raspberry pi forum https://www.raspberrypi.org/forums/viewtopic.php?f=32&t=188181
I tried various ways of implementing the fairly simple functionality of the module here
https://github.com/migurski/atkinson

Hopefully these notes can be used by others as a template for adding external compiled
functions to their python applications. This is a summary of the speed improvements, the
non-accelerated version of the code (see atk_python.py) takes 120 to 180 times as long to
run. The simplest increase in speed comes from using numba which gets round the whole
complexity of compiling modules at a stroke!


``` bash
20,400ms for non-accelerated PIL Image pixel manipulation 
   140ms for 1a vanilla C version using ctypes, passing PIL.tobytes
   138ms for 1b vanilla C version using ctypes, passing numpy array
   127ms for 2a numba @njit decorator on numpy array
   116ms for 2b cython version using standard import passing numpy array
   118ms for 3 standard C python module import passing PIL.tobytes
   115ms for 4a vanilla rust version using ctypes, passing PIL.tobytes
   116ms for 4b vanilla rust version using ctypes, passing numpy array
   169ms for 4c python module using rust pyo3 passing numpy array
```

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

2. Using python converted to C:

  2.a First using numba which is very simple. You need to have numba
  installed
  

  ``` bash
  # on raspbian I had to
  # sudo apt-get install llvm
  # before this..
  pip3 install numba --user
  ```

  ``` python
  from numba import njit

  @njit
  def  adderror(b, e):
  return min(max(b + e, 0x00), 0xFF) 

  @njit(cache=True)
  def atk(pixels):
  h = pixels.shape[0]
  w = pixels.shape[1]
  ...
  ```

  2.b Using cython code `atk_mod_a.pyx` compiled to a python module (shared 
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

  imported into python without
  ctypes or numpy (i.e. 

  ``` python
  from PIL import Image

  import python_module.atk
  im = Image.open('lenna_l2.png')

  img = im.tobytes()
  python_module.atk.atk(im.size[0], im.size[1], img)
  Image.frombytes('L', im.size, img).save('lenna_bw.png')
  ```

4. Using Rust as in the sub-directory `rust`. The project was created using
`cargo new rust` in the top directory then Cargo.toml edited and src/lib.rs
relatively easily (for someone new to rust!) modified from the cython code.
A noticeable difference is the explicit casting between i32, u8 and usize.

  ``` bash
  cd rust
  cargo build --release
  cd ..
  ```

  The option using pyo3 is in the subdirectory pyo3_module. Although there is,
  in theory, the option of using setup.py --inplace as with cython and the
  standard python module, at the moment that route seems to make setup.py
  default to creating a debug version.

  ``` bash
  # pyo3 has to use nightly
  rustup install nightly
  rustup default nightly
  # 
  cd pyo3_module
  cargo build --release
  mv target/release/libatk_mod_rm.so ../atk_mod_rm.so
  cd ..
  ```

  i.e. The file gets a lib stuck on the begining of its name which has to be
  removed!

  The alternative is to generate a wheel file as below, which would make sense for
  distributing, but for local experimenting you might not want to install it so
  you would have to extract the module file from the created `dist/atk_mod_rm-etc-etc.whl/atk_mod_rm/`
  (essentially the wheel is just a zip file) and paste it into top level directory.

  ``` bash
  python3 setup.py bdist_wheel
  ```
  
  The pyo3 module is a little bit slower than the C python one but it is simpler
  and safer in that bounds checking happens and processing is done using the
  rust ndarray crate - which, as with cython and numba, allows lots of other
  functionality to be easily accessed in the module.

Although the size pyx file is similar to C, the shared object file produced by 
cython is much bigger. However it does run slightly faster than the standard
python module written in C and the vanilla C version using ctypes.CDLL
and using cython keeps the option of using other numpy (highly 
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
accessed via ctypes. Slowest is the rust library build with pyo3, which is interesting.
Maybe.