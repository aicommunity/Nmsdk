# Реальный schema2 coordinator: Classic и Branch pilot

06.11.2026 на Elder завершены два реальных cold pipeline: Classic-v1 и Branch-v2.
Tool root `d43780822a7b9e2b7c0229c323cda174abc7fce8`, compiled SDK
`2e0618110a9abb48b94f6edc6b63c51f829ec810` / PulseLib
`12d8c8a41c998ae1516496f716a0ae0f3d312b3e`. Runtime/сборка/физика не обновлялись.

## Что проверено реальным выполнением

Для каждого случая: cold Train → завершённая граница → continuation → export →
измеренная grid calibration с confirmation → frozen evaluation. Это четыре
различных managed native phase units на случай, восемь всего. Заранее сохранённая
модель не импортировалась вместо cold Train; исторические данные дали декларации,
profile archives и исходные условия. Новый actual learned package получен от Train.

Schema2 condition binding записан до Train и повторно проверен после продолжения.
Его fingerprint не изменился при переименовании operational IDs. На границе
paused Train и после calibration/Test сохраняются bytes binding и solo package.
Повторное continuation полностью завершённого pipeline не создало новых unit
и вернуло тот же audit. Исходный schema1 interpreted protocol не переписывался.

Оба frozen контроля дали TP2/FP0/FN0/TN2. Это прежние инженерные двухвходовые
профили с LTMembrane и явно заданными допусками, same-matrix calibration;
не stock4-input/8-pattern, не independent evaluation и не новая независимая
случайная реплика. ModelSpec1/2 — варианты декларации, не научные повторы.
Condition declaration bound=true не меняет condition_identity_attested=false:
полная effective-factor attestation остаётся открытой.

## Доказательства и ресурсы

[Полный primary bundle](../../../Reports/StructTrain/TimeLearner/s10-pipeline-condition-native-elder-a1/bundle.json),
data commit `bd10072c73d7c8296f1a4d02c051459f29f8c039`:
990 файлов,253385299 несжатых bytes,4492472 bytes xz,
SHA256 `574eecd5ae76a62b954422c9daeacadda2be9cda4f9184288e08240906774702`.
Включены реальные модели, JSON/CSV наблюдения, journals, conditions, phase manifests,
process ownership/loaded mappings, registry snapshots, исходный producer и runtime.

На сервере production audit_pipeline повторно проверил обе цепочки и bindings.
Каждая из восьми native групп свежо проверена через manager/kernel, case leases
и общая reservation освобождены. Проверены восемь разных boot/PID/start identities,
returncode0, bound_cgroup closure и executable mapping реального Console.
[Независимая локальная сверка](PipelineConditionNativePilotVerification.json)
проверила все990 members, все340 source/fixture hashes и исходные process records.
Локальных численных прогонов или повторного scorer не было.

Parent ограничен512MiB, последовательные native units —4GiB. Общий slot/RAM/disk
lease учитывает4.5GiB и384MiB output budget; это не filesystem quota. До старта
проверены прежние объёмы тех же двух случаев250999635 bytes, свободное место
и MemAvailable. Monitor мог отменить только принадлежащую pipeline фазу при
free disk<1GiB. Глобальная политика ресурсов не менялась. Предыдущие jobs
не перезапускались, работающий M40 ASan133 не затрагивался.

## Что ещё требуется

[Новый полный8 native suite](PipelineConditionBinding.ru.md) для обеих топологий,
ModelSpec1/2 и N0/N1 stopped controls, серверная проверка деклараций этого suite,
временные отчёты всех сом/паттернов этого корпуса с реальными входными импульсами
и visual QA. Затем — отдельная приёмка production integration. Модели/данные
данного pilot могут использоваться для воспроизводимого render без нового Train.

Ветка содержит pending C++ slice; этот pilot не заменяет ASan lifecycle133,
полную матрицу исходного плана и необходимые child-first merges.
Все этапы1–12 остаются частичными; общая цель не завершена.
