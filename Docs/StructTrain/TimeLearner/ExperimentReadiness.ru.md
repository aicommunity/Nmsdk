# Готовность к научным экспериментам — 09.11.2026

## Последнее состояние допуска

[Canonical preparation A2](NativeCanonical25A2Outcome-20261109.ru.md) прошла25/25 metadata проверок на M40. Исправлена только test fixture: читаются exact Scripts Git blobs, production canonical/owner не менялись. Предыдущая A1 сохранила13PASS/12not-run и отдельный setup error.

Свежая полная SDK956 доставлена и сверена:8repos/4030physicalfiles. Следующие обязательные шаги — actual full-SDK canonical preparation, новая сборка и48 адресных native проверок (37 прежних +11 затронутых). Они ещё не выполнены; новый assigned-window научный контур не допущен. Baseline250 и исторические научные результаты сохраняют ранее принятый объём.

Дополнительный открытый алгоритмический/интеграционный пункт подтверждён в Pulse `f7a0e3e63ec29d4647790a695606d1ca32164ef3`, `Core/TimeLearner/NativeLearnedState.cpp`: экспорт service protocol5 явно запрещён с `candidate_window_training_requires_package6`. Поэтому48PASS также не завершит новый Train→export→Test: требуется настоящий versioned package6 и его import/evaluation, без подстановки старого protocol4. Этот запрет сохраняет честность результата; снимать его без полной реализации формата нельзя.

## Уточнение последней проверки 09.11

Последняя попытка A3 на Root `f015db2d4f6ac8c239e07c050ff596524604060c` / Pulse `f7a0e3e63ec29d4647790a695606d1ca32164ef3` завершилась ошибкой компиляции test TU: **0/37 tests, 0 leaf**. Pulse library скомпилирована; девять compiler errors имеют две причины: protected getter в тестовом коде и два EXPECT_THROW на одной строке. Root повторно прочитал terminal и kernel state: MainPID=0, пустой ControlGroup, тот же invocation; полный compiler log совпал по SHA256. [Снимок Root и полный сжатый журнал](../../../Reports/StructTrain/TimeLearner/s07-cold-envelope-manual-corrected-m40-a3-root-observation/terminal-observation.json.gz). Это не scientific FAIL модели и не PASS нового контроллера. Отрицательная публикация `f2a16f8f66814fa2ce064434eb0d1ea4130bd659` доступна в origin; Root независимо повторил metadata verifier9fe07; [receiptb673](../../../Reports/StructTrain/TimeLearner/s07-cold-envelope-manual-corrected-m40-a3-root-observation/build-negative-independent-verification.json) подтверждает0/37tests,154missing rules, exact closure и released lease. Объектный cache переход380→438 проверен по SHA:378 неизменных,2 пересобраны,58 новых,0 потеряно;15 профильных cache entries сохранены. Build завершился до native-runtime preparation: current-runtime-before/after отсутствуют, новый CPP runtime не считается проверенным. Следующее исправление ограничено test TU, production protected API не расширяется.

A3 использовала закрытый build-cache A2 после отдельной проверки сохранности; runtime A3 новый. Это incremental build, а не новая чистая сборка. Исходные A1/A2 observations сохраняются; абзацы ниже про их RUNNING/«ещё не собрана» являются историческими снимками, не текущим состоянием.


## Текущий допуск нового burst-контроллера

Новый контур сопоставления закреплённых пиков пока не допущен к научной серии.
Приняты core143, диагностические пробы и отдельная арифметика окон; это разные
срезы, их нельзя складывать в доказательство готовности всего контроллера.
Elder service-проверка обнаружила потерю уведомления об отменённой пробе.
Исправление на Pulse88 проверено в полном baseline A3 частично:230PASS,
одинFAIL и17NOT RUN. Падение выявило другой дефект cold6 JSON producer:
в actual6 source configurations версия записалась строкой `sample0`.
[Отрицательная попытка независимо принята как отрицательный результат](CompositeFull248A3NegativeAcceptance-20261109.ru.md),
а весь248 и semantic reader этих конфигураций не приняты.

