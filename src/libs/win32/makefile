PATH_VCEXPRESS := "C:/Program Files/Microsoft Visual Studio 10.0/Common7/IDE/vcexpress.EXE"

# If this is a 64 bit machine then fix the path to visual studio
TEST = $(shell ls "C:/Program Files (x86)/Microsoft Visual Studio 10.0/Common7/IDE/VCExpress.exe")
ifneq ("$(TEST)", "")
     override PATH_VCEXPRESS := ${TEST}
endif


all:
	vcvars32.bat && "${PATH_VCEXPRESS}" /build release cairo_access.sln
	cp Release/_cairo_access.pyd ../.
	cp *.dll ../.
