# Fast terminal21600: распознавание — 16 ноября 2026

**Новый реальный Test при единственном объявленном пороге0.054353792695896797 завершён: TP=1, FP=1, FN=0, TN=6 —7/8.** Target event0.493с следует через3мс после последнего входа0.490с. Единственный FP —phasea-row-4, event8.253с до последнего входа8.492с. Все16 наблюдений двух серий полны/valid; процессы закрыты, модель frozen внутри каждой серии, исходное stopped state неизменно. Это Same-Matrix diagnostic без общего сертификата обучения и без независимой scientific evaluation. [Квитанция, actual trial IDs, timestamps и внешние primary refs](FastN1FullTrainingThresholdScientificAcceptance-20261116.json).

Исходный frozen Test при100 также завершён и принят: execution completed, validity valid, восемь полных наблюдений, модель неизменна. При исходном threshold100 все восемь реакций без спайков: TP=0, FP=0, FN=1, TN=7. Это пропуск target, а не успешная классификация. Production CLI/DATA/physical/frozen проверка1/1, все процессы закрыты. [Квитанция](FastN1FullTrainingFrozenAcceptance-20261116.json).

## Модель и протокол

Использована целиком фактическая terminal-модель [cold Train21600](FastN1FullTrainingScientificReport-20261116.ru.md): revision07101c0b0b29e746ad601050613786b1450f5a733464b501c5738ab92d3d7b22, L=[201,201,121,1], Rs=[86M,86M,9.73184034290068M,86M]Ω, Ns=1. Branch N4/N1, Fast3 C2.5e-10F/TC0.002с/2000Гц. LTMembrane отсутствует; C-trim Off. Conversion=identity, все физические входы включены, reset-per-trial, rotation0, полное2с окно. Train остановлен по бюджету измерительной группы, общего TrainingCertificate нет; Test маркируется diagnostic.

| sample_id | Метка | Recorded LT maximum | Время max, абсолютные с | Max после последнего входа, мс | Спайки при100 |
|---|---|---:|---:|---:|---:|
|phasea-row-0|target|0.0553659185106|0.4935|3.5|0|
|phasea-row-1|foil|0.0529735215422|2.4940|3.5|0|
|phasea-row-2|foil|0.0533416668812|4.4945|3.5|0|
|phasea-row-3|foil|0.0292341910694|6.5745|83.0|0|
|phasea-row-4|foil|0.0715976332951|8.2560|-236.0|0|
|phasea-row-5|foil|0.0530360995858|10.4960|3.5|0|
|phasea-row-6|foil|0.0410902137184|12.3000|-193.0|0|
|phasea-row-7|foil|0.0410902137184|14.7005|207.0|0|

Потенциалы — native model units, SI не подтверждена. Target maximum0.4935с идёт на3.5мс после последнего фактического входа0.49с. У прежнего terminal7200 наибольшая target вершина была до последнего входа. В этой новой nonspiking матрице один foil(row4) выше target, peak margin−0.016231714784472495. Это характеристика записанного потенциала, не подмена настоящего spiking Test. [Числа, actual timestamps, SHA исходных наблюдений и внешняя квитанция](FastN1FullTrainingNonspikingDiagnostics-20261116.json).

Нет также early/late событий. Accuracy7/8 отражает только преобладание отрицательных примеров; target hit rate0. Все фактические входы и полные waveforms сохранены. Прежние Fast TP1/FP3 относятся к другой terminal7200 модели и не переносятся на эту структуру.

## Один объявленный порог и визуальная проверка

После полной приёмки baseline выполнен s11-fast-full-training-threshold-m40-a1, source5248368b75194c657163f51f747f4512605e0e1b/controls0e40284ad7900cc709531d24ac739cd11854e63b. [Протокол](FastN1FullTrainingRecognitionProtocol-20261116.ru.md) зафиксирован заранее: точный native baseline repeat всех8, затем один midpoint-кандидат0.054353792695896797. Proposal SHA256df108918e731e9936a1ffd1569ee9ad6d9bc69d8a8d3f7ab01d3f7fbe808d802. Все исходные baseline waveforms воспроизведены точно. Native candidate завершён; TP1/FP1/FN0/TN6 получены по фактическим спайкам, а не по offline peak proxy.

