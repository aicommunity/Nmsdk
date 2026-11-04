# Исходная матрица Phase A для новых native probes

Production CLI `phasea-matrix --bin-repository PATH --output matrix.json`
читает точные Git blobs из Bin commit
`1c1464e248f8744e858bd66df0be99e39969fd65`,
`Configs/SpikeSamples/StructTrain/SelectivityPhaseA/EXP00_baseline/Test/`:
`Parameters_00.xml` и `SelectivityLog/results.csv`. Новых процессов модели нет.
Другой источник допускается только как полный40-значный `--revision`.
Имена веток/latest не принимаются. Существующий output не перезаписывается.

## Проверяемые данные

XML DatasetMatrix имеет NumSamples8, NumFeatures1, MaxSpikesPerFeature4,
MatrixData32×1 и MatrixClasses1×8. TrainingPattern должен совпасть с единственным
target. CSV проверяется по уникальному trial ID0–7 и target_class, а не по
положению строки. Все восемь полных ISI извлекаются из XML:

| Source ID | Метка | Полный ISI, s |
|---|---|---|
|0|target|0.01,0.08,0.16,0.24|
|1|foil|0.01,0.24,0.16,0.08|
|2|foil|0.01,0.16,0.08,0.24|
|3|foil|0.01,0.16,0.16,0.16|
|4|foil|0.01,0.02,0.22,0.24|
|5|foil|0.01,0.24,0.22,0.02|
|6|foil|0.01,0.04,0.04,0.40|
|7|foil|0.01,0.40,0.04,0.04|

CSV содержит только три **межимпульсных** интервала: начальная0.01 s там
отсутствует. Четвёртый isi slot CSV должен быть пустым. Parser сравнивает три
интервала с XML и не добавляет начальную задержку по догадке. Дубликаты,
пропуски, повреждённые числовые поля, NaN и расхождения меток запрещают extraction.
Source paths, commit, blob SHA1, byte SHA256 и размеры сохраняются в артефакте.
Отдельная semantic matrix SHA зависит от ID/labels/паттернов. Перестановка CSV
меняет source SHA, но не semantic matrix SHA. Response amplitudes, spikes,
старый match/verdict из CSV не импортируются.

## Новая native постановка не является историческим replay

`trial_design` сверяет target матрицы с фактическим target обученной модели.
По умолчанию создаются8 циклических порядков ×8 паттернов, каждый target position,
reset-per-trial,2000Hz и окно2.0 s;4005 maximum samples включает запас на границы
окна. Можно явно выбрать один порядок или continuous dynamics. Векторы разных
trial не разделяют mutable storage. Это подготовка деклараций, не выполнение
Train/export/calibration/Test и не подтверждение frozen состояния.

Исторические Dataset Delay1.5/AdvanceSampleAfterBurst/LoopSamples/StateGeneration
сохраняются как source metadata. `historical_presentation_reproduced=false`
запрещает трактовать выбор тех же паттернов как повтор исходного scheduler/ITI/
reset policy. Период2s и reset-per-trial объявляются новыми условиями. Результат
августовского baseline и наблюдения4/8–6/8 остаются историческими результатами.

Пять reader tests используют настоящие Git XML/CSV: blobs/onset/labels,
перестановка CSV, повреждённые/дублирующиеся входы,64 trial IDs/target positions/
защита от alias mutation и production CLI с отказом overwrite/symbolic revision.
Серверная проверка завершена:5/5 без errors/failures/skips на каждом worker.
Elder proof `fe97c6016b7180a7b4525f63d1322e983cbb446f`, M40 proof
`bbe37a22629f829f1a376f6775bb07dc2931cca6`, source root
`d3ef795caaea9877ef3e1d8fdbfe0595b5bd751a`. Независимо проверены все10 members
каждого архива, outer/member hashes и291 точных Git source hashes на worker.
Оба исходных XML/CSV совпадают байт-в-байт со старым Bin Git commit; старый
commit — предок текущего Bin99f58da9. Полученные matrix.json побайтно одинаковы
на двух workers. Scope — extraction и native trial declarations; моделей
не рассчитывали, old response metrics не импортировали. Это не приёмка всего
Train→Test, scientific physics matrix или полного исходного этапа11.

Получение матрицы не подтверждает успешного cold Train; до валидного завершённого package новый
Test не запускается. Временные отчёты будущих проб должны содержать все паттерны,
реальные входные импульсы и читаемые Soma traces согласно исходному плану.
