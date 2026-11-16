# Cold Branch N1: штатные Stock и PSI2.5 — 16.11.2026

Оба холодных обучения дали локальное решение для input2, затем остановились на неоднозначной принадлежности раннего отклика input1. Общего сертификата сходимости нет. В этой конкретной паре PSI2.5 не устранил слияние вершин. Один детерминированный cold run каждого профиля не доказывает общий эффект PSI на обучаемость или классификацию.

## Протокол и источники

Использованы штатные storage-образы NSPNeuronGen и NSPNeuronGenPreinh2_5. Production comparator проверил полные effective initial graphs: разрешены замена образов и соответствующие параметры PSI; остальная физика, связи, порядок расчёта и runtime совпадают. Частота2000Гц, LTMembrane отсутствует. Цель CapturedPerInput: каждый профиль заново захватывает собственные амплитуды. У обоих одинаковые исходные L1/Ns1/Rs86M, математические допуски amplitude_absolute1e-5, amplitude_relative0, SyncTolerance.02 и бюджеты поиска. Состав факторов и полный контроль сохранены в [production-протоколе](PresynapticTrainingComparison-20261116.ru.md) и [квитанции](PresynapticTrainingComparisonAcceptance-20261116.json).

Native runtime root7b495ebf753259ae8b78c6d0eadd561fb3d2c835/Pulse9e7653a400761d6c2f3ea68fddcd40a4307d85e7. Producer Stock64327e103d7085972f6512db77a2195f27c5b2fc, PSI1f551388cf62f2c3d427796c7d5ced635ecd7530; различие Python producer связано с подготовкой относительных окон. Полное сравнение configuration/runtime, включая производные guards, выполнено report producer1d95dbd475eaa6f0f808484b54e09a579d9f88d9.

Первый PSI A1 не входит в научную пару: он корректно отказал до поиска из-за окна[12,3612] вне записанного[0,3600]. Исправлена подготовка guards на основе измеренных координат собственного reference-пика. Опорный пик сдвинут1009→1021 кадров, то есть на6мс при dt=.0005с; raw guards должны различаться, чтобы effective полное окно совпадало. Production prepare проверен на реальных PSI данных; отдельная compatibility проверка Fast-profile завершена1/1. Чужие амплитуды и обученные параметры в Train не импортировались. [Исходный setup failure](PresynapticWindowSetupFailure-20261116.json), [приёмка подготовки](PresynapticWindowPreparationAcceptance-20261116.json), [последняя проверка серверов](PlanStatusReadback-20261116.json).

## Результаты обучения

| Наблюдение | Stock | PSI2.5 |
|---|---:|---:|
| Полные группы измерений |58|56|
| Native probes |348|336|
| Scalar candidates |22|21|
| Локальные jointly-ready candidates |1, input2|1, input2|
| Последний исход |invalid_observation|invalid_observation|
| Причина |rejected_candidate_window:ambiguous, input1|rejected_candidate_window:ambiguous, input1|
| Общий сертификат |отсутствует|отсутствует|
| Terminal L |36/35/27/1|36/35/27/1|
| Terminal Rs, MΩ |86/2.8800716/21.2323043/86|86/2.8800716/20.4214997/86|

Все процессы закрыты; production CLI, DATA и physical audits приняты1/1 для каждого запуска. [Stock primary/метрики](PresynapticStockColdAcceptance-20261116.json), [PSI primary/метрики](PresynapticColdScientificAcceptance-20261116.json).

Локально успешное PSI измерение относится к модели L28/28/27/1, input2 Rs20.421499653382123MΩ: timing residual+.0019999999999527063с, amplitude residual−5.406867076285238e-8. Model revision ebb1a212e2158d8a0f5b4d73492a7fdae37b99451d3b2384a7a102c8a344ae1f. Эти остатки нельзя переносить на terminal L36/35/27/1 после изменения общего кабеля. Для Exact требуется свежая общая проверка.

