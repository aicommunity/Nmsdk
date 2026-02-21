# DeployVcpkgDlls.cmake
# Function to copy all required DLLs from vcpkg into the output directory

function(deploy_vcpkg_dlls TARGET_NAME)
    if(NOT WIN32)
        return()
    endif()

    # Determine path to vcpkg_installed
    if(DEFINED VCPKG_INSTALLED_DIR)
        set(_vcpkg_installed_dir "${VCPKG_INSTALLED_DIR}")
    elseif(EXISTS "${CMAKE_BINARY_DIR}/vcpkg_installed")
        set(_vcpkg_installed_dir "${CMAKE_BINARY_DIR}/vcpkg_installed")
    else()
        message(WARNING "DeployVcpkgDlls: Cannot find vcpkg_installed directory")
        return()
    endif()

    # Path to vcpkg bin directory
    set(_vcpkg_bin_dir "${_vcpkg_installed_dir}/${VCPKG_TARGET_TRIPLET}/bin")
    set(_vcpkg_debug_bin_dir "${_vcpkg_installed_dir}/${VCPKG_TARGET_TRIPLET}/debug/bin")

    if(NOT EXISTS "${_vcpkg_bin_dir}")
        message(WARNING "DeployVcpkgDlls: vcpkg bin directory not found: ${_vcpkg_bin_dir}")
        return()
    endif()

    # Copy all DLLs from the release bin directory (skip Qt* — Qt is from C:\Qt)
    file(GLOB _dll_files "${_vcpkg_bin_dir}/*.dll")
    foreach(_dll_file IN LISTS _dll_files)
        get_filename_component(_dll_name "${_dll_file}" NAME)
        # Skip debug DLLs (with 'd' suffix before .dll)
        if(NOT _dll_name MATCHES "d\\.dll$")
            # Skip Qt DLLs; they are supplied from C:\Qt into Bin\Platform\Win
            if(NOT _dll_name MATCHES "^Qt")
                add_custom_command(TARGET ${TARGET_NAME} POST_BUILD
                    COMMAND ${CMAKE_COMMAND} -E copy_if_different
                        "${_dll_file}"
                        "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/${_dll_name}"
                    COMMENT "Copying ${_dll_name} to output directory"
                )
            endif()
        endif()
    endforeach()

    # Copy debug DLLs (if they exist); skip Qt* DLLs
    if(EXISTS "${_vcpkg_debug_bin_dir}")
        file(GLOB _debug_dll_files "${_vcpkg_debug_bin_dir}/*.dll")
        foreach(_dll_file IN LISTS _debug_dll_files)
            get_filename_component(_dll_name "${_dll_file}" NAME)
            if(NOT _dll_name MATCHES "^Qt")
                add_custom_command(TARGET ${TARGET_NAME} POST_BUILD
                    COMMAND ${CMAKE_COMMAND} -E copy_if_different
                        "${_dll_file}"
                        "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/${_dll_name}"
                    COMMENT "Copying debug ${_dll_name} to output directory"
                )
            endif()
        endforeach()
    endif()

    # Copy Qt WebEngine files, if present
    if(RDK_USE_QT_WEBENGINE)
        # QtWebEngineProcess.exe / QtWebEngineProcessd.exe
        get_filename_component(_vcpkg_root "${_vcpkg_bin_dir}" DIRECTORY)

        # Qt5 layout: tools/qt5/bin
        set(_tools_qt5_bin "${_vcpkg_root}/tools/qt5/bin")
        # Qt6 layout: tools/qt6
        set(_tools_qt6_bin "${_vcpkg_root}/tools/qt6")

        set(_webengine_process_candidates
            "${_vcpkg_bin_dir}/QtWebEngineProcess.exe"
            "${_tools_qt5_bin}/QtWebEngineProcess.exe"
            "${_tools_qt6_bin}/QtWebEngineProcess.exe"
        )

        set(_found_release FALSE)
        foreach(_cand IN LISTS _webengine_process_candidates)
            if(EXISTS "${_cand}")
                add_custom_command(TARGET ${TARGET_NAME} POST_BUILD
                    COMMAND ${CMAKE_COMMAND} -E copy_if_different
                        "${_cand}"
                        "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/QtWebEngineProcess.exe"
                    COMMENT "Copying QtWebEngineProcess.exe from ${_cand}"
                )
                set(_found_release TRUE)
                break()
            endif()
        endforeach()

        # Debug version
        set(_webengine_processd_candidates
            "${_vcpkg_debug_bin_dir}/QtWebEngineProcessd.exe"
            "${_tools_qt5_bin}/QtWebEngineProcessd.exe"
            "${_tools_qt6_bin}/QtWebEngineProcessd.exe"
        )

        foreach(_cand IN LISTS _webengine_processd_candidates)
            if(EXISTS "${_cand}")
                add_custom_command(TARGET ${TARGET_NAME} POST_BUILD
                    COMMAND ${CMAKE_COMMAND} -E copy_if_different
                        "${_cand}"
                        "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/QtWebEngineProcessd.exe"
                    COMMENT "Copying QtWebEngineProcessd.exe from ${_cand}"
                )
                break()
            endif()
        endforeach()

        # Qt WebEngine DLLs (Qt5 and Qt6)
        file(GLOB _webengine_dlls
            "${_vcpkg_bin_dir}/Qt5WebEngine*.dll"
            "${_vcpkg_bin_dir}/Qt6WebEngine*.dll"
            "${_vcpkg_bin_dir}/QtWebEngine*.dll"
        )
        foreach(_dll_file IN LISTS _webengine_dlls)
            get_filename_component(_dll_name "${_dll_file}" NAME)
            add_custom_command(TARGET ${TARGET_NAME} POST_BUILD
                COMMAND ${CMAKE_COMMAND} -E copy_if_different
                    "${_dll_file}"
                    "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/${_dll_name}"
                COMMENT "Copying ${_dll_name}"
            )
        endforeach()

        # WebEngine resources
        get_filename_component(_vcpkg_root "${_vcpkg_bin_dir}" DIRECTORY)
        set(_resources_dir "${_vcpkg_root}/resources")
        if(EXISTS "${_resources_dir}")
            add_custom_command(TARGET ${TARGET_NAME} POST_BUILD
                COMMAND ${CMAKE_COMMAND} -E copy_directory
                    "${_resources_dir}"
                    "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/resources"
                COMMENT "Copying Qt WebEngine resources"
            )
        endif()

        # WebEngine translations
        set(_translations_dir "${_vcpkg_root}/translations")
        if(EXISTS "${_translations_dir}")
            add_custom_command(TARGET ${TARGET_NAME} POST_BUILD
                COMMAND ${CMAKE_COMMAND} -E make_directory "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/translations"
                COMMAND ${CMAKE_COMMAND} -E copy_directory
                    "${_translations_dir}"
                    "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/translations"
                COMMENT "Copying Qt WebEngine translations"
            )
        endif()
    endif()

    message(STATUS "DeployVcpkgDlls: Configured DLL deployment for ${TARGET_NAME}")
endfunction()
