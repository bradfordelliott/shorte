include version.inc

uname := $(shell uname)
os    := ${uname}

cairo_path := libs/unix
echo       := echo
mkdir      := mkdir
archive    := tar -czf shorte.linux64.${version}.tar.gz *
libdir     := libs/unix

ifeq ("$(uname)", "Darwin")
    SHELL      := /bin/bash
	cairo_path := libs/osx
    echo       := echo
	mkdir      := mkdir
	archive    := tar -czf shorte.osx.${version}.tar.gz *
    libdir     := libs/osx
endif

ifeq ("$(uname)", "CYGWIN_NT-6.1")
	cairo_path := libs/cygwin
    echo       := echo
	mkdir      := mkdir
	archive    := tar -czf shorte.${version}.tar.gz *
    libdir     := libs/cygwin
endif

ifeq ("$(uname)","CYGWIN_NT-6.3")
	cairo_path := libs/cygwin
    echo       := echo
	mkdir      := mkdir
	archive    := tar -czf shorte.${version}.tar.gz *
    libdir     := libs/cygwin
endif

ifeq ("$(uname)", "windows32")
	cairo_path := libs/win32
    echo       := gecho
	mkdir      := gmkdir
	archive    := zip -R shorte.win32.${version}.zip *
    libdir     := libs/win32
endif

python:=python
python-config:=python-config

ifneq ("${PATH_PYTHON}","")
    override python:=${PATH_PYTHON}/python
    override python-config:=${PATH_PYTHON}/python-config
endif

swig:=swig
ifneq ("${PATH_SWIG}","")
    override swig:=${PATH_SWIG}/swig
endif
