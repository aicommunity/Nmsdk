include_guard(GLOBAL)
function(deploy_vcpkg_dlls target_name)
  # Configure resource locations for both apps; these are generated machine-local
  # paths, never checked-in absolute paths. Do not overwrite a user's edited ini.
  configure_file("${CMAKE_SOURCE_DIR}/cmake/NmsdkApp.ini.in"
                 "${CMAKE_CURRENT_BINARY_DIR}/${target_name}.ini" @ONLY)
  add_custom_command(TARGET ${target_name} POST_BUILD
    COMMAND "${CMAKE_COMMAND}" "-DSOURCE=${CMAKE_CURRENT_BINARY_DIR}/${target_name}.ini"
      "-DDEST=$<TARGET_FILE_DIR:${target_name}>/${target_name}.ini"
      -P "${CMAKE_SOURCE_DIR}/cmake/InitializeAppIni.cmake" VERBATIM)
  if(NOT WIN32)
    return()
  endif()
  set_property(TARGET ${target_name} APPEND PROPERTY LINK_DEPENDS
    "${CMAKE_SOURCE_DIR}/cmake/DeployVcpkgDlls.cmake"
    "${CMAKE_SOURCE_DIR}/cmake/DeployVcpkgRuntimeDlls.cmake"
    "${CMAKE_SOURCE_DIR}/cmake/DeployQtRuntime.cmake")
  if(VCPKG_INSTALLED_DIR)
    add_custom_command(TARGET ${target_name} POST_BUILD
      COMMAND "${CMAKE_COMMAND}"
        "-DRELEASE_BIN=${VCPKG_INSTALLED_DIR}/${VCPKG_TARGET_TRIPLET}/bin"
        "-DDEBUG_BIN=${VCPKG_INSTALLED_DIR}/${VCPKG_TARGET_TRIPLET}/debug/bin"
        "-DCONFIG=$<CONFIG>" "-DOUTPUT_DIR=$<TARGET_FILE_DIR:${target_name}>"
        -P "${CMAKE_SOURCE_DIR}/cmake/DeployVcpkgRuntimeDlls.cmake"
      VERBATIM)
  endif()
  # Resolve deployment from the selected Qt, including vcpkg's tools/Qt6/bin
  # layout. Never take another Qt's windeployqt from PATH.
  set(_qmake "")
  foreach(_suffix "" _RELEASE _NOCONFIG _DEBUG)
    get_target_property(_candidate Qt${QT_VERSION_MAJOR}::qmake IMPORTED_LOCATION${_suffix})
    if(_candidate AND EXISTS "${_candidate}")
      set(_qmake "${_candidate}")
      break()
    endif()
  endforeach()
  if(NOT _qmake)
    message(FATAL_ERROR "Selected Qt has no usable qmake tool for runtime deployment")
  endif()
  get_filename_component(_qt_bin "${_qmake}" DIRECTORY)
  find_program(_windeployqt NAMES windeployqt HINTS "${_qt_bin}" NO_DEFAULT_PATH REQUIRED)
  add_custom_command(TARGET ${target_name} POST_BUILD
    COMMAND "${CMAKE_COMMAND}" -E env --unset=QT_PLUGIN_PATH --unset=QML2_IMPORT_PATH
      "${CMAKE_COMMAND}" "-DDEPLOY_TOOL=${_windeployqt}" "-DQT_BIN=${_qt_bin}"
      "-DCONFIG=$<CONFIG>" "-DOUTPUT_DIR=$<TARGET_FILE_DIR:${target_name}>"
      "-DEXECUTABLE=$<TARGET_FILE:${target_name}>" -P "${CMAKE_SOURCE_DIR}/cmake/DeployQtRuntime.cmake"
    VERBATIM COMMENT "Deploy selected Qt${QT_VERSION_MAJOR} runtime for ${target_name}")
endfunction()
