# Fast Branch N1: восемь реальных frozen-паттернов — 16 ноября2026

При исходном threshold100 модель не отвечает ни на один паттерн: TP0/FP0/FN1/TN7. Target пропущен. Все восемь наблюдений полны и valid, модель и исходный обученный пакет неизменны. Это диагностика остановленного Train, общего TrainingCertificate нет. Семь правильных молчаний foil не означают работающую детекцию.

[Полная галерея Soma и входов](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-frozen8-elder/index.html), [native/primary acceptance](FastN1FrozenDiagnosticAcceptance-20261116.json), [независимый replay и временные графики](FastN1FrozenTemporalAcceptance-20261116.json), [исходное обучение](FastN1BracketScientificReport-20261116.ru.md).

## Какая модель проверена

Точный terminal7200 из s11-fast-bracket-wall7200-m40-a1: Branch N4/N1, TLNativeFast3F2000_Neuron, C2.5e-10F/DissociationTC0.002с/2000Гц, LTMembrane отсутствует. L=[122,121,121,1], Rs=[86M,9.73184034290068M,9.73184034290068M,86M]Ω, Ns=1. Входы index1/index2 имеют общую точку подключения и физический банк; индивидуально независимыми их Rs не являются. Solo-модель импортирована полностью, recognition conversion=identity, все физические входы включены.

Model revision f122a9ba82c154cf28e4081fcee0ab1d3b977eaaa19ad659211a4323e6af95f6. Native before/after и source_solo проверены production integration1/1. Source package SHA256 9ee28ee89f7120772efc0278c0990eb58e6199a823f22d04c3b4ce9b8ac290cb. Нативный runtime root7b495ebf753259ae8b78c6d0eadd561fb3d2c835/Pulse9e7653a400761d6c2f3ea68fddcd40a4307d85e7 не пересобирался и не изменялся во время задания.

## Все паттерны и читаемый масштаб

Исходная PhaseA матрица revision1c1464e248f8744e858bd66df0be99e39969fd65, порядок rotation0. Reset-per-trial, полное окно2с; таблица использует фактически записанные времена. Время максимума отсчитано от первого фактического входа данного паттерна. Значения — native model units, SI для потенциала не подтверждена. В этой nonspiking baseline максимумы LT potential и Soma1 совпадают численно; метрики определяются реальными spike events.

| Паттерн | Метка | Фактические входы от onset, мс | Глобальный максимум | Время от onset, с | LT spikes при100 | Графики Soma+inputs |
|---|---|---|---:|---:|---:|---|
| phasea-row-0 | target | 0.0; 80.0; 240.0; 480.0 | 0.0560300622014 | 0.2435 | 0 | [обзор](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-frozen8-elder/trial-0000-soma-001/overview.png), [native zoom](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-frozen8-elder/trial-0000-soma-001/zoom-006.png) |
| phasea-row-1 | foil | 0.0; 240.0; 400.0; 480.0 | 0.0559880448687 | 0.4835 | 0 | [обзор](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-frozen8-elder/trial-0001-soma-001/overview.png), [native zoom](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-frozen8-elder/trial-0001-soma-001/zoom-010.png) |
| phasea-row-2 | foil | 0.0; 160.0; 240.0; 480.0 | 0.0563355523413 | 0.4835 | 0 | [обзор](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-frozen8-elder/trial-0002-soma-001/overview.png), [native zoom](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-frozen8-elder/trial-0002-soma-001/zoom-010.png) |
| phasea-row-3 | foil | 0.0; 160.0; 320.0; 480.0 | 0.0300170118807 | 0.4035 | 0 | [обзор](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-frozen8-elder/trial-0003-soma-001/overview.png), [native zoom](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-frozen8-elder/trial-0003-soma-001/zoom-009.png) |
| phasea-row-4 | foil | 0.0; 20.0; 240.0; 480.0 | 0.0769129413876 | 0.2440 | 0 | [обзор](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-frozen8-elder/trial-0004-soma-001/overview.png), [native zoom](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-frozen8-elder/trial-0004-soma-001/zoom-006.png) |
| phasea-row-5 | foil | 0.0; 240.0; 460.0; 480.0 | 0.0560505143405 | 0.4835 | 0 | [обзор](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-frozen8-elder/trial-0005-soma-001/overview.png), [native zoom](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-frozen8-elder/trial-0005-soma-001/zoom-010.png) |
| phasea-row-6 | foil | 0.0; 40.0; 80.0; 480.0 | 0.0461003469422 | 0.2875 | 0 | [обзор](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-frozen8-elder/trial-0006-soma-001/overview.png), [native zoom](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-frozen8-elder/trial-0006-soma-001/zoom-006.png) |
| phasea-row-7 | foil | 0.0; 400.0; 440.0; 480.0 | 0.0461003469422 | 0.6875 | 0 | [обзор](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-frozen8-elder/trial-0007-soma-001/overview.png), [native zoom](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-frozen8-elder/trial-0007-soma-001/zoom-014.png) |

