# Завершённые проверки и освобождение места, 05.11.2026

Приняты три набора первичных данных. Это адресные инженерные проверки; только исходный этап 0 полностью завершён, этапы 1–12 остаются частичными. Изменения алгоритмов PulseLib и production coordinator пока не объединены в develop.

| Проверка | Фактический результат | Ограничения |
|---|---|---|
| Совместный ASan, root `8021301e894368aefd045f9d77274fcce9f60245`, PulseLib `cc97149c90ce98ff24ca688452f4a40d54e0e63d` | 44/44, полный заявленный список, без failed IDs | Расширенный 304 ещё выполняется; owner replay/readers этого ASan runtime ожидаются. Leak detection выключен. |
| Managed live routing, package `8c9ee9f6b319a06224d6ebdcdd537b88e993fc4a`, Console SDK `33fc48278cff860d20c570cb703198847f028065` | 6/6, 10 реальных native units: Classic/Branch fixed/grid и два stopped-Train controls | Широкая fault/cancel/publish матрица и semantic ConditionSpec ещё не приняты. |
| Устаревшая сборка `build-capacitance-schema4-normal-j3` на Elder | Удалён только проверенный generated build/vendor cache; освобождено 703 688 704 bytes | Исходники SDK, runtime, ресурсы, модели и уникальные результаты сохранены; глобальная ёмкость очереди не менялась. |

ASan44 выполнен с ограничением всей группы 42 GiB. Измеренный пик группы до завершения native — 9 299 521 536 bytes; `memory.events.max/oom/oom_kill=0`, swap=0. Максимальный RSS отдельнего завершённого дочернего процесса — 8 526 948 KiB; это другая метрика, её нельзя подменять пиком всей группы. Старый остановленный 8-GiB прогон сохранён отдельно и не повышен до PASS. Новый 304 использует тот же неизменяемый SDK; результат ещё не заявляется.

В live-routing оба fixed случая при пороге 1.0 дают TP0/FP0/FN2/TN2: модель молчит, успешной детекции нет. Оба grid случая после measured calibration и confirmation дают TP2/FP0/FN0/TN2. Это двухвходовые fixtures с historical_same_matrix, а не stock 4-input/8-pattern или independent evaluation. Два отрицательных Train намеренно завершились process_error/exit 2; pipeline остановился на train, Test отсутствует. Успех теста здесь означает корректную обработку отказа. Standalone поля `source_training_evidence_checked=false` и `native_execution_verified=false` сохранены; внешние процессные receipts не превращены в scientific verdict.

При удалении j3 проверены все файлы, чистота vendor Git и отсутствие stash, непересечение с действующими reservations. Отдельный привилегированный процесс только прочитал kernel process metadata: 97 пользовательских процессов, ссылок на удаляемый каталог и ошибок чтения нет. Удаление выполнил обычный пользователь в ограниченной группе 512 MiB. Runtime regular-file hashes совпали до/после; сохранённые symlinks не повреждены. Свободное место непосредственно до/после: 2 965 897 216 → 3 669 585 920 bytes. Это замер операции, а не обещание постоянного остатка диска.

Все три parent groups закрыты; соответствующие leases released. Для live-routing отдельно проверены 10 различных native unit IDs и закрытие каждой группы, шесть SQLite integrity checks. Локально выполнялись только Git/hash/archive/SQLite metadata операции; модели и интеграционные тесты — на серверах.

| Primary | Evidence commit | Members | Сжатый объём |
|---|---|---:|---:|
| [ASan44](../../../Reports/StructTrain/TimeLearner/s07-joint-asan44-a3/bundle.json) | `bc64516a2501be36e42049a6d7cb570108abd9eb` | 1266 | 4 329 632 bytes |
| [Live routing](../../../Reports/StructTrain/TimeLearner/s10-managed-live-routing-normal-a5/bundle.json) | `4610cd382cad493ba7904018197cc4a2eec9aa40` | 1109 | 6 099 312 bytes |
| [Очистка j3](../../../Reports/StructTrain/TimeLearner/s02-obsolete-schema4-j3-build-cache-a1/bundle.json) | `08269811c5eab9e6954e8f37eaec60afa4995575` | 26 | 535 664 bytes |

[Независимая проверка](CompletedGates-2026-11-05.verification.json) охватывает каждый archived member и published checksum, 683 C++ source blobs ASan SDK и 294 Python blobs package8c. Первичные данные сжаты без потери; полные изображения хранятся как воспроизводимый кэш на M40 Data.

Собственный временной отчёт coordinator8 строится на M40 из evidence `2776bd89fb53a4c32324a445d771e75d010a30d0`, без повторного запуска моделей. Попытки A4/A5 остановились до графиков из-за выбора системного Python без matplotlib. В A6 добавлен явный вход в существующую plotting venv до создания outputs; исходный primary cache повторно проверяется по всем 2238 hashes и используется read-only. A6 ещё не принят: нужны завершение всех 16 отчётов, проверки масштаба/входных импульсов/полноты и визуальная проверка выбранных оригиналов.

Следующие действия: дождаться полного ASan304, выполнить его owner replay/readers; завершить A/B старых восьми Owner cases и независимый133; проверить отдельный test-only candidate `2cb855677f3e7160cd01837f62c649b18803ebf0` на новом SDK. Его короткий initial burst — гипотеза для downstream Owner fixture, без изменения алгоритма и допусков; старые отрицательные результаты остаются отрицательными. Затем продолжить незакрытые пункты общего аудита, включая научную матрицу и физические профили/LTMembrane.
