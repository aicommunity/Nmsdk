# Общие опции и переменные окружения, ранее задавались в RdkDefines.pri

option(RDK_USE_PYTHON "Use Python integration" OFF)
option(RDK_USE_DARKNET "Use Darknet integration" OFF)
option(RDK_USE_TENSORFLOW "Use Tensorflow integration" OFF)
option(RDK_USE_OPENCV "Use OpenCV" OFF)
option(RDK_USE_CUDA "Use CUDA" OFF)
option(RDK_USE_SQL "Use Qt SQL" OFF)
option(RDK_USE_ODESOLVER "Use ODE solver" OFF)
option(RDK_USE_MATLAB "Use MATLAB" OFF)

# Проверка существования папки ode-solver
if(RDK_USE_ODESOLVER)
  if(NOT EXISTS "${CMAKE_SOURCE_DIR}/Rdk/ThirdParty/ode-solver")
    message(STATUS "ode-solver directory not found, disabling RDK_USE_ODESOLVER")
    set(RDK_USE_ODESOLVER OFF CACHE BOOL "Use ODE solver" FORCE)
  endif()
endif()

add_compile_definitions(RDK_UNICODE_RUN RDK_QT QT_NO_VERSION_TAGGING)

if (MSVC)
  add_compile_definitions(NOMINMAX)
  # Отключаем предупреждения для MSVC
  add_compile_options(/W4 /wd4996)
  # Используем многопоточную DLL библиотеку времени выполнения для совместимости с vcpkg
  set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<IF:$<CONFIG:Debug>,Debug,>DLL" CACHE STRING "")
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
# Сначала пытаемся найти Boost через find_package (работает с vcpkg)
# Временно очищаем BOOST_PATH, чтобы find_package использовал vcpkg
set(BOOST_PATH_SAVED ${BOOST_PATH})
unset(BOOST_PATH CACHE)
find_package(Boost QUIET COMPONENTS program_options thread filesystem system chrono atomic)
if (Boost_FOUND)
  # Boost найден через find_package (vcpkg) - используем его
  # Не используем BOOST_PATH, чтобы избежать конфликтов версий компилятора
  message(STATUS "Boost found via find_package (vcpkg): ${Boost_VERSION}")
else()
  # Восстанавливаем BOOST_PATH для fallback
  set(BOOST_PATH ${BOOST_PATH_SAVED} CACHE PATH "Path to Boost root")
  if (BOOST_PATH)
    # Если find_package не нашел Boost, используем BOOST_PATH (fallback)
    include_directories(${BOOST_PATH} ${BOOST_PATH}/include)
    link_directories(${BOOST_PATH}/lib)
    message(STATUS "Boost found via BOOST_PATH: ${BOOST_PATH}")
  endif()
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
  elseif(WIN32)
    # Windows: попытка найти Python через find_package или стандартные пути
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

# CUDA (минимальная интеграция)
if (RDK_USE_CUDA)
  add_compile_definitions(GPU)
  if (WIN32)
    # Windows: стандартные пути для CUDA
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

# Windows-специфичные настройки
if (WIN32)
  # Qt через vcpkg или стандартные пути
  if (NOT Qt5_FOUND)
    find_package(Qt5 QUIET COMPONENTS Core)
  endif()
  
  # OpenCV через vcpkg (если не задан путь вручную)
  if (RDK_USE_OPENCV AND NOT DEFINED OPENCV4_PATH AND NOT DEFINED OPENCV3_PATH)
    find_package(OpenCV QUIET)
    if (OpenCV_FOUND)
      add_compile_definitions(OPENCV_FOUND)
    endif()
  endif()
endif()


