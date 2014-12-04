platform=$(shell uname -o)
arch=$(shell uname -m)

prefix=/usr
export CC:=gcc
export CXX:=g++
export CFLAGS:=-I$(prefix)/include -I${prefix}/include/cairo
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