Порог — единственное объявленное изменение recognition state: baseline revision07101c0b0b29e746ad601050613786b1450f5a733464b501c5738ab92d3d7b22, candidate revision2f22a5732cff349873805d1c6ba637f262ed27792739129b85cbf5a411fa0764. Нового Train, независимой scientific partition и принятого CalibrationResult нет. Target hit1/1; foil response1/7=14.29%; precision1/2=50%. Счёт7/8 здесь включает правильное обнаружение target. При100 тот же accuracy7/8 означал его пропуск. FP до последнего входа учитывается полностью; он не удалён из метрик.

У прежнего terminal7200 было TP1/FP3 и ранний target event. Новый остановленный terminal21600 даёт меньше FP и target после последнего входа, однако пороги у снимков выбирались отдельно по одному заранее заданному правилу. Это сравнение фактических результатов; оно не изолирует причинное действие одной морфологии при фиксированном пороге.

Построен новый actual candidate Soma/LT report:1287PNG, production1/1, процессы закрыты. Просмотрены18 выбранных оригиналов1920×960: все8 Soma overview, все8 native LT peak windows и два дополнительных positive-lobe Soma overview для target/FP. Обычные виды сохраняют полный отрицательный recovery; дополнительные positive-lobe виды явно сообщают об ограничении Y. Все native zoom имеют не менее8px на tick; полный просмотр1287 изображений не заявляется. LTMembrane отсутствует; LT decision channel —штатный $.LTZone.Potential.

Elder независимо восстановил все489 logical members:488 regular files после исключения одного доказанного glog alias. Production DATA/scorer и Soma/LT report завершены1/1, все процессы закрыты: s11-restored-full-training-frozen8-report-elder-a1, sourcec60560a38eeda634947ae5cd3ef3872ee4258b6f/controls679e41adea204bc4ee515c7fad89a4672909d0d7. Метрики воспроизведены точно. Построено1009PNG;16 выбранных оригиналов просмотрены — обзор сомы и native detail максимума LT каждого паттерна. Полного ручного просмотра1009 изображений не заявляется. Самостоятельный replay не создаёт новой научной выборки. [Приёмка и внешние refs](FastN1FullTrainingFrozenTemporalAcceptance-20261116.json).

## Первичные данные

Самодостаточный XZ primary28,003,840байт,489 logical members, SHA25678a197ec5897643e095ef1724be7f18038b6a6997ae420fb582772d922cbef6e. Bundle manifest9506f5413a5a63db9bbcee0bc39098be4eccc19209edb0b44e3a85c6d97a691d. Полная provenance/controls квитанцияa31a3d73c4e3c600273c1ed5c5ad9ba79fc9bedd7ec6c8f61f522d0b0f381050. Точные refs/размеры в [приёмке](FastN1FullTrainingFrozenAcceptance-20261116.json).

Архив и будущий воспроизводимый кэш графиков размещаются во внешнем /media/user/Data/Nmsdk-StructTrainExpArchive, каталогexperiments/2026-11-16/fast-profile-wall-budget/full-training-frozen8-primary-a1.json. Тяжёлые файлы в Git не добавляются.

## Временные графики всех паттернов baseline100

Полный2с отклик показан на общей Y-шкале Soma. LT detail сохраняет native отсчёты около записанного максимума, фактический вход и явное указание threshold100 вне локальной шкалы. Модель LTMembrane не содержит; LT decision channel — штатный $.LTZone.Potential. Длинные абсолютные времена на некоторых деталях записаны с явно напечатанным offset около оси. Потенциалы — model units, SI не подтверждена.

