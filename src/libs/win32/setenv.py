#!/usr/bin/env python
import os

path_visual_studio = "C:/Program Files (x86)/Microsoft Visual Studio 10.0"
if(not os.path.exists(path_visual_studio)):
    path_visual_studio = "C:/Program Files/Microsoft Visual Studio 10.0"

path_swig = "C:/usr/tools/swig/swig.exe"
path_python = "C:/usr/tools/python"
if(not os.path.exists(path_python)):
    path_python = "C:/usr/tools/python27"

print "set PATH_VISUAL_STUDIO=%s&& " % path_visual_studio
print "set PATH_VCEXPRESS=%s/Common7/IDE/vcexpress.EXE&& " % path_visual_studio
print "set PATH_VCVARS=%s/VC/bin/vcvars32.bat&& " % path_visual_studio
print "set PATH_PYTHON=%s&& " % path_python
print "set PATH_SWIG=%s" % path_swig
