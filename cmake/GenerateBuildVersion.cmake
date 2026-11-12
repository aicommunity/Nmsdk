include_guard(GLOBAL)

function(nmsdk_add_build_version target_name)
  if(NOT TARGET ${target_name})
    message(FATAL_ERROR "nmsdk_add_build_version: unknown target ${target_name}")
  endif()

  find_package(Git QUIET)
  set(_git_executable "")
  if(Git_FOUND)
    set(_git_executable "${GIT_EXECUTABLE}")
  endif()

  file(TO_CMAKE_PATH "${CMAKE_BINARY_DIR}/generated/nmsdk_build_version" _version_dir)
  set(_version_header "${_version_dir}/NmsdkBuildVersion.h")
  set(_version_source "${_version_dir}/NmsdkBuildVersion.cpp")

  if(NOT TARGET nmsdk_generate_build_version)
    add_custom_target(nmsdk_generate_build_version
      COMMAND "${CMAKE_COMMAND}"
        "-DGIT_EXECUTABLE=${_git_executable}"
        "-DSOURCE_DIR=${CMAKE_SOURCE_DIR}"
        "-DOUTPUT_HEADER=${_version_header}"
        "-DOUTPUT_SOURCE=${_version_source}"
        -P "${CMAKE_SOURCE_DIR}/cmake/WriteBuildVersion.cmake"
      BYPRODUCTS "${_version_header}" "${_version_source}"
      COMMENT "Generating Nmsdk build version"
      VERBATIM
    )
  endif()

  set_source_files_properties("${_version_source}" PROPERTIES GENERATED TRUE)
  add_dependencies(${target_name} nmsdk_generate_build_version)
  target_sources(${target_name} PRIVATE "${_version_source}")
  target_include_directories(${target_name} PRIVATE "${_version_dir}")
  target_compile_definitions(${target_name} PRIVATE NMSDK_GENERATED_BUILD_VERSION=1)
endfunction()