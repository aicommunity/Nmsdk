if(NOT ACTIVE_CONFIG STREQUAL "Debug")
    return()
endif()

file(GLOB _debug_dll_files "${SOURCE_DIR}/*.dll")
foreach(_dll_file IN LISTS _debug_dll_files)
    get_filename_component(_dll_name "${_dll_file}" NAME)
    if(NOT _dll_name MATCHES "^Qt")
        execute_process(
            COMMAND "${CMAKE_COMMAND}" -E copy_if_different
                "${_dll_file}"
                "${DEST_DIR}/${_dll_name}"
            RESULT_VARIABLE _copy_result
        )
        if(NOT _copy_result EQUAL 0)
            message(FATAL_ERROR "Failed to deploy Debug DLL ${_dll_name}: ${_copy_result}")
        endif()
    endif()
endforeach()
