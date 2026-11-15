# Кандидат совместного C-search / construction threshold

Ветка от принятого root developcd09e64c объединяет C-search roota58a4b13
и Pulse `cc97149c90ce98ff24ca688452f4a40d54e0e63d`. Сохраняет Rdk10e9d05,
Bin99f58da и текущие native Console/probe/report paths. В develop этот кандидат
пока не принимается; работающий K1 остаётся на прежних root69789b8cb/Pulse84e456d.

## Разрешение неоднозначной оснастки

Один и тот же14-й positional bool у LearnedBoundary означал ModelSpec2 в
threshold ветке и tracked C0 в C-search ветке. Автоматическое разрешение
текстового конфликта могло бы собрать тест с другой семантикой. В официальном
integration test file введён BoundaryExtras с именованными modelSpec2,
productionCalibrationSeed, trackedCapacitance и capacitanceSearch. Все11
расходящихся calls сопоставлены с исходными parent versions:6 threshold/seed,
5 C-search/history. Первые13 аргументов, физика, бюджеты и assertions сохранены.
[Реестр сопоставления](BoundaryFixtureOptionsMergeReview.json) содержит каждый
исходный вызов и его новые named options. Остальной позиционный интерфейс пока
сохранён; это адресное устранение коллизии, не завершение всего code cleanup.

## Подготовленные controls

Восемь NativeCapacitanceModelSpec2Codec cases: Classic/Branch ×N0/N1 ×2000/20000Hz.
Проверяют независимость вложенного ModelSpec2 initial_threshold100 и внешней
configuration schema4, C-search On/Off encode/decode, strict missing/bool/downgrade
negative inputs. Codec не применяет конфиг к живому графу; прежняя revision/C0
обязана сохраниться. Эти cases не доказывают физическую динамику.

Ещё восемь NativeCapacitanceModelSpec2Boundary: Classic/Branch ×N0/N1 ×C Off/On,
2000Hz, реальное configured обучение с recorded C0, ModelSpec2 initial100,
полный learned-state roundtrip и recognition в новом владельце. Они используют
тот же engineering LT профиль и явный sync0.2, что исходные C-history/C-search
transport controls, без ослабления нового baseline0.02 и без научного PASS.
Случай может сохранить итоговый unit C-scale; доказательство вмешательства C
остаётся у activation/minimal-context cases и требует отдельной сверки.

Focused gate42 =18 прежних physical threshold/archive +8 calibration precondition
+8 новых codec +8 новых boundary. Declared full304 = прежние C-search262 и эти42.
Все списки уникальны и versioned. До исполнения они являются декларациями,
а не PASS. Должны быть выполнены на Elder и M40 ASan с actual source/runtime
closure, primary artifacts и independent readers. Сборка и численные запуски
этого joint source пока не выполнялись.

Поздний threshold0.005 после C On, его полноценный calibrated transfer,
heterogeneous/dormant geometry, весь physics/mode matrix и frozen independent
scientific evaluation остаются открытыми; эти16 новых cases их не подменяют.
CapturedPerInput, fixed last reference и defaults1e-5/relative0/sync0.02 не меняются.
Изменения структуры/физики выполняются прежними native boundary механизмами;
новых вложенных Calculate или tick-time repair в библиотеку не добавлялось.
