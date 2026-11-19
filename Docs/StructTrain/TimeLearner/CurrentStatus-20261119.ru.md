# TimeLearner: проверенный статус на 19 ноября 2026

Цель этапов0–12 активна. Полностью принят только этап0; этапы1–12 частичны.
Новые изменения находятся в feature-ветке; accepted root develop остаётся
87e7da0205b6bb0d582f7b4f2551c935fd7f2350. Научные8/8 не являются условием
успешного рефакторинга. Scope отдельных успешных проверок не расширяется до
полной приёмки поддерживаемых режимов.

## Текущие научные задания

На двух workers одновременно выполняются первоначальные cold N4 Train:

- M40: Branch/On,547 записанных native probe packets в последнем срезе.
  [Точный handle и наблюдение](../../../Reports/StructTrain/TimeLearner/TerminalScienceAB-20261119/branch-on-observation.json).
- Elder: Classic/On,143 записанных native probe packets в последнем срезе.
  [Точный handle](../../../Reports/StructTrain/TimeLearner/TerminalScienceAB-20261119/classic-on-running.json).

В обоих случаях supervisor и native kernel groups живы, последняя проба
complete/valid, terminal результата ещё нет. Количество native packets не
является процентом выполнения или сертификатом. Срез проверен19.11 около16:58МСК;
[readback обоих workers](../../../Reports/StructTrain/TimeLearner/TerminalScienceAB-20261119/status-readback-1658-msk.json).
Серийный номер search в trial_id учитывает также изменения модели и не является
счётчиком использованных logical probes. Действует исходный
[A/B протокол](TerminalPolicyScienceAB-20261119.ru.md): CapturedPerInput,
N1, sync0.02, amplitude1e−5/rel0, один sweep,24 candidates/input,
160 logical probes,10000 model seconds; C-trim/PostTune/autoThreshold Off.

Classic/On переназначен с M40 на Elder: исходные bytes подписанного Train
и initial inputs не изменены. Старый M40 Classic/On не запускался и не должен
запускаться повторно. Native Root893/Pulsec508 одинаковы; runtime identities
отдельных сборок сохранены. [Назначение и лимиты](../../../Reports/StructTrain/TimeLearner/TerminalScienceAB-20261119/classic-on-assignment.json).
Classic/Off и Branch/Off подготовлены, ещё не запущены.

После каждого Train приоритет — actual-state Test всех8 паттернов, реальное
подтверждение выбранного порога и читаемые Soma/input графики. Для stopped8
подготовлен проверенный diagnostic reader: Test использует actual graph,
historical source не подставляется вместо него. Completed Train требует
штатного recognition export/evaluation. Незавершённое обучение сохраняет свой
исходный статус. [Подготовка](../../../Reports/StructTrain/TimeLearner/TerminalScienceAB-20261119/evaluation-preparation.json).

## Что закрыто последними проверками

- Native A8:78/78 PASS, все группы закрыты, полный primary опубликован.
  [Архив](../../../Reports/StructTrain/TimeLearner/TerminalPortable-20261119/m40-a8-accepted.archive.json).
- Production13:13/13 PASS, включая4 real Console cases и16 frozen observations.
  [Архив](../../../Reports/StructTrain/TimeLearner/TerminalPortable-20261119/m40-production13-console4-a3.archive.json).
- Остальные12 Console cases на Elder:2/2 test methods PASS,42 native operations,
 6 completed и6 restored stopped Train,48 frozen observations. Все группы
  закрыты;2727 members полного primary проверены и сохранены на M40.
  [Архив](../../../Reports/StructTrain/TimeLearner/TerminalPortable-20261119/elder-console-remaining12-a1.archive.json).
- Вместе закрыты16 объявленных N2 вариантов Classic/Branch × Fixed4/Window5 ×
  N0/N1 × completed/restored. Это не полная физическая/режимная матрица и не
  N4 научная сходимость. [Покрытие](../../../Reports/StructTrain/TimeLearner/TerminalPortable-20261119/Console16-coverage.json).
- Elder SDK: свежая сборка Console и7/7 physical model cases.
  [Primary](../../../Reports/StructTrain/TimeLearner/TerminalPortable-20261119/elder-recognition7-a1.archive.json).
- Recorded-source DATA3:3/3 на реальных restored Classic/Branch источниках,
  включая отказ при повреждении external CSV и разделение actual/historical epoch.
  [Primary](../../../Reports/StructTrain/TimeLearner/TerminalPortable-20261119/elder-recorded-source3-a1.archive.json).

Все прежние отказы A2–A6/DATA36/DATA11 сохранены как отрицательные outcomes.
Последующие исправления не переименовывают их в PASS.

## Подтверждённые научные результаты

| Модель и протокол | TP | FP | FN | TN | Ограничения |
|---|---:|---:|---:|---:|---|
|Cold Classic,8 исходных паттернов|1|2|0|5|Same-Matrix threshold; Train BudgetExhausted, certificate отсутствует.|
|Cold Branch,8 исходных паттернов|1|2|0|5|Те же ограничения.|
|Сохранённая Elder Branch,8 исходных паттернов|1|1|0|6|Порог0.09874840158355691 подтверждён actual Test; stopped модель.|
|Та же Elder Branch, цель и3 новых foil|1|0|0|3|Модель/порог frozen до новых ответов; одна модель, знакомый target.|

