# Branch N4:geometry replay и читаемые временные графики —12.11.2026

**2/2 PASS**,128.20s,без skips/errors/failures. Source20e404281bc6a82be293b106cfb1d9a2de9758a7. [Unittest](completed/worker/validation/unittest.log), [result](completed/worker/validation/result.json), [closure/released lease](completed/closure-and-reservation.json). Source/fixtures before/after побайтно совпадают; новая модель не рассчитывалась, исходный Train не изменён.

## Вывод по реальным данным

Все пять missing — промах узкого прогнозного окна:тот же assigner на полной записи находит valid максимум закреплённого input2. Предыдущая контрольная группа18 valid в обоих доменах.

| Group | Recorded | Full observation | Window start,s | Assigned peak,s | Peak−start,ticks |
|---|---|---|---:|---:|---:|
| 18 | valid | valid | 0.2880 | 0.2925 | 9 |
| 20 | missing | valid | 0.3025 | 0.3020 | -1 |
| 22 | missing | valid | 0.3025 | 0.3020 | -1 |
| 24 | missing | valid | 0.3170 | 0.3115 | -11 |
| 26 | missing | valid | 0.3170 | 0.3115 | -11 |
| 28 | missing | valid | 0.3315 | 0.3210 | -21 |

Первая ошибка:sample604 исключён окном605..685. При2000Hz это0.5ms. Full geometry выбирает third/input2 maximum0.00829352955716034, хотя second/input1 maximum0.008612371704209809 выше. Значит assigned peak подтверждён независимо от глобального максимума пачки. [Полный replay](completed/worker/tmp/recovery-N4-diagnostic-replay.json).

## Графики и визуальная проверка

Автоматически проверены24figures для6groups×1soma×4views; каждая содержит6actual full/omission controls. PNG2880×2880,SVG/PDF; нет сглаживания/downsampling. Native виды по обе стороны границ окна дают≥8pixels/tick и sample markers; общийY сохраняется внутри controls. CSV soma0 соответствует Branch $.Soma1.SumPotential, не компоненту Soma0. Actual input берётся из каждого собственного CSV; в узком post-stimulus zoom он может быть вне видимого фрагмента.

Полный cache:/media/user/Data/TimeLearnerRefactor/readbacks/s07-recovery-N4-window-analysis-m40-a1/worker/tmp/Branch-N4-recovery-temporal. В Git перенесены8PNG+manifest/replay; [Git transport](selected-figure-git-transport.json) проверен fsck и SHA256 каждого файла. **Все8выбранных PNG просмотрены**, весь24-figure cache не объявлен вручную проверенным. [Точный scope](visual-inspection.json). Native measured frames и картинки дополняют друг друга:1tick разницу у плоской вершины определяют исходные числа, а не считывание высоты пикселей.

Оригинальный outcome остаётся invalid_observation, certificate=null, Test отсутствует; post-hoc valid не выдаётся за обучение. [Исправление постановки нового измерения](../../ObservationDomainWindowFix-20261112.ru.md) подготовлено отдельно, не применено задним числом.
