#!/usr/bin/env python


from distutils.core import setup


setup(name='pkssh',
      version='0.1',
      description='Python SSH utils',
      author='Cristian Stoica',
      author_email='crististm@gmail.com',
      py_modules=['pkssh'],
      license='GPLv2',
      requires=['paramiko'],
      )
