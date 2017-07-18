from distutils.core import setup
from Cython.Build import cythonize

setup(
    name = "atk_mod",
    version = 0.0,
    ext_modules = cythonize("atk_mod_a.pyx")
)
