from distutils.core import setup, Extension
setup(name='application1', version='1.0', ext_modules=[Extension('hist', ['hist.c'])])
