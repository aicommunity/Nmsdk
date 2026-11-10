# SDKf39: Load/XML исправлены в адресных контролях, package cohort остановлен OOM

M40 fresh build Root `f39b9ebdcd0e7a64e388d778ca32374a65ae4e0c`, Pulse
`991d933a5a3f6fe1d17986118656be98cda31392`, Rdk
`de4134235c0dcb8b91fd9a43b267348ad1a163ca`, Bin8cb завершён.
Итог исходной декларации17: **12 audited completed / 12 PASS / 5 unobserved**.
Полный17-case gate **не пройден**.

Полное сохранение выполнено в evidence219ceb0c439ef91ce410cf564f9a1dc9f2f63364:
414 originals,1796972 bytes compressed primary, два выбранных1920×960 PNG.
Проверены все hashes,4074 compiled-source и652/650 reader/runner blobs.
См. [рисунки, независимую сверку и ограничения capture](NativeArchiveGatePairReports.ru.md).
Оригиналы на M40 `readbacks/s05-native-load-xml-repair17-m40-a1` и соседний
controller сохранены. Приёмка полного17 этим не заменяется.

| Часть | Фактический результат |
|---|---|
| Load/XML8 | 8/8 JUnit: противоречивый XML native/derived образов отклонён; Fresh/Connected/Detached Load проходят на2000/20000Hz |
| Реальные значения Load | Во всех шести наблюдениях input1×1=0.25 после Load и Init/Reset; все восемь Feedback samples=0.5, полный physical identity valid/match |
| Membrane stages | 1/1 |
| Saved-model replay | 1/1, semantic image/model comparison |
| Fresh-process waveform transfer | 2/2; complete100ms windows,200/2000 samples, actual input и soma arrays; max_soma_pairwise_error=0 |
| Packages5 | Нет итогового JUnit; результат incomplete_test_observation/not_assessed |

В stdout Packages5 есть два OK (Classic255.572s, Branch223.005s), затем
начат AsymmetricChildPhysicsAndC0Roundtrip. Они не превращаются в два
дополнительных audited PASS: процесс не завершил свой declared inventory.
Третья проверка оборвалась; две warm continuation проверки не начинались.

Причина установлена по конкретной kernel-bound unit:
`timelearner-224e7153-f48e-4c14-aef0-72a88b8820c0.service`, invocation
`ceaccb542c2546c6a70ef2b7bdde2772`, binding SHA256
`b753000e98f8d1322cc8d2624010d5d03dac75e17a490bae41d448edc1050452`.
Result=oom-kill, ExecMainCode=2, ExecMainStatus=9,
MemoryPeak=MemoryMax=4294967296 bytes. Process wall857.819s,
returncode−9; cooperative exit capture не состоялся. Это не timeout и не
доказательство нарушения математических допусков или PhysicalInfeasible.

Supervisor399987 отсутствует, outer и все пять recorded child groups закрыты;
record_errors пуст. Lease85f51a63-14c2-48e0-9c02-9ced2cbc55fb released.
Source/runtime после задания сохранены. Автоматический перезапуск не выполнялся.

Следующая диагностика должна изолировать тот же C0 case в свежем процессе
того же runtime при прежних4GiB/128tasks и ASAN_OPTIONS=detect_leaks=0.
Это различит накопление памяти между cases и проблему отдельного C0 пути;
простое увеличение cap не является исправлением. Whole package/reader16,
Console Train→Test и научная матрица остаются открытыми.

## Изолированный C0: повторный OOM

Fresh process того же SDKf39 также остановлен OOM на4GiB через1798.632s,
не по timeout. Native group
`timelearner-2102ee0b-5728-4f5b-a552-8b3a63db8437.service`, invocation
`9ee6edacc57b4ccab9474b895d39bfa0`, MainPID520962/start338632340,
MemoryPeak=MemoryMax=4294967296. Группа закрыта; lease
af21428d-e5f1-4a74-84fa-502902a81e01 released. Это исключает объяснение
только накоплением между предыдущими cases. Итогового JUnit снова нет;
case остаётся not_assessed, не PASS и не PhysicalInfeasible.

До отказа записаны39 файлов исходного C0 package,88467244 bytes,
`gate/native-composite/package6-branch/source-1`. Source summary7 сообщает
state=finished/outcome=exact, reference_complete=true,
certificate_matches_actual_model=true, applied_edits=0, search_probes=4.
Это сохранённое завершение инженерного холодного источника, не успешный
roundtrip, Test или классификация. Полный пакет ещё требует отдельного
сохранения и codec-проверки; отсутствие фазовых markers пока не позволяет
точно назвать строку импорта/replay, на которой исчерпана память.

Подготовлен сравнимый pre-fix SDKff42/Pulse608/Rdkd6 контроль: тот же C0 case,
исходник Test_PulseLib_CompositeTraining.cpp и PhysicalArchiveComparison.h
побайтно совпадают с SDKf39, тот же4GiB cap и ASAN_OPTIONS=detect_leaks=0.
Ни один runtime не пересобирается и не меняется. Независимый Windows normal
counterpart использует SDKf39 после closed-build audit. Его Job committed
virtual-memory cap и Linux ASan cgroup memory имеют разную семантику;
успех одного OS/compiler сам по себе не локализует причину другого.

## Отчёты с временными графиками

[Новый reader/общий CLI](NativeArchiveGatePairReports.ru.md) проверяется отдельно
на реально завершённой waveform паре, не подставляя её за Packages5.
Первый запуск11 дал10PASS/1FAIL: CLI корректно отказался строить графики из
системного Python без matplotlib. Данные/модель не пересчитывались.
Подготовлено отдельное owned Python environment с copied interpreter и
существующими matplotlib3.9.4/Pillow13.0.0 из неизменённого plot-venv-a1;
повтор использует тот же reader source и те же25 fixture hashes.
Первый отказ сохранён; повтор A2 прошёл11/11 и создал44 читаемых вида.
Два выбранных рисунка просмотрены и опубликованы; полный набор остаётся кэшем.
