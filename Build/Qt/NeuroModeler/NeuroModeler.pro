#-------------------------------------------------
#
# Project created by QtCreator 2016-07-25T14:35:21
#
#-------------------------------------------------

QT       += core gui charts
QT += network


QT      += sql
QT      += xml


greaterThan(QT_MAJOR_VERSION, 4): QT += widgets printsupport

TARGET = NeuroModeler
TEMPLATE = app

VERSION = 1.0.9.0

include($$PWD/../../../Rdk/Build/Lib/Qt/RdkDefines.pri)

windows {
message("NeuroModeler: using "msvc-$$(VisualStudioVersion) compiler)
DESTDIR = $$PWD/../../../Bin/Platform/Win/
    LIBS += -L$$(ANACONDA_PATH)/libs/

} else {
DESTDIR = $$PWD/../../../Bin/Platform/Linux/
}

windows:msvc {
 QMAKE_CXXFLAGS += /bigobj
}

CONFIG -= debug_and_release debug_and_release_target

DEFINES += QT_DLL QT_WIDGETS_LIB

DEFINES += RDK_DISABLE_EXT_GUI

CVS_VERSION = $$system(hg parents --template '{rev}')
DEFINES += RDK_APP_VERSION=$$CVS_VERSION

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
 Rdk-BasicStatisticLib \
 Rdk-BasicLib \
 Rdk-IoLib \
 Rdk-SourcesLib \
 Rdk-CRLib \
 Rdk-CvAriphmeticLib \
 Rdk-CvBasicLib \
 Rdk-CvDetectionLib \
 Rdk-CvGuiLib \
 Rdk-CvSimulatorLib \
 Rdk-CvStatisticLib \
 Rdk-CvVideoCaptureLib \
 Rdk-NoiseGenLib \
 Nmsdk-ActLib \
 Nmsdk-BasicLib \
 Nmsdk-MathLib \
 Nmsdk-MotionControlLib \
 Nmsdk-NeuronLifeLib \
 Nmsdk-PhysLib \
 Nmsdk-PulseClassicModelsLib \
 Nmsdk-PulseLib \
 Nmsdk-PulseNeuronLib \
 Nmsdk-ReceiverLib \
 Nmsdk-SensorLib \
 Nmsdk-SourceLib \
 rdk.static \
 Nmsdk-YCorticalLib

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
    ../../../Rdk/GUI/Qt/UMatrixForm.cpp \
    ../../../Rdk/GUI/Qt/UWatch.cpp \
    ../../../Rdk/GUI/Qt/UWatchChart.cpp \
    ../../../Rdk/GUI/Qt/UWatchChartOption.cpp \
    ../../../Rdk/GUI/Qt/UWatchSerie.cpp \
    ../../../Rdk/GUI/Qt/UWatchSeriesOption.cpp \
    ../../../Rdk/GUI/Qt/UWatchTab.cpp \
        main.cpp\
    ../../../Rdk/GUI/Qt/UComponentsListWidget.cpp \
    ../../../Rdk/GUI/Qt/UGEngineControllWidget.cpp \
    ../../../Rdk/GUI/Qt/UVisualControllerWidget.cpp \
    ../../../Rdk/GUI/Qt/UDrawEngineWidget.cpp \
    ../../../Rdk/GUI/Qt/UDrawEngineImageWidget.cpp \
    ../../../Rdk/GUI/Qt/UClassesListWidget.cpp \
    ../../../Rdk/GUI/Qt/UComponentLinksWidget.cpp \
    ../../../Rdk/GUI/Qt/UImagesWidget.cpp \
    ../../../Rdk/GUI/Qt/USingleImageWidget.cpp \
    ../../../Rdk/GUI/Qt/UComponentPropertySelectionWidget.cpp \
    ../../../Rdk/GUI/Qt/UPropertyXMLWidget.cpp \
    ../../../Rdk/GUI/Qt/UCalculationChannelsWidget.cpp \
    ../../../Rdk/GUI/Qt/UEngineControlQt.cpp \
    ../../../Rdk/GUI/Qt/ULoggerWidget.cpp \
    ../../../Rdk/GUI/Qt/UCreateConfigurationWizardWidget.cpp \
    ../../../Rdk/GUI/Qt/UImageLoader.cpp \
    ../../../Rdk/GUI/Qt/UCreateTestWidget.cpp \
    ../../../Rdk/GUI/Qt/UComponentPropertyChanger.cpp \
    ../../../Rdk/GUI/Qt/UStatusPanel.cpp \
    ../../../Rdk/GUI/Qt/USingleImagePainter.cpp \
    ../../../Rdk/GUI/Qt/qcustomplot.cpp \
    ../../../Rdk/GUI/Qt/UGraphWidget.cpp \
    ../../../Rdk/GUI/Qt/UGraphControlDialog.cpp \
    ../../../Rdk/GUI/Qt/UGraphPaintWidget.cpp \
    ../../../Rdk/GUI/Qt/UTableInfo.cpp \
    ../../../Rdk/GUI/Qt/UWatchFormWidget.cpp \
    ../../../Rdk/GUI/Qt/UWatchSettingsDialog.cpp \
    ../../../Rdk/GUI/Qt/UTcpServerControlWidget.cpp \
    ../../../Rdk/GUI/Qt/UCurlFtpClientTestWidget.cpp


