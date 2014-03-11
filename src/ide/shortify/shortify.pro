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
    widgets/common/widgetfiledownloader.cpp

HEADERS  += mainwindow.h \
    widgets/common/settings/settingsmanager.h \
    widgets/common/scripts/widgeteditor.h \
    widgets/common/widgetfiledownloader.h \
    gui_types.h

FORMS    += mainwindow.ui \
    widgets/common/scripts/dialogrunadvanced.ui \
    widgets/common/scripts/scripts.ui \
    widgets/common/scripts/widgeteditor.ui \
    widgets/common/scripts/widgetgotopanel.ui \
    widgets/common/scripts/widgetscriptlibrary.ui \
    widgets/common/scripts/widgettoolspanel.ui

DEFINES += SCI_NAMESPACE

INCLUDEPATH +=  3rdparty/scintilla/qt/ScintillaEditBase 3rdparty/scintilla/include 3rdparty/scintilla/src 3rdparty/scintilla/lexlib

unix: {
    mac: {
        #QMAKE_LFLAGS += -static-libgcc -static-libstdc++
        #QMAKE_LIBS += ../support/drivers/cs_usb_driver.so
        #DEFINES += SQLITE_HAS_CODEC CODEC_TYPE=CODEC_TYPE_AES256
        LIBS += -framework ScintillaEditBase
        QMAKE_LFLAGS += -F../gringo/3rdparty/scintilla/bin

        libScintillaEditBase.path = Contents/Frameworks
        libScintillaEditBase.files = ../gringo/3rdparty/scintilla/bin/ScintillaEditBase.framework
        QMAKE_BUNDLE_DATA += libScintillaEditBase
        QMAKE_LFLAGS_SONAME = -Wl,-install_name,@executable_path/../Frameworks/
    }
}
