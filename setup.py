#! /usr/bin/env python3
# -*- coding:Utf8 -*-

#--------------------------------------------------------------------------------------------------------------
# All necessary import:
#--------------------------------------------------------------------------------------------------------------
import os, sys, glob

#  try:
    #  import InitialCond
#  except ImportError:
    #  print("You need the InitialCond package for some import part of the module.")
    #  sys.exit(-1)

try:
    import numpy as np
except ImportError:
    print("Numpy is a needed dependancy.")
    sys.exit(-1)

try:
    import matplotlib
except ImportError:
    print("You really need matplotlib")
    sys.exit(-1)

#from setuptools import find_packages
import setuptools as st
from distutils.core import setup
from distutils.command.install_data import install_data

from Cython.Distutils.extension import Extension
from Cython.Distutils import build_ext
from Cython.Build import cythonize

#--------------------------------------------------------------------------------------------------------------
# For adding support of pkg-config:
#--------------------------------------------------------------------------------------------------------------
def pkgconfig(*packages, **kw):
    flag_map = {'-I': 'include_dirs', '-L': 'library_dirs', '-l': 'libraries'}
    for token in commands.getoutput("pkg-config --libs --cflags %s" % ' '.join(packages)).split():
        kw.setdefault(flag_map.get(token[:2]), []).append(token[2:])
        return kw

def scandir(dir, files=[]):
    for file in os.listdir(dir):
        path = os.path.join(dir, file)
        if os.path.isfile(path) and path.endswith(".pyx"):
            files.append(path.replace(os.path.sep, ".")[:-4])
        elif os.path.isdir(path):
            scandir(path, files)
            return files

def makeExtension(extName, test=False, **kwargs):
    """
    Create an extension for Cython with the path for the
    directory in which .pyx files are presents.
    """
    extPath = [extName.replace(".", os.path.sep) + ".pyx"]
    cfile = extName.split(".")
    dir = os.path.join(*cfile[:-1])
    cfile = glob.glob(os.path.join(dir, "c*.c"))
    extPath += cfile

    opt_dict = dict(
        include_dirs=["."],   # adding the '.' to include_dirs is CRUCIAL!!
        extra_compile_args=["-std=c99"],
        extra_link_args=['-g'],
        libraries=[],
        cython_include_dirs=[
            os.path.join(
                os.getenv("HOME"),
                '.local/lib/python' + ".".join(
                    [str(a) for a in sys.version_info[:2]]
                ) + '/site-packages/Cython/Includes'
            )
        ]
    )

    for key in kwargs.keys():
        if key in opt_dict:
            opt_dict[key] += kwargs[key]
        else:
            opt_dict[key] = kwargs[key]

    if test:
        return extPath, opt_dict
    else:
        return Extension(
            extName,
            extPath,
            **opt_dict
        )

#  def makeExtension(extName, test=False, **kwargs):
    #  extPath = [ extName.replace(".", os.path.sep)+".pyx" ]
    #  cfile   = extName.split(".")
    #  dir     = os.path.join(*cfile[:-1])
    #  cfile   = "c" + cfile[-1] + ".c"
    #  cfile   = os.path.join(dir, cfile)

    #  if os.path.isfile(cfile):
        #  extPath += [ cfile ]

    #  opt_dict = dict(
        #  include_dirs = ["."],   # adding the '.' to include_dirs is CRUCIAL!!
        #  extra_compile_args = ["-fopenmp", "-std=c99"], #, "-DP_DBG_TREECODE_P_CALC2"],
        #  extra_link_args = ['-fopenmp'],
        #  libraries = [],
        #  cython_include_dirs = [
            #  King.get_include(),
            #  #os.path.join(os.getenv("HOME"), '.local/lib/python' + ".".join([ str(a) for a in sys.version_info[:2]]) + '/site-packages/Cython/Includes')
        #  ]
    #  )

    #  for key in kwargs.keys():
        #  if key in opt_dict:
            #  opt_dict[ key ] += kwargs[ key ]
        #  else:
            #  opt_dict[ key ] = kwargs[ key ]

    #  if test:
        #  return extPath, opt_dict
    #  else:
        #  return Extension(
            #  extName,
            #  extPath,
            #  **opt_dict
        #  )

extNames = scandir("LibThese")

#extensions = [makeExtension(name, include_dirs = [ "include/" ]) for name in extNames]
extensions = []
for name in extNames:
    extensions.append(
        makeExtension(
            name,
            cython_directives={
                "embedsignature": True,
            }
        )
    )
    #  if "Gadget" in name or "Types" in name or "Tree" in name:
        #  opt = pkgconfig("iogadget")
        #  if "include_dirs" in opt:
            #  opt["include_dirs"] += [ "include/" ]
        #  else:
            #  opt["include_dirs"]  = [ "include/" ]
            #  opt["include_dirs"] += [ np.get_include() ]
            #  opt["cython_directives"] = {
                #  "embedsignature" : True,
                #  "language_level" : 3
            #  }
            #  extensions.append( makeExtension(name, **opt) )
    #  else:
        #  extensions.append(
            #  makeExtension(
                #  name,
                #  include_dirs = [ "include/" ],
                #  cython_directives = {
                    #  "embedsignature" : True,
                    #  "language_level" : 3
                #  }
            #  )
        #  )

print(extensions, extNames, sep='\n')

#--------------------------------------------------------------------------------------------------------------
# Packages names:
#--------------------------------------------------------------------------------------------------------------
#  packages = [ 'LibThese', 'LibThese.Carte', 'LibThese.Data', 'LibThese.dir', 'LibThese.Gadget', 'LibThese.Models', 'LibThese.Physics', 'LibThese.Plot', 'LibThese.Pretty', 'LibThese.Utils' ]
packages = st.find_packages()

#--------------------------------------------------------------------------------------------------------------
# Call the setup function:
#--------------------------------------------------------------------------------------------------------------
setup(
    name        = 'LibThese',
    version     = '2.0',
    description = 'Python Module for analysis gadget simulation.',
    author      = 'Guillaume Plum',
    packages    = packages,
    cmdclass    = {'install_data': install_data, 'build_ext': build_ext},
    data_files  = [
        ('share/LibThese/animation-plugins', ["share/LibThese/animation-plugins/__init__.py"]), #glob.glob("share/LibThese/animation-plugins/*.py")),
        ('share/LibThese/', ["share/LibThese/config.yml", "share/LibThese/filter.yml"]), #glob.glob("share/LibThese/animation-plugins/*.py")),
    ],
    scripts     = [
        'scripts/animationv2.py',
        'scripts/models_plot.py',
        'scripts/roi.py',
        'scripts/verif_python.py',
    ],
    ext_modules = cythonize(
        extensions ,
        include_path = [ '.' ]
    ),
)

#vim:spelllang=
