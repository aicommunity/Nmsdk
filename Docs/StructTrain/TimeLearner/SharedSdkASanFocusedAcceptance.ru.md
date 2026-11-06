# Shared SDK2e/Pulse12d: ASan build и focused8 приняты

06.11.2026 приняты отдельная ASan-сборка нового общего среза и восемь
NativeRecognitionOwner случаев на M40. Compiled root
`2e0618110a9abb48b94f6edc6b63c51f829ec810`, PulseLib
`12d8c8a41c998ae1516496f716a0ae0f3d312b3e`; native partition tool
`86118630da6fed4763715209e4405980cad59f0d`.

## Сборка и runtime

Сборка выполнена последовательно: CMake parallel1 и NMSDK_BUILD_PARALLEL_JOBS1,
RelWithDebInfo, -O1 -g1 -fsanitize=address -fno-omit-frame-pointer,
link -fsanitize=address. Отдельные source/build/runtime не заменяют SDK802.
Использованный resource Bin snapshot и его отличия от записанного gitlink
явно перечислены в shared-resource-binding.json; конфиги/физика/данные не менялись.
Build сам по себе не запускает модели и не доказывает успешные тесты.

Executable SHA256 `051c7cdc4fff8c59efee6a5b7f59c50fabb73492f6881b57755f67271236fae3`;
runtime fingerprint `93b11ba8e6294327ec8f53688f4b133d7559835ec96f1a3f6cd1566d30fc82b5`.
[Build bundle](../../../Reports/StructTrain/TimeLearner/s07-integrated-acceptance-asan-build-a2/bundle.json):
19 файлов,64880 bytes xz, SHA256
`7dec8d89f23db8a4ea23c9966a7c937ed3f0b808117695b368c740c8d00418d8`.

## Восемь адресных нативных проверок

Classic/Branch × FreshDestination, SpikingFreshDestination, N0, N1:
8/8 в восьми отдельных настоящих C++ процессах. Исходные JUnit содержат
точно объявленные ID, без disabled/skipped/failure/error. В каждом процессе
проверены returncode0, executable/runtime identity и фактически загруженная libasan.
Декларация тестов сохранена; расширены только явные wall budgets ASan,
без изменения модельного времени или численных допусков. detect_leaks=0:
отсутствие утечек не доказано.

[Focused primary bundle](../../../Reports/StructTrain/TimeLearner/s06-integrated-acceptance-asan-focused-a3/bundle.json):
575 файлов,776104 bytes xz, SHA256
`9861d53b10626378be2b444714026a8df7fa8b45ee27fa070dffcbc417693c51`.
Producer сохранил binding шести declaration fixtures и103 PostTune saved-state
files с проверкой against их опубликованных manifests. Saved-state fixtures
не объявляются новым холодным обучением.

## Независимая сверка и публикация

Data commits `4bd624d69d61f8f687c145325b50fbd2543234cb` и
`86c761c90a1d52fb49dca5c0aab4bd9334a5d02e` сохраняют обе первичные серии
и отдельный аудит закрытия сборщика.
[Сверка](SharedSdkASanFocusedVerification.json) проверила все19+575 archive members,
720 build source hashes и321 native/323 Python/325 partition tool hashes против
точных Git blobs, исходные aggregate/per-case JUnit и восемь уникальных
boot/PID/start identities. Production fresh dependency подтверждает closed/released
для build и focused worker. Локальных численных запусков не выполнялось.

Первый evidence collector после успешного создания data commit завершился
TypeError: при release собственной lease был пропущен обязательный note.
Этот отказ не изменил первичные результаты. Отдельное явное административное
восстановление проверило отсутствие исходного PID и относящихся к каталогу Git
процессов, сохранило исходную строку lease и освободило только её.
Первый recovery отказал на PermissionError до commit; затем nondumpable
PAM/ssh-agent/sshd helpers выделены по comm/parent. Их executable/cwd не проверены
и не объявляются проверенными. Receipt и recovery collector сохранены; append
завершён с штатным release(note). Native jobs и работающий lifecycle133 не менялись.
Это адресная операция восстановления, не приёмка общего scheduler recovery.

## Границы

Открыт ASan lifecycle133. Ранее accepted SDK802 ASan304 и новый SDK2e normal304
не подменяют этот gate. Успех focused8 не доказывает полную матрицу lifecycle,
режимов/физики, корректность всех PostTune вариантов или научную классификацию.
Pending C++ branches не объединяются только по этой приёмке.
Все исходные этапы1–12 и общая цель остаются открытыми.
