# Передача opt-in CMake-флага:26 server checks

Source 448b153f2fea3486ff40f3a626b8f1110b9e3ee2. Проверяется весь native acceptance worker module, включая real CMake project(NONE) с option defaultOFF и явным ON. CMake /usr/bin/cmake закреплён SHA256. Новые checks требуют ровно одну передачу ON/OFF, запрет неверных type/value; неизвестные postconditions остаются read-only. Без C++ compilation/model execution. До фактического результата не принято.
