if(NOT DEFINED VCPKG_RELEASE_BIN OR NOT DEFINED OUTPUT_DIR OR NOT DEFINED CONFIG)
    message(FATAL_ERROR "DeployVcpkgRuntimeDlls requires VCPKG_RELEASE_BIN, OUTPUT_DIR, and CONFIG")
endif()

set(_source_dir "${VCPKG_RELEASE_BIN}")
if(CONFIG STREQUAL "Debug" AND DEFINED VCPKG_DEBUG_BIN AND EXISTS "${VCPKG_DEBUG_BIN}")
    set(_source_dir "${VCPKG_DEBUG_BIN}")
endif()

if(NOT EXISTS "${_source_dir}")
    message(FATAL_ERROR "Selected vcpkg DLL directory does not exist: ${_source_dir}")
endif()

file(MAKE_DIRECTORY "${OUTPUT_DIR}")
file(GLOB _dll_files "${_source_dir}/*.dll")
foreach(_dll_file IN LISTS _dll_files)
    get_filename_component(_dll_name "${_dll_file}" NAME)
    # Qt DLLs are supplied from the configured Qt installation.
    if(NOT _dll_name MATCHES "^Qt")
        execute_process(
            COMMAND "${CMAKE_COMMAND}" -E copy_if_different
                "${_dll_file}" "${OUTPUT_DIR}/${_dll_name}"
            RESULT_VARIABLE _copy_result
        )
        if(NOT _copy_result EQUAL 0)
            message(FATAL_ERROR "Failed to deploy ${_dll_file} to ${OUTPUT_DIR}")
        endif()
    endif()
endforeach()

message(STATUS "Deployed ${CONFIG} vcpkg DLLs from ${_source_dir}")
