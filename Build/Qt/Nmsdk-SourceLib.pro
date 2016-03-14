#-------------------------------------------------
#
# Project created by QtCreator 2012-11-11T15:17:55
#
#-------------------------------------------------

QT       -= gui

TARGET = Nmsdk-SourceLib.qt
TEMPLATE = lib
CONFIG += staticlib

DEFINES += LIBRDK_LIBRARY_EXPORT
DEFINES += RDK_UNICODE_RUN
DEFINES += RDK_QT
INCLUDEPATH += $$PWD/../../../../Rdk/Deploy/Include

unix {
    target.path = /usr/lib
    INSTALLS += target
    DESTDIR = $$PWD/../../../../Bin/Platform/Unix/Lib.Qt
}

windows {
    DESTDIR = $$PWD/../../../../Bin/Platform/Win/Lib.Qt
}

HEADERS += \
    ../../Core/NConstGenerator.h \
    ../../Core/NControlObjectSource.h \
    ../../Core/NFileGenerator.h \
    ../../Core/NManipulatorSource.h \
    ../../Core/NManipulatorSourceEmulator.h \
    ../../Core/NPulseGenerator.h \
    ../../Core/NSinusGenerator.h \
    ../../Core/NSourceLibrary.h

SOURCES += \
    ../../Core/NConstGenerator.cpp \
    ../../Core/NControlObjectSource.cpp \
    ../../Core/NFileGenerator.cpp \
    ../../Core/NManipulatorSource.cpp \
    ../../Core/NManipulatorSourceEmulator.cpp \
    ../../Core/NPulseGenerator.cpp \
    ../../Core/NSinusGenerator.cpp \
    ../../Core/NSourceLibrary.cpp
