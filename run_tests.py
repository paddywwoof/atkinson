import timeit
setup = '''
import ctypes
from PIL import Image
import numpy as np

PATH = '/home/patrick/raspberry_pi/atkinson/'
atklib = ctypes.CDLL(PATH + 'atk.so')
atklib_r = ctypes.CDLL(PATH + 'rust/target/release/libatk_mod_r.so')
import atk_mod_a
import python_module.atk
im = Image.open(PATH + 'lenna_l2.png')
'''
funcs = [['1a vanilla C version using ctypes, passing PIL.tobytes','''
img = im.tobytes()
atklib.atk(im.size[0], im.size[1], 
           ctypes.c_char_p(img))
Image.frombytes('L', im.size, img).save('lenna2_bw.png')
'''],['1b vanilla C version using ctypes, passing numpy array','''
img = np.array(im)
atklib.atk(img.shape[0], img.shape[1], 
           img.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte)))
Image.fromarray(img).save('lenna2_bw.png')
'''],['2 cython version using standard import passing numpy array','''
img = np.array(im)
atk_mod_a.atk(img)
Image.fromarray(img).save('lenna2_bw.png')
'''],['3 standard python module import passing PIL.tobytes','''
img = im.tobytes()
python_module.atk.atk(im.size[0], im.size[1], img)
Image.frombytes('L', im.size, img).save('lenna_bw.png')
'''],['4a vanilla rust version using ctypes, passing PIL.tobytes','''
img = im.tobytes()
atklib_r.atk(im.size[0], im.size[1], 
           ctypes.c_char_p(img))
Image.frombytes('L', im.size, img).save('lenna2_bw.png')
'''],['4b vanilla rust version using ctypes, passing numpy array','''
img = np.array(im)
atklib_r.atk(img.shape[0], img.shape[1],
           img.ctypes.data_as(ctypes.POINTER((ctypes.c_ubyte))),)
Image.fromarray(img).save('lenna3_bw.png')
''']]
for f in funcs:
  print('{:5.3f}s for 10x {}'.format(timeit.timeit(f[1], setup=setup, number=10), f[0]))

