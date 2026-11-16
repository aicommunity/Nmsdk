# Fast Branch N1: влияние времени поиска на текущем ядре — 16 ноября 2026

Оба холодных Train завершены и прошли production CLI/DATA/physical audit 1/1 каждый. При 7200 с один вход достиг исходных допусков; сходимость всей модели не подтверждена. Классификация этой пары ещё не измерена: отдельный frozen Test восьми паттернов выполняется. Это адресное сравнение бюджета, без новой правки математического алгоритма.

[Машиночитаемая квитанция](FastN1BracketScientificAcceptance-20261116.json), [полная временная галерея](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-n1-current-wall-pair/index.html).

## Условия и результаты

Один и тот же текущий native runtime и исходный холодный профиль: Branch N4/N1, TLNativeFast3F2000_Neuron, C=2.5e-10 F, DissociationTC=0.002 с, 2000 Гц, без LTMembrane. Начальные L=1, Ns=1, Rs=86 MΩ; Lmax=256, опорный вход index3 ограничен L=1. Цель CapturedPerInput, amplitude tolerance=1e-5, relative tolerance=0, SyncTolerance=0.02 с. References захвачены заново. Логические бюджеты одинаковы: 128 probes, 1280 edits, 128 candidates, четыре sweeps/recoveries, максимум model time=7200 с. Различаются run ID и maximum_wall_seconds.

| Наблюдение | 3600 с | 7200 с |
|---|---:|---:|
| Измеренные scalar candidates | 19 | 28 |
| Полные composite groups | 42 | 61 |
| Неполные terminal groups | 1 | 1 |
| Native probes / sampled frames | 257 / 925124 | 371 / 1333530 |
| Локально одновременно в timing/amplitude допусках | 0 | 1: input index2 |
| Исход обучения | budget_exhausted | budget_exhausted |
| Общий TrainingCertificate | отсутствует | отсутствует |

Первые 19 consumed scalar candidates совпадают точно: input index, полные и активные параметры, timing bounds, amplitude residual и признаки допусков. Это два детерминированных холодных прогона с общим префиксом, а не независимые случайные повторы. Uniform physics сохраняется при росте с 2 до 123 membranes.

## Локально готовый input2 и границы вывода

В 7200-секундном Train group52/epoch23: L=[122,122,121,1], Rs=[86M,86M,9.73184034290068M,86M] Ω, Ns=1. Для input2 timing residual=-0.0005 с, amplitude residual=-1.515471309554428e-7. Оба исходных допуска выполнены. Model revision f122a9ba82c154cf28e4081fcee0ab1d3b977eaaa19ad659211a4323e6af95f6; semantic proof ff858eafc91d4d5c786e99f186057e8228c21f1a6d3fecad70f205a9bb1157b2.

Далее контроллер перешёл к input1. Измерены L122 и L123: временные ошибки около -0.159/-0.157 с, амплитудные около -0.023443/-0.023455. Допуски не выполнены. Третья проба не закончена до бюджета. Terminal groups43/62 явно incomplete/censored: остатки предыдущего кандидата им не присваиваются. Ни один terminal state не имеет полного consumed scalar observation или общего сертификата.

У terminal7200 L=[122,121,121,1], Rs=[86M,9.73184034290068M,9.73184034290068M,86M] Ω. Совпадающие attach positions input1/input2 используют общий физический банк; их Rs не независимы. Локальный сертификат прежнего input2 нельзя переносить на всю изменённую модель. Совпадение model hash с group52 не доказывает stale-hash: набор физических портов остаётся прежним, меняется логическое назначение входа. Полный fresh all-input gate ещё не пройден.

## Визуальные материалы

Построены 28 PNG с SVG/PDF и HTML index; просмотрены семь оригинальных overview, перечисленных ниже. Они показывают Soma, фактические входные импульсы и omission controls. Native zoom около границ окон имеет не менее 22.464 px/tick; полный ручной просмотр всех 28 видов и покадровых окрестностей каждого пика не заявляется.

- [3600: исходный group4](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-n1-current-wall-pair/wall3600/group-000004-soma-000-overview.png), [кандидат group40](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-n1-current-wall-pair/wall3600/group-000040-soma-000-overview.png), [неполный group43](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-n1-current-wall-pair/wall3600/group-000043-soma-000-overview.png).
- [7200: исходный group4](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-n1-current-wall-pair/wall7200/group-000004-soma-000-overview.png), [локальная готовность input2, group52](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-n1-current-wall-pair/wall7200/group-000052-soma-000-overview.png), [input1, group54](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-n1-current-wall-pair/wall7200/group-000054-soma-000-overview.png), [неполный group62](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-n1-current-wall-pair/wall7200/group-000062-soma-000-overview.png).

В group52 отдельная вершина закреплённого input2 исчезает при omit2; измеренные residuals подтверждены независимым от ручного просмотра аудитом. У input1/group54 ответ различим, но слишком ранний и слабый. Истинное слияние вершин по-прежнему неоднозначно; максимум всей пачки не подставляется вместо закреплённого импульса.

## Источники и сохранение

Producer source 5ca731a696713a7787700e1fc553485ec5264a18; controls 67a3a73367c70b6840ec0b9f81704bcfef9b79bd. Runtime root 7b495ebf753259ae8b78c6d0eadd561fb3d2c835 / Pulse 9e7653a400761d6c2f3ea68fddcd40a4307d85e7; Core соответствует принятому Pulse23d039e44f927eb8040473845d3c391270d9d15e. Полные источники и controls отчёта/collector записаны в квитанции.

Внешний primary содержит 2211 logical members обеих исходных кампаний: SHA256 2f2594cf1180250508dc02c8f9474333f4fad14ca1a52a324f49fac2c9a110b5, 21898004 байта. Архив отчёта: 85b31fa49497c438b9828688d282a63bde78b73fa01712655ac02b0ce93873c5, 17572836 байт. Полные модели, CSV и графики находятся только в /media/user/Data/Nmsdk-StructTrainExpArchive. Компактные refs, hashes и результаты находятся в Git. Нового независимого восстановления primary этой пары на другом worker пока нет.

Следующий конечный опыт — actual frozen8 из terminal7200, job s11-fast-bracket-frozen-m40-a2, source5248368b75194c657163f51f747f4512605e0e1b, controls cd0f95d24da03f1023eef6958b611f44c1e88d7a. По проверке 16.11,09:49МСК он выполняется на M40. Это diagnostic evaluation stopped-модели с threshold100, без утверждения о завершённом Train. Итог восьми проб будет опубликован отдельно. Исходный setup A1 не запускал native/worker job из-за ошибки временного launcher; A2 использует отдельные controls.

Больший бюджет позволил достичь измеренной локальной цели, но не доказывает достаточность бюджета для всей модели, физическую невозможность оставшихся целей или исправление алгоритма. Исходный план этапов1–12 остаётся частичным; 8/8 не является условием завершения рефакторинга.
