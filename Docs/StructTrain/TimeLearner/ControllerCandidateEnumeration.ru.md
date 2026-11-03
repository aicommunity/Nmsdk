# Проверка механического выделения candidate enumeration

Кандидат PulseLib03b004aa36121766b8eac3040a282e272b392eb5 группирует состояние
перебора L/Ns/Rs в CandidateCursor. Родитель21435c8d5a11d2670cdc1609757d3a9973877314
является исходным вариантом. Типы/defaults перенесены без изменения. После
нормализации CRLF/LF обратная подстановка cursor.field → field восстанавливает
полный прежний BoundedTraining.cpp. Это не реализация C-search On.

Проверка выполняется отдельной командой корневого пакета:

```text
python3 -m Scripts.StructTrain.TimeLearner controller-ab job.json \
  --root-repository ROOT_GIT --pulselib-repository PULSE_GIT \
  --compiler /usr/bin/g++ --gtest-source GOOGLETEST_SOURCE --output NEW_OUTPUT_DIRECTORY
```

Шаблон: Scripts/StructTrain/TimeLearner/specs/candidate-cursor-ab-v1.json.
В job указывается полный candidate_root SHA; baseline_root зафиксирован.
Оба gitlinks PulseLib читаются из соответствующих root commits. Рабочие деревья
не переключаются; исходники читаются как обычные Git blobs. Компилируются целиком
17 production headers/sources и семь существующих test files,130 cases. Тела
функций не извлекаются и не подменяются тестовыми копиями. Корпус tests должен
иметь одинаковые hashes у baseline и candidate. Native scheduler/model tests
в этот isolated decision gate не входят и не считаются подтверждёнными.

Baseline/candidate имеют отдельные каталоги исходников, executable и journals.
Output запрещён внутри репозиториев. Обе сборки используют одинаковые compiler,
flags, очищенную environment и одну копию оригинального GoogleTest. Его source
берётся из заданного FetchContent checkout: полные include/src файлы сверяются
с точным Git commit и копируются в job. Оба executable собирают эти оригинальные
.cc files; библиотеки активного Nmsdk build не используются. Хранятся
source hashes, compiler/library/header hashes, точные compile/run arguments,
owned PID/start_ticks/boot ID, elapsed wall time, JUnit и строгая проверка полного
уникального test inventory. Timeout завершает только собственную process group.
Ненулевой exit не становится PASS, отсутствие/skip/unfinished test не принимается.
Фактически загруженные mappings быстрого unit executable не захватываются;
resolved libraries не объявляются actual loaded closure.

Сборки/запуски разрешены только на указанных Elder/M40 через jump host.
Локально выполнены AST/declaration/diff проверки. Серверный A4 A/B прошёл:
130/130 tests на каждой стороне; строгие результаты и hashes проверены независимо.
Результат130/130 с обеих сторон подтвердит этот корпус pure decisions. Он не
доказывает полную operation-trace equivalence, Rdk integration, C-trim, качество
распознавания или выполнение всей матрицы исходного плана. Перед приёмкой нужны
также соответствующие native regressions и общая согласованная Git closure.


Первый a1 worker не запускал CLI: historical proof checkout оказался sparse без
PulseLib. A2 использовал private bare object store, но остановился до компиляции
из-за отсутствия системного libgtest_main.a. Это ошибка предположения runner,
не отказ алгоритма. Evidence849cb6e8b446982c288ac7f437598a6638949ecf сохраняет
not_accepted и обе причины; эти попытки не объявляются numerical runs. Кандидат
runner исправлен на explicit Git-verified GoogleTest source, runtime ещё ожидается.


A3 обе стороны остановились на одинаковых двух relative include errors:
FinalVerification/ProbeObservation tests ожидают штатный root/Libraries/PulseLib
layout. Evidence da3612b95ec70d34f638b626fa41d9102bce74de сохраняет обе compiler
диагностики. Исправление runner размещает целые исходные файлы в реальной структуре
корень/сабмодуль, не меняя include directives или test bodies. Успех130/130 пока
не заявляется; повторный A/B должен проверить исправленную production CLI.


## Подтверждённый A4 срез и следующая native проверка

Root c04850a81bb7f1918519d72bc4c18214438d9ed0, baseline root2194eeadcb3f29e1b2047ae1bcf3e6e7e48e4747.
PulseLib baseline21435c8d5a11d2670cdc1609757d3a9973877314 → candidate03b004aa36121766b8eac3040a282e272b392eb5.
Evidence bcdae6c4985310850f89356a072ca80b3cbe7ca3:36 members,45377 compressed bytes.
Независимо сверены346 Git source hashes, оба JUnit inventories130/130 без failures,
errors/skips и одинаковые семь test files. Обратная подстановка cursor.field в
production .cpp точно воспроизводит baseline после CRLF/LF normalization.
Принят только этот pure-decision corpus. Native/Rdk integration и полная
operation-trace equivalence пока не подтверждены; C-search не включён.

