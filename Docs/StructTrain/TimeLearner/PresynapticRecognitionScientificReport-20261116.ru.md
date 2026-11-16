# PSI2.5: реальные ответы всех восьми паттернов — 16.11.2026

При исходном пороге100 остановленная Branch N1 модель молчит на всех восьми паттернах. Один заранее предложенный по объявленной процедуре порог0.189057455929736 проверен настоящим native Test: target обнаружен, но ложные ответы получены на шесть из семи foils. Оба target event возникают до последнего входного импульса. Успешный классификатор полного паттерна этим опытом не подтверждён.

## Модель и процедура

[Холодное PSI2.5 обучение](PresynapticColdScientificReport-20261116.ru.md) остановлено на ambiguous input1 после одного локально готового input2. Общего сертификата нет. Terminal L36/35/27/1, Rs86/2.8800715552629367/20.421499653382123/86MΩ, Ns1/1/1/1. Штатный storage-профиль NSPNeuronGenPreinh2_5;2000Гц, CapturedPerInput/anchor3, C-trim/PostTune Off, LTMembrane отсутствует. Diagnostic recognition явно включает все входы через identity conversion. Порог относится к LTZone.Potential.

Использован неизменяемый runtime root7b495ebf753259ae8b78c6d0eadd561fb3d2c835/Pulse9e7653a400761d6c2f3ea68fddcd40a4307d85e7. Python producer1f551388cf62f2c3d427796c7d5ced635ecd7530, job s11-psi-k2p5-threshold-m40-a2, controls bbefbc6c6770c1873ca5b40b38e1d20a7a14e073. Для каждого паттерна полное2с окно, reset_per_trial; исходная PhaseA матрица, target в первой позиции. Перестановки, изменение ITI и независимая выборка сюда не входят.

Выполнены две реальные native серии по восемь проб: повторный baseline100 и candidate. Baseline waveform samples точно совпали с ранее записанным PSI frozen8. Candidate threshold заранее определён как середина между target maximum и максимальным foil maximum, строго меньшим target. Это Historical Same-Matrix diagnostic на остановленной модели, без заявления завершённого обучения, полноценной калибровки или independent evaluation.

Source recognition revision21f992b5244b7ee673303d7d3b5fc98f2c4bb8bafea5081eaec3272998de8d37. После явной смены порога candidate revision801fb52a215e76151be469804f0612e18e4cdfa6e6d8163c03c669233bee7ef4. Каждая серия сохраняет собственную модель замороженной; равенство revisions моделей с разными порогами не требуется.

## Фактическое распознавание

|Порог|TP|FP|FN|TN|Вывод|
|---|---:|---:|---:|---:|---|
|100|0|0|1|7|Полное молчание, target пропущен|
|0.189057455929736|1|6|0|1|Target реагирует;85.7% foils дают ложный ответ|

|Sample ID|Метка|Спайков при100|Спайков при candidate|Исход candidate|
|---|---|---:|---:|---|
|phasea-row-0|target|0|2|TP по историческому onset-критерию|
|phasea-row-1|foil|0|2|FP|
|phasea-row-2|foil|0|3|FP|
|phasea-row-3|foil|0|0|TN|
|phasea-row-4|foil|0|3|FP|
|phasea-row-5|foil|0|3|FP|
|phasea-row-6|foil|0|7|FP|
|phasea-row-7|foil|0|7|FP|

Оба target event записаны в0.348 и0.380с, раньше последнего входа около0.490с. Пустой массив scorer early_spikes этому не противоречит: он означает отсутствие событий до начала response window, а не отсутствие событий до последнего входа. Эти два временных критерия нельзя смешивать. Полный список фактических событий сохранён в [квитанции](PresynapticThresholdScientificAcceptance-20261116.json).

В baseline target full-response maximum0.206546611039785; максимальный foil0.32439989808365666. Margin target−max(foil)=−0.11785328704387166: target не является самым высоким откликом этой матрицы. Сам по себе offline sweep не заменяет спайковую проверку, поскольку изменение порога может влиять на динамику. Здесь выбранный порог подтверждён реальными прогонами.

