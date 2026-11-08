# Подготовленное дерево для native-проверки manual control lifetime

Статус: только локальная интеграция исходников, без сборки, тестов, серверного checkout и изменения действующего M40 runtime. Исходные corrected Root4c/Pulseb287 и unfixed Rootf74/Pulse800 сохранены. Новый code root: `e11bbd403a5f93790a7ad6c5a245c1964797d63d`, ветка `codex/timelearner-manual-control-native-preparation`.

Первый обычный merge `1e43e8d43b86971458765bd17f2b24ffb006ef88` объединяет4c с17db. Его фактические изменения: один тестовый TU (шесть значений deadline/sleep и два предыдущих diagnostic-only теста с helper) и документ диагностики. Production Pulse, App, CMake, Bin и Rdk не меняются.

Второй обычный merge `e11bbd403a5f93790a7ad6c5a245c1964797d63d` объединяет первый сdb2. Он приносит полную ancestry:47 Scripts paths,79 Docs paths и220 Reports paths; это не копирование двух helper-файлов. При этом App/Tests/CMake и все gitlinks относительно первого merge не меняются. `native_acceptance_worker.py` и `native_preparation.py` byte-identical db2. Pulse остаётся `b2878e565febe20a4ba7c9c64536d6e66f672626`, Bin918/Rdkd6. Исторические renderer CRCRLF bytes сохранены; предупреждения `git diff --check` не маскируются нормализацией.

[Git-derived manifest](ManualControlNativePreparedSource-20261108.json) содержит все изменённые пути, parents, точные module/test hashes и20 targeted source IDs. В TU337 literal tests, включая два diagnostic-only IDs; они не прибавляются к selected regression. Это не фактический compiled inventory и не20/490 PASS.

До запуска остаются: независимая приёмка действующего baseline248, свежая восьмирепозиторная source closure и materialized-byte preflight, реальный профиль CMake/ресурсов, production canonical2 с фактическим runplan, отдельная сборка/actual inventory, native controls и независимая проверка всех primary/process closures. Worker проверяет запрошенные cache tokens, но сам не устанавливает произвольные ASan/O1/LLM flags из этого списка: неподготовленный cache не является готовой сборкой. Source integration не устраняет этот отдельный build-profile prerequisite.

Unfixed negative A/B требует собственного descendant f74/800 с теми же явно раскрытыми fixture/helper integrations. Это дерево не создаёт отрицательный результат вместо запуска исходной production-версии и не заменяет её corrected-версией. Новые CLI/defaults/physics и package6 не активированы; матрица и этапы исходного плана остаются открытыми.
