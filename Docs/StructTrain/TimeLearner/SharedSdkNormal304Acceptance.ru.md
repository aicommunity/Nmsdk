# Общий SDK2e/Pulse12d: полный normal304 принят

06.11.2026 на Elder завершены304/304 объявленных C++ случаев в одном процессе,
без failures/errors/skips. В отличие от прежнего SDK802, это новый общий срез:
root `2e0618110a9abb48b94f6edc6b63c51f829ec810`,
PulseLib `12d8c8a41c998ae1516496f716a0ae0f3d312b3e`.
Orchestration tool `10d45ed93f08928a9992a3cf569c6a4938cdcd64`.

## Исполнение и первичные данные

Использован ранее собранный неизменяемый runtime; пересборки и изменений модели,
математических допусков или списка304 случаев перед прогоном не было.
Native wall time5886.344300684053s. Executable SHA256
`bcc51673ce59f1605567e7d8c998e6785ab978e0ff33c82aa116af39f52c9291`.
Runtime fingerprint `4b6267db0bc38e64426de6e9e54380f6765da9070cfda4bec066132b823697ca`.

[Полный primary bundle](../../../Reports/StructTrain/TimeLearner/s07-integrated-native304-normal-a1/bundle.json),
data commit `d3429a33209a9985a3d30164df69206713f8d724`:
3936 файлов,1489800745 несжатых bytes,11738976 bytes xz,
SHA256 `e95626641478c04131900bf17aebed1cca3264f8ad6e05499d4409d3e5a97414`.
Архив содержит исходный JUnit, нативные пробы, process/runtime observations,
ресурсную историю, спецификации и точный producer.

[Независимая сверка](SharedSdkNormal304Verification.json) проверила все3936
archive members, ровно304 уникальных ID исходного JUnit против декларации,
completed/run и отсутствие disabled/skipped/failure/error, returncode0,
фактическую executable mapping и26 loaded files. Все720 compiled-source hashes
проверены против Git blobs соответствующих root/Pulse commits;282 tool hashes —
против отдельного tool commit. Никаких численных проверок локально не выполнялось.

Процесс ограничивался8GiB в общей группе задания. Измеренный peak до archive:
1885511680B; memory events max/oom/oom_kill=0. Это не final peak после упаковки.
Disk cancellation не срабатывала, exception/archive-exception отсутствуют.
Свежий production dependency после завершения подтверждает closed group и
released lease. Исторический cleanup-closed.json относится к предыдущей очистке;
для closure этого задания используется отдельный fresh-operational-dependency.json.

## Область приёмки и открытые требования

Принимается полный normal software regression gate нового общего среза.
Это не ASan, не новая научная серия, не подтверждение независимой классификации
восьми паттернов. Результаты отдельных тестов с ожиданием честной остановки
обучения являются успешными проверками контракта, не успешным обучением модели.

Новая ASan-сборка/focused8 требуют отдельной приёмки первичных данных;
lifecycle133 выполняется отдельно. Pending C++ ветки этим одним normal receipt
не объединяются в develop. Полный lifecycle/storage/physics/mode matrix,
legacy/V2 сравнение, stock Train и frozen independent evaluation остаются открытыми.
Все исходные этапы1–12 частичны; общая цель не завершена.
