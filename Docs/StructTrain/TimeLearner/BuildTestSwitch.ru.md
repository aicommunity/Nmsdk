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

Адресная приёмка на Elder завершена: реальные configure ON / legacy OFF /
conflict дали ожидаемый результат; проверены обе unit/native цели и их
отсутствие при OFF. Исполнены 9/9 unit и 14/14 native проверок. CMakeLists
в численном root58d941c2 и исправлении7290955b имеет один blob
`2a54513b75286c025142c1972f26a74b3ee2e176`.

Компактные первичные configure logs/cache и результаты выполнения:
`Reports/StructTrain/TimeLearner/s02-test-switch-configure-b3`.
Они извлечены с проверкой SHA из evidence
`57383f8d93ebf660bd2f80d08ac315a67abe2896`. Ошибка независимого C₀ reader
в исходном cohort сохранена там отдельно и не выдаётся за успешную приёмку
всего cohort. Этот отчёт принимает только CMake-флаг и доступность целей;
он не закрывает весь этап 2 и не меняет gitlinks PulseLib/Rdk.
