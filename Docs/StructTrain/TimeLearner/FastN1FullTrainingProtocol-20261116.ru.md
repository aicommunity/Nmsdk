# Конечный cold Train всей Fast Branch-модели — 16 ноября 2026

## Основание и научный вопрос

[Принятая пара3600/7200](FastN1BracketScientificReport-20261116.ru.md) имеет точный общий префикс19 consumed scalar candidates. При7200с input2 впервые выполнил исходные timing/amplitude допуски, затем измерены только две разные длины input1 до wall stop. Это ещё не проверка полного поиска следующего входа и не доказательство физической невозможности общей цели. Новый единственный cold опыт проверяет, позволяет ли тот же измеряемый алгоритм пройти оставшиеся входы при конечном большем времени. Сходимость и хорошая классификация не требуются как заранее заданный результат.

## Неизменяемые условия

- Native runtime root7b495ebf753259ae8b78c6d0eadd561fb3d2c835 / Pulse9e7653a400761d6c2f3ea68fddcd40a4307d85e7; Core соответствует принятому Pulse23d039e44f927eb8040473845d3c391270d9d15e. Production producer source5ca731a696713a7787700e1fc553485ec5264a18 используется из существующего отдельного actor без его обновления.
- Точно тот же job, что current-wall7200, после удаления signature различаются лишь configuration.run_id и configuration.maximum_wall_seconds. Сравнение полного job обязательно до запуска.
- Холодное исходное состояние, новые references; model/search/controller checkpoint предыдущего Train не импортируется. Старые characterization frames задают только координаты полного окна[0,3600].
- Branch N4/N1, профиль TLNativeFast3F2000_Neuron, C2.5e-10F, TC0.002с,2000Гц, Lmax256, anchor index3/Lmax1, начальные L1/Ns1/Rs86MΩ, CapturedPerInput. Все per-input Rs bounds, логические budgets и отключённый C-trim остаются как в исходном job.
- amplitude_absolute1e-5, amplitude_relative0, SyncTolerance0.02с. Закреплённый импульс, distinct early crest допустима; настоящая слившаяся вершина ambiguous. Прогноз задержки предлагает кандидата, не заменяет измерение.

## Единственное вмешательство и ресурсы

Native search wall21600с, run label current-wall21600. Native finalization allowance300с отдельно, внешний controller deadline27000с включает подготовку и DATA audit; он не продлевает learner search. Не повышать logical search/model-time budgets после начала. Один новый job s11-fast-bracket-wall21600-m40-a1, отдельные controls/output; существующие frozen controller/runtime/source не менять.

Используется штатный uniform_profile_study.run и production UniformProfileTrainTest,8GiB/64 tasks внешнего controller,4GiB/64 tasks native leaf. Перед запуском минимум32GiB свободной памяти и32GiB диска Data, фактическая нагрузка сохраняется в controls. Общие readonly runtime/refs не обновляются. Истечение heartbeat reservation само по себе не освобождает ресурсы: стандартный managed-unit ledger сохраняет владение до проверенного закрытия. При timeout сначала проверять тот же owned unit; автоматический повтор исключён.

## Проверки и публикация

1. Effective preflight/cold identity/profile, частота, all-input bounds и точное сравнение job с7200 подтверждены до Train.
2. Сохраняются все события, полные/неполные composite groups, scalar candidates, модель и причина остановки. Проверить фактический общий measured prefix; различие расследовать, а не считать случайностью.
3. Только свежая проверка всех входов текущей revision даёт общий TrainingCertificate. Локально готовый input не гарантирует сохранения свойства после правки общего кабеля.
4. Любой валидный отрицательный исход сохраняется: ambiguous/unresolved/budget/saturation не переименовывать в Exact или PhysicalInfeasible. Частичные terminal observations не дополнять предыдущими остатками.
5. После закрытия — внешний primary CAS, читаемые Soma+input graphs в пригодном масштабе, residuals/фактические параметры и отдельный frozen Test всех8 паттернов. Условия порога и Same-Matrix/independent role объявлять отдельно; исходный threshold100 не считать успешным classifier при молчании.
6. Новый опыт не заменяет оставшиеся исходные этапы1–12; больших автоматических sweep и возобновления SeriesD нет.
