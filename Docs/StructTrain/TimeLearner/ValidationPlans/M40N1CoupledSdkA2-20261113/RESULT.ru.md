# SDK A2: ошибка компиляции,0 из93 cases выполнены

Root45f76e89ab62dac0429e615a176c82571116b4da/Pulse7c6c94785af0c83104d348bb3b733ed1f149c8a8. [Terminal](native/terminal.json):built=false, expected93, executed0, scientific_verdict=null. [Build log](native/build.log) фиксирует redeclaration gtest_trace_994: два SCOPED_TRACE на одной строке C++ fixture. [Exception](native/exception.json), [outer closure](controller/outer-closure.json), [terminal CMake cache](native/CMakeCache-terminal.txt). Kernel group закрыта до любых изменений source/build. Научный Train не запускался.

Исправление74e5d206d4b619fcf81f77f11b54ebec7b8f0f6e разносит только эти макросы по строкам; production Pulse и scientific limits прежние. Попытка A3 использовать существующий build cache отвергнута canonical fresh-build guard до запуска компилятора; [исход](../M40N1CoupledSdkA3-20261113/RESULT.ru.md). Guard сохранён; следующая A4 имеет чистый build/runtime. Source working tree частного SDK-каталога разрешено обновлять только после closure; исходный45 commit и полные before/after source captures сохранены. Изменений работающего эксперимента нет.

Git producer65ffbe9d9fff7fd217343f9ff292d86e7f397e95, pack1,057,365 bytes SHA2561266b54c5e5c83f12492d529d08e3d7ac8ac944ebd68971848b1d7c069eaefe9. Исходный compile failure не является выполненными failed assertions и не переименован в PASS.