Совпадение TP1/FP6 с [умеренным Stock опытом](N1ModerateRecognitionScientificReport-20261116.ru.md) характеризует эти две конкретные остановленные модели. Оно не доказывает общую бесполезность PSI или эквивалентность их физики. Один детерминированный запуск каждого профиля не является серией независимых повторов.

## Графики всех восьми паттернов

Elder независимо восстановил исходный frozen8 package и пересчитал production metrics. Его отчёт завершён1/1,569PNG; полные2с окна и native zoom не прорежены. Восемь overview и восемь увеличений вокруг фактических полных максимумов просмотрены вручную. В увеличениях14.208px/native tick, единая вертикальная шкала между паттернами. Просмотр всех569 изображений не заявляется.

|Sample|Baseline full-response maximum|Полное окно с входами|Native zoom максимума|
|---|---:|---|---|
|target, row0|0.2065466110|[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-frozen8-elder/trial-0000-soma-001/overview.png)|[zoom](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-frozen8-elder/trial-0000-soma-001/zoom-008.png)|
|foil, row1|0.2082815740|[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-frozen8-elder/trial-0001-soma-001/overview.png)|[zoom](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-frozen8-elder/trial-0001-soma-001/zoom-016.png)|
|foil, row2|0.2283752273|[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-frozen8-elder/trial-0002-soma-001/overview.png)|[zoom](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-frozen8-elder/trial-0002-soma-001/zoom-011.png)|
|foil, row3|0.1715683008|[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-frozen8-elder/trial-0003-soma-001/overview.png)|[zoom](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-frozen8-elder/trial-0003-soma-001/zoom-011.png)|
|foil, row4|0.2240067529|[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-frozen8-elder/trial-0004-soma-001/overview.png)|[zoom](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-frozen8-elder/trial-0004-soma-001/zoom-007.png)|
|foil, row5|0.2246396025|[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-frozen8-elder/trial-0005-soma-001/overview.png)|[zoom](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-frozen8-elder/trial-0005-soma-001/zoom-017.png)|
|foil, row6|0.3243998765|[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-frozen8-elder/trial-0006-soma-001/overview.png)|[zoom](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-frozen8-elder/trial-0006-soma-001/zoom-008.png)|
|foil, row7|0.3243998981|[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-frozen8-elder/trial-0007-soma-001/overview.png)|[zoom](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-frozen8-elder/trial-0007-soma-001/zoom-016.png)|

[Полная baseline галерея](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-frozen8-elder/index.html), [приёмка и hashes просмотренных оригиналов](PresynapticFrozenTemporalAcceptance-20261116.json). На overview видны все входные импульсы и возврат к rest-state; увеличение показывает локальную форму вершины. Выбор полного максимума здесь относится к Test. Он не меняет правило Train: максимум закреплённого импульса, настоящие слившиеся вершины ambiguous.

Спайковый candidate отчёт завершён1/1:1121PNG, все восемь Soma и восемь LT decision проекций, полные окна и native zoom. Просмотрены32 оригинала: overview и фокус на первом фактическом спайке для обоих каналов каждого паттерна; для молчащего row3 выбран фактический максимум. На LT-графиках показан реальный порог, на Soma он не переносится. Шкала14.208px/native tick, прореживания нет. [Приёмка и hashes32 просмотренных изображений](PresynapticThresholdTemporalAcceptance-20261116.json). Полный ручной просмотр1121 графика не заявляется.