HEADERS += \
        ../../../Libraries/Libraries.h \
    ../../../Rdk/GUI/Qt/UComponentsListWidget.h \
    ../../../Rdk/GUI/Qt/UGEngineControllWidget.h \
    ../../../Rdk/GUI/Qt/UMatrixForm.h \
    ../../../Rdk/GUI/Qt/UVisualControllerWidget.h \
    ../../../Rdk/GUI/Qt/UDrawEngineWidget.h \
    ../../../Rdk/GUI/Qt/UDrawEngineImageWidget.h \
    ../../../Rdk/GUI/Qt/UClassesListWidget.h \
    ../../../Rdk/GUI/Qt/UComponentLinksWidget.h \
    ../../../Rdk/GUI/Qt/UImagesWidget.h \
    ../../../Rdk/GUI/Qt/USingleImageWidget.h \
    ../../../Rdk/GUI/Qt/UComponentPropertySelectionWidget.h \
    ../../../Rdk/GUI/Qt/UPropertyXMLWidget.h \
    ../../../Rdk/GUI/Qt/UCalculationChannelsWidget.h \
    ../../../Rdk/GUI/Qt/UEngineControlQt.h \
    ../../../Rdk/GUI/Qt/ULoggerWidget.h \
    ../../../Rdk/GUI/Qt/UCreateConfigurationWizardWidget.h \
    ../../../Rdk/GUI/Qt/USingleImagePainter.h \
    ../../../Rdk/GUI/Qt/UImageLoader.h \
    ../../../Rdk/GUI/Qt/UCreateTestWidget.h \
    ../../../Rdk/GUI/Qt/UComponentPropertyChanger.h \
    ../../../Rdk/GUI/Qt/UStatusPanel.h \
    ../../../Rdk/GUI/Qt/USettingsReaderWidget.h \
    ../../../Rdk/GUI/Qt/UWatch.h \
    ../../../Rdk/GUI/Qt/UWatchChart.h \
    ../../../Rdk/GUI/Qt/UWatchChartOption.h \
    ../../../Rdk/GUI/Qt/UWatchSerie.h \
    ../../../Rdk/GUI/Qt/UWatchSeriesOption.h \
    ../../../Rdk/GUI/Qt/UWatchTab.h \
    ../../../Rdk/GUI/Qt/qcustomplot.h \
    ../../../Rdk/GUI/Qt/UGraphWidget.h \
    ../../../Rdk/GUI/Qt/UStructSingleGraph.h \
    ../../../Rdk/GUI/Qt/UGraphControlDialog.h \
    ../../../Rdk/GUI/Qt/UGraphPaintWidget.h \
    ../../../Rdk/GUI/Qt/UTableInfo.h \
    UWatchWidgetForm.h \
    ../../../Rdk/GUI/Qt/UWatchFormWidget.h \
    ../../../Rdk/GUI/Qt/UWatchSettingsDialog.h \
    ../../../Rdk/GUI/Qt/UTcpServerControlWidget.h \
    ../../../Rdk/GUI/Qt/UCurlFtpClientTestWidget.h

FORMS   += \
    ../../../Rdk/GUI/Qt/UComponentsListWidget.ui \
    ../../../Rdk/GUI/Qt/UGEngineControllWidget.ui \
    ../../../Rdk/GUI/Qt/UDrawEngineWidget.ui \
    ../../../Rdk/GUI/Qt/UClassesListWidget.ui \
    ../../../Rdk/GUI/Qt/UComponentLinksWidget.ui \
    ../../../Rdk/GUI/Qt/UImagesWidget.ui \
    ../../../Rdk/GUI/Qt/UMatrixForm.ui \
    ../../../Rdk/GUI/Qt/USingleImageWidget.ui \
    ../../../Rdk/GUI/Qt/UComponentPropertySelectionWidget.ui \
    ../../../Rdk/GUI/Qt/UPropertyXMLWidget.ui \
    ../../../Rdk/GUI/Qt/UCalculationChannelsWidget.ui \
    ../../../Rdk/GUI/Qt/UCreateConfigurationWizardWidget.ui \
    ../../../Rdk/GUI/Qt/UCreateTestWidget.ui \
    ../../../Rdk/GUI/Qt/UComponentPropertyChanger.ui \
    ../../../Rdk/GUI/Qt/UStatusPanel.ui \
    ../../../Rdk/GUI/Qt/UGraphWidget.ui \
    ../../../Rdk/GUI/Qt/UGraphControlDialog.ui \
    ../../../Rdk/GUI/Qt/UGraphPaintWidget.ui \
    ../../../Rdk/GUI/Qt/UTableInfo.ui \
    ../../../Rdk/GUI/Qt/UWatch.ui \
    ../../../Rdk/GUI/Qt/UWatchChart.ui \
    ../../../Rdk/GUI/Qt/UWatchChartOption.ui \
    ../../../Rdk/GUI/Qt/UWatchFormWidget.ui \
    ../../../Rdk/GUI/Qt/UWatchSeriesOption.ui \
    ../../../Rdk/GUI/Qt/UWatchSettingsDialog.ui \
    ../../../Rdk/GUI/Qt/UTcpServerControlWidget.ui \
    ../../../Rdk/GUI/Qt/UCurlFtpClientTestWidget.ui \
    ../../../Rdk/GUI/Qt/UWatchTab.ui


