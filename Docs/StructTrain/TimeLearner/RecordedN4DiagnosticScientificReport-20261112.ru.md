# Recorded N4: временные реакции на восемь паттернов — 12.11.2026

**Обе остановленные модели при унаследованном пороге100 молчат на всех паттернах, включая target. Успешная классификация не получена.** Мембранные реакции ненулевые: ниже фактические кривые с входными импульсами. Это диагностика сохранённых промежуточных состояний, а не новое холодное обучение или окончательная научная сводка всего рефакторинга.

## Модели и протокол

| Модель | Исходный Train | L | TP / FP / FN / TN |
|---|---|---|---|
| Classic | invalid_observation: ambiguous | 45,1,1,1 | 0 / 0 / 1 / 7 |
| Branch | budget_exhausted | 27,27,26,1 | 0 / 0 / 1 / 7 |

N4, CapturedPerInput, N1,2000Hz; восемь Phase A patterns, target в позиции0, reset-per-trial, окно2s. Все16 проб complete/valid,4001 native samples каждая. Модели и порог зафиксированы; calibration/retarget/PostTune не выполнялись, certificates нет. В этих stock графах LTMembrane отсутствует. Августовские визуальные4/8–6/8 другого исходного протокола этим результатом не отменяются.

Ось X — фактическое абсолютное время; последующие пробы сдвинуты. Оранжевый вход использует правую шкалу, синий SumPotential — левую. Общий Y масштаб сохранён для одного выхода на всех паттернах. Единицы модели, SI не подтверждены; mV не предполагаются. PNG1920×960 открывается в полном размере. Полная галерея содержит native zooms без downsampling, не менее8 пикселей на timestep.

## Максимумы и распознавание

| Паттерн | Метка | Classic Soma1 max | Classic LT max | Branch Soma1/LT max | Спайки Classic/Branch |
|---|---|---:|---:|---:|---:|
| 0 | target | 0.0047691 | 0.0130037 | 0.0245486 | 0 / 0 |
| 1 | foil | 0.0048345 | 0.0125274 | 0.0231521 | 0 / 0 |
| 2 | foil | 0.0048345 | 0.0125084 | 0.0257710 | 0 / 0 |
| 3 | foil | 0.0031990 | 0.0125039 | 0.0198734 | 0 / 0 |
| 4 | foil | 0.0055982 | 0.0172078 | 0.0295671 | 0 / 0 |
| 5 | foil | 0.0056268 | 0.0177012 | 0.0301973 | 0 / 0 |
| 6 | foil | 0.0076147 | 0.0136725 | 0.0182645 | 0 / 0 |
| 7 | foil | 0.0076147 | 0.0136772 | 0.0182645 | 0 / 0 |

[Точные числа, ISI и времена максимумов](RecordedN4ResponseSummary-20261112/responses.json) вычислены на Elder из восстановленного Git пакета, с проверкой SHA каждой пробы. Здесь максимум всей полной реакции. При обучении нужен максимум закреплённого импульса; глобальный максимум не разрешает неоднозначность слившихся вершин.

Classic LT potential записан отдельно от Soma1 и не подменяется им при оценке порога. Некоторые foil имеют максимум выше target. Это описание трасс при threshold100: результат меньшего порога требует реального native прогона, поскольку спайк изменяет динамику. Семь правильных молчаний foil не компенсируют пропуск target.

## Classic: Soma1, все паттерны

### Паттерн 0 — target

![Classic pattern 0](../../../Reports/StructTrain/TimeLearner/RecordedN4DiagnosticGallery-M40-20261112/classic-pattern-00-soma-01.png)

### Паттерн 1 — foil

![Classic pattern 1](../../../Reports/StructTrain/TimeLearner/RecordedN4DiagnosticGallery-M40-20261112/classic-pattern-01-soma-01.png)

### Паттерн 2 — foil

![Classic pattern 2](../../../Reports/StructTrain/TimeLearner/RecordedN4DiagnosticGallery-M40-20261112/classic-pattern-02-soma-01.png)

### Паттерн 3 — foil

![Classic pattern 3](../../../Reports/StructTrain/TimeLearner/RecordedN4DiagnosticGallery-M40-20261112/classic-pattern-03-soma-01.png)

### Паттерн 4 — foil

![Classic pattern 4](../../../Reports/StructTrain/TimeLearner/RecordedN4DiagnosticGallery-M40-20261112/classic-pattern-04-soma-01.png)

### Паттерн 5 — foil

![Classic pattern 5](../../../Reports/StructTrain/TimeLearner/RecordedN4DiagnosticGallery-M40-20261112/classic-pattern-05-soma-01.png)