Минимальный исправленный baseline A4 Root478/Pulse4a завершён на M40:
250PASS/0FAIL/error/skip,137leaves/138closedgroups, released lease.
[Native assertions и transport/provenance независимо приняты](CompositeFull250A4Acceptance-20261109.ru.md);
обрыв VPN не потребовал повторного запуска. Код/evidence объединены в
maintained feature branch. [Actual6 native archive reader принят:7/7](CompositeNativeA4Semantic7Acceptance-20261109.ru.md),
на неизменённых archive1 exports; отдельно нужны candidate-window/lifetime gates; App execution3/codecs и будущий
Train5/control-lifetime source не включены в минимальный baseline A4.

Прежние source-only E11/BB1 дополнены общей cold6/cold7/execution3 исправленной
[парой corrected/unfixed](ColdEnvelopeLifetimePairReadiness-20261109.ru.md),
которая доставлена в отдельные source-копии, но ещё не собрана и не получила
runtime-приёмку. Fresh-build worker profile прошёл19/19 configure-only tests на sourcea208
([приёмка и ограничения](NativeAcceptanceWorker.ru.md)); сама будущая SDK-пара ещё не собрана.
Не смешивать эту пару со снимком A4.
27проверок запуска/renderer на другом tool-source и Classic render независимо
приняты. [Выбранный overview просмотрен](ClassicLTReadableOverview-20261109.ru.md):
LT Potential ненулевой, старуюflatpanel объясняет масштаб threshold100.
Full163visualQA не заявляется. Эти проверки не подтверждают качество обучения
и не меняют прежний packet observation valid=False.

Дополнительный source-only blocker archive2: в Root `7ad96da0e66fe1ef51fc76acb2114174ab6a4e68`
`Tests/Integration/Libraries/Test_PulseLib_CompositeTraining.cpp`, `SaveCompositeBoundary`,
для service protocol5 пишет `runtime-plan-scope.json` с `runtime_plan2_exported:false`,
а public reader `composite_archive_case.py` в Root7352 требует оригинальный
`runtime-plan.json`. Поэтому будущие33 native checks и45DATA+8archive1 checks
по отдельности не подтверждают archive2→public CLI. Нужны настоящий owning
runtime2 export, unmocked positive whole-archive2 auditor/CLI и rehashed tamper
на его реальных выходах. Дополнительно source7352
`candidate_window_archive_evidence.py:291–295` передаёт runtime plan в
`validate_protocol`, где ожидается cold configuration7: это разные документы.
Нужен отдельный строгий runtime2 validator/binding test;45DATA+8archive1
не покрывают этот positive join и не принимают archive2.
Не реконструировать недостающий план из index или
старого archive1. Это выявлено чтением исходников, runtime ещё не проверен.

[Scoped reader53 принят](CandidateWindowReader53Acceptance-20261109.ru.md), но следующий73 gate завершился72PASS/1FAIL в fixture boundary; полный runtime2/export admission отсутствует. [Corrected33](ColdEnvelopeLifetime33Launch-20261109.ru.md) остановился при компиляции до0/33 tests из-за missing owning include; отрицательный результат опубликован, direct include исправлен только в source. Исправленная свежая пара готовится отдельно.

До следующего целевого cold Train необходимо последовательно принять:

1. Lifecycle/cancellation и service-интеграцию; получить реальные native-архивы
   через production export и проверить их независимым reader.
2. Неизменяемые исходные references всех входов и candidate windows для
   штатной пачки. При двух отдельных вершинах ранняя допустима; неразличимое
   слияние остаётся ambiguous. Train измеряет закреплённый импульс, Test —
   полный паттерн. Прогноз не заменяет измеренную вершину.
3. Полный model/package roundtrip, cold CLI Train → Test и сохранение frozen
   модели при выбранном протоколе калибровки и оценки.

