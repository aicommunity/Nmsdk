# Диагностический отчёт измерительного тракта — 8 ноября 2026

Проверен тракт штатные native callbacks → capture → portable packet/CSV →
независимый reader → временные графики. Выполнены четыре контрольные пробы
Classic/Branch при2000 и20000 Гц. Это фиксированные контрольные модели N=2;
завершённое структурное обучение и классификация здесь не исследовались.

При обучении целью остаётся максимум отклика закреплённого импульса.
При тестировании общий максимум реакции служит характеристикой вместе с
фактическими спайками. Попадание вершины во временное окно само по себе не
доказывает её происхождение; диагностические domain packets не допускаются
к TrainingCertificate. Общая вершина/плато остаётся неоднозначной.

| Контроль | Частота | Записанные сомы |
|---|---:|---|
| Classic |2000 Гц|Soma1,Soma2|
| Branch |2000 Гц|Soma1|
| Classic |20000 Гц|Soma1,Soma2|
| Branch |20000 Гц|Soma1|

## Данные и проверки

Producer primary: `b10750b5cde0c9977b0d1861f3c205a4ef3fdd07`.
Renderer source: `b7312b9fd6abaf7fae74e2f54f63a924fa9892f4`.
Schema2 report evidence: `23e78e7e0e9fbd44a6052468b600ad247f02eaae`;
Elder renderer tests: `b093dd227d0c9cba728343120922fcb6eaf92c01`.

[Normal capture/codec](ResponseDomainEvidenceNormalVerification.json),
[ASan capture/codec](ResponseDomainEvidenceAsanVerification.json),
[совместный old/new output](ResponseDomainJointOutputVerification.json),
[проверка schema2 отчёта](ResponseDomainTemporalCenteredVerification.json).
По5 renderer tests прошли на каждом сервере без skipped. Локально выполнены
проверка Git/hash/metadata и визуальный просмотр; расчёт моделей и рендер —
только на серверах.

В полном кэше132 рисунка для шести сочетаний «проба×сома»: overview,
последовательные100-тактовые tiles и дополнительные input views вокруг
каждого фактического события. Во всех видах наложен записанный вход,
пунктиром отмечены его реальные timestamps. Детальные виды имеют не менее
8px на такт; input views содержат20 тактов до события и80 после, в пределах
записи. Отсчёты не прорежены. ОбщийY используется для соответствующей сомы
одной топологии между частотами. Единицы потенциала native; SI не подтверждён.

Восемь выбранныхPNG проверены визуально: шесть overview совпадают побайтно
с ранее просмотренными, два новых input views просмотрены при1920×960.
Все132 рисунка вручную не просматривались. Input views показывают фронт и
спад входа, но их короткое окно не обязано включать поздний максимум;
для него служат overview и последовательные tiles.

## Все контрольные реакции

### Classic,2000 Гц,Soma1

![Classic,2000 Гц,Soma1](../../../Reports/StructTrain/TimeLearner/s07-domain-reports-m40-a3/selected/case-0001-Classic/channel-000-overview.png)

### Classic,2000 Гц,Soma2

![Classic,2000 Гц,Soma2](../../../Reports/StructTrain/TimeLearner/s07-domain-reports-m40-a3/selected/case-0001-Classic/channel-001-overview.png)

### Branch,2000 Гц,Soma1

![Branch,2000 Гц,Soma1](../../../Reports/StructTrain/TimeLearner/s07-domain-reports-m40-a3/selected/case-0002-Branch/channel-000-overview.png)

### Classic,20000 Гц,Soma1

![Classic,20000 Гц,Soma1](../../../Reports/StructTrain/TimeLearner/s07-domain-reports-m40-a3/selected/case-0003-Classic/channel-000-overview.png)

### Classic,20000 Гц,Soma2

![Classic,20000 Гц,Soma2](../../../Reports/StructTrain/TimeLearner/s07-domain-reports-m40-a3/selected/case-0003-Classic/channel-001-overview.png)

### Branch,20000 Гц,Soma1

![Branch,20000 Гц,Soma1](../../../Reports/StructTrain/TimeLearner/s07-domain-reports-m40-a3/selected/case-0004-Branch/channel-000-overview.png)

## Входной импульс в крупном масштабе

Оба вида привязаны к actual event `pulse0`, timestamp0.01005s. Они показывают
записанный вход и начало реакции, без утверждения о принадлежности вершины.

![Classic,Soma1,20000 Гц,input-001](../../../Reports/StructTrain/TimeLearner/s07-domain-reports-m40-a3/selected/case-0003-Classic/channel-000-input-001.png)

![Branch,Soma1,20000 Гц,input-001](../../../Reports/StructTrain/TimeLearner/s07-domain-reports-m40-a3/selected/case-0004-Branch/channel-000-input-001.png)

## Хранение и ограничения

Полный воспроизводимый HTML/SVG/PNG кэш на M40:
`/media/user/Data/TimeLearnerRefactor/ReportsCache/domain-evidence-normal-a3/figures/index.html`.
В Git находятся сжатые primary, метрики и выбранныеPNG. Кэш не является
единственным доказательством: входные файлы связаны с исходным Git archive
контрольными суммами, а отчёт воспроизводится штатным renderer.

Эта проверка подтверждает согласованность producer/consumer на указанных
контролях. Она не подтверждает причинную принадлежность пика, полную матрицу
физики, завершённый Train, accuracy/FP/FN или8/8. Спайковая классификация этим
отчётом не оценивалась. Августовские4/8–6/8 относятся к собственному протоколу
и здесь не пересматриваются.