Каждый обзор охватывает всё окно наблюдения и имеет общую Y-шкалу для сравнения амплитуд. Native zoom:1920×960,14.208px на timestep0.5мс, без прореживания. Для широких максимумов rows6/7 просмотрен также следующий участок: [row6 после максимума](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-frozen8-elder/trial-0006-soma-001/zoom-007.png), [row7 после максимума](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-frozen8-elder/trial-0007-soma-001/zoom-015.png). Максимум находится близко к границе исходного zoom; соседний вид показывает спад.

Лично просмотрены18 оригинальных PNG: восемь обзоров, восемь zoom максимума и два следующих участка. Всего создано432PNG с SVG/PDF; полный ручной просмотр432 изображений не заявляется. Галерея этого подэтапа содержит Soma; отдельные LT decision projections с фактическим порогом/событиями остаются открытой частью полного временного протокола и будут опубликованы вместе с реальным threshold study. Приёмка полного протокола не объявляется.

## Что следует из наблюдений

Target имеет первый глобальный максимум0.05603006220139539 в абсолютное время0.2535с — до последнего входа0.49с, за0.2365с. Это nonspiking максимум, не target event. На обзоре видны несколько разных вершин; Test использует общий максимум полного отклика. При обучении по-прежнему требуется максимум закреплённого импульса.

Три foil имеют глобальный максимум выше target; полный nonspiking peak margin=-0.02088287918618892. Эти maxima служат диагностикой разделимости и предложением порога. Их нельзя выдавать за измеренный результат spiking Test при другом пороге, поскольку событие LT меняет последующую динамику.

На рисунках видны быстрые пики около входов и более поздние широкие волны. Причинная декомпозиция по отдельным путям этим frozen8 не выполнена. Частичная сходимость input2 и эти совпадения не дают сертификата всей модели.

## Независимая проверка и данные

Elder восстановил все459 logical members primary побайтно, сохранив458 regular files после одного явно подтверждённого glog alias. Исходного каталога M40 на Elder нет. Production restore/audit/scorer воспроизвёл метрики1/1; temporal report также проверен этим сценарием. Это независимый анализ сохранённых данных, новая научная выборка или новое native обучение не создавались.

Первичный архив SHA256 9ad4b3c9cfe52f58f65b640a67eae6e4a2802c33009dfa9a7980b11c650279f5,25409028байт; он восстанавливает1.4835GB исходных files/aliases. Независимый отчёт SHA256 18df83e2c42e8eef161e0d8b8e8c7069f3d62b22f9f0908e20232a6642cf8d99,81211346байт/1374files. Полные модели, CSV, изображения и повторно создаваемый HTML cache находятся в /media/user/Data/Nmsdk-StructTrainExpArchive, Git хранит компактные refs и документы.

## Следующие уже объявленные опыты

[Один Same-Matrix threshold diagnostic](FastN1ThresholdDiagnosticProtocol-20261116.ru.md) повторяет исходный baseline на том же SDK и затем измеряет реальные spikes всех восьми паттернов при одном фиксированном пороге. Его результаты пока не приняты. [Один cold21600с](FastN1FullTrainingProtocol-20261116.ru.md) даёт текущему алгоритму конечное дополнительное время для оставшихся входов, сохраняя физику, исходные допуски и логические бюджеты. Ни один из этих будущих результатов не предполагается положительным заранее.