Python wire67 и collector39 приняты совместно106/106; они проверяют формат и
происхождение данных, а не физическое обучение. Все перечисленные технические
gates должны ссылаться на точные согласованные commits и реальные артефакты.
Подготовленные source-only изменения не получают runtime-допуск автоматически.
Подробности и текущие handles: [единая сводка](ImplementationStatus.ru.md),
[service/архивы](CompositeArchive206AttemptStatus.ru.md),
[границы проверки окон](CandidateWindowScopeReview-20261108.ru.md).

## Ранее проверенные сквозные пути

Сквозной процесс cold Train → boundary continuation → полный model export →
измеренная калибровка с confirmation → frozen evaluation уже выполняется на
реальных компонентах Classic/Branch. **Итоговая научная матрица ещё не готова.**
Проверенные N2 LT engineering cases не заменяют штатную четырёхвходовую модель,
исторические8 паттернов или независимую оценку. Текущий статус всех этапов и
разделение develop/кандидата находятся в [единой сводке](ImplementationStatus.ru.md).

[Запрет повторного учёта общей вершины](AssignedVertexCertificateGuard-2026-11-07.ru.md)
проверен адресно: Elder normal23 и M40 ASan23. Это проверка
контролируемых сигналов в production verifier, без native физических моделей;
исправление не даёт допуска stock burst assignment или всей научной матрице.

## Обязательные условия ограниченной серии

| Условие | Есть | Осталось для допуска целевого научного задания |
|---|---|---|
|Неизменяемый runtime|Раздельные сборки, manifests, actual loaded files/process identities и Git source closure|Принять используемый общий SDK срез; зафиксировать точные code/profile/binary/data hashes именно задания|
|Эффективная физическая модель|Native storage construction, graph readback, полный state transport проверены адресно|Выбрать проверенный профиль, подтвердить дочернюю физику/частоту/связи; не считать parent defaults описанием всего дерева|
|Обучение|Native measured search и completed/stopped outcomes существуют|Получить валидный результат целевого cold Train либо честный unresolved/budget outcome; исправить/исследовать stock burst ambiguity без вымышленных пиков|
|Реальный перенос Train→Test|Экспорт, native import и frozen owner работают в проверенных путях|Сверить полный semantic model fingerprint; после неудачного Train/переноса не оценивать шаблонный Test как обученный|
|Порог|Fixed и measured calibration/confirmation проверены|Явно выбрать Same-Matrix или независимый протокол; любой выбранный порог проверить реальным spiking run|
|Полные наблюдения|Строгие trial/sample IDs, labels/pattern hashes, clocks, windows, spikes и arbitrary-N soma traces|Подтвердить expected set и полные окна каждой объявленной пробы выбранного протокола; отсутствие данных не означает молчания|
|Оценка|Есть versioned scorer и реальные frozen controls|Зафиксировать модель/порог до независимого Test; отделить TP/FP/FN/timing/morphology/robustness от выполнения и сходимости|
|Управление запуском|Public CLI/coordinator, owned cancellation, leases и Git publisher применяются в адресных gates|Preflight выбранных факторов и возможностей, ресурсный бюджет/диск, все primary/model/metric артефакты и проверенная публикация|
|Визуальный отчёт|Production renderer строит все recorded patterns/somas с actual input overlays|Включить в отчёт каждого нового научного задания overview, читаемые zoom/local-Y и visual QA; графики не заменяют scorer|

Существуют команды корневого `python -m Scripts.StructTrain.TimeLearner`:
inventory, preflight/prepare, train/export, calibrate/evaluate, analyze/report,
pipeline, publish и history. Наличие команды не означает поддержки любого
параметра или физического профиля. Для конкретного запуска использовать exact
проверенный source snapshot и capability preflight. Native dataset/clock,
whole graph/storage и параметрические ограничения проверяются до дорогого Train.
Reserved/no-op поля нельзя использовать как действующие факторы эксперимента.

Начальная научная серия должна явно ограничить поддерживаемую область:
Classic/Branch, объявленные N0/N1/profiles и единая частота дерева. C-trim и
PostTune можно оставить выключенными; базовый контур обязан честно завершаться
без них. Включённую неподдерживаемую опцию нельзя молча игнорировать. Новая общая
амплитудная цель, аксонные задержки и другая нелинейная физика не подменяют
рефакторинг исходной задачи CapturedPerInput с опорным входомN−1.

