import timeit
setup = '''
from PIL import Image

PATH = '/home/patrick/raspberry_pi/atkinson/'
import atk
im = Image.open(PATH + 'lenna_l2.png')
'''
funcs = ['''
img = im.tobytes()
atk.atk(im.size[0], im.size[1], img)
Image.frombytes('L', im.size, img).save('lenna_bw.png')
''',]
for f in funcs:
  print(timeit.timeit(f, setup=setup, number=10))