| Паттерн | Soma и фактические входы | LT maximum, native detail |
|---|---|---|
|phasea-row-0|[обзор](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-frozen8-elder/trial-0000-soma-001/overview.png)|[деталь](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-frozen8-elder/trial-0000-lt-decision/measured-peak-00987-detail.png)|
|phasea-row-1|[обзор](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-frozen8-elder/trial-0001-soma-001/overview.png)|[деталь](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-frozen8-elder/trial-0001-lt-decision/measured-peak-00987-detail.png)|
|phasea-row-2|[обзор](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-frozen8-elder/trial-0002-soma-001/overview.png)|[деталь](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-frozen8-elder/trial-0002-lt-decision/measured-peak-00987-detail.png)|
|phasea-row-3|[обзор](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-frozen8-elder/trial-0003-soma-001/overview.png)|[деталь](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-frozen8-elder/trial-0003-lt-decision/measured-peak-01146-detail.png)|
|phasea-row-4|[обзор](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-frozen8-elder/trial-0004-soma-001/overview.png)|[деталь](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-frozen8-elder/trial-0004-lt-decision/measured-peak-00508-detail.png)|
|phasea-row-5|[обзор](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-frozen8-elder/trial-0005-soma-001/overview.png)|[деталь](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-frozen8-elder/trial-0005-lt-decision/measured-peak-00987-detail.png)|
|phasea-row-6|[обзор](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-frozen8-elder/trial-0006-soma-001/overview.png)|[деталь](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-frozen8-elder/trial-0006-lt-decision/measured-peak-00594-detail.png)|
|phasea-row-7|[обзор](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-frozen8-elder/trial-0007-soma-001/overview.png)|[деталь](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-frozen8-elder/trial-0007-lt-decision/measured-peak-01394-detail.png)|

[Полная галерея](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-frozen8-elder/index.html). Primary отчёта162,201,060байт/3106files, SHA25623ad31857c43969f5618d19b19f2d6391ccce3d9aed7813e7703693dfbd27e7d. Все тяжёлые первичные данные и рисунки остаются во внешнем M40 архиве.


## Реальные ответы при выбранном пороге и графики

| Паттерн | Actual spikes, абсолютные с | Итог | Soma: полный отклик / положительная часть | Native LT detail |
|---|---|---|---|---|
|phasea-row-0|0.493|TP|[полный](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-threshold-m40/trial-0000-soma-001/overview.png) / [positive](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-threshold-m40/trial-0000-soma-001/positive-lobe-detail/overview.png)|[деталь](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-threshold-m40/trial-0000-lt-decision/positive-lobe-detail/zoom-010.png)|
|phasea-row-1|нет|TN|[полный](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-threshold-m40/trial-0001-soma-001/overview.png)|[деталь](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-threshold-m40/trial-0001-lt-decision/measured-peak-00987-detail.png)|
|phasea-row-2|нет|TN|[полный](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-threshold-m40/trial-0002-soma-001/overview.png)|[деталь](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-threshold-m40/trial-0002-lt-decision/measured-peak-00987-detail.png)|
|phasea-row-3|нет|TN|[полный](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-threshold-m40/trial-0003-soma-001/overview.png)|[деталь](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-threshold-m40/trial-0003-lt-decision/measured-peak-01146-detail.png)|
|phasea-row-4|8.253|FP|[полный](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-threshold-m40/trial-0004-soma-001/overview.png) / [positive](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-threshold-m40/trial-0004-soma-001/positive-lobe-detail/overview.png)|[деталь](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-threshold-m40/trial-0004-lt-decision/positive-lobe-detail/zoom-006.png)|
|phasea-row-5|нет|TN|[полный](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-threshold-m40/trial-0005-soma-001/overview.png)|[деталь](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-threshold-m40/trial-0005-lt-decision/measured-peak-00987-detail.png)|
|phasea-row-6|нет|TN|[полный](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-threshold-m40/trial-0006-soma-001/overview.png)|[деталь](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-threshold-m40/trial-0006-lt-decision/measured-peak-00594-detail.png)|
|phasea-row-7|нет|TN|[полный](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-threshold-m40/trial-0007-soma-001/overview.png)|[деталь](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-threshold-m40/trial-0007-lt-decision/measured-peak-01394-detail.png)|

[Полная actual candidate галерея](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/fast-full-training-threshold-m40/index.html). Первичные данные двух native серий и исходного frozen run:58,742,968байт XZ/1423 logical members, SHA25664c9d5499c4000ecd686e79731bce4a37ca725a0eb04971850631f6b343f0768. Полный report archive216,794,682байт/3925files, SHA256d80b314db15863c383c27e120c85851d176849fdaae027f2f881149a99448b9b. Все тяжёлые объекты вне Git; exact refs и provenance приведены в квитанции.
