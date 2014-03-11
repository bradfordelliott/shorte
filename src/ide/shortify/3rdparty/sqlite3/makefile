include ../../../bin/tools.inc

ifeq ("$(os)","windows32")
	override target=vcvars32.bat && \
		cl /O2 /I. /D_WINDOWS /Fesqlite3e.exe \
		/DCODEC_TYPE=CODEC_TYPE_AES256 \
		/DSQLITE_HAS_CODEC \
		sqlite3secure.c shell.c
else
    ifeq ("$(os)","CYGWIN_NT-5.1")
    else
		override target=/usr/bin/gcc -o sqlite3e \
		    -D CODEC_TYPE=CODEC_TYPE_AES256 \
		    -D SQLITE_HAS_CODEC \
		    -DSQLITE_ENABLE_EXTFUNC \
		    -I . sqlite3secure.c shell.c \
                    -lpthread -lm -ldl
    endif
endif

# Build the version of SQLite that supports encyrpted
# datatabases. Use AES256 by default because it looks like
# it forces the more secure SHA hashing algorithm for
# the key
sqlite:
	echo ${os}
	${target}

sqlite3lib:
	${targetlib}
