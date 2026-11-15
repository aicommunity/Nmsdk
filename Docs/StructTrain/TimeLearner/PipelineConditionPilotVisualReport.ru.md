# Пилот: читаемые временные отклики Classic/Branch

[Открыть компактный отчёт с графиками](../../../Reports/StructTrain/TimeLearner/s11-pipeline-condition-pilot-visual-a2/index.html).
Показаны46 выбранных оригиналов1920×960: все объявленные frozen target/foil
предъявления и каналы сомы, увеличения и confirmation выбранного порога.
Полный кэш содержит214 recorded trial/soma пар и2620 views всех6 фазовых
отчётов Train/calibration/frozen двух случаев. Дополнительные series views
объясняют2638 PNG на диске. Все кривые построены по полным native samples,
с наложенными actual input pulses; на zoom не менее8px/native tick.

| Случай | Измеренный фиксированный порог Test | TP | FP | FN | TN |
|---|---:|---:|---:|---:|---:|
|Classic-v1|0.004780132099175549|2|0|0|2|
|Branch-v2|0.009589717471100379|2|0|0|2|

Суффиксы v1/v2 в именах относятся к ModelSpec и сами по себе не являются
сравнением legacy/V2 контроллеров.

Это двухвходовые LT engineering profiles и same-matrix calibration. Четыре
предъявления на случай содержат повторные target/foil, а не четыре независимых
обучения. Target здесь находится в позициях0/3; это не проверка всех позиций,
не штатная четырёхвходовая восьмипаттерновая задача и не independent Test.
Порог и потенциалы имеют модельные единицы; SI не подтверждены. Фиолетовая
вертикаль — фактическое событие общего LT output, не отдельный spike каждой
наблюдаемой сомы. Влияние LT на результат без отдельного A/B не установлено.

## Сохранность и визуальная проверка

Primary data Git `bd10072c73d7c8296f1a4d02c051459f29f8c039`; renderer/tool
`2e0f378c97884eceaeb2b3fb864944e250f7347a`; report data
`cc039481e217cd06d2812d0fbf5d7291420950c5`. Проверены117 compact archive
members, все46 PNG hashes и348 tool/fixture hashes. Сжатые метаданные487596
bytes, выбранные PNG6387892 bytes (~6.4MB). Исходные primary повторно не
дублируются; полный PNG/SVG/PDF cache остаётся на M40:
`/media/user/Data/TimeLearnerRefactor/readbacks/s11-pipeline-condition-pilot-visual-a2/full-report-cache`.
Recipe и full-cache inventory сохранены; численных запусков при render не было.
[Сверка источников](SharedControllerNovember6Verification.json).

В исходном разрешении вручную просмотрены9 именованных рисунков: обе топологии,
обе сомы Classic, target/foil, позднее target-предъявление, общий/локальный Y,
увеличение реального отклика и calibration confirmation. Заголовки, временные
оси, легенды и overlay читаемы. [Точный QA перечень](PipelineConditionPilotVisualQA.json).
Полная ручная проверка всех2620 views не заявляется; исходные manifests
сохраняют visual_acceptance_complete=false. Обзор не заменяет измерения;
локальное увеличение вблизи границы следует читать вместе с соседним окном.

Первый renderA1 корректно отказал из-за dereferenced glog aliases в старом
архиве. Явный production restoration adapter проверил990 исходных members,
оставил982 regular files и описал8 redundant aliases. Signed manifests и
trace bytes не исправлялись; strict artifact auditor не ослаблен. A1 отказ
сохранён рядом с публикацией. При отборе zoom учтены абсолютные native clocks;
разные trial offsets не были приведены к придуманному общему onset.

Это готовый для чтения инженерный отчёт, а не окончательный научный результат
исходного плана. Полная физическая/режимная матрица и stock frozen order/ITI
исследования остаются открытыми; августовские4/8–6/8 не пересматриваются.
