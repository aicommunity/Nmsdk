# M40: свежая SDK и 36/36 native проверок приняты

Root08b898b1ad89d002cccde534e08e0925e080e45d / Pulse e9b80746103750d3b5a100d74549462d6d2c46c6. Canonical source4145 files/29 SDK modules, отдельные build/runtime. [Исходный terminal](accepted-native/native/terminal.json):36 expected,36 audited,36 assertion PASS, без failed IDs/heartbeat/final-capture errors. Все36 исходных JUnit сохранены в accepted-native/native.

Четыре новые проверки NativeValidatedArchiveExport охватывают Classic/Branch и stopped/completed. Проверяются равенство document/primary между старым API wrapper и новым API **в одном новом binary**, независимое decode внешнего primary, отказ изменённого CSV/foreign source, перенос проверенного proof и неизменность живого графа. Это не сравнение старого и нового бинарников и не проверка производительности большого N4. Старые32 контроли сохранены:4 Build boundary,7 Console publication/execution,11 legacy wire,10 recognition.

[Original outcome](accepted-native/controller/original-outcome.json) сохраняет exit0 до cleanup; [supervisor](accepted-native/controller/supervisor-result.json) подтверждает outer+36 children closed, record_errors пуст; [reservation](accepted-native/controller/reservation-final.json) released. Cleanup не используется как доказательство успешного выполнения.

Source Git closure и source hashes до/после совпали побайтно, как и protected files и current runtime. [Source closure](accepted-native/native/source-closure-after.json), [runtime](accepted-native/native/current-runtime-after.json), [SHA256 всех55 raw proofs](accepted-native/readback-integrity.json). Test binary SHA256 6d14f4207f1b610a2f2351bb784a8d72027a46ed04f0b832bb3407915b496a83; Console d70c563e1ecab7552c76037395328c06571742d4770e5159678480441b5097a0.

Приёмка ограничена этими36 проверками на M40. Полный compact native corpus ещё не опубликован; independent semantic replay, Elder и большой N4 export/performance открыты. Полный план0–12, новые N4 Train и scientific Test этим результатом не закрываются.
