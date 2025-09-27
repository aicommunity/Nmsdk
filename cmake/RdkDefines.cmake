# Общие опции и переменные окружения, ранее задавались в RdkDefines.pri

option(RDK_USE_PYTHON "Use Python integration" OFF)
option(RDK_USE_DARKNET "Use Darknet integration" OFF)
option(RDK_USE_TENSORFLOW "Use Tensorflow integration" OFF)
option(RDK_USE_OPENCV "Use OpenCV" OFF)
option(RDK_USE_CUDA "Use CUDA" OFF)
option(RDK_USE_SQL "Use Qt SQL" OFF)
option(RDK_USE_ODESOLVER "Use ODE solver" OFF)
option(RDK_USE_MATLAB "Use MATLAB" OFF)

add_compile_definitions(RDK_UNICODE_RUN RDK_QT QT_NO_VERSION_TAGGING)

if (MSVC)
  add_compile_definitions(NOMINMAX)
endif()

# Пути окружения (могут быть заданы через -D)
set(BOOST_PATH "$ENV{BOOST_PATH}" CACHE PATH "Path to Boost root")
set(OPENCV3_PATH "$ENV{OPENCV3_PATH}" CACHE PATH "Path to OpenCV3 root")
set(OPENCV4_PATH "$ENV{OPENCV4_PATH}" CACHE PATH "Path to OpenCV4 root")
set(ANACONDA_PATH "$ENV{ANACONDA_PATH}" CACHE PATH "Path to Anaconda root")
set(TENSORFLOW_PATH "$ENV{TENSORFLOW_PATH}" CACHE PATH "Path to Tensorflow root")

# OpenCV
if (RDK_USE_OPENCV)
  if (DEFINED OPENCV4_PATH)
    set(OpenCV_DIR "${OPENCV4_PATH}")
  elseif(DEFINED OPENCV3_PATH)
    set(OpenCV_DIR "${OPENCV3_PATH}")
  endif()
  find_package(OpenCV QUIET)
  if (OpenCV_FOUND)
    add_compile_definitions(OPENCV_FOUND)
    include_directories(${OpenCV_INCLUDE_DIRS})
  endif()
endif()

# Boost
if (BOOST_PATH)
  include_directories(${BOOST_PATH} ${BOOST_PATH}/include)
  link_directories(${BOOST_PATH}/lib)
endif()
find_package(Threads REQUIRED)

# Python/NumPy через Boost.Python (упрощённо)
if (RDK_USE_PYTHON)
  add_compile_definitions(BOOST_PYTHON_STATIC_LIB BOOST_NUMPY_STATIC_LIB)
  if (ANACONDA_PATH)
    include_directories(
      ${ANACONDA_PATH}/include
      ${ANACONDA_PATH}/lib/python3/site-packages/numpy/core/include
    )
    link_directories(${ANACONDA_PATH}/lib)
  else()
    include_directories(/usr/include/python3 /usr/include/python3/numpy)
  endif()
endif()

# CUDA (минимальная интеграция)
if (RDK_USE_CUDA)
  add_compile_definitions(GPU)
  include_directories(/usr/local/cuda/include)
endif()

# Tensorflow (placeholders)
if (RDK_USE_TENSORFLOW AND TENSORFLOW_PATH)
  include_directories(
    ${TENSORFLOW_PATH}
    ${TENSORFLOW_PATH}/bazel-bin/tensorflow
    ${TENSORFLOW_PATH}/bazel-tensorflow/external/eigen_archive
    ${TENSORFLOW_PATH}/bazel-tensorflow/external/protobuf_archive/src
    ${TENSORFLOW_PATH}/bazel-tensorflow/external/com_google_protobuf/src
    ${TENSORFLOW_PATH}/bazel-tensorflow/external/com_google_absl
  )
endif()


