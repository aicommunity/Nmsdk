# Classic N4 budget16: реакции на восемь паттернов — 13.11.2026

**Работающая классификация этим опытом не получена:** при исходном пороге100 модель молчит на всех восьми паттернах, включая target. Мембранные реакции ненулевые и различаются по форме. Ниже представлены реальные временные кривые с наложенными входными импульсами, без прореживания.

Это frozen diagnostic сохранённого состояния прежнего Train, завершившегося timeout/budget_exhausted. Отдельный новый cold Train с исправленным экспортом имеет собственный job и не подменяется этим отчётом. [Исходный Train и его ограничения](ValidationPlans/M40DataSdkBudget16TrainA1-20261113/RESULT.ru.md), [восемь завершённых diagnostic проб](ValidationPlans/M40Budget16FrozenDiagnostic8A1-20261113/RESULT.ru.md).

## Модель и протокол

Classic N4/N1,2000Hz, CapturedPerInput, anchor3; stock storage безLTMembrane. Native Console использовал SDK Root92ad93cdf453967ac29108a9bbef5fd3905da59d/Pulsedfb9a98244f91b4f4029d8470465fd40116436ca. Model revision89681f2f4ee996b4a1208b18cbdaa3c3c2c2b487e78d7aa56ccec1d37a8a1f0b неизменна между пробами. Identity conversion, reset-per-trial,2s полное окно, исходные8 PhaseA patterns, target в позиции0. Threshold100 унаследован от nonspiking characterization; калибровки, PostTune, retarget и независимой выборки в этом опыте нет.

| Показатель | Результат |
|---|---|
| Выполнение diagnostic | completed/valid,8/8 complete observations |
| Состояние исходного обучения | budget_exhausted, certificate=null |
| Target | TP0/FN1, hit rate0 |
| Foils | FP0/TN7, response rate0 |
| Accuracy |7/8 за счёт семи молчаний foil; это не успешная детекция |

Наличие или отсутствие подходящего меньшего порога здесь не проверялось. Сам максимум Soma1 не подменяет вход LTZone или настоящий spiking Test: выбранный порог требует реального native прогона. При обучении нужен максимум закреплённого импульса; приведённые whole-pattern Test кривые не разрешают принадлежность слившейся вершины.

## Как читать рисунки

Синий — actual SomaN.SumPotential, оранжевый — общий фактически поданный вход на правой оси. X — native absolute time: последовательные2s пробы сдвинуты. Y одинаков для одного выхода на всех восьми паттернах; между разными сомами масштабы различаются. Единицы модели, SI не подтверждены. PNG1920×960 открывается в исходном размере. Полная cache-галерея дополнительно содержит native zooms ≥8pixels/tick и SVG/PDF.

Визуально на Soma1 foils6/7 дают более высокий максимум, чем target; это наблюдение одного выхода, а не окончательный вывод о разделимости всей модели. На target Soma2–4 видны быстрые отдельные ответы на импульсы, тогда как Soma1 имеет более широкий и поздний отклик. Одна полная кривая не доказывает однозначность назначения пика для обучения: нужны соответствующие full/omission контроли.

## Soma1: все паттерны

### Паттерн 0 — target

![Classic pattern 0, actual input and Soma1](../../../Reports/StructTrain/TimeLearner/Budget16DiagnosticGallery-M40-20261113/classic-pattern-00-soma-01.png)

### Паттерн 1 — foil

![Classic pattern 1, actual input and Soma1](../../../Reports/StructTrain/TimeLearner/Budget16DiagnosticGallery-M40-20261113/classic-pattern-01-soma-01.png)

### Паттерн 2 — foil

![Classic pattern 2, actual input and Soma1](../../../Reports/StructTrain/TimeLearner/Budget16DiagnosticGallery-M40-20261113/classic-pattern-02-soma-01.png)

### Паттерн 3 — foil

![Classic pattern 3, actual input and Soma1](../../../Reports/StructTrain/TimeLearner/Budget16DiagnosticGallery-M40-20261113/classic-pattern-03-soma-01.png)

### Паттерн 4 — foil

![Classic pattern 4, actual input and Soma1](../../../Reports/StructTrain/TimeLearner/Budget16DiagnosticGallery-M40-20261113/classic-pattern-04-soma-01.png)

