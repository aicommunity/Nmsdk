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

## Проверка на Elder

Native root `b82f76e2fe543acf25d6c3076abbd864f965b3a8`, readers
`59f28159bf5518d01871062fb90813ebd3d55cab`. Все8 native cases прошли за403.122s:
четыре реальные Exact source models дошли до калибровки; два schema2 случая
также до переноса в другого владельца; четыре legacy случая сохранили
budget_exhausted без certificate. Семь independent readers прошли без
failures/errors/skips и проверили весь набор, фактические target/foil окна,
сохранённые параметры поиска и отсутствие подмены stopped→completed.

Proof `3824e7eb2068812c94af33ef2775a7c25f8556f9`:
`Reports/StructTrain/TimeLearner/s05-calibration-preconditions-elder-a1`.
Независимо проверены все812 native и8 reader archive members,438 native
source hashes и reader source hashes. Native primary3,862,024B;
reader primary56,408B. Проверка восьми source packages нашла ровно4 completed
и4 stopped,4 calibrated packages и2 distinct-owner transfer records:
[CalibrationFixtureNormalVerification.json](CalibrationFixtureNormalVerification.json).

## Проверка на M40 ASan

Тот же native root прошёл8/8 cases за2950.468s;7/7 readers из того же
reader root прошли без failures/errors/skips. Получены4 настоящих completed
Exact sources,4 stopped sources,4 calibrated packages и2 schema2 transfers.
Фактически загруженный libasan подтверждён, detect_leaks=0.

Proof `ec7934bfd4a838b397298f9cf8ad18774b28e0f9`, раздел
`Reports/StructTrain/TimeLearner/s05-calibration-preconditions-m40-a2`.
Все812 native archive members,438 native source hashes и reader archive
проверены независимо: [CalibrationFixtureASanVerification.json](CalibrationFixtureASanVerification.json).
Native primary3,890,968B, reader primary56,452B.

Код подготовлен в отдельной ветке от develop с merge prerequisites через
`--no-ff`. Адресная приёмка восьми cases завершена на обоих workers; общая
closure с другими ожидающими feature branches ещё не принята. Первая подготовка M40 остановлена до
checkout/build, потому что old runtime ещё использовался отдельной cold
regression. После закрытия её owner запущен новый readback
`s05-calibration-preconditions-asan-a2`; исходный отказ a1 сохранён, не считается
ошибкой алгоритма и не заменён результатом a2. Оба исходных отказа входят
отдельными проверенными архивами в новый proof. Научная классификация stock
четырёхвходовой модели этим набором не проверяется.


## Приёмка объединения в develop04.11

Адресный threshold/calibration подэтап подготовлен к merge в develop.
PulseLib develop `9ec4566d71bf56d4eeb5c8a920bbc683fcd85299` имеет тот же Core
`a4768548668becf13b1af26ad242acff87e61183`, что проверенный Pulse541bf89;
после tests менялась только документация. В корневом объединении App, Tests,
CMakeLists.txt и точные Rdk/Bin gitlinks совпадают с native sourceb82f76e2.
Production Python pipeline и readers совпадают с проверенным reader root59f28159;
добавлены только отдельно проверенный resource reservation API и его tests.
[Точное сравнение деревьев](InitialThresholdIntegrationVerification.json)
позволяет использовать фактические normal/ASan результаты этого же кода, без
объявления нового численного запуска под merge commit.

Это не combined gate с ещё не принятыми C-search, CandidateCursor и explicit
native probe ветками. Их дальнейшее объединение и checks остаются отдельными.
Проверенные четыре Exact engineering-LT модели не становятся научным PASS
для stock четырёхвходового нейрона. Весь исходный план остаётся открытым.
