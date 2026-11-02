# Общий флаг сборки тестов корня и Rdk

Дефект воспроизведён в fresh isolated build переноса C₀ B2: native integration
executable собран, затем make завершился с No rule to make target
Test_UComponent_Lifecycle. Корень объявлял BUILD_TESTS после добавления Rdk,
а Rdk проверял независимый BUILD_TESTING. Старый cache с явно включённым
BUILD_TESTING скрывал расхождение.

Root теперь разрешает BUILD_TESTING до add_subdirectory(Rdk) через CTest.
BUILD_TESTS принимается как legacy input alias и удаляется из cache после
переноса значения. Внутри configure сохранён обычный alias для совместимости
с дочерними CMake-файлами. Противоречащие явно сохранённые значения обоих
флагов запрещены; они не должны молча исключать часть обязательного gate.
В таком старом cache нужно согласовать значения либо удалить один флаг.

Новые конфигурации: -DBUILD_TESTING=ON/OFF; fresh legacy конфигурации
-DBUILD_TESTS=ON/OFF также поддерживаются. Действующие Rdk методы
Default/Build/Calculate/Reset и параметры learner от изменения не зависят.

Приёмка ещё требуется: реальные configure ON/legacy OFF/conflict и наличие
обеих ожидаемых целей в первом случае, затем unit/native gate на workers.
