
gcc:=gcc
g++:=g++
python:=/usr/bin/python
python_config:=/usr/bin/python-config
swig:=/usr/local/bin/swig

args:=  -fPIC -Wall -I. -Iplatform -I/opt/local/include/cairo

all:
	cp ../cairo_access.i .
	${swig} -c++ -Iplatform -I. -DRELEASE_PLATFORM -DCS_LITTLE_ENDIAN -DCS_HAS_PYTHON -DCS_HAS_FILESYSTEM -DHAS_CAIRO -python cairo_access.i
	${g++} ${args} -o cairo_access_wrap.o -DHAVE_CONFIG_H -DHAS_CAIRO `${python_config} --cflags` -c cairo_access_wrap.cxx
	${g++} -g -o _cairo_access.so -shared cairo_access_wrap.o -L`${python_config} --prefix`/lib `${python_config} --ldflags` -L/opt/local/lib -lcairo -lcairo-gobject