### Паттерн 5 — foil

![Classic pattern 5, actual input and Soma1](../../../Reports/StructTrain/TimeLearner/Budget16DiagnosticGallery-M40-20261113/classic-pattern-05-soma-01.png)

### Паттерн 6 — foil

![Classic pattern 6, actual input and Soma1](../../../Reports/StructTrain/TimeLearner/Budget16DiagnosticGallery-M40-20261113/classic-pattern-06-soma-01.png)

### Паттерн 7 — foil

![Classic pattern 7, actual input and Soma1](../../../Reports/StructTrain/TimeLearner/Budget16DiagnosticGallery-M40-20261113/classic-pattern-07-soma-01.png)

## Target: остальные выходы сомы

### Soma2

![Target Soma2](../../../Reports/StructTrain/TimeLearner/Budget16DiagnosticGallery-M40-20261113/classic-pattern-00-soma-02.png)

### Soma3

![Target Soma3](../../../Reports/StructTrain/TimeLearner/Budget16DiagnosticGallery-M40-20261113/classic-pattern-00-soma-03.png)

### Soma4

![Target Soma4](../../../Reports/StructTrain/TimeLearner/Budget16DiagnosticGallery-M40-20261113/classic-pattern-00-soma-04.png)

## Увеличение около максимума полной реакции

В выбранном50ms участке вход может быть нулевым: наложена записанная линия, новые импульсы не достраиваются. Эти участки предназначены для анализа формы; полный причинный контекст находится на обзорах выше.

![Паттерн 0, Soma1, native maximum neighborhood](../../../Reports/StructTrain/TimeLearner/Budget16DiagnosticGallery-M40-20261113/classic-pattern-00-soma-01-maximum-zoom.png)

![Паттерн 0, Soma4, native maximum neighborhood](../../../Reports/StructTrain/TimeLearner/Budget16DiagnosticGallery-M40-20261113/classic-pattern-00-soma-04-maximum-zoom.png)

![Паттерн 6, Soma1, native maximum neighborhood](../../../Reports/StructTrain/TimeLearner/Budget16DiagnosticGallery-M40-20261113/classic-pattern-06-soma-01-maximum-zoom.png)

## Данные и область проверки

[Exact compact primary](../../../Reports/StructTrain/TimeLearner/Budget16DiagnosticPrimary-M40-20261113/bundle.json): исходная model.json282794133B и все8 observations,28 logical members/320078865B в19575080B XZ. Archive SHA256 fe5fb13532f0ea0155bf3c4aaa3b1d2e179f583f74eef44ce4e0125fc2b7ef1e. [Production export/restore/rescore10/10](ValidationPlans/M40DeclaredDiagnosticPrimaryA1-20261113/RESULT.ru.md) повторил исходные метрики. [Независимый bundle-only Elder replay принят1/1](ValidationPlans/ElderBudget16CompactReplayA1-20261113/RESULT.ru.md):335.39s, original M40 directories отсутствовали, весь original readback совпал, whole group closed/lease released.

Воспроизведение DATA анализа существующим модулем, в новом output каталоге на worker:

~~~text
python -B -m Scripts.StructTrain.TimeLearner.recorded_matrix_primary audit <bundle.json> --output <new-restored-directory> --maximum-member-bytes 402653184
~~~

[Полный report gate2/2](ValidationPlans/M40Budget16DiagnosticReportA1-20261113/RESULT.ru.md) проверил32 пары и все их виды. Вручную просмотрены только14 опубликованных originals; source visual_acceptance_complete=false сохранён. Полная галерея1803 PNG/SVG/PDF — воспроизводимый кэш M40, не новый тяжёлый Git архив. [Точные SHA и область visual QA](ValidationPlans/M40Budget16DiagnosticReportA1-20261113/VISUAL_REVIEW.json).

Отчёт не проверяет перестановки, увеличенный ITI, continuous stream, другую физику или окончательную сходимость N4. Исторические августовские4/8–6/8 исходного протокола остаются рабочими наблюдениями. Следующее решение по алгоритму должно опираться на полный outcome нового ограниченного Train, затем на конкретные measured residuals и search history; автоматического роста бюджета или возобновления SeriesD нет.
