Принято адресно:19/19 прошли,64 primary members и757 source hashes сверены; loaded libasan и fresh closed/released подтверждены. [Сверка](CandidateRecoveryAsan19Verification.json). Это не full SDK ASan и не leak check. Ниже сохранена постановка запуска.

# Recovery: адресный ASan19 gate

Запущена отдельная изолированная сборка M40 s07-candidate-recovery-asan19-a1.
Она не использует и не меняет работающий stock runtime. Source rootd8d738751 /
Pulse416 / Bin37ff211f. Перед запуском проверено совпадение Git blobs/scopes
App, Tests, CMakeLists.txt, PulseLib и Rdk с ранее normal-проверенным root84d6.
Изменения Python/docs/retired Bin tools не выдаются за изменение C++ математики.

[Точный job/test inventory](CandidateRecoveryAsan19Jobs.json):19 test functions —
4 общего invalid budget,2 классификатора,7 переходов recovery,4 cold codec/
real component configuration и2 общего event serializer. Эти функции входят в
предыдущий normal118. Build/test output и runtime отдельные; один compiler,
cgroup4GiB/128 tasks, C++/link ASan flags, detect_leaks=0. Предыдущий native118
worker проверен closed/released до начала сборки; исходники детей копируются
только через Git в новую private source, без alternates и обновления donor.

Это адресная memory-safety проверка последних изменений, а не новый научный
эксперимент, отсутствие утечек или весь ASan SDK. Прежний ASan133 относится к
Pulse12d и не заменяет этот gate. Во время фиксации заметки CMake уже завершился,
шёл compile; C++ tests ещё не начинались. Наблюдение owner PID/start_ticks не
означает, что job будет жив после указанного момента. Приёмка требует свежего
closure/released lease, полного JUnit/loaded-libasan/runtime и Git primary.
