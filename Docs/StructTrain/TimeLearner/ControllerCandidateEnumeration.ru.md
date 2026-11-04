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


## Независимо проверенный H17 normal результат

Root `a97a4448e90f77cb87fa66204bb83295383382e3`, Pulse
`5fed73a0379d5599656e40f58e0600469d43f28c`. Evidence
`44c793e6d868527120a8d92153ece3aaf3e3c8aa` содержит native213/213 и readers105/105,
без failures/errors/skips. Все2132 archive members /30060996 compressed bytes
независимо сверены. Runtime manifest подтверждает7 clean exact child commits.

Все104 CSV двух объявленных deterministic families automatic service и
capacitance bridge побайтно совпадают с Git-bound H12 baseline; каждый набор
содержит Classic/Branch N0/N1. Сверены имена, actual candidate bytes и SHA256
неизменяемого baseline bundle. App/Tests/CMake источники baseline/candidate
идентичны; child Core diff только BoundedTraining.cpp/.h. Ни global operation
trace equivalence, ни scientific recognition этим не подтверждаются.

Normal native A/B принят в этом scope. ASan и fresh closure остаются отдельными
условиями перед develop merge; исходный этап6 полностью не закрывается.

## ASan очередь03.11: H20, приёмки пока нет

Baseline H14 с root5c9b92350ee48d130d954bf10bf9521251f99e4e и
Pulse54516bcc0aa7b0437c68f818598a19788e20eb55 продолжает настоящий native213
прогон на M40; лимит native process43200s. Отдельная publisher-квитанция должна
сохранить его исходный результат, включая старый reader87, если он не пройдёт.
Поздний corrected reader не изменяет первоначальный overall verdict.

H19 остановился до checkout/build/numerical work: проверка памяти требовала12GiB,
когда доступно около10GiB. Publisher тоже отказался: пытался прочитать .gitmodules
из ещё не созданного checkout. Оба exception receipts сохраняются в readbacks;
они включаются в следующий пакет, а не считаются численным результатом.

Исправленный H20 ждёт точный H14 supervisor PID3024065/start_ticks278028377.
После подтверждённого закрытия owner и native children он требует фактические
native213 pass, actual libasan mapping и опубликованный original evidence.
Далее повторно проверяет12GiB available/20GiB disk и создаёт новые private
source/build/runtime/framework каталоги `candidate-cursor-native-asan-h20`.
Чужие процессы для освобождения памяти не останавливаются.

Кандидат root9c39adbbbd7afd6af4a64393e719fd48efce4dd5 / Pulse
5fed73a0379d5599656e40f58e0600469d43f28c; production C-search/schema4 отсутствует.
Декларация:6 addressed ownership cases,213 native cases,105 corrected readers,
точное сравнение полного original/candidate CSV inventory и bytes. Бюджет
full native43200s; failure или mismatch запрещает положительную приёмку.
Build timeout завершается только для принадлежащей worker process group с
подтверждёнными PID/start_ticks. Publisher проверяет reachability каждого
child commit по parent Git metadata даже при отказе до checkout.

На момент записи H20 worker3299200 подтверждён живым в состоянии ожидания;
publisher3299201 запущен отдельно. Это очередь, а не ASan pass. Fresh recursive
closure и исходные полные этапы6/7 остаются открытыми.

## Уточнение publisher H20: отдельная замена, численный worker не изменён

Первоначальный publisher3299201 ошибочно разбирал .gitmodules через Python
ConfigParser: неодинаковый отступ branch мог стать продолжением URL.
До остановки подтверждены PID/start_ticks и отсутствие публикации; остановлен
только этот ожидающий publisher. H20 worker3299200 и H14 native не прерывались.
Receipt superseded.json сохранён в исходном publication каталоге.

Новый publisher-v2 PID3362315 использует штатный git config --blob для точного
parent commit. Публикация ожидается в отдельной evidence ветке
codex/evidence-s07-candidate-cursor-native-asan-h20-v2. Исходный отказ не
переписывается и включается в архив. Это исправление одноразовой обвязки:
production publisher.py уже использовал native Git parser. Новый regression
этой особенности .gitmodules прошёл в составе17/17 production publisher tests
на Elder и M40 (proof8a435e495eb6a1e548141bc64fad484f59a01897 и
8f53372908ab94515ad2527ca73a8b389b0da355); он не подменяет ASan проверку.

