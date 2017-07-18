from distutils.core import setup, Extension

atk = Extension('atk',
                    sources = ['atkmodule.c'])

setup (name = 'AtkinsonDither',
       version = '0.0',
       description = 'atkinson dither package',
       ext_modules = [atk])
