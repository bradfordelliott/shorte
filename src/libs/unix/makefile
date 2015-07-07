include os.inc
platform=$(shell uname -o)
os=$(shell cat /etc/redhat-release)
arch=$(shell uname -m)

ifeq ("${os}","Red Hat Enterprise Linux WS release 4 (Nahant Update 7)")
    export RHEL:=rhel4
else
    ifeq ("${os}","CentOS release 6.4 (Final)")
        export RHEL:=rhel6
    else
        export RHEL:=rhel5
	endif
endif

# Paths for Linux
#cairodir := /home/belliott/modules/${arch}/${RHEL}/include/cairo
cairodir :=/usr/include/cairo
extension:=.so

python:
	cp ../cairo_access.i .
	${swig} -c++ -python cairo_access.i 
	$(CXX) -o _cairo_access${extension} \
		cairo_access_wrap.cxx \
        `$(python-config) --cflags` \
		-DHAVE_CONFIG_H -DHAS_CAIRO \
		-I${cairodir} \
        `${python-config} --ldflags` \
		-shared -Wall -fPIC \
                ${LDFLAGS} \
		-lstdc++ -lcairo

clean:
	rm -rf sample
	rm -rf cairo_access${extension} _cairo_access${extension}
	rm -rf cairo_access_wrap.*
