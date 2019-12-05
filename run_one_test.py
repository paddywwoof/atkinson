import timeit

N = 1

setup = '''
from PIL import Image

PATH = '/home/pi/atkinson/'
import atk_python
im = Image.open(PATH + 'lenna_l2.png')
'''


funcs = [
['basic python loops with PIL.Image.getpixel()','''
atk_python.atk(im)
im.save('lenna10_bw.png')
''']]
for f in funcs:
  print('{:.0f}ms for {}'.format(timeit.timeit(f[1], setup=setup, number=N) * 1000 / N, f[0]))