Первые два результата подтверждены фактическими спайками с выбранными
порогами, не только offline maxima. [Cold threshold отчёт](FairInputColdThresholdStudy-20261118.ru.md).
Heldout4 не отменяет FP исходной матрицы и не является независимым повторным
обучением. [Архив и audit](../../../Reports/StructTrain/TimeLearner/SingleSweepBranch-20261118/frozen-heldout4-primary.archive.json).
Новых N4 результатов классификации текущих двух Train пока нет.
Августовские визуальные4/8–6/8 сохраняются для своего исходного протокола.

Работающие примеры уже пригодны для промежуточного научного отчёта и DOCX.
Завершение N4 обучения с общим сертификатом исходных timing/amplitude допусков
в текущей серии ещё не подтверждено. Систематическое сравнение контроллеров,
режимов и физических профилей остаётся основной научной частью до итогового отчёта.

## Готовность этапов

| Этап | Реализовано и проверено в части области | Что удерживает полную приёмку |
|---|---|---|
|0|Согласованное начальное объединение develop/gitlinks.|Этап принят.|
|1|Исторические источники, реестры дефектов и публичных параметров.|Оставшиеся audit unknowns, inherited properties и effective-factor coverage.|
|2|Изолированные сборки/runtime, manifests, внешний архив и восстановление primary.|Полная build/resource/fault matrix и closure всех принятых публикаций.|
|3|Строгие ID/completeness/finite проверки, versioned scorer, реальные frozen observations.|Полнота исторических адаптеров и единый verdict во всей поддерживаемой области.|
|4|Настоящие lifecycle/storage/physical DATA fixtures.|Полная fresh/reuse/Copy/Load/Build/growth/heterogeneous и режимная матрица.|
|5|Export/import, stopped/completed state, native Train→Test roundtrip.|Остальные физические/связевые варианты и независимое восстановление полного корпуса. Mid-probe resume не обещается.|
|6|Общий native service/controller и Classic/Branch adapters.|Legacy/V2 A/B, оставшееся дублирование, отдельная multirate verification.|
|7|Measured bounded L/Ns/Rs search, N0 repeats, причины остановки, final verification; explicit terminal restore проверен44/44 M40 и14/14 Elder.|Полная bounds/physics/reset/C-search матрица и научные N4 A/B. Portable переход и16 объявленных N2 Console cases приняты адресно.|
|8|Solo/recognition state, transactions, реальное подтверждение порога, первые unseen foil.|Все PostTune/inhibition/reset modes и расширенная независимая frozen evaluation.|
|9|Корневой пакет/CLI, manifest357 и адресные migration gates.|Оставшиеся Bin analysis/matrix/shared tools и callers; complete=false.|
|10|Owned groups, leases/budgets, provenance и fail-closed publisher.|Полная effective-factor, cancel/recovery/publication fault matrix.|
|11|Реальные положительные и отрицательные результаты, order/window/reset проверки отдельных моделей, временные отчёты.|Систематическая legacy/V2 и физическая/режимная матрица, новые независимые условия и повторы.|
|12|Поддерживаемые отчёты; DOCXv3 Classic15/Branch14 страниц,9 примеров,29 страниц проверены.|Сквозная сверка root/PulseLib/Bin/config/ClDesc, завершение миграции и очередная актуализация примеров.|


## Данные и документы

В feature подготовлена поддержка прямого физического DATA export из solo
terminal8 и дополнительные native/Python проверки. Серверная приёмка ещё
не выполнена. На Windows .14 запущен отдельный fresh SDK build; kernel Job жив,
в приватном source проверены5092 файла и восемь репозиториев.
Это третья вычислительная машина для инженерной проверки; научные Train
продолжаются на M40/Elder, их runtime остаются прежними. Это работа этапа5,
а не новый научный результат. [Контракт и оставшиеся проверки](TerminalPhysicalData8-20261119.ru.md).

Тяжёлые primary, модели и полные галереи находятся только в
`/media/user/Data/Nmsdk-StructTrainExpArchive`; Git содержит код, документы
и компактные ссылки. [Политика и Samba](ExternalExperimentArchive.ru.md).
Для возвращения Elder к науке удалены4064 точных архивных JSON/CSV дубля
из трёх закрытых старых заданий,12.913GB. Проверены11 kernel units, hash/size
каждого файла и наличие central primary. Не совпавшие файлы, source/runtime
и уникальные данные сохранены. Дополнительно удалён только проверенный локальный
дубль54MB уже опубликованного архива. [План и квитанции](../../../Reports/StructTrain/TimeLearner/TerminalScienceAB-20261119/elder-science-capacity-restored.json).

DOCXv3 Classic/Branch:15+14 страниц,9 работающих примеров, все29 страниц
проверены. Следующая актуализация примеров следует после новых фактических Test;
эксперименты имеют приоритет. Полная матрица, завершение миграции и stage merges
children-first через--no-ff остаются обязательными.

Предыдущий полный срез этой сводки сохранён в Git commit
170dae54951c2a1b8b4c629a4a48c44b8b413ecd по тому же пути. Датированные отчёты и первичные измерения сохранены;
их старые live-статусы относятся к своим снимкам.
