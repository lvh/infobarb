#!/usr/bin/env python

from distutils.core import setup

setup(name='infobarb',
      version='0',
      description='Twisted-based modular IRC bot',
      author='Laurens Van Houtven',
      author_email='_@lvh.cc',
      url='https://github.com/lvh/infobarb',
      packages=['infobarb', 'infobarb.test'],
      license='ISC',
      classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Framework :: Twisted",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Topic :: Communications :: Chat :: Internet Relay Chat",
        ])
