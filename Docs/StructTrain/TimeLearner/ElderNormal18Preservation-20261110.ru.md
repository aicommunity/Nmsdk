# Elder: завершённые normal18 и полное сохранение primary — 10.11.2026

На Elder завершены все18 объявленных C++ checks в10 отдельных leaf-группах. Все18 JUnit cases выполнены и прошли; нет failed/not-completed/unobserved cases. Это адресная инженерная проверка, не результат классификации и не полный native119.

## Исходники и исполнение

SDK355c60df066bdc8da09bd6d7872b47f6e71c0494, PulseLib165d49da7e65cd6ac59bca2812ce52884ddd50c2, Rdkde4134235c0dcb8b91fd9a43b267348ad1a163ca, Bin8cb6dba07b30432272984c8ce3136b48ad06f064. Native worker1386206616d82952166ece926e814cd2c5aafbb9, отдельный canonical tool98ed6da0da8bc0cb46512ebe92150570c2909206. [Заранее зафиксированный cohort](https://github.com/aicommunity/Nmsdk/blob/4692ea63de8afce248ff22ae36d9f0e724a890ab/Docs/StructTrain/TimeLearner/ValidationPlans/ElderNativeArchiveMove18Retry-20261110/cohort.json). Исходная A1 preflight-ошибка несовместимого worker сохранена отдельно; A2 её не переименовывает в PASS.

Release/O3, GCC/Qt6, LLM Off, без ASan, parallel2. Leaf-лимит4GiB/128tasks; внешний build/controller8GiB. Runtime и source отдельные, прежние задания не изменялись. Все10 leaf groups и outer закрыты; owner7419/start388721787 отсутствует, reservation освобождена по штатному recovery. Исходный worker_terminal подтверждает built/job_validation/cohort_assertions_passed; cleanup сам по себе не считается подтверждением успеха.

## Проверенный объём

| Проверки | Cases |
|---|---:|
| Production archive move/copy ownership |1|
| XML existing-image validation и native Load: fresh/connected/detached при2000/20000Hz |8|
| Фактические membrane Copy/Load stages |1|
| Saved Classic replay после освобождения исходного графа |1|
| Fresh-process waveform transfer при2000/20000Hz |2|
| Classic/Branch полный физический roundtrip |2|
| Asymmetric child physics и C0 roundtrip |1|
| Classic/Branch C0 imported warm continuation |2|

C0 roundtrip272.652s, Classic warm83.052s, Branch C0 warm546.079s по исходным JUnit. Эти fixtures используют инженерные условия, в частности SyncTolerance0.2 для package6; они не подтверждают Exact при default0.02 или распознавание stock N4.

На M40 тот же SDK355 в ASan-профиле завершён15 audited PASS, C0 incomplete после kernel OOM4GiB, две warm проверки не запускались. Поэтому исправление move ownership имеет адресный PASS, но не объявлено достаточным исправлением памяти. Различаются worker/build profiles; причинность ASan либо особенностей машины не доказана. [Полные отрицательные metadata M40](https://github.com/aicommunity/Nmsdk/blob/0b1ea04e53c102a079b65319942fd699377f1b9d/Docs/StructTrain/TimeLearner/ValidationPlans/NativeArchiveMove18-20261110/terminal-readback.json).

## Доступные в Git данные

[Evidence commit8a7cd95c54b53b56b17bf2c3a771a72591ad45ae](https://github.com/aicommunity/Nmsdk/tree/8a7cd95c54b53b56b17bf2c3a771a72591ad45ae/Reports/StructTrain/TimeLearner/ElderNativeArchiveMove18-20261110) содержит полный original output и controller output:713 regular files,406275316 исходных байт. Lossless primary.tar.xz2296104bytes, SHA256702a896a862c6911851214583fe8e9f9178bf9f7960ad191ae16145fc23a1403. Сжатие не меняет исходные JSON/XML/models/traces/logs.11 относительных INFO log links записаны отдельно в inventory; каждая разрешается в сохранённый regular file, повторных копий её содержимого нет. В архив включены source/runtime closure, compiler/cache metadata, JUnit, модели, embedded/external primary, original outcomes и process/lease closures.

[Независимая проверка](ValidationPlans/ElderNormal18Preservation-20261110/verification.json) прочитала Git blobs, проверила точное множество и SHA256 всех713 originals,18 уникальных completed JUnit cases, исходный terminal outcome и closure. Сам архив передан как Git pack; source commit и child commits доступны в origin. Это не HTML/PNG cache и не новая тяжёлая серия производных рисунков.

## Следующие обязательные gates

Полный native119 на согласованном source, actual package6 reader16 с полным объявленным corpus, Console cold Train→export→calibration→frozen Test, затем научная серия и общая матрица. Текущие18 не содержат всех stopped/partial/zero-group package6 variants, поэтому не заменяют reader16. Elder снова пригоден для заданий; при проверке после завершения свободно около16GiB. Перед новым заданием требуется новая проверка места/резервов. Этапы1–12 остаются частичными; автоматического возобновления SeriesD нет.