### Паттерн 6 — foil

![Classic pattern 6](../../../Reports/StructTrain/TimeLearner/RecordedN4DiagnosticGallery-M40-20261112/classic-pattern-06-soma-01.png)

### Паттерн 7 — foil

![Classic pattern 7](../../../Reports/StructTrain/TimeLearner/RecordedN4DiagnosticGallery-M40-20261112/classic-pattern-07-soma-01.png)

## Branch: Soma1, все паттерны

### Паттерн 0 — target

![Branch pattern 0](../../../Reports/StructTrain/TimeLearner/RecordedN4DiagnosticGallery-M40-20261112/branch-pattern-00-soma-01.png)

### Паттерн 1 — foil

![Branch pattern 1](../../../Reports/StructTrain/TimeLearner/RecordedN4DiagnosticGallery-M40-20261112/branch-pattern-01-soma-01.png)

### Паттерн 2 — foil

![Branch pattern 2](../../../Reports/StructTrain/TimeLearner/RecordedN4DiagnosticGallery-M40-20261112/branch-pattern-02-soma-01.png)

### Паттерн 3 — foil

![Branch pattern 3](../../../Reports/StructTrain/TimeLearner/RecordedN4DiagnosticGallery-M40-20261112/branch-pattern-03-soma-01.png)

### Паттерн 4 — foil

![Branch pattern 4](../../../Reports/StructTrain/TimeLearner/RecordedN4DiagnosticGallery-M40-20261112/branch-pattern-04-soma-01.png)

### Паттерн 5 — foil

![Branch pattern 5](../../../Reports/StructTrain/TimeLearner/RecordedN4DiagnosticGallery-M40-20261112/branch-pattern-05-soma-01.png)

### Паттерн 6 — foil

![Branch pattern 6](../../../Reports/StructTrain/TimeLearner/RecordedN4DiagnosticGallery-M40-20261112/branch-pattern-06-soma-01.png)

### Паттерн 7 — foil

![Branch pattern 7](../../../Reports/StructTrain/TimeLearner/RecordedN4DiagnosticGallery-M40-20261112/branch-pattern-07-soma-01.png)

## Classic: дополнительные выходы на target

Все32 Classic и8 Branch trial×soma pairs находятся в полном M40 отчёте; ниже дополнительно Soma2–4 на target.

![Classic target Soma2](../../../Reports/StructTrain/TimeLearner/RecordedN4DiagnosticGallery-M40-20261112/classic-pattern-00-soma-02.png)

![Classic target Soma3](../../../Reports/StructTrain/TimeLearner/RecordedN4DiagnosticGallery-M40-20261112/classic-pattern-00-soma-03.png)

![Classic target Soma4](../../../Reports/StructTrain/TimeLearner/RecordedN4DiagnosticGallery-M40-20261112/classic-pattern-00-soma-04.png)

## Проверка и границы

[Original Console16/16](ValidationPlans/M40RecordedN4Diagnostic16A2-20261112/RESULT.ru.md), [compact roundtrip1/1](ValidationPlans/M40RecordedMatrixCompact1A1-20261112/RESULT.ru.md), [независимый Elder replay1/1](ValidationPlans/ElderRecordedMatrixPortable1A1-20261112/RESULT.ru.md), [report gate2/2](ValidationPlans/M40RecordedMatrixPrimary2A2-20261112/RESULT.ru.md). [Primary28.1MB в Git и точные версии](RecordedN4DiagnosticPrimaryPublication-20261112.ru.md).

Все19 опубликованных overview просмотрены: кривые/входы видны, заголовки/оси/легенды не обрезаны и не перекрываются. Каждый native zoom вручную не просматривался; original manifest сохраняет visual_acceptance_complete=false. [SHA и исходные пути рисунков](../../../Reports/StructTrain/TimeLearner/RecordedN4DiagnosticGallery-M40-20261112/FIGURES.json), [отдельная visual review](ValidationPlans/M40RecordedMatrixPrimary2A2-20261112/VISUAL_REVIEW.json). В Git только выбранные19 PNG (~2.5MB); полная рабочая папка и тысячи производных PNG/SVG/PDF остаются кэшем M40.

Полный HTML cache: `/media/user/Data/TimeLearnerRefactor/readbacks/s11-recorded-matrix-primary2-m40-a2/worker/tmp/recorded-n4-diagnostic-gallery/index.html`. Отчёт закрывает эту диагностическую публикацию, а не весь план. Native before/after обучения, окончательная калибровка, порядок/ITI и полная матрица режимов остаются отдельными пунктами [плана](ImplementationStatus.ru.md).
