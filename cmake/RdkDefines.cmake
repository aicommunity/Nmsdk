# Common options and environment variables, previously defined in RdkDefines.pri

option(RDK_USE_PYTHON "Use Python integration" OFF)
option(RDK_USE_DARKNET "Use Darknet integration" OFF)
option(RDK_USE_TENSORFLOW "Use Tensorflow integration" OFF)
option(RDK_USE_OPENCV "Use OpenCV" OFF)
option(RDK_USE_CUDA "Use CUDA" OFF)
option(RDK_USE_SQL "Use Qt SQL" OFF)
option(RDK_USE_ODESOLVER "Use ODE solver" OFF)
option(RDK_USE_MATLAB "Use MATLAB" OFF)
option(RDK_USE_LLM "Build RDK LLM assistant module (Rdk/LLM, GUI/Llm)" OFF)
option(RDK_LLM_BUILD_EMBEDDED "Build embedded llama.cpp provider (requires RDK_USE_LLM)" OFF)

# Check that the ode-solver directory exists
if(RDK_USE_ODESOLVER)
  if(NOT EXISTS "${CMAKE_SOURCE_DIR}/Rdk/ThirdParty/ode-solver")
    message(STATUS "ode-solver directory not found, disabling RDK_USE_ODESOLVER")
    set(RDK_USE_ODESOLVER OFF CACHE BOOL "Use ODE solver" FORCE)
  endif()
endif()

add_compile_definitions(RDK_UNICODE_RUN RDK_QT QT_NO_VERSION_TAGGING)

if (MSVC)
  add_compile_definitions(NOMINMAX)
  # Disable warnings for MSVC
  add_compile_options(/W4 /wd4996)
  # Use multi-threaded DLL runtime library for compatibility with vcpkg
  set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<IF:$<CONFIG:Debug>,Debug,>DLL" CACHE STRING "")
endif()

# Environment paths (can be set via -D)
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
# On Windows use CONFIG mode (for vcpkg), on Linux the regular mode (for system packages)
set(BOOST_PATH_SAVED ${BOOST_PATH})
unset(BOOST_PATH CACHE)

if(WIN32)
  # Windows: use MODULE mode for vcpkg
  # CONFIG mode searches for libraries with vc143 (VS2022) suffix, but vcpkg provides vc140
  # MODULE mode (FindBoost.cmake) correctly determines vc140 library names
  # Warnings about newer Boost versions are not critical and do not affect functionality
  find_package(Boost QUIET COMPONENTS program_options thread filesystem system chrono atomic)
  if (Boost_FOUND)
    message(STATUS "Boost found via find_package (vcpkg): ${Boost_VERSION}")
    message(STATUS "Boost libraries: ${Boost_LIBRARIES}")
  endif()
else()
  # Linux: use MODULE mode (default) for system packages
  find_package(Boost QUIET COMPONENTS program_options thread filesystem system chrono atomic)
  if (Boost_FOUND)
    message(STATUS "Boost found via find_package (system): ${Boost_VERSION}")
  endif()
endif()

# Fallback to BOOST_PATH if find_package did not find Boost
if (NOT Boost_FOUND)
  set(BOOST_PATH ${BOOST_PATH_SAVED} CACHE PATH "Path to Boost root")
  if (BOOST_PATH)
    include_directories(${BOOST_PATH} ${BOOST_PATH}/include)
    link_directories(${BOOST_PATH}/lib)
    message(STATUS "Boost found via BOOST_PATH: ${BOOST_PATH}")
  endif()
endif()
find_package(Threads REQUIRED)

# Python/NumPy via Boost.Python (simplified)
if (RDK_USE_PYTHON)
  add_compile_definitions(BOOST_PYTHON_STATIC_LIB BOOST_NUMPY_STATIC_LIB)
  if (ANACONDA_PATH)
    include_directories(
      ${ANACONDA_PATH}/include
      ${ANACONDA_PATH}/lib/python3/site-packages/numpy/core/include
    )
    link_directories(${ANACONDA_PATH}/lib)
  elseif(WIN32)
    # Windows: try to find Python via find_package or standard paths
    find_package(Python3 QUIET COMPONENTS Interpreter Development NumPy)
    if (Python3_FOUND)
      include_directories(${Python3_INCLUDE_DIRS})
      if (Python3_NumPy_FOUND)
        include_directories(${Python3_NumPy_INCLUDE_DIRS})
      endif()
    endif()
  else()
    include_directories(/usr/include/python3 /usr/include/python3/numpy)
  endif()
endif()

# CUDA (minimal integration)
if (RDK_USE_CUDA)
  add_compile_definitions(GPU)
  if (WIN32)
    # Windows: standard locations for CUDA
    if (EXISTS "C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA")
      file(GLOB CUDA_VERSIONS "C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/*")
      if (CUDA_VERSIONS)
        list(SORT CUDA_VERSIONS)
        list(REVERSE CUDA_VERSIONS)
        list(GET CUDA_VERSIONS 0 CUDA_LATEST)
        include_directories("${CUDA_LATEST}/include")
      endif()
    endif()
  else()
    include_directories(/usr/local/cuda/include)
  endif()
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

# Windows-specific settings
if (WIN32)
  # OpenCV via vcpkg (if path is not provided manually)
  if (RDK_USE_OPENCV AND NOT DEFINED OPENCV4_PATH AND NOT DEFINED OPENCV3_PATH)
    find_package(OpenCV QUIET)
    if (OpenCV_FOUND)
      add_compile_definitions(OPENCV_FOUND)
    endif()
  endif()
endif()