|Sample|Soma с входами и LT events|LT decision с реальным порогом|LT native zoom|
|---|---|---|---|
|target, row0|[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-threshold-m40/trial-0000-soma-001/overview.png)|[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-threshold-m40/trial-0000-lt-decision/overview.png)|[zoom](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-threshold-m40/trial-0000-lt-decision/zoom-007.png)|
|foil, row1|[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-threshold-m40/trial-0001-soma-001/overview.png)|[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-threshold-m40/trial-0001-lt-decision/overview.png)|[zoom](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-threshold-m40/trial-0001-lt-decision/zoom-015.png)|
|foil, row2|[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-threshold-m40/trial-0002-soma-001/overview.png)|[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-threshold-m40/trial-0002-lt-decision/overview.png)|[zoom](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-threshold-m40/trial-0002-lt-decision/zoom-010.png)|
|foil, row3|[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-threshold-m40/trial-0003-soma-001/overview.png)|[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-threshold-m40/trial-0003-lt-decision/overview.png)|[zoom](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-threshold-m40/trial-0003-lt-decision/zoom-011.png)|
|foil, row4|[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-threshold-m40/trial-0004-soma-001/overview.png)|[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-threshold-m40/trial-0004-lt-decision/overview.png)|[zoom](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-threshold-m40/trial-0004-lt-decision/zoom-007.png)|
|foil, row5|[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-threshold-m40/trial-0005-soma-001/overview.png)|[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-threshold-m40/trial-0005-lt-decision/overview.png)|[zoom](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-threshold-m40/trial-0005-lt-decision/zoom-016.png)|
|foil, row6|[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-threshold-m40/trial-0006-soma-001/overview.png)|[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-threshold-m40/trial-0006-lt-decision/overview.png)|[zoom](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-threshold-m40/trial-0006-lt-decision/zoom-007.png)|
|foil, row7|[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-threshold-m40/trial-0007-soma-001/overview.png)|[overview](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-threshold-m40/trial-0007-lt-decision/overview.png)|[zoom](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-threshold-m40/trial-0007-lt-decision/zoom-015.png)|

[Полная candidate галерея](//10.245.1.12/Nmsdk-StructTrainExpArchive/report-cache/2026-11-16/psi-threshold-m40/index.html). Отрицательные выбросы после LT events являются записанной динамикой с feedback/reset; offline неспайковая кривая не подставляется. Baseline и candidate имеют собственные графики и модели.

## Архив и ограничения

Исходный frozen8 primary67924bf6f3faf3c84970d37da435d3c9d967163d2fc018fe6707b46f15b07a37:424 members/42,203,440B. Новый actual threshold primary81d606dd30443d398633c34947d8fc59dce3a4abd4c8ac566d46ffd9201281ed:804 members/69,650,908B, обе реальные серии и их модели/наблюдения. Bundle manifest f0412ef31d6215f20aee83fcf25760d8b7a1334257e30cb3f0830a4bc403ccdc; provenance03b9c75125cc88e03f2fcc7e00c721b2515c5bc9486ffc2569e602038d3d4928. Elder report archive971c5c21a986c8731f28914fba086e0586f92ed01c422838dfc89437afccc763:105,227,288B/1785 files. Candidate report archive1860717c5fde6f0a427e476d8b34007d02e44f9ca76e2a08de26ab63c212b734:186,950,305B/3427 files.

Все payloads находятся в /media/user/Data/Nmsdk-StructTrainExpArchive; [каталог](//10.245.1.12/Nmsdk-StructTrainExpArchive/experiments/2026-11-16/psi-storage-control). В Git сохранены только компактные refs и документы. [Threshold receipt](PresynapticThresholdScientificAcceptance-20261116.json), [baseline primary](PresynapticFrozenPrimaryAcceptance-20261116.json). Независимый Elder replay нового threshold primary завершён1/1:804 logical members проверены,802 regular files сохранены; два glog aliases исключены только после byte/hash equality проверки. Production restore/audit/scorer точно воспроизвели обе реальные серии. Нового native расчёта, независимой научной выборки или изменения источника нет. [Квитанция](PresynapticThresholdIndependentReplayAcceptance-20261116.json); evidence archive b7c64c903e7b22d43398539f9b9aeaf20d523b0b6b307e38b59c6796382e342b,319025B/49 files, без дублирования1.56GB восстановленной экспансии.

Открыты обучение всех входов, свежий all-input certificate, frozen order/ITI/reset проверки и независимая научная оценка. Августовские визуально подтверждённые4/8–6/8 остаются результатами исходного протокола; этот опыт их не отменяет. Общий план остаётся активным.
