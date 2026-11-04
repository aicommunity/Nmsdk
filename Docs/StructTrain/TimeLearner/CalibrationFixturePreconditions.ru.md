# Предусловия native калибровочных tests

Четыре `NativeCalibratedState` / `NativeCalibratedModelSpec2` cases завершались
на Train с `maximum_sweeps_exhausted`, не достигая calibration/fresh import.
Эти реальные отказы сохранены: normal proof
`470a9251af14e50f47e89815edafe5b6d7471513`, ASan proof
`29da1f5bc1dfdd401d8bceb97cc7650f537dd5b5`. Они не устанавливают регрессию
ModelSpec2 или физическую недостижимость обучения.

Исходная постановка: ISI `[.01,.08]`, начальные L `[2,1]`, первая область
L `[2,3]`, Rs `[86,172]` МОм, четыре кандидата, нулевая subdivision depth,
один sweep; после построения C первого канала меняется на1.41nF. Эти условия
сохраняются в четырёх `NativeCalibrationPrecondition.Legacy*` controls с
явной проверкой остановки без certificate, отказом solo→recognition и
проверкой диагностического переноса. Они не называются тестами успешной
калибровки.

Положительные downstream tests получают самостоятельную явную постановку,
основанную на уже проверенном реальном production cold Train:
`a4344242c4cbbc8df7d3795ab5176c7dd694c6d6` и соответствующем ASan proof,
раздел `s05-model-spec-production-{normal,asan}-a4`.

| Условие | Новая calibration precondition |
|---|---|
| Модель | Два входа, прежний engineering LT storage profile |
| Начальное состояние | L `[1,1]`, Ns `[1,1]`, Rs `[86,86]` МОм |
| Паттерн / окно | ISI `[.01,.03]`,0.26s,540 samples limit при2000Hz |
| Первый вход | L1–3, Ns1, Rs43–86МОм |
| Опорный вход | L1, Ns1, Rs86МОм, фиксирован |
| Поиск |80 кандидатов, depth4,256 probes,128 edits, один sweep |
| Ограничения |180 model seconds,1800 wall seconds |
| Цель / допуски |CapturedPerInput; sync0.02, abs amp1e-5, relative0 |
| Физика | Storage profile без добавочной записи C после Build |

Тест обязан получить настоящий Exact certificate до вызова RecognitionChecks;
готовое обученное состояние и certificate не подставляются. Новая постановка
включается только явным `productionCalibrationSeed` у четырёх указанных cases.
Остальные heterogeneous, capacitance, default-tolerance и transport fixtures
не меняют свою постановку. Legacy отрицательные cases остаются отдельными.

Код подготовлен в отдельной ветке от develop с merge prerequisites через
`--no-ff`. Приёмка ещё открыта: нужны восемь адресных native cases на Elder и
M40 ASan, фактические traces/сертификаты/калибровка/import и независимые readers.
Научная классификация stock четырёхвходовой модели этим не проверяется.
