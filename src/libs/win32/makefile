PATH_VCEXPRESS := "C:/Program Files (x86)/Microsoft Visual Studio 10.0/Common7/IDE/vcexpress.EXE"

all:
	vcvars32.bat && ${PATH_VCEXPRESS} /build release cairo_access.sln
	cp Release/_cairo_access.pyd ../.
	cp *.dll ../.
