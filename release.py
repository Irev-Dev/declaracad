"""
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the GPL v3 License.

The full license is in the file COPYING.txt, distributed with this software.

Created on Dec 5, 2017

@author
"""
import os
import sys
import importlib
from glob import glob
from os.path import dirname, split, exists
from cx_Freeze import setup, Executable


def find_enaml_files(*modules):
    """ Find .enaml files to include in the zip """
    files = {}
    for name in modules:
        mod = importlib.import_module(name)
        mod_path = dirname(mod.__file__)
        pkg_root = dirname(mod_path)

        for file_type in ['enaml', 'png']:
            for f in glob('{}/**/*.{}'.format(mod_path, file_type),
                          recursive=True):
                pkg = f.replace(pkg_root+os.path.sep, '')
                files[f] = pkg

    return files.items()


def find_data_files(*modules):
    files = {}
    for name in modules:
        mod = importlib.import_module(name)
        mod_path = name#mod.__file__# if hasattr(mod, '__file__') else name
        pkg_root = name#dirname(mod_path)

        for f in glob('{}/**/*.png'.format(mod_path), recursive=True):
            pkg = f.replace(pkg_root+os.path.sep, '')
            files[f] = pkg
    return files.items()


def find_occt_libs():
    """ Find all the libTK*.so files """
    import OCCT
    root = dirname(dirname(dirname(OCCT.__path__[0])))
    print(f'root={root} occt={OCCT.__path__[0]}')
    if sys.platform == 'win32':
        root = os.path.join(root, 'Library', 'lib')
        target = 'lib'
        libs = 'TK*.lib'
    elif sys.platform == 'darwin':
        target = '..'
        libs = 'libTK*.dylib'
    else:
        target = '..'
        libs = 'libTK*.so'
    print(os.listdir(root))

    results = []
    pattern = os.path.join(root, libs)

    for filename in glob(pattern):
        lib = os.path.split(filename)[-1]
        dest = os.path.join(target, lib)
        results.append((filename, dest))
    print(results)
    assert results, "No occt libraries found!"
    return results


setup(
  name='declaracad',
  author="CodeLV",
  author_email="frmdstryr@gmail.com",
  license='GPLv3',
  url='https://github.com/codelv/declaracad/',
  description="A declarative parametric 3D modeling application",
  long_description=open("README.md").read(),
  version='1.0',
  options=dict(
      build_exe=dict(
          packages=[
              'declaracad',
              'enaml.core.compiler_helpers',
              'enaml.core.template_',
              'enaml.scintilla.api',
              'enaml.workbench.core.api',
              'enaml.workbench.ui.ui_plugin',
              'enamlx.widgets.api',
              'markdown',
              'pygments',
              'ipykernel',
              'zmq.utils.garbage',
          ],
          zip_include_packages=[
            'asyncqt',
            'alablaster',
            'curses',
            'dateutil', 'distutils', 'docutils',
            'email',
            'enamlx',
            'encodings',
            'ezdxf',
            'IPython',
            'http',
            'json', 'jsonpickle', 'jupyter_client', 'jupyter_core',
            'logging',
            'numpydoc',
            'parso', 'pygments',  'pytest', 'pluggy', 'ply', 'prompt_toolkit',
            'pytz', 'pydoc_data', 'pycparsre', 'ptyprocess',
            'qtpy', 'qtconsole',
            'sqlite3', 'sphinx', 'serial', 'scipy',
            'traitlets', 'tornado', 'toml', 'test',
            'unittest', 'urllib',
            'wcwidth',
            'xml', 'xmlrpc',
          ],
          zip_includes=find_enaml_files('enaml'),
          include_files=find_occt_libs(),
          excludes=[
              'wx',
              'tkinter',
              'enamlx.qt.qt_occ_viewer',
              'zmq.eventloop.minitornado',
          ],
      )
  ),
  executables=[
      Executable('main.py',
                 targetName='declaracad',
                 base='Win32GUI' if sys.platform == 'win32' else None)
  ]
)
