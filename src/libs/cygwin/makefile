platform=$(shell uname -o)
os=$(shell cat /etc/redhat-release)
arch=$(shell uname -m)

ver_swig:= 2.0.1
ver_python:= 2.6.6

prefix=/usr
export CC:=/usr/bin/gcc
export CXX:=/usr/bin/g++
export LDFLAGS:= -L$(prefix)/lib -L$(prefix)/tools/python/Python-${ver_python}/lib
export CFLAGS:=-I$(prefix)/include -I$(prefix)/include/ncurses -I${prefix}/include/cairo
export PATH:=${prefix}/bin:${prefix}/lib:${PATH}
export LD_LIBRARY_PATH:=${prefix}/lib:${LD_LIBRARY_PATH}

swig:=swig
pyconfig:=python-config

cairodir:= /usr/include/cairo
extension:=.dll

python:
	$(swig) -c++ -python ../cairo_access.i 
	$(CXX) -o _cairo_access${extension} \
		../cairo_access_wrap.cxx \
        `$(pyconfig) --cflags` \
		-DHAVE_CONFIG_H -DHAS_CAIRO \
		-I${cairodir} \
        `$(pyconfig) --ldflags` \
		-shared -Wall -fPIC \
		-lstdc++ -lcairo
	cp _cairo_access${extension} ..

clean:
	rm -rf sample
	rm -rf cairo_access${extension} _cairo_access${extension}
	rm -rf cairo_access_wrap.*
