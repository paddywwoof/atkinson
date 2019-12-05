import timeit

N = 10

setup = '''
import ctypes
from PIL import Image
import numpy as np

PATH = '/home/pi/atkinson/'
atklib = ctypes.CDLL(PATH + 'atk.so')
atklib_r = ctypes.CDLL(PATH + 'rust/target/release/libatk_mod_r.so')
import atk_numba
import atk_mod_a
import python_module.atk
import atk_mod_rm
im = Image.open(PATH + 'lenna_l2.png')
'''


funcs = [['1a vanilla C version using ctypes, passing PIL.tobytes','''
img = im.tobytes()
atklib.atk(im.size[0], im.size[1], 
           ctypes.c_char_p(img))
Image.frombytes('L', im.size, img).save('lenna2_bw.png')
'''],
['1b vanilla C version using ctypes, passing numpy array','''
img = np.array(im)
atklib.atk(img.shape[0], img.shape[1], 
           img.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte)))
Image.fromarray(img).save('lenna3_bw.png')
'''],
['2a numba @njit decorator on numpy array','''
img = np.array(im)
atk_numba.atk(img)
Image.fromarray(img).save('lenna4_bw.png')
'''],
['2b cython version using standard import passing numpy array','''
img = np.array(im)
atk_mod_a.atk(img)
Image.fromarray(img).save('lenna5_bw.png')
'''],
['3 standard C python module import passing PIL.tobytes','''
img = im.tobytes()
python_module.atk.atk(im.size[0], im.size[1], img)
Image.frombytes('L', im.size, img).save('lenna6_bw.png')
'''],
['4a vanilla rust version using ctypes, passing PIL.tobytes','''
img = im.tobytes()
atklib_r.atk(im.size[0], im.size[1], 
           ctypes.c_char_p(img))
Image.frombytes('L', im.size, img).save('lenna7_bw.png')
'''],
['4b vanilla rust version using ctypes, passing numpy array','''
img = np.array(im)
atklib_r.atk(img.shape[0], img.shape[1],
           img.ctypes.data_as(ctypes.POINTER((ctypes.c_ubyte))),)
Image.fromarray(img).save('lenna8_bw.png')
'''],
['4c python module using rust pyo3 passing numpy array','''
img = np.array(im)
atk_mod_rm.atk(img)
Image.fromarray(img).save('lenna9_bw.png')
''']]
for f in funcs:
  print('{:.0f}ms for {}'.format(timeit.timeit(f[1], setup=setup, number=N) * 1000 / N, f[0]))
