#!/usr/bin/env python

from setuptools import setup

setup(name='gomoku',
      description='Gomoku server',
      license='BSD',
      version='1.0',
      author='Alexander Solovyov',
      author_email='alexander@solovyov.net',
      url='http://github.com/piranha/gomoku/',
      install_requires=['tornado', 'opster'],
      packages=['gomoku'],

      entry_points={
        'console_scripts': ['gomoku=gomoku.main:main.command']
        },

      classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Utilities',
        ],
      platforms='any',
      )
