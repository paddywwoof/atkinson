import timeit
setup = '''
import ctypes
from PIL import Image
import numpy as np

PATH = '/home/patrick/raspberry_pi/atkinson/'
atklib = ctypes.CDLL(PATH + 'atk.so')
import atk_mod_a
im = Image.open(PATH + 'lenna_l2.png')
'''
funcs = ['''
img = np.array(im)
atklib.atk(img.shape[0], img.shape[1], 
           img.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte)))
Image.fromarray(img).save('lenna2_bw.png')
''','''
img = im.tobytes()
atklib.atk(im.size[0], im.size[1], 
           ctypes.c_char_p(img))
Image.frombytes('L', im.size, img).save('lenna2_bw.png')
''','''
img = np.array(im)

atk_mod_a.atk(img)
Image.fromarray(img).save('lenna2_bw.png')
''']
for f in funcs:
  print(timeit.timeit(f, setup=setup, number=10))

