# Parallel build defaults for Nmsdk (Qt Creator, cmake --build, presets).
# ENV{CMAKE_BUILD_PARALLEL_LEVEL} set at configure time does not apply to later
# "cmake --build" invocations from the IDE; Unix Makefiles need -j on make itself.

include(ProcessorCount)
ProcessorCount(_nmsdk_processor_count)
if(_nmsdk_processor_count EQUAL 0)
  set(_nmsdk_processor_count 4)
endif()

if(NOT DEFINED NMSDK_BUILD_PARALLEL_JOBS)
  set(NMSDK_BUILD_PARALLEL_JOBS "${_nmsdk_processor_count}"
      CACHE STRING "Parallel compile jobs (make -jN / cmake --build --parallel)")
endif()

message(STATUS "Parallel build: ${NMSDK_BUILD_PARALLEL_JOBS} jobs "
  "(Qt Creator: Build step Tool arguments '--parallel' and env CMAKE_BUILD_PARALLEL_LEVEL=${NMSDK_BUILD_PARALLEL_JOBS}; "
  "or cmake --build -j ${NMSDK_BUILD_PARALLEL_JOBS})")

if(CMAKE_GENERATOR MATCHES "Visual Studio")
  if(NOT DEFINED CMAKE_VS_PARALLEL_BUILD_THREADS)
    set(CMAKE_VS_PARALLEL_BUILD_THREADS "${NMSDK_BUILD_PARALLEL_JOBS}"
        CACHE STRING "Number of parallel build threads for Visual Studio" FORCE)
    message(STATUS "CMAKE_VS_PARALLEL_BUILD_THREADS=${CMAKE_VS_PARALLEL_BUILD_THREADS}")
  endif()
  if(NOT DEFINED CMAKE_VS_GENERATE_DEVENV_LAUNCHER)
    set(CMAKE_VS_GENERATE_DEVENV_LAUNCHER ON
        CACHE BOOL "Generate Visual Studio devenv launcher" FORCE)
  endif()
endif()

if(CMAKE_GENERATOR MATCHES "Unix Makefiles")
  if(NOT NMSDK_REAL_MAKE_PROGRAM)
    if(CMAKE_MAKE_PROGRAM MATCHES "nmsdk-make\\.sh$")
      find_program(NMSDK_REAL_MAKE_PROGRAM NAMES gmake make)
    else()
      set(NMSDK_REAL_MAKE_PROGRAM "${CMAKE_MAKE_PROGRAM}" CACHE FILEPATH "Underlying make for parallel wrapper")
    endif()
  endif()

  if(NMSDK_REAL_MAKE_PROGRAM)
    set(_nmsdk_make_wrapper "${CMAKE_BINARY_DIR}/cmake/nmsdk-make.sh")
    file(MAKE_DIRECTORY "${CMAKE_BINARY_DIR}/cmake")
    configure_file(
      "${CMAKE_CURRENT_LIST_DIR}/nmsdk-make.sh.in"
      "${_nmsdk_make_wrapper}"
      @ONLY
    )
    file(CHMOD "${_nmsdk_make_wrapper}"
         FILE_PERMISSIONS
           OWNER_READ OWNER_WRITE OWNER_EXECUTE
           GROUP_READ GROUP_EXECUTE
           WORLD_READ WORLD_EXECUTE)
    set(CMAKE_MAKE_PROGRAM "${_nmsdk_make_wrapper}"
        CACHE FILEPATH "Parallel make wrapper (-j${NMSDK_BUILD_PARALLEL_JOBS})" FORCE)
    message(STATUS "Unix Makefiles: ${CMAKE_MAKE_PROGRAM} -> ${NMSDK_REAL_MAKE_PROGRAM} -j${NMSDK_BUILD_PARALLEL_JOBS}")
  else()
    message(WARNING "Could not find make; parallel wrapper not installed")
  endif()
endif()