## Что проверено и что это не доказывает

Normal304 и адресные ASan8 SDK2e прошли. ASan133 A3 дал132 passed/1 output-directory
assertion failure; runner исправлен и адресно проверен на прежних бинарниках.
Полный свежий A5 прошёл133/133. Сверены4888 primary members,321 native,
323 Python и335 tool source hashes; fresh closure/released lease подтверждены.
[Точные версии и scope](IntegratedSharedAsan133Verification.json): root2e061/
Pulse12d, без последующих invalid-budget/recovery изменений. Это закрывает
заявленный ASan133 gate, не всю обязательную матрицу SDK. Старые ASan304 относятся
к другому SDK. Detect_leaks=0 не доказывает отсутствие утечек.

Coordinator schema1/schema2 прошёл16/16 cases /40 native phases, попарные CSV
совпали. ConditionSpec binding при этом декларативен; он не доказывает полную
effective-factor attestation. Два engineering N2 LT случая TP2/FP0/FN0/TN2
используют same-matrix calibration с одним повторяемым target и одним foil.
Это более узкий набор, чем прежняя восьмипаттерновая N2 LT серия5/8 с FP3;
её [измеренный результат](ScientificResults-2026-11-03.ru.md) сохраняется.
Суффиксы ModelSpec1/2 не являются версиями
контроллера или независимыми случайными репликами.
[Исходники, результаты и графики](https://github.com/aicommunity/Nmsdk/blob/ec15c06b1a52917b7a1a49abbddbd095e4b6bb7f/Docs/StructTrain/TimeLearner/SharedControllerNovember6Status.ru.md).

На stock NSPNeuronGen без дополнительной LT membrane валидного завершённого
обучения новой целевой серии пока нет. Missing/ambiguous peak, численная ошибка,
неполное окно и отсутствие spike — разные причины. Предсказанное время прихода
не может подтверждать отсутствующий измеренный пик. Не поднимать автоматически
minimum amplitude/tolerances ради положительного verdict и не объявлять локальный
stall доказательством физической невозможности.

## Последовательность научных проверок

1. [Saved-state replay августа](HistoricalAugustReplay.ru.md) уже воспроизвёл
   три исходных результата4/8,5/8,6/8 с первоначальным протоколом. Его receipt
   не является V2 certificate или независимой оценкой.
2. [Настоящий historical cold Train→Test](HistoricalAugustColdStart.ru.md)
   также уже воспроизвёл эти результаты с полным переносом нейрона. Осталось
   legacy/V2 A/B при согласованных исходных условиях. До интерпретации различий
   проверить effective graph/params и реальные волны; совпадение L само по себе
   не доказывает эквивалентность алгоритмов.
3. Frozen evaluation с target в каждой позиции, изменениями порядка и ITI.
   Reset-per-trial и continuous stream проверять отдельно, с полными окнами,
   неизменным learned-state hash и фиксированным порогом.
4. Расширять профили, торможение, C-trim и все PostTune modes после адресной
   приёмки соответствующих возможностей. Не смешивать новую физику с исправлением
   реализации. Влияние LT устанавливать контролируемым A/B, а не сравнением
   одновременно изменённых профилей.

Августовские визуально подтверждённые4/8–6/8 сохраняются как рабочие результаты
исходного протокола с плохой разделимостью. Перестановки и увеличенный ITI тогда
не проверялись; результаты изменённого протокола не отменяют исходное наблюдение.
Same-Matrix разрешён с явной маркировкой, но не выдаётся за независимый Test.
Silent threshold не делает молчаливые target успешной детекцией. СерияD не
возобновляется автоматически;8/8 не является условием завершения рефакторинга.

Сборки, численные проверки и render выполняются на Elder/M40 через jump host.
Синхронизация source/config/results — Git. В Git сохраняются сжатые primary,
модели, метрики и выбранные PNG; полные воспроизводимые отчёты — кэш M40 Data.
[Требования масштаба и visual QA](VisualTestReports.ru.md).

Первая ограниченная серия не требует окончания всей исторической миграции
скриптов и всех удобств очереди. Она требует доказанного сквозного процесса
именно своего задания. Общая рекомендация ControllerVersion2 и завершение
[исходного плана](RefactoringPlan.ru.md) требуют всей обязательной матрицы.
Предыдущая накопительная постановка29.10 с поздними дополнениями сохранена в
[Git](https://github.com/aicommunity/Nmsdk/blob/ec15c06b1a52917b7a1a49abbddbd095e4b6bb7f/Docs/StructTrain/TimeLearner/ExperimentReadiness.ru.md).


## Текущее применение допуска — 07.11.2026

[Fair-domain stock Train](FairDomainStockTrainVerification.json) допущен и
полностью исполнен:8 preflight/8 Train,16 run manifests; все Train остановлены
InvalidObservation. Его диагностическая оценка64 проб и render160 trial/soma
pairs завершены; primary опубликован и проверен, процессы закрыты и lease
released. [Приёмка](FairDomainStockEvaluationVerification.json) связывает
9190 views с фактическими моделями. [Ручная visual QA](FairDomainStockSelectedVisualQA.json)
охватывает четыре PNG. Полный ручной просмотр cache не заявляется.
Это не повод повторять Train или менять текущий runtime. Исторические
наблюдения запуска сохранены в [журнале задания](FairDomainStockEvaluationJobs.json).

Обе серии используют исходную физику без дополнительной LTMembrane.
[Сравнение](FairDomainStockScientificReport-2026-11-07.ru.md) подтверждает расширение
покрытия Advance и неизменность728 Retry CSV, но не улучшение классификации.
Готовность конкретного отрицательного результата и общая рекомендация V2
остаются разными решениями.


[Диагностика каналов](NativeChannelDiagnostics.ru.md) дополнена адресным ASan
того же SDK на M40 и совместными временными графиками Soma/Exc/Inh/Feedback/LT.
Невмешательство observer подтверждено равенством Off/On первичных CSV.
Четыре выбранных рисунка прошли ручную QA; полный кэш не просматривался вручную.
Это подготовка к исправлению измерений, а не новый успешный Train или Test.
Следующий контроль — отдельная одноимпульсная характеристика при неизменном
training target и с явным восстановлением временной конфигурации предъявления.


## Обновление07.11: диагностика волн

[Feedback12 и читаемые temporal figures](FeedbackProfileScientificReport-2026-11-07.ru.md)
завершены в адресной области: baseline reconstruction exact; gain0 устранил
дополнительные maxima в двух состояниях, изменив также амплитуду/время/LT Output.
Это не выбор новой default physics или доказательство разделимости.
[Clock comparator](RelativeClockAlignment.ru.md) исправлен и проверен отдельно;
подтверждённого дефекта model transfer в high replay не было. Training100 study
завершена в диагностическом scope: Branch2 reused, Classic2 выполнены;
[verification](HighThresholdCombinedVerification.json). Механизм missing иvisual
QA ещё требуют анализа. Остаток полного
плана и условия приёмки выше сохраняются.


## Уточнение Console измерителя одиночного отклика

[Console replay Classic/Branch](SingleMaximumConsoleReplay.ru.md) принят на
Root038/Pulse217: четыре операции, пять design tests, точное воспроизведение
архивных и A/B waveforms при threshold0.0117. Уникальный наибольший пик
допускается при нескольких меньших пиках. Это diagnostic single impulse,
а не замена максимума закреплённого импульса в штатном Train burst. Новых
результатов классификации этот gate не добавляет. Построены193 temporal views
на M40; выбранные четыре проверены по оформлению, два дополнительных positive-lobe
увеличения приняты с явной маркировкой clipping и парными full-range видами.
Whole-burst assignment остаётся открытым; ASan native38 запущен отдельно.