Для native H10 зафиксирован root f5845fb78d906f9e7d95a55a8b0c217a73fa281c.
Elder supervisor546230/start_ticks326149080 и publisher546231/326149080 проверены
живыми; readbacks s07-candidate-cursor-native-normal-h10 и
s07-candidate-cursor-native-publication-normal-h10. Очередь ждёт успешный baseline
H9b209/87 и освобождение его source/build, затем выполняет209 native tests и104
reader checks. Включены ранее исправленные17 диагностических/certificate controls.
Отдельно требуется точное совпадение наборов и SHA256 детерминированных primary CSV
Classic/Branch N0/N1 automatic service и capacitance bridge с H9b baseline.
Receipt сохраняет все имена/hashes и любое различие запрещает приёмку. Текущий
H10 ещё не запускал сборку; дополнительные неучтённые сбои baseline останавливают
переход. До native/ASan приёмки изменения не объединяются в develop.


## Независимый native A/B после исправления владения explicit probe

Прежний H10 отказался от сборки из-за неуспешного baseline H9b; поздний H11
сохранил два explicit-probe ownership failures. Теперь baseline — точный H12
rootfd8a10b02797ceace0eb87e0d9de4e36bd1e9e62/Pulse54516bcc0aa7b0437c68f818598a19788e20eb55.
Кандидат Pulse5fed73a0379d5599656e40f58e0600469d43f28c включает тот же guard
через --no-ff merge. Все Core files кроме BoundedTraining.cpp/.h побайтно
совпадают. Два оставшихся файла содержат только grouping enumeration state
в CandidateCursor; новые C-context algorithms/schema4/region helper отсутствуют.

Корневой кандидат включает те же четыре ownership tests и остальные native
fixtures; declaration213 сохраняет parity с H12. Pure A/B specification тоже
привязана к точному H12 root; прежний130/130 A4 corpus не переименовывается
в проверку нового native runtime. Следующий worker должен дождаться успешных
H12 full213/readers87 и закрытия owners, затем проверить candidate native213,
independent readers104 (87 +17 existing diagnostic/certificate controls) и
точное совпадение имён/SHA256 объявленных детерминированных primary CSV с H12.
Любой failure baseline или waveform mismatch запрещает приёмку. ASan и fresh
closure остаются самостоятельными условиями; весь исходный этап6 не закрыт.


Native H15 поставлен в очередь на Elder: source root2700af9e46479de96270efafdbe303560b430026,
Pulse5fed73a0379d5599656e40f58e0600469d43f28c. Supervisor738540/start_ticks327554764
подтверждён живым; он ждёт закрытия всех H12 owners и положительного полного
H12 evidence перед любым checkout/build в повторно используемом b1 каталоге.
J2 имеет отдельные source/build/runtime и не затрагивается. H15 декларация —
213 native /104 readers; waveform receipt обязателен, успех пока не заявляется.

Каталоги readbacks: s07-candidate-cursor-native-normal-h15 и
s07-candidate-cursor-native-publication-normal-h15-v2. Ожидающий первый publisher
заменён до публикации, чтобы исправить устаревшую текстовую метку SDK209 на
SDK213; строгие counters уже требовали213. Worker и численные процессы не
перезапускались; исходная superseded.json квитанция сохранена. Для приёмки
используется только v2 publisher с актуальным scope и обязательным byte compare.


## H15 отказ и следующий исправленный gate

H12 native213/213 и адресные6/6 завершены; readers86/87 обнаружили только
несоответствие exact diagnostic в отрицательном test. H15 корректно отказался
до сборки, исходная квитанция86914b5cdc115858dc5e8aded1502281bd47a319 сохранена.
[Два раздельных контроля](BoundaryReaderInventoryControls.ru.md) проверены
из новым reader source90c4074a6d2049b298fd923052112e738db9ae3b на тех же данных:
88/88, evidenceaeb9664b092332555d41eefd0ac8de5fd63cc9b4. Алгоритмы и production
auditor не менялись, C++ заново не запускался. Обе исходные версии source
записаны отдельно; первоначальный overall H12 not_accepted не переписывается.

Следующий H17 явно требует эту составную baseline native213/6 + readers88,
полные original archives и неизменность C++/child sources у reader repair.
Кандидат включает исправленный test; native213, reader105 (88 +17) и точные
baseline/candidate CSV sets/SHA256 обязательны. C-search/schema4 сюда не входят;
Kernel A4 остаётся отдельным уже проверенным доказательством130/130 с каждой
стороны. Положительная native A/B приёмка пока отсутствует.
