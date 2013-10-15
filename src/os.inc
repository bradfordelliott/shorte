include version.inc

uname := $(shell uname)

cairo_path := libs/unix
echo       := echo
mkdir      := mkdir
archive    := tar -czf shorte.linux64.${version}.tar.gz *

ifeq ("$(uname)", "Darwin")
    SHELL      := /bin/bash
	cairo_path := libs/osx
    echo       := echo
	mkdir      := mkdir
	archive    := tar -czf shorte.osx.${version}.tar.gz *
endif

ifeq ("$(uname)", "CYGWIN_NT-6.1")
	cairo_path := libs/cygwin
    echo       := echo
	mkdir      := mkdir
	archive    := tar -czf shorte.${version}.tar.gz *
endif

ifeq ("$(uname)", "windows32")
	cairo_path := libs/win32
    echo       := gecho
	mkdir      := gmkdir
	archive    := zip -R shorte.win32.${version}.zip *
endif