# ???????? OpenCV
contains(DEFINES, RDK_USE_OPENCV) {

    windows {
        CONFIG(debug){
#            message("VideoAnalytics: using OpenCv from "$${OPENCV_LIB_PATH}/Debug)
            LIBS += -L$${OPENCV_LIB_PATH}/Debug $$addPostfix($$OPENCV_LIBS_LIST, $${OPENCV_LIBS_VERSION}d)
        }

        CONFIG(release) {
#            message("VideoAnalytics: using OpenCv from "$${OPENCV_LIB_PATH}/Release)
            LIBS += -L$${OPENCV_LIB_PATH}/Release $$addPostfix($$OPENCV_LIBS_LIST, $${OPENCV_LIBS_VERSION})
        }

    } else:unix {
        LIBS += -L$${OPENCV_LIB_PATH}/lib $$OPENCV_LIBS_LIST
    }
}

#Boost
unix {
    LIBS += -L$$(BOOST_PATH)/lib -lboost_system \
        -lboost_system \
        -lboost_chrono \
        -lboost_thread \
        -lboost_program_options \
        -lboost_filesystem \
        -lboost_date_time \
        -lboost_timer

    LIBS += -L$$(QTDIR)/lib -lQt5Core -lQt5Widgets -lQt5Gui -lQt5PrintSupport -lGL
    LIBS += -L/usr/lib/x86_64-linux-gnu -lcurl

    contains(DEFINES, RDK_USE_PYTHON) {
        LIBS += -L$$(BOOST_PATH)/lib -lboost_python$${RDK_PYTHON_MAJOR}$${RDK_PYTHON_MINOR} \
            -lboost_numpy$${RDK_PYTHON_MAJOR}$${RDK_PYTHON_MINOR}

    isEmpty(ANACONDA_PATH) {
         LIBS += -L/usr/lib/python$${RDK_PYTHON_MAJOR}.$${RDK_PYTHON_MINOR}/config-$${RDK_PYTHON_MAJOR}.$${RDK_PYTHON_MINOR}m-x86_64-linux-gnu -lpython$${RDK_PYTHON_MAJOR}.$${RDK_PYTHON_MINOR}m -lpython$${RDK_PYTHON_MAJOR}.$${RDK_PYTHON_MINOR}
         LIBS += -L/usr/lib/python$${RDK_PYTHON_MAJOR}.$${RDK_PYTHON_MINOR}/config-$${RDK_PYTHON_MAJOR}.$${RDK_PYTHON_MINOR}m-aarch64-linux-gnu -lpython$${RDK_PYTHON_MAJOR}.$${RDK_PYTHON_MINOR}m -lpython$${RDK_PYTHON_MAJOR}.$${RDK_PYTHON_MINOR}
    } else {
         LIBS += -L$$(ANACONDA_PATH)/lib -lpython$${RDK_PYTHON_MAJOR}.$${RDK_PYTHON_MINOR}m -lpython$${RDK_PYTHON_MAJOR} #-lpng -lssl
    }
    }

}

windows {
    BOOST_COMPILED_VERSION = msvc-$$(VisualStudioVersion)

    !contains(QMAKE_TARGET.arch, x86_64) {
        LIBS += -L$$(BOOST_PATH)/$${BOOST_COMPILED_VERSION}-x86/lib/
    } else {
         LIBS += -L$$(BOOST_PATH)/$${BOOST_COMPILED_VERSION}-x64/lib/
    }

    LIBS +=   -lWldap32
    LIBS +=   -lAdvapi32

    LIBS += -L$$(ANACONDA_PATH)/libs/
}


contains(DEFINES, RDK_USE_DARKNET) {
    unix {
        LIBS+= -L$$PWD/../../../Libraries/Rdk-DarknetLib/ThirdParty/darknet -ldarknet
    }
}

contains(DEFINES, RDK_USE_TENSORFLOW) {

    windows {
        LIBS += -L$$(TENSORFLOW_PATH)/bazel-bin/tensorflow -ltensorflow_framework.dll.if -ltensorflow.dll.if -ltensorflow_cc.dll.if
    } else:unix {
        LIBS += -L$$(TENSORFLOW_PATH)/bazel-bin/tensorflow -ltensorflow_cc -ltensorflow_framework
    }

}
