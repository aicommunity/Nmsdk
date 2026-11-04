# Joint44: временные отклики сомы на все объявленные паттерны

[Компактный HTML с графиками](../../../Reports/StructTrain/TimeLearner/s11-joint44-frozen-visual-a3/index.html).
Он содержит все40 объявленных предъявлений и60 пар «проба — сома» десяти
инженерных моделей: Classic/Branch × N0/N1 × C Off/On при threshold100,
а также два существующих threshold0.0001 positive-spike controls.
Синие кривые — фактический Soma SumPotential, оранжевые — реальные входные
импульсы; фиолетовые отметки показывают реальные LT spike events.

Каждая проба имеет полный overview, а full cache — общие/локальные масштабы,
увеличения и series. Формат1920×960; на увеличениях не менее8px/native tick,
без сокращения samples. Графики кликабельны в полном разрешении. Единицы
модельные: SI descriptor отсутствует, поэтому подпись «мВ» не присвоена.
Пять production-reader проверок прошли без skips: portable primary повторяет
metrics, покрытие полное, hashes/PNG/SVG/PDF и временной масштаб проверены,
labels/patterns/reset policies/model state совпадают с декларацией.
Независимо проверены53 members compact archive,80 selected PNG и два новых
исходных blobs. Визуально просмотрены17 именованных рисунков, представляющих
все10 моделей, обе топологии, второй Classic soma, target/foil/reset variants,
увеличения и две серии. [Полный receipt](Joint44FrozenReportsVerification.json).
Полная ручная приёмка всех275 figure views не заявляется; исходные manifests
сохраняют visual_acceptance_complete=false и scientific verdict=null.

## Измеренный результат

| Модели | TP | FP | FN | TN | Примечание |
|---|---:|---:|---:|---:|---|
|Каждая из8 high100|0|0|2|2|Нет выходных spikes; потенциалы сомы ненулевые|
|Classic N0 threshold0.0001|0|1|2|1|Ранний target spike вне допустимого окна; один foil FP|
|Branch N1 threshold0.0001|0|1|2|1|Ранний target spike вне допустимого окна; один foil FP|

Это pooled counts четырёх проб на модель, не восьмиклассовая точность.
Отдельные metrics по reset policies сохранены в render-summary.json и HTML.
Target оценивается после последнего реально поданного импульса, foil — во
всём наблюдаемом окне; ранний target spike не считается попаданием.
Positive guard «есть хоть один spike» проверяет работу тракта, а не эту
классификацию. High100 silence не означает нулевой мембранный потенциал.
C On/Off здесь не является отдельным доказательством выполненной C-поправки
или эквивалентности алгоритмов по похожим waveform.

Это LT engineering fixtures с двумя входами и explicit sync0.2, не
августовские четырёхвходовые stock результаты4/8–6/8. Влияние LTMembrane
без отдельного контролируемого A/B не установлено. Никакой научный PASS,
PhysicalInfeasible либо общая невозможность классификации не присваивается.
Normal44 прошёл, но full304/readers/ASan joint native остаются отдельными gates.

## Воспроизводимость и объём

Recipe: Scripts/StructTrain/TimeLearner/specs/native-joint44-frozen-report-v1.json;
job source94c3fa262b6691faa0bef7ed1479d7b7882a6ab8, production renderer
8021301e894368aefd045f9d77274fcce9f60245. Проверяемый первичный native archive
берётся из proof82910cad87425fcad0ef67480d612bb917c6d933, без второй копии в Git.
Report proofdf29f5d469baec8d987a40e643f2a188158618b2 хранит compact manifests,
metrics/checks и80 выбранных PNG общим объёмом10887157 bytes (~10.4MiB).
Полный SVG/PDF/PNG cache остаётся на M40:
`/media/user/Data/TimeLearnerRefactor/readbacks/s11-joint44-frozen-visual-a3/full-report-cache`.
Он полностью воспроизводится из recipe и первичного Git archive. Две ошибки
подготовки (пустой origin служебной копии; системный Python без Matplotlib)
сохранены как previous-a1/a2 primary, без повторного модельного расчёта.
Финальный worker использовал прежний plot-venv-a1,2GiB/64tasks; после упаковки
вся группа закрыта и lease освобождена точной PID/start-time recovery.
