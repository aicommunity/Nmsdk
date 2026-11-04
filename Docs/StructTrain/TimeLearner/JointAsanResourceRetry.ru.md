# Joint ASan: остановка по ресурсам и повтор,04.11.2026

Attempt44 A2 на M40 остановлен оператором после достижения8GiB whole-cgroup memory cap. Перед остановкой memory.peak==memory.max==8589934592 bytes, memory.max events исчислялись миллионами; oom/oom_kill оставались0. Native процесс и управляющий worker находились в одной cgroup. Результат — ограниченный ресурсами незавершённый запуск, а не неуспех алгоритма, PASS или доказательство ошибки интегратора. Полного JUnit нет.

Остановлена только exact owned unit с её controller/native descendants; kernel closure и освобождение её global lease проверены заново. Старая full304 A1 очередь отказала при отсутствии native44 verdict до создания bounded worker. Она ничего не тестировала; traceback сохранён.

[Полный primary](../../../Reports/StructTrain/TimeLearner/s07-joint-asan-resource-retry-a1/bundle.json), evidence `868446020fb75e9746612e0312773131e594f0b0`:1269 members, включая все1251 частичных файла прежнего44, controller, operator stop, queued refusal. Архив7 488 956 bytes,SHA256 `7b309fae7c87e8357c5310f5679df93bd6685075f8e96be88141c77d2ccdd3e7`. [Независимая проверка](JointAsanResourceRetryVerification.json) пересчитала каждый файл и published checksum. Доставка только через Git; локально численные тесты не запускались.

## Повтор без изменения научной постановки

Новый44 A3 использует прежний immutable SDK root `8021301e894368aefd045f9d77274fcce9f60245`, PulseLib `cc97149c90ce98ff24ca688452f4a40d54e0e63d`. Runtime manifest побайтно семантически совпадает сA2; те же44 expected IDs, native21600s, schema2 cooperative capture и ASAN_OPTIONS=detect_leaks=0. Сборка, физика, допуски и исходники не менялись.

Whole-job memory cap42GiB проверен по фактическому memory.max. Native наследует cgroup управляющего worker; это один суммарный лимит, не два независимых лимита. Число задач128 сохранено. До запуска доступно46 420 402 176 bytes RAM и409 250 750 464 bytes на Data. Контроллер записывает memory.current/peak/events/swap каждые5s, сохраняет memory.peak до закрытия группы и usage завершённых дочерних процессов. При исчерпании42GiB результат снова останется ресурсным ограничением, без PASS.

На момент публикации44 A3 работает; первые проверки проходят, memory.max events=0 в доступном readback. Full304 A2 ждёт его complete valid44 PASS, kernel closure и lease release до старта собственной bounded unit. У неё прежние304 IDs, native86400s и42GiB cap. Итога44/304, owner replay/readers нового ASan среза и научной классификации ещё нет. Leak absence не проверяется. Старый принятый K1 остаётся отдельным snapshot34/262/119.
