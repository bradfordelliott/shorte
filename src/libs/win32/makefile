PATH_VCEXPRESS := "C:/Program Files (x86)/Microsoft Visual Studio 10.0/Common7/IDE/vcexpress.EXE"
ifeq ($(wildcard $(PATH_VCEXPRESS)),)
PATH_VCEXPRESS := "C:/Program Files/Microsoft Visual Studio 10.0/Common7/IDE/vcexpress.EXE"
endif

all:
	vcvars32.bat && ${PATH_VCEXPRESS} /build release cairo_access.sln
	cp Release/_cairo_access.pyd ../.
	cp *.dll ../.
