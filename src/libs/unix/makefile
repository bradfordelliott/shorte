platform=$(shell uname -o)
os=$(shell cat /etc/redhat-release)
arch=$(shell uname -m)

ver_swig:= 2.0.1
ver_python:= 2.6.6

ifeq ("${platform}","Cygwin")
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
else
    ifeq ("${os}","Red Hat Enterprise Linux WS release 4 (Nahant Update 7)")
        prefix=/home/belliott/modules/${arch}/rhel4
        export CC:=/usr/bin/gcc
        export CXX:=/usr/bin/g++
        export LDFLAGS:= -L$(prefix)/lib
        export CFLAGS:=-I$(prefix)/include -I$(prefix)/include/ncurses
        export PATH:=${prefix}/bin:${prefix}/lib:${PATH}
        export LD_LIBRARY_PATH:=${prefix}/lib:${LD_LIBRARY_PATH}
        export RHEL:=rhel4
    else
        ifeq ("${os}","CentOS release 6.4 (Final)")
            prefix=/home/belliott/modules/${arch}/rhel6
            export CC:=/usr/bin/gcc
            export CXX:=/usr/bin/g++
            export LDFLAGS:= -L$(prefix)/lib
            export CFLAGS:=-I$(prefix)/include -I$(prefix)/include/ncurses
            export PATH:=${prefix}/bin:${prefix}/lib:${PATH}
            export LD_LIBRARY_PATH:=${prefix}/lib:${LD_LIBRARY_PATH}
            export RHEL:=rhel6
        else
            prefix=/home/belliott/modules/${arch}/rhel5
            export CC:=/usr/bin/gcc34
            export CXX:=/usr/bin/g++34
            export LDFLAGS:= -L/usr/lib/gcc/x86_64-redhat-linux/3.4.6/ -L$(prefix)/lib
            export CFLAGS:=-I$(prefix)/include -I$(prefix)/include/ncurses
            export RHEL:=rhel5
	    endif
    endif

    # Paths for Linux
    cairodir := /home/belliott/modules/${arch}/${RHEL}/include/cairo
    swig := /home/belliott/modules/${arch}/${RHEL}/tools/swig/swig-2.0.5/bin/swig
    pyconfig:=/auto/tools/common/c5b64/activestate/ActivePython-2.7.2.5/bin/python-config
    extension:=.so

endif


python:
	$(swig) -c++ -python ../cairo_access.i 
	$(CXX) -o _cairo_access${extension} \
		../cairo_access_wrap.cxx \
        `$(pyconfig) --cflags` \
		-DHAVE_CONFIG_H -DHAS_CAIRO \
		-I${cairodir} \
        `$(pyconfig) --ldflags` \
		-shared -Wall -fPIC \
                ${LDFLAGS} \
		-lstdc++ -lcairo
	cp ../cairo_access.py ../../.
	cp _cairo_access${extension} ../../.

clean:
	rm -rf sample
	rm -rf cairo_access${extension} _cairo_access${extension}
	rm -rf cairo_access_wrap.*