При последней проверке03.11 H14 native3052995 и owner3024065 живы,
H20 worker3299200 и новый publisher3362315 живы. Прежний текст о3299201 выше
описывает исторический запуск. Ни ASan pass, ни завершение этапа6 не заявлены.

## Завершение H14/H20 и адресный повтор H21

Оригинальный H14 опубликован в `cd39ea2a903236357a1b5965ce859d6fca5f30c9`:
2264 members проверены по outer/member hashes и фактическому JUnit.
Targeted6/6, full212/213; единственный отказ
NativeCapacitanceHistoryBoundary.ClassicN1StoppedBeforeFirstTick —
child.waitForFinished(120000). Actual libasan mapping присутствует.
Reader87 после этого отказа не запускался; overall остаётся not_accepted.

H20 корректно прекратился до нового SDK после отрицательного baseline gate.
Его original receipt и заменённый publisher сохранены в
`81ca263780419ad2bdbda322365923474a193db6`; все7 members независимо проверены.
Этот пакет не содержит нового ASan candidate runtime или A/B результата.
Ни baseline pass, ни CandidateCursor ASan pass не присваиваются.

H21 повторяет исходный failing case на том же неизменённом H14 executable,
не увеличивая внутренние120000ms. После освобождения памяти на M40 доступно
около43GiB. Standalone case прошёл1/1 (126805ms всего теста); это совместимо
с влиянием ресурсов, но не доказывает причину исходного таймаута и не заменяет
полный ordered gate. Затем начат прежний213-case набор в том же порядке,
с бюджетом43200s. Owner3416749 и native runtime подтверждены живыми.
Файл memory-samples.jsonl фиксирует MemAvailable, SwapFree и RSS процессов
именно этого executable с PID/start_ticks. Чужие процессы не останавливались.

H21 out: /media/user/Data/TimeLearnerRefactor/readbacks/s07-configured-probe-ownership-asan-h21.
После полного native213 всё ещё нужны original/corrected reader проверки,
публикация и независимая проверка primary. Новый CandidateCursor ASan A/B
после H20 пока не запущен. Fresh closure, develop merge и исходные полные
этапы6/7 остаются открытыми.


## Уточнение04.11: baseline H21 принят, candidate ASan не подменяется им

H21 owner3416749 закрыт. Git proof
`37cc03f72cdd461f0bde508fbc466ac976081f9c` подтверждает standalone1/1 и
полный213/213 native gate в исходном runtime H14. Это root
`5c9b92350ee48d130d954bf10bf9521251f99e4e`, Pulse
`54516bcc0aa7b0437c68f818598a19788e20eb55`, Rdk
`acc3de8d1af2480d61ddb723c3288f7e81003049`, Bin
`39d811e5e0798eecf124f32356c9fc6edbe4538a`. Длительность native26818.657s.
Исправленные88/88 readers rootab95ba64323114f9b8a3fb05cdb46527c20d452a
прошли; исходные87 сохранены с одним отказом, а не объявлены прошедшими.
Actual libasan mapping,2155 archive members и899 source hashes проверены.
Этот успешный повтор при неизменных120000ms не устанавливает причину H14 timeout.

Новый downstream ASan gate C-search K1 запущен отдельно на root
`69789b8cb93dbc2ce44fe7a8d90aed758cf93f76` / Pulse
`84e456d6fb551021e0222ebaf51fa313df2623b4`, owner3649813/start_ticks284056538.
Git ancestry подтверждает включение mechanical cursor commit
`03b004aa36121766b8eac3040a282e272b392eb5` и codec fix253fe87; declared262
содержит все213 IDs исходной регрессии. Но это другой snapshot с C-search,
а не отдельный candidate5fed73 без него. K1 сейчас строится; он пока не
подтверждает ни ASan pass, ни waveform/operation-trace equivalence.

Таким образом normal A/B и normal213/105 с104 byte-equal CSV остаются
принятыми своими доказательствами; ASan baseline теперь завершён. Проверка
candidate/downstream, точное сравнение соответствующих primary и объединение
с актуальными initial-threshold/Rdk/Bin ещё открыты. Полные этапы6/7 не закрыты.
