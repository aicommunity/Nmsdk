# Август: воспроизведение сохранённых моделей Phase A

01.11.2026 на Elder заново собран исходный корневой commit
`de02a3809395dd0bbd11e2ba792bfc04a51c89f3` от13.08.2026 с его точными gitlinks.
Свежие Test-прогоны трёх сохранённых моделей воспроизвели исторические4/8,
5/8 и6/8. Target обнаружен во всех трёх случаях; ложных срабатываний4,3 и2.
Это runtime-подтверждение исходного протокола, а не только повторный анализ CSV.

| Исходный Test | Порог в overlay | Совпадений | TP / FP / FN / TN |
|---|---:|---:|---|
| EXP00_baseline/Test |0.0115|4/8|1 /4 /0 /3|
| EXP01_ltz_threshold_sweep/Test_thr00130 |0.0130|5/8|1 /3 /0 /4|
| EXP01_ltz_threshold_sweep/Test_thr00135 |0.0135|6/8|1 /2 /0 /5|

Сохраняются исходные порядок предъявления, интервалы, reset policy, частота
2000Гц и морфология49/41/25/1. IsNeedToTrain=0 проверяется в Model и Parameters.
Cold retrain, перестановки и увеличение ITI этим опытом не проверены. Они
остаются отдельными уровнями сравнения и не отменяют августовских наблюдений.

## Происхождение и исполнение

| Дерево | SHA |
|---|---|
| Root |de02a3809395dd0bbd11e2ba792bfc04a51c89f3|
| Bin |1c1464e248f8744e858bd66df0be99e39969fd65|
| PulseLib |cbf76fbe077a7003dccf72b142d7136721fa1afb|
| Rdk |237ce0f177280049ab1eae305a09ce3e8c63833a|
| BasicLib |2927cad5a7456b301217b7abb228f12c9a359ea9|
| MotionControlLib |85e4494e8596b0998feebff7da2f8d421a6df66f|
| CvBasicLib |c471297811367abd348c6258bdaeaf8e1a40c7bd|
| HardwareLib |ac53a6011bfedf97d459b47bcd4d525fb6c9b811|

Release-сборка NeuroModelerConsole, BUILD_TESTS=OFF, NO_MOTION_CONTROL=ON,
RDK_LLM_BUILD_EMBEDDED=OFF, parallel4. Historical CMake пишет в Bin/Platform
собственного изолированного checkout; общий пользовательский runtime не менялся.
SHA256 executable:
`1642857243c8235466a62c64a4a9b5e9a36b75e48e44c66e5326f3e8d6735357`.
После терминального завершения первого build отдельная incremental-проверка
вернула0 и подтвердила неизменность binary. Сохраняются оба журнала.

Свежие case directories получают только tracked конфиги из Bin указанного SHA.
Исторический results.csv хранится отдельно как reference; SelectivityLog,
StatisticLog и EventsLog не копируются в новый work directory. Console работает
через production process_runner с owned PID/start ticks и loaded-files hashes.
Для каждого случая model time40s, wall limit900s; все три процесса завершились0.
СерияD и старые очереди не запускались.

У старой Console нет --app-ini: она загружает NeuroModelerConsole.ini из cwd.
Поэтому подготовлен явный ini с ресурсами исторического Bin и offscreen Qt;
его hash проверяется до и после запуска. Пользовательский ini не наследуется.

## Границы доказательности

Историческая16-колоночная схема CSV не содержит complete/censored,
полного списка спайков и late-response evidence. Root adapter
`historical_selectivity.py` сохраняет native match criterion и TP/FP/FN/TN,
но возвращает unknown для полноты и null для строгого verdict. На каждом
worker29/29 Python checks:9 исторических CSV/CLI/corruption controls и20
существующих Branch dynamics/domain CLI regression checks. Это не native
матрица всех режимов и не завершённая миграция общего scorer из Bin.

Сверка post-run XML подтверждает одинаковые пути/классы графа и выбранные
свойства. Она не является полным frozen-model fingerprint. Save меняет
десятичный формат некоторых векторов; кроме того, нативная структурная
настройка переносит порог parent Neuron в child LTZone. Поэтому простое
сравнение Model+Parameters с post-run XML обнаруживает ожидаемое изменение
child threshold в двух threshold cases. Без effective pre-run readback нельзя
объявлять все выбранные child properties неизменными. Полный экспорт V2
не подменяет собой семантику исторического файла.

На старте Console выдаёт Dataset PrepareDataset rejected data / Build exception.
Предупреждение сохранено вместе с stderr. Оно не скрывается и не объявляется
безвредным без отдельной проверки. Реальные DatasetMatrix пробы дали8 строк
с ожидаемыми ID, метками и ISI во всех случаях; это ограниченное наблюдение,
не общее доказательство валидности любой исторической конфигурации.

## Временные диаграммы: обязательная незавершённая проверка

Первый отдельный observer-прогон a1 использовал штатный исторический
UStatisticDoubleMatrix. Stimulus, LT output и learner SomaNeuronAmplitude
записаны; CSV baseline побайтно совпал с untouched replay. Однако четыре
SumPotential-файла не созданы: это ptPubState без ptOutput, тогда как recorder
открывает файлы через FindOutputProperty. Producer корректно завершился ошибкой
historical_native_trace_missing:soma1. Попытка сохранена как failed, не PASS.

Исправленный observer a2 записывает ExcChannel.Output и InhChannel.Output
каждой сомы, общий Neuron.SomaSumPotential, фактические stimulus и LT output,
а также learner cached soma vector. Исторический NPulseMembraneCommon::ACalculate
вычисляет SumPotential как сумму Outputs каналов; именно эта явно обозначенная
сумма должна использоваться на рисунке. C++ исторической модели не патчится.
Cached learner vector служит отдельной диагностикой порядка, а не незаявленной
заменой прямых измерений каналов.

До визуальной приёмки обязательны: все потоки/finite значения, общий clock и
шаг,32 фактических импульса/8 пачек, соответствие ISI и ID, покрытие окон,
побайтное сравнение CSV с untouched replay, рисунки всех8 паттернов с входными
импульсами и читаемыми zoom. Полный cache хранится на M40, в Git — сжатые
первичные данные, метрики и выбранные рисунки. На момент этой записи a2 ещё
не принят; temporal_report_complete=false. Offline sweep spiking trace не
заменяет новый прогон выбранного порога.

Этот результат закрывает адресный saved-state replay трёх случаев, но не весь
этап11. Остаются cold retrain, legacy/V2 A/B, order/ITI и полная исходная матрица.
