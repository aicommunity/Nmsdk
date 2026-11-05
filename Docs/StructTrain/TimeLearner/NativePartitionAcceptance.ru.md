# ASan: явная изоляция native tests по процессам

## Реальная адресная проверка

Tool root `86118630da6fed4763715209e4405980cad59f0d`, native SDK root802/Pulsecc; новая сборка и изменение алгоритмов не выполнялись. Production native_partition вызывает production run_native_gate schema2 отдельно для каждого ID, с cooperative loaded-file capture. Режим задан явно; старые неуспешные результаты не переносятся в новый итог.

На M40 прошли5/5 адресных tests: два actual ASan native processes плюс проверки повреждённых первичных наблюдений и schema budgets. Actual native cases — NativeCapacitanceModelSpec2Codec/ClassicN0_2000 и /BranchN0_2000. Два разных PID/start/boot доказаны первичными owned-process records; оба process result completed/exit0/loaded_files_captured, XML содержат точные IDs. Производный JUnit связан с исходными XML/hashes; общий фиктивный process/result.json не создаётся. Неполный XML, повторный process identity, конфликт имён native-файлов и неверные бюджеты не дают PASS.

[Все67 primary файлов](../../../Reports/StructTrain/TimeLearner/s07-native-partition-addressed-asan-a2/bundle.json), compressed36808B, SHA256 `1d22e88be20b72f1c08b2c46ba860b33ecc52bab61bf379f92e34e9800b499e2`; data commit `900ed669960ac66ce5e0172468b8673b4abec099`. [Независимая сверка](NativePartitionVerification.json) повторно проверяет каждый archive member, оба actual processes и точные Git blobs нового модуля/tests. Fresh whole-group closure и released lease сохранены. Это приёмка двухпроцессного механизма на выбранных реальных случаях, не всей304 матрицы или shared Pulse12d.

A1 до native запуска обнаружила string/path adapter error: strict native_evidence.load получает Path. Ошибка исправлена отдельным commit86118630, A1 не переписана: [12 первичных файлов](../../../Reports/StructTrain/TimeLearner/s07-native-partition-addressed-asan-a1/bundle.json), data commit `a5c18c55172440e29fac86c864a4bd99b061380b`. A2 — новая попытка с отдельным source Git store. Научные tolerances и Core не менялись.

## Runtime binding

Старый binary, app ini, compiler, source closure и build flags остались неизменными. На сервере изменились фактические hashes двух PCRE libraries (pcre2-16 и pcre2-8), при одинаковых размерах. Обе версии hashes сохранены в runtime-delta.json. Поэтому A2 захватывает новый runtime manifest; старый invalid provenance не «починен» задним числом. Runtime каждой новой пробы проверяется до/после выполнения. Detect_leaks=0 сохранён; absence of leaks не доказана.

## Полная304 проверка выполняется

[Точный worker/launcher/job и kernel snapshot](../../../Reports/StructTrain/TimeLearner/s07-native-partition-full-asan-a2-pending/job.json): PID202412/start295322316 kernel-live, runtime/source остаются read-only. Весь исходный набор304 IDs сохранён, каждый ID выполняется отдельно; результат каждого процесса и исходный XML остаются primary. Lossless hardlink view native/ нужен существующим readers; одинаковое имя с разным содержимым запрещает положительный общий verdict вместо скрытой перезаписи.

42GiB/tasks128; whole-worker limit86400s, общий native budget82800s, individual case7200s. Последние3600s оставлены архивированию/завершению. Это явные wall-time ограничения запуска, не изменение model time или tolerances. Исчерпание бюджета означает неполное наблюдение. Первоначальная full-A1 декларация90000s отклонена API contained_limits_invalid до создания unit; исходный launcher log сохранён. A2 использует поддерживаемый лимит; контент остановленного A1 не заменён.

PASS требует304 отдельных полных valid наблюдения, точного общего inventory, неизменного runtime, memory events, whole-group closure и опубликованного compressed primary. После этого нужны новый origin-bound owner replay8/readers128 и отдельная новая shared-controller SDK ASan-проверка. Старые очереди, привязанные к неуспешному монолитному304 A2, не означают готовность новых результатов и требуют адресной перенастройки зависимостей. Shared native очередь с parent budget129600 дополнительно требует разделения на допустимые bounded этапы до запуска: используемый backend принимает максимум86400. Не выдавать её за выполненную или гарантированно запускаемую проверку.

Общая цель и исходные этапы1–12 открыты. Никакой scientific stock8/8 PASS из этих адресных тестов не следует.