## Временные графики и визуальная проверка

Галерея содержит70 оригинальных PNG2880×2880, SVG/PDF и навигацию. Для каждой выбранной группы доступны overview, detail, обе границы окна и native response zoom. Общая Y внутри группы позволяет сравнивать полный отклик и omission controls. На response zoom22.464px/native tick, без прореживания. Глобальный максимум используется только для выбора оси увеличения: он не становится измерением закреплённого импульса.

| Состояние | Stock | PSI2.5 |
|---|---|---|
| Reference, group4 |[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/stock-psi-cold/stock/group-000004-soma-000-overview.png)|[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/stock-psi-cold/psi/group-000004-soma-000-overview.png)|
| Local input2, groups48/46 |[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/stock-psi-cold/stock/group-000048-soma-000-overview.png)|[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/stock-psi-cold/psi/group-000046-soma-000-overview.png)|
| Terminal input1, groups58/56 |[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/stock-psi-cold/stock/group-000058-soma-000-overview.png)|[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/stock-psi-cold/psi/group-000056-soma-000-overview.png)|
| Terminal native zoom |[Stock](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/stock-psi-cold/stock/group-000058-soma-000-response-maximum-native.png)|[PSI](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/stock-psi-cold/psi/group-000056-soma-000-response-maximum-native.png)|

Просмотрены все восемь перечисленных оригинальных PNG: шесть overview и два terminal native zoom. Их контрольные суммы сохранены в квитанции. Полный ручной просмотр70 изображений не заявляется. [Полная галерея](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/stock-psi-cold/index.html).

В reference видны четыре раздельные вершины. На локальном шаге input2 его вершина различима и исчезает при omit2; более высокий ранний максимум всей пачки не подменяет её. На terminal input1 ранняя вершина содержит вклады нескольких импульсов: omission controls показывают изменение формы и положения. Поэтому ambiguous соответствует согласованному критерию настоящего слияния. Надпись outcome на графике относится к финалу всего Train; selection=valid на локальной группе не означает общего успешного обучения.

PSI меняет форму, амплитуду и задержку отклика. В штатной реализации положительная ветвь проводимости содержит4k·p·(1−k·p)/R, а при отрицательном gate действует отдельное ограничение на время активного входа. Из названия «торможение» не следует уменьшение мембранного пика при том же R. В reference full-before зарегистрированные максимумы .0158285724 для Stock и .0369111058 для PSI; это диагностические максимумы пачки, а не новая общая амплитудная цель. Сравнение сырых амплитуд без учёта изменения усиления не доказывает улучшения или ухудшения разделимости.

## Распознавание и ограничения

PSI terminal state проверен при frozen threshold100 на всех восьми паттернах: TP0/FP0/FN1/TN7, модель не менялась. Это молчание и пропуск target. Полный primary424 members сохранён в42,203,440байтах XZ: [квитанция](PresynapticFrozenPrimaryAcceptance-20261116.json). Elder восстановил424 members, сохранил423 regular files после исключения подтверждённого дублирующего glog alias; построение его независимого восьмипаттернного отчёта запущено отдельно. Новый низкопороговый PSI Test не выполнялся. Текущий Stock moderate recognition с одним фактически проверенным пониженным порогом даёт TP1/FP6/FN0/TN1 и ранние target events: [отчёт](N1ModerateRecognitionScientificReport-20261116.ru.md). Это не завершённая независимая оценка пары PSI/Stock по калиброванному порогу.

Все тяжёлые данные и изображения находятся в /media/user/Data/Nmsdk-StructTrainExpArchive; в Git — код, условия, этот отчёт и проверяемые refs. Training primary Stock52.54MB, PSI51.08MB и сравнительный report43.12MB доступны по своим квитанциям. Исходный setup failure сохранён и не превращён в научный отказ PSI. Полный план и его этап11 остаются частичными; исторические августовские наблюдения сохраняются для своего протокола.
