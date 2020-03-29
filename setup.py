#!/usr/bin/env python
"""
Copyright (c) 2017-2019, Jairus Martin.
Distributed under the terms of the GPL v3 License.
The full license is in the file COPYING.txt, distributed with this software.
Created on Dec 13, 2017
"""
import re
import sys
from setuptools import setup, find_packages


requirements = [
    'enaml>=0.10.4',
    'jsonpickle',
    'qtconsole',
    'QScintilla',
    'numpydoc',
    'markdown',
    'enamlx',
    'qt-reactor',
    'pyserial',
    'lxml',
    'PyQt5',
    'PyQtWebEngine',
]

if sys.platform == 'win32':
    requirements.extend([
        'pywin32',
        'git',
        'service_identity',
    ])



def find_version():
    with open('declaracad/__init__.py') as f:
        for line in f:
            m = re.search(r'version = [\'"](.+)["\']', line)
            if m:
                return m.group(1)
    raise Exception("Could not find version in declaracad/__init__.py")


setup(
    name='declaracad',
    version=find_version(),
    description='Parametric 3D modeling with enaml and OpenCascade',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='CodeLV',
    author_email='frmdstryr@gmail.com',
    license='GPL3',
    url='https://github.com/codelv/declaracad',
    entry_points={'console_scripts': [
        'declaracad = declaracad:main',
    ]},
    packages=find_packages(),
    install_requires=requirements,
)
