DEFINES += "RDK_APP_URL=\\\"https://neuromodeler.ru\\\""
DEFINES += "RDK_APP_LICENSE=\"\\\"There is a public domain software (2000-2023)\\\"\""
DEFINES += "RDK_APP_NAME=\"\\\"Neuro Modeler\\\"\""


#DEFINES += RDK_USE_CUDA
#DEFINES += RDK_USE_PYTHON

unix {
#    DEFINES += RDK_USE_DARKNET
}

#DEFINES += RDK_USE_TENSORFLOW
DEFINES -= RDK_UNICODE_RUN

#DEFINES += RDK_USE_MATLAB

windows:!windows-g++ { # visual studio spec filter
#    QMAKE_CXXFLAGS += /MP /O2
}
