TEMPLATE = subdirs

CONFIG += ordered

include($$PWD/../../../Rdk/Build/Lib/Qt/RdkDefines.pri)


defineReplace(addSubdirsRdkNmsdk) {
    for(name, 1) {
        SUBDIRS += $$name
        eval($${name}.file = $$PWD/../../../Libraries/$${name}/Build/Qt/$${name}.pro)
        export($${name}.file)
    }
    export(SUBDIRS)
    return(1)
}

Rdk_Nmsdk_libs = Rdk-BasicLib \
        Rdk-CvBasicLib \
        Rdk-HardwareLib \
        Nmsdk-MotionControlLib \
        Nmsdk-PulseLib \

contains(DEFINES, RDK_USE_PYTHON) {
  Rdk_Nmsdk_libs += Rdk-PyMachineLearningLib
}

contains(DEFINES, RDK_USE_DARKNET) {
  Rdk_Nmsdk_libs += Rdk-DarknetLib
}

contains(DEFINES, RDK_USE_TENSORFLOW) {
  Rdk_Nmsdk_libs += Rdk-TensorflowLib
}

SUBDIRS +=  rdk-static-qt
rdk-static-qt.file = $$PWD/../../../Rdk/Build/Lib/Qt/rdk.static.qt.pro

$$addSubdirsRdkNmsdk($$Rdk_Nmsdk_libs)


windows {
    SUBDIRS += curl
    curl.file = $$PWD/../../../Rdk/ThirdParty/curl/build/qt/curl.pro
}


SUBDIRS += $$PWD/../NeuroModeler/NeuroModeler.pro
SUBDIRS += $$PWD/../NeuroModelerConsole/NeuroModelerConsole.pro
