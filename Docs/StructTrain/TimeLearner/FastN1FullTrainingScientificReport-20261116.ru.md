# Fast N1: итог увеличенного общего времени — 16 ноября 2026

Cold Train завершён с budget_exhausted и без TrainingCertificate. Общий лимит21600с не исчерпан: фактически8075.12с. Остановила последняя измерительная группа, превысившая свой wall limit300с. Это ограничение выполнения; физическая невозможность цели или сходимость модели не доказаны. [Квитанция и точные внешние refs](FastN1FullTrainingScientificAcceptance-20261116.json).

## Условия и проверка

Job s11-fast-bracket-wall21600-m40-a1, producer5ca731a696713a7787700e1fc553485ec5264a18, controls1ea945c3520bbd80121c0a0a74f9f0002ff65e3a. Runtime root7b495ebf753259ae8b78c6d0eadd561fb3d2c835/Pulse9e7653a400761d6c2f3ea68fddcd40a4307d85e7; Core соответствует принятому Pulse23d039e44f927eb8040473845d3c391270d9d15e. Branch N4/N1, Fast3 C2.5e-10F/TC0.002с/2000Гц; LTMembrane отсутствует, C-trim Off. CapturedPerInput, амплитудный допуск1e-5/relative0, SyncTolerance0.02с. [Объявленный до запуска протокол](FastN1FullTrainingProtocol-20261116.ru.md).

Исходное состояние холодное; references захвачены заново. От current-wall7200 изменены только run_id и общий wall limit. Первые28 scalar candidates точно совпадают по input, индивидуальным и полным параметрам, обоим signed timing residuals, amplitude residual и local flags; разные run/trial IDs не сравниваются как физика. Это детерминированный общий префикс, не независимые случайные повторы. Production CLI/DATA/physical проверка1/1 прошла, все три owned units закрыты. PASS проверки не означает успешное обучение.

## Измеренный результат

31 scalar candidate,63 logical search requests,30 изменений;66 полных composite groups и одна неполная. Всего401 native probe. Input2 локально достиг исходных допусков при L121/Rs9.73184034290068MΩ: timing−0.0005с, amplitude−1.515471309554428e-7. После последующих правок всей модели это не является свежей финальной проверкой input2.

Последние завершённые измерения input1:

| L | Rs, MΩ | Timing residual, с | Amplitude residual | Примечание |
|---:|---:|---:|---:|---|
|122|86|−0.159|−0.0234429237055|Оба допуска нарушены|
|123|86|−0.157|−0.0234550613882|Оба допуска нарушены|
|121|9.7318403429|−0.161|+0.0003373052370|Общая точка с input2; это другое физическое состояние|
|124|86|−0.155|−0.0234670270437|Повторная оценка при L0=125 сохраняет те же остатки|

После них предложена структура L=[201,201,121,1], Rs=[86M,86M,9.73184034290068M,86M]Ω, Ns=[1,1,1,1]. На ней последняя группа не завершена: это повторное измерение опорного input3, а не input1. До измерения input1 на L201 алгоритм ещё не дошёл. Остатки предыдущего L124 не переносятся на L201; прогноз задержки не заменяет измерение.

Две предыдущие полные группы заняли195.689 и204.183с при модельной длительности10.803с. Последняя группа:300.616с wall,8.9555с model; записаны пять из шести проб, последний отклик частичен. Model budget20с не исчерпан. Причина native_composite_group_time_budget_exhausted согласована с сырыми clocks и omission_group_time_budget_exhausted. Дополнительного автоматического увеличения лимитов не выполнялось.

Terminal model revision07101c0b0b29e746ad601050613786b1450f5a733464b501c5738ab92d3d7b22. Final verification отсутствует, certificate=null, model_state_kind=diagnostic. Сохранённое состояние не является checkpoint незавершённой пробы или controller search.

## Данные и продолжение

Полный primary:1381 logical members,862678486байт expanded,16125384байт XZ. SHA2564f11c876c309e8b511b3787d02606c5ba6ad888fce6cd010d36615c3e6277f63. Отдельные bundle manifest и provenance содержат точные исходные модели, summary, CSV, события, неполную terminal group, controls и квитанции закрытия. Все оригинальные байты сохранены; тяжёлые данные находятся только в /media/user/Data/Nmsdk-StructTrainExpArchive.

Запущен предусмотренный frozen Test всех8 исходных паттернов новой terminal-модели при исходном threshold100, reset-per-trial и полном2с окне: s11-fast-full-training-frozen-m40-a1. Его итог ещё не принят; прежний Fast TP1/FP3 относится к другой модели terminal7200. Новый Train и изменение математических допусков ради улучшения счёта не выполнялись. [Сравнительный временной отчёт7200/21600](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-comparison/index.html) готов1/1:32PNG, SVG/PDF; четыре overview нового Train просмотрены. Обычные views сохраняют все полные/omission кривые и явный CENSORED. Native edge zooms этого выпуска показывают границы полного окна; приёмка native zoom около самой вершины ещё открыта.

## Выбранные временные графики обучения

| Группа terminal21600 | Назначение | График |
|---|---|---|
|4|Исходный anchor input3|[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-comparison/wall21600/group-000004-soma-000-overview.png)|
|52|Локально готовый input2|[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-comparison/wall21600/group-000052-soma-000-overview.png)|
|62|Завершённое измерение input1 при L121|[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-comparison/wall21600/group-000062-soma-000-overview.png)|
|67|Повторный anchor input3 на новой L201 структуре; неполная группа|[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-comparison/wall21600/group-000067-soma-000-overview.png)|

Отсутствующий full repeat последней группы не достраивается. Её full-before на картинке относится к anchor input3; его быстрые пики не описывают ещё не измеренный input1 на L201. Все кривые показаны с фактически записанными входами, без сглаживания.
