#-------------------------------------------------
#
# Project created by QtCreator 2016-07-25T14:35:21
#
#-------------------------------------------------

QT       += core
QT       -= gui
greaterThan(QT_MAJOR_VERSION, 4): QT += network


QT      += sql
QT      += xml
QT      += serialport


#greaterThan(QT_MAJOR_VERSION, 4): QT += widgets #printsupport

TARGET = NeuroModelerConsole
TEMPLATE = app

VERSION = 1.1.3.0
include($$PWD/../../../Rdk/Build/Lib/Qt/RdkDefines.pri)

windows {
message("NeuroModelerConsole: using "msvc-$$(VisualStudioVersion) compiler)
DESTDIR = $$PWD/../../../Bin/Platform/Win/
    LIBS += -L$$(ANACONDA_PATH)/libs/

} else {
DESTDIR = $$PWD/../../../Bin/Platform/Linux/
}

windows:msvc {
 QMAKE_CXXFLAGS += /bigobj
}

CONFIG -= debug_and_release debug_and_release_target
CONFIG += c++17
CONFIG -= app_bundle
CONFIG += console

DEFINES += QT_DLL QT_WIDGETS_LIB

CVS_VERSION = 0 # $$system(hg parents --template '{rev}')
DEFINES += RDK_APP_VERSION=$$CVS_VERSION

DEFINES += "RDK_APP_URL=\\\"https://neuromodeler.ru\\\""
DEFINES += "RDK_APP_LICENSE=\"\\\"There is a public domain software (2000-2023)\\\"\""
DEFINES += "RDK_APP_NAME=\"\\\"Neuro Modeler\\\"\""


contains(DEFINES, RDK_USE_ODESOLVER) {
  windows {
    ODESOLVER_DEPLOY_DIR = $$PWD/../../../Bin/Platform/Win
    ODESOLVER_LINKER_LINE = -L$$ODESOLVER_DEPLOY_DIR -lode-solver

  } else:unix {
    ODESOLVER_DEPLOY_DIR = $$PWD/../../../Bin/Platform/Linux
    ODESOLVER_LINKER_LINE = -L$$ODESOLVER_DEPLOY_DIR -lode-solver
  }

  CMAKE_PROJECT_DIR = $$PWD/../../../Rdk/ThirdParty/ode-solver
  CMAKE_BUILD_DIR = $$PWD/ode-solver-build

  configure_cmake.target = configure_cmake
  configure_cmake.commands = \
      cmake -S $$CMAKE_PROJECT_DIR -B $$CMAKE_BUILD_DIR "-D DEPLOY_DIR=$$ODESOLVER_DEPLOY_DIR"
  QMAKE_EXTRA_TARGETS += configure_cmake

  build_cmake.target = build_cmake
  build_cmake.depends = configure_cmake
  build_cmake.commands = \
      cmake --build $$CMAKE_BUILD_DIR
  QMAKE_EXTRA_TARGETS += build_cmake

  PRE_TARGETDEPS += $$build_cmake.target
}

INCLUDEPATH += ../../../Gui/Qt \
    ../../../Deploy/Include \
    ../../../Rdk/Core/Graphics \
    GeneratedFiles \
    GeneratedFiles/Debug \
    ../../../Rdk/Deploy/Include \
    ../../../Rdk/GUI/Qt

unix {
INCLUDEPATH += /usr/local/include
}

MOC_DIR = GeneratedFiles/release

OBJECTS_DIR = release

UI_DIR = GeneratedFiles

RCC_DIR = GeneratedFiles

#including our libs
NMSDK_LIBS_NAMES = \
 Rdk-BasicLib \
 Rdk-CvBasicLib \
 Rdk-HardwareLib \
 Nmsdk-MotionControlLib \
 Nmsdk-PulseLib \
 rdk.static

contains(DEFINES, RDK_USE_PYTHON) {
  NMSDK_LIBS_NAMES += Rdk-PyMachineLearningLib
}

contains(DEFINES, RDK_USE_DARKNET) {
  NMSDK_LIBS_NAMES += Rdk-DarknetLib
}

contains(DEFINES, RDK_USE_TENSORFLOW) {
  NMSDK_LIBS_NAMES += Rdk-TensorflowLib
}

windows:!windows-g++ {

 for(lib, NMSDK_LIBS_NAMES) {
  NMSDK_LIBS_LIST += -l$${lib}.qt
  NMSDK_LIBS_FILES += $$PWD/../../../Bin/Platform/Win/Lib.Qt/$${lib}.qt.lib
 }

 LIBS += -L$$PWD/../../../Bin/Platform/Win/Lib.Qt/ $$NMSDK_LIBS_LIST -lcurl.qt
 LIBS +=   -lWldap32 -lWs2_32 -lCrypt32
 PRE_TARGETDEPS += $$NMSDK_LIBS_FILES

} else:unix {

 for(lib, NMSDK_LIBS_NAMES) {
  NMSDK_LIBS_LIST += -l$${lib}.qt
  NMSDK_LIBS_FILES += $$PWD/../../../Bin/Platform/Linux/Lib.Qt/lib$${lib}.qt.a
 }
 LIBS += -L$$PWD/../../../Bin/Platform/Linux/Lib.Qt/ $$NMSDK_LIBS_LIST
 PRE_TARGETDEPS += $$NMSDK_LIBS_FILES
}

SOURCES += \
        ../../../Libraries/Libraries.cpp \
        main.cpp \ #\
    ../../../Rdk/GUI/Qt/UEngineControlQt.cpp


HEADERS += \
        ../../../Libraries/Libraries.h \
    ../../../Rdk/GUI/Qt/UEngineControlQt.h

#FORMS   += \


# �������� OpenCV
contains(DEFINES, RDK_USE_OPENCV) {

    windows {
        LIBS += $$OPENCV_WIN_LINKER_LINE

    } else:unix {
        LIBS += $$OPENCV_UNIX_LINKER_LINE
    }
}

contains(DEFINES, RDK_USE_ODESOLVER) {
    LIBS += $$ODESOLVER_LINKER_LINE
}

#Boost
windows {
    LIBS += $$BOOST_WIN_LINKER_LINE
} else:unix {
    LIBS += $$BOOST_UNIX_LINKER_LINE
}

contains(DEFINES, RDK_USE_DARKNET) {
    unix {
        LIBS+= $$DARKNET_UNIX_LINKER_LINE
    }
}

contains(DEFINES, RDK_USE_TENSORFLOW) {
    windows {
        LIBS += $$TENSORFLOW_WIN_LINKER_LINE
    } else:unix {
        LIBS += $$TENSORFLOW_UNIX_LINKER_LINE
    }
}

contains(DEFINES,RDK_USE_MATLAB) {
    windows {
        LIBS += $$MATLAB_WIN_LINKER_LINE
    } else:unix {
        LIBS += $$MATLAB_UNIX_LINKER_LINE
    }
}

