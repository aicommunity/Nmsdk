# Native A2: отказ после configure, до compile

Canonical A4 остаётся PASS только подготовки. Actual native job s08-recorded-n4-sdk36-m40-a2 остановился с changed_cached_build_profile:NMSDK_BUILD_RECORDED_MODEL_INPUT_TESTS. Новый BOOL cache token декларировался как ON, но configure_arguments не включал его в явный whitelist применяемых опций; CMake штатно оставил defaultOFF. Проверка cache корректно отказала. C++ tests не запускались. Whole cgroup закрыт; повторное использование этого build как fresh запрещено.

Source448b153f2fea3486ff40f3a626b8f1110b9e3ee2 разрешает передачу только этого известного BOOL ON/OFF; неизвестные checks не становятся произвольными CMake assignments. Real CMake regression26 объявлена отдельно. Следующая сборка требует нового SDK source/build/runtime и самостоятельной canonical подготовки. Raw proofs в failed-native-configure.
