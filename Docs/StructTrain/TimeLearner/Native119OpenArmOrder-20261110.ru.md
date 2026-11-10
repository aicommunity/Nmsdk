# Native119: Branch open-arm order fixture — 10.11.2026

На обоих Linux workers исходный normal119/SDK355 завершён отрицательно:44 выполнены,43 PASS,1 FAIL,75 не запускались.33 leaf groups и outer закрыты, supervisor отсутствуют. Не объявлять эти прогоны работающими или119/119. Полный compact primary сохранён в Git и независимо проверен; исходные результаты не переписываются.

Единственный FAIL: NativeManualControlLifetime/BranchOpenArmCannotOutliveFailedBegin, manual-r20-16. JUnit Elder11.879s, M409.970s: next->inputIndex равен0 при ожидаемом1. Assertion срабатывает после первого принятого входа, до callback с foreign Begin. Это не доказательство дефекта отзыва production control lifetime: тест не дошёл до проверяемой границы.

## Контракт и правка

FinalVerificationSession формирует Classic0→1 и Branch1→0 для N=2. Обратный порядок Branch предусмотрен алгоритмом; менять его ради теста нельзя. Общий fixture ошибочно требовал next1 в обеих топологиях и комментарий предполагал, что Branch открывает baseline route1 вторым.

Правка ограничена Test_PulseLib_CompositeTraining.cpp/WindowManualOpenArmAfterFailedBeginIsRejected:

- Проверять оба индекса: Classic first0/next1, Branch first1/next0.
- При открытии Branch0 допускать штатную временную solo routing, отличную от baseline. Сохранить actual prepared revision, а не требовать baseline до takeover.
- Failed Begin обязан оставить lifecycle актуальным, Need=true, C0 отсутствующим и восстановить исходный baseline graph. Это прежние обязательные assertions после Begin, они сохранены.
- Передать именно original open prepared token в final.ArmCandidateWindow после takeover. Ожидать InvalidObservation с точной причиной native_training_owner_control_replaced, AcceptedInputs=1 и отсутствие certificate. Эти assertions не ослаблены.
- Дополнительный open-arm-routing-context.json сохраняет actual first/open indices и baseline/prepared/after-failed-begin revisions. Формат существующего actual-open-arm.json сохранён.

Production Rdk/PulseLib, физика, defaults, tolerances, расписание и mathematical goal не меняются. Предполагаемая достаточность правки требует runtime-проверки callback и post-Begin restoration; по одному исправленному ASSERT она не объявляется принятой.

## Адресная проверка и полная регрессия

Сначала два cases ClassicOpenArmCannotOutliveFailedBegin и BranchOpenArmCannotOutliveFailedBegin на новом source/runtime. В следующем полном119 оба стоят первыми (manual-r20-15, manual-r20-16); прежние119 IDs/42groups/308 artifact rules сохранены, selected_ids должны соответствовать новому flattened runplan order. Остальные случаи не исключаются, исходные43 PASS не переносятся автоматически на новый source.

Нужны полная серверная syntax compilation изменённого TU, затем реальные2 cases с original JUnit/primary/control/closure, и полное119. Если callback выявит новый реальный lifecycle/route дефект, исправлять владельца и не заменять конкретную причину отказа общим «любой error». Новый corpus reader16 и Console cold7 отложены до получения полного закрытого корпуса. Начальная научная задача8/8 не является критерием этого исправления.

## Сохранённые исходные прогоны и новый запуск

[Elder evidence f73e8e004be38b18e7fc327fe728ed40a304715f](https://github.com/aicommunity/Nmsdk/tree/f73e8e004be38b18e7fc327fe728ed40a304715f/Reports/StructTrain/TimeLearner/Native119NormalFailure-20261110/Elder) содержит2687 originals/432191105bytes, archive4483540bytes. [M40 evidence f6b5e64b59b650aefad30a5811d1001c57d2e2c8](https://github.com/aicommunity/Nmsdk/tree/f6b5e64b59b650aefad30a5811d1001c57d2e2c8/Reports/StructTrain/TimeLearner/Native119NormalFailure-20261110/M40) содержит2687 originals/432415347bytes, archive4510372bytes. Все primary/model/log/JUnit/source-runtime/control files сохранены lossless,33 INFO aliases на каждом сервере описаны в inventory и разрешаются в сохранённые originals. Данные переданы Git pack, оба data refs опубликованы; это не производные PNG/PDF cache.

[Независимая проверка](ValidationPlans/Native119OpenArmPreservation-20261110/verification.json) сверила все5374 originals и hashes, точные44 IDs, единственный failed ID и все66 recorded leaf closures.75 not-run на каждом сервере остаются not-run. Original failure/worker terminal/lease recovery сохранены.

Исправленный source8ec5ec265a5995df75e35cebdb78aab5e89dcfe3/Pulse165/Rdkde413/Bin8cb содержит4078 ожидаемых source files. [Полная syntax compilation TU](ValidationPlans/Native119OpenArmPreservation-20261110/syntax-result.json) завершилась на M40 return0/diagnostics clear/8.6557s; это не2 runtime PASS. Полный отдельный syntax primary ещё не опубликован.

Новые isolated normal builds на [Elder](ValidationPlans/ElderNative119OpenArm-20261110/launch-observation.json) и [M40](ValidationPlans/M40Native119OpenArm-20261110/launch-observation.json) запущены после canonical PASS66.7897s/82.6780s. Те же Release/O3/LLM Off/parallel2 и kernel bounds; active source/runtime предыдущих заданий не изменялись. Supervisor/outer подтверждены живыми. Адресная пара стоит первой; runtime verdict исправления и полный119 ещё отсутствуют.
