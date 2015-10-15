PATH_VCEXPRESS := "${PATH_VISUAL_STUDIO}/Common7/IDE/devenv.EXE"
PATH_VCVARS    := "${PATH_VISUAL_STUDIO}/VC/bin/vcvars32.bat"

all:
	cd cairo && unzip -o cairo_sources.zip
	cp ../cairo_access.i .
	${PATH_VCVARS} && ${PATH_VCEXPRESS} /build release cairo_access.sln
	cp Release/_cairo_access.pyd .
	cp cairo/bin/*.dll .
