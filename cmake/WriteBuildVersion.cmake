if(NOT DEFINED SOURCE_DIR OR NOT DEFINED OUTPUT_HEADER OR NOT DEFINED OUTPUT_SOURCE)
  message(FATAL_ERROR "WriteBuildVersion requires SOURCE_DIR, OUTPUT_HEADER, and OUTPUT_SOURCE")
endif()

set(_version "0.0.0.0 (unknown:unknown)")
set(_git_executable "${GIT_EXECUTABLE}")
if(NOT _git_executable OR NOT EXISTS "${_git_executable}")
  find_program(_git_executable NAMES git git.exe)
endif()

if(_git_executable)
  execute_process(
    COMMAND "${_git_executable}" describe --tags --always
    WORKING_DIRECTORY "${SOURCE_DIR}"
    OUTPUT_VARIABLE _git_version
    OUTPUT_STRIP_TRAILING_WHITESPACE
    ERROR_QUIET
    RESULT_VARIABLE _git_result
  )
  if(_git_result EQUAL 0 AND NOT _git_version STREQUAL "")
    set(_version "${_git_version}")
  endif()
endif()

string(REPLACE "\\" "\\\\" _version_cpp "${_version}")
string(REPLACE "\"" "\\\"" _version_cpp "${_version_cpp}")

set(_header_content "#pragma once\n\nnamespace nmsdk\n{\nconst char* build_version() noexcept;\n}\n")
set(_source_content "#include \"NmsdkBuildVersion.h\"\n\nnamespace nmsdk\n{\nconst char* build_version() noexcept\n{\n    return \"${_version_cpp}\";\n}\n}\n")

function(_write_if_different path content)
  get_filename_component(_directory "${path}" DIRECTORY)
  file(MAKE_DIRECTORY "${_directory}")
  if(EXISTS "${path}")
    file(READ "${path}" _existing)
    if(_existing STREQUAL content)
      return()
    endif()
  endif()
  file(WRITE "${path}" "${content}")
endfunction()

_write_if_different("${OUTPUT_HEADER}" "${_header_content}")
_write_if_different("${OUTPUT_SOURCE}" "${_source_content}")
message(STATUS "Nmsdk build version: ${_version}")