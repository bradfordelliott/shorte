#-------------------------------------------------
#
# Project created by QtCreator 2014-03-07T14:06:35
#
#-------------------------------------------------

QT       += core network gui

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

TARGET = shortify
TEMPLATE = app


SOURCES += main.cpp\
        mainwindow.cpp \
    3rdparty/sqlite3/sqlite3secure.c \
    widgets/common/settings/settingsmanager.cpp \
    widgets/common/scripts/widgeteditor.cpp \
    widgets/common/widgetfiledownloader.cpp \
    widgets/common/settings/dialogsettingsmanager.cpp

HEADERS  += mainwindow.h \
    widgets/common/settings/settingsmanager.h \
    widgets/common/scripts/widgeteditor.h \
    widgets/common/widgetfiledownloader.h \
    gui_types.h \
    widgets/common/settings/dialogsettingsmanager.h

FORMS    += mainwindow.ui \
    widgets/common/scripts/dialogrunadvanced.ui \
    widgets/common/scripts/scripts.ui \
    widgets/common/scripts/widgeteditor.ui \
    widgets/common/scripts/widgetgotopanel.ui \
    widgets/common/scripts/widgetscriptlibrary.ui \
    widgets/common/scripts/widgettoolspanel.ui \
    widgets/common/settings/dialogsettingsmanager.ui

DEFINES += SCI_NAMESPACE

INCLUDEPATH +=  3rdparty/scintilla/qt/ScintillaEditBase 3rdparty/scintilla/include 3rdparty/scintilla/src 3rdparty/scintilla/lexlib 3rdparty/sqlite3

unix: {
    mac: {
        #QMAKE_LFLAGS += -static-libgcc -static-libstdc++
        #QMAKE_LIBS += ../support/drivers/cs_usb_driver.so
        #DEFINES += SQLITE_HAS_CODEC CODEC_TYPE=CODEC_TYPE_AES256
        LIBS += -framework ScintillaEditBase
        QMAKE_LFLAGS += -F../shortify/3rdparty/scintilla/bin

        libScintillaEditBase.path = Contents/Frameworks
        libScintillaEditBase.files = ../shortify/3rdparty/scintilla/bin/ScintillaEditBase.framework
        QMAKE_BUNDLE_DATA += libScintillaEditBase
        QMAKE_LFLAGS_SONAME = -Wl,-install_name,@executable_path/../Frameworks/
    }
}

win32: {
    win32-g++: {
        QMAKE_LIBS += -L../shortify/3rdparty/scintilla/bin/ -lScintillaEditBase3
    } else {
        QMAKE_LIBS += ../shortify/3rdparty/scintilla/bin/ScintillaEditBase3.lib
    }

    DEFINES += SCINTILLA_QT=1 SCI_LEXER=1 _CRT_SECURE_NO_DEPRECATE=1
}

# Build the Scintilla DLL in MinGW
win32-g++: {

scintillalib.target = scintilla

CONFIG(release, debug|release) {
    scintillalib.commands = cd ../shortify/3rdparty/scintilla/qt/ScintillaEditBase && \
                        ${QMAKE} ScintillaEditBase.pro -r -spec win32-g++ && \
                        mingw32-make -f Makefile release release-install && \
                        cp -f ../../bin/ScintillaEditBase3.dll $$OUT_PWD/. && \
                        echo "Done building debug scintilla.";
} else {
    scintillalib.commands = cd ../shortify/3rdparty/scintilla/qt/ScintillaEditBase && \
                        ${QMAKE} ScintillaEditBase.pro -r -spec win32-g++ && \
                        mingw32-make -f Makefile debug debug-install && \
                        cp -f ../../bin/ScintillaEditBase3.dll $$OUT_PWD/. && \
                        echo "Done building debug scintilla.";
}

scintillalib.depends =
QMAKE_EXTRA_TARGETS += scintillalib
PRE_TARGETDEPS = scintilla

}

SUBDIRS += \
    3rdparty/scintilla/qt/ScintillaEditBase/ScintillaEditBase.pro

RESOURCES += \
    shortify.qrc
