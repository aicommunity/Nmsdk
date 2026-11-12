# Диагностика двух полных N4 моделей на восьми паттернах

Декларация подготовлена; запуск допускается после acceptance28 controller/decoder checks. Source Tool `742bc6618f47054e9db72b91be6b0b3e27c15cd2`, Console SDK `448b153f2fea3486ff40f3a626b8f1110b9e3ee2`, Pulse7b524b8. Runtime создан production `runtime.snapshot` из готовой изолированной сборки; binary/loader/source hashes закреплены manifest, без новой сборки или подмены executable.

Полные source models берутся из Git-derived qCompress cache, raw size/SHA закреплены. Они уже прошли actual native2 roundtrip и independent composition5/5. Classic model35d849faa2aaea5d2620f0fd59d9934c77760b7fde0dd49d3284539f69f68263 остановлен invalid_observation; Branch efc6bacd25770cb3ccde41b952b2e09638296e401be88e2b6f5f7bd3548e9ecd — budget_exhausted. Certificate null. Транспортные summary8 — readout после roundtrip того же canonical package, а не поддельные результаты старого Train.

XML и CSV восьми паттернов получены из Bin commit `1c1464e248f8744e858bd66df0be99e39969fd65`; production reader сверяет структуру, ISI, метки и target. Входной Git cache `e48a05fdde0a43e441e8718278501cfd16b11510`; исходные bytes сохраняются. Каждая модель предъявляется всем8 паттернам в исходном порядке matrix, по2 s, reset-per-trial,2000 Hz. Реальные timestamps и полные окна наблюдения обязательны. Новые порядок/ITI/continuous stream и independent partition в этом запуске не проверяются.

Путь: ограниченная распаковка → production model7/summary audit → явный external primary snapshot → existing Console `diagnostic-evaluate` → проверка полного frozen evaluation. Никаких Train, retarget, PostTune, threshold sweep или шаблонного Test fallback. Порог наследуется из actual stopped model, все effective параметры и frozen hashes контролируются production reader.

Supervisor знает ровно два child directories и закрывает их по собственной kernel identity; outer budget4 GiB/21600 s, leaf8 GiB/3600 s, aggregate reservation12 GiB, output8 GiB. Отказ подготовки/аудита не означает завершённого Test. Незавершённый набор не получает положительного итога.

Ожидаемые артефакты: источники и applied jobs, runtime/source/input proofs, обе native execution/recognition models, все16 полных trial observations с Soma/LT/stimulus, versioned metrics и closure/release. На их основе нужен временной отчёт по всем паттернам и всем записанным сомам с входными импульсами, full и читаемыми detail views. Compact Git сохраняет первичные данные/модели/метрики/выбранные фигуры; полная галерея — кэш M40.

Результат имеет только диагностическую интерпретацию сохранённых остановленных моделей. Молчание, FP/FN и неудовлетворительная разделимость публикуются как измеренные свойства; сходимость обучения и scientific PASS не заявляются. После этого остаются самостоятельные cold/replay/robustness/mode matrix и performance gates исходного плана.
