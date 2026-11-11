if(CONFIG STREQUAL "Debug")
  set(_mode --debug)
else()
  set(_mode --release)
endif()
set(_arguments ${_mode} --no-translations --no-compiler-runtime --dir "${OUTPUT_DIR}"
  --plugindir "${OUTPUT_DIR}/plugins" "${EXECUTABLE}")
# vcpkg supplies a debug wrapper selecting its debug Qt prefix/plugins; --debug
# alone on the release-prefix tool is insufficient for this split layout.
if(CONFIG STREQUAL "Debug" AND EXISTS "${QT_BIN}/windeployqt.debug.bat")
  execute_process(COMMAND "$ENV{ComSpec}" /d /c call "${QT_BIN}/windeployqt.debug.bat" ${_arguments}
    RESULT_VARIABLE _result)
else()
  execute_process(COMMAND "${DEPLOY_TOOL}" ${_arguments} RESULT_VARIABLE _result)
endif()
if(NOT "${_result}" STREQUAL "0")
  message(FATAL_ERROR "Qt deployment failed for ${EXECUTABLE}: ${_result}")
endif()
if(NOT EXISTS "${OUTPUT_DIR}/qt.conf")
  file(WRITE "${OUTPUT_DIR}/qt.conf" "[Paths]\nPrefix=.\nPlugins=plugins\n")
endif()
